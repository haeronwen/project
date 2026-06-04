from locale import currency

import requests
import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Prague Student Cost of Living", layout="wide", page_icon=":school:")

from source_code.cost_calculator import compute_monthly_cost, build_scenario_table, get_housing_cost, get_dorm_options

ZONE_MAP = {
    "Center": "center",
    "Inner city": "inner_city",
    "Outer city / suburbs": "outer_or_suburbs",
}

ROOM_TYPES = ["GARSONIERA", "1+KK", "1+1", "2+KK", "2+1", "3+KK", "3+1", "4+KK", "4+1"]
ROOM_ORDER = {r: i for i, r in enumerate(ROOM_TYPES)}

CATEGORY_LABELS = {
    "housing": "Housing & rent",
    "canteen": "University canteen",
    "groceries": "Groceries",
    "transport": "Public transport",
    "leisure": "Leisure",
}

CURRENCY_SYMBOLS = {
    "CZK": "Kč", "EUR": "€", "USD": "$", "GBP": "£",
    "PLN": "zł", "HUF": "Ft", "NOK": "kr", "SEK": "kr", "CHF": "Fr",
}

FALLBACK_RATES = {
    "CZK": 1.0, "EUR": 0.040, "USD": 0.044, "GBP": 0.035,
    "PLN": 0.18, "HUF": 16.2, "NOK": 0.47, "SEK": 0.46, "CHF": 0.039,
}

@st.cache_data(ttl=259200)
def fetch_fx_rates():
    currencies = ",".join(c for c in CURRENCY_SYMBOLS if c != "CZK")
    try:
        r = requests.get(
            f"https://api.frankfurter.dev/v2/rates?base=CZK&quotes={currencies}",
            timeout=5
        )
        data = r.json()
        rates = {"CZK": 1.0}
        rates.update(data["rates"])
        return rates
    except Exception:
        return FALLBACK_RATES

PIE_COLORS = ["#4A7C72", "#C0513A", "#D4A043", "#7B9E87", "#B8956A"]

def fmt(czk):
    converted = czk * rate
    symbol = CURRENCY_SYMBOLS[currency]
    if currency == "CZK":
        return f"{converted:,.0f} Kč"
    if currency in ("HUF", "NOK", "SEK", "PLN", "CHF"):
        return f"{converted:,.0f} {symbol}"
    return f"{symbol}{converted:,.0f}"

st.markdown("""
<style>
    div[data-testid="stMetric"] { 
        background: rgba(128,128,128,0.1); 
        border-radius: 8px; 
        padding: 0.6rem 1rem;
        border: 1px solid rgba(128,128,128,0.2);
    }
</style>
""", unsafe_allow_html=True)

fx_rates = fetch_fx_rates()

title_col, fx_col = st.columns([4, 1])
with title_col:
    st.title("Cost of Living Simulator for Students in Prague")
    st.caption("Estimates your monthly cost of living based on your lifestyle choices.")
with fx_col:
    st.write("")
    st.write("")
    currency = st.selectbox("Display currency", list(CURRENCY_SYMBOLS.keys()), index=0,
                        help="Rates updated from the European Central Bank.")

rate = fx_rates.get(currency, FALLBACK_RATES[currency])

st.divider()


left, right = st.columns([1, 1.6])

with left:
    st.subheader("Your Preferences")

    housing_type = st.radio("Accommodation type", ["Apartment", "Dorm"], horizontal=True)
    if housing_type == "Apartment":
        st.caption("Data from [Bezrealitky.cz](https://bezrealitky.cz)")
    else:
        st.caption("Data from [rehos.cuni.cz](https://rehos.cuni.cz)")

    people = 1

    if housing_type == "Apartment":
        c1, c2, c3 = st.columns(3)
        with c1:
            zone_display = st.selectbox("Zone", list(ZONE_MAP.keys()),
                help="Center = Praha 1-2, Inner city = Praha 3-7, Outer = Praha 8+")
            zone = ZONE_MAP[zone_display]
        with c2:
            disposition = st.selectbox("Room type", ROOM_TYPES, index=1,
                help="+KK = kitchenette, +1 = separate kitchen, GARSONIERA = bedsit")
        with c3:
            people = st.number_input("Sharing", min_value=1, max_value=4, value=1,
                help="Rent is split equally between occupants")
    else:
        available_beds, dorms_df = get_dorm_options()
        c1, c2 = st.columns(2)
        with c1:
            beds = st.selectbox("Beds per room", sorted(available_beds))
        with c2:
            available_facilities = dorms_df[dorms_df["beds"] == beds]["facilities"].unique().tolist()
            facilities_options = []
            for f in ["Shared", "Private"]:
                val = "No" if f == "Shared" else "Yes"
                if val in available_facilities:
                    facilities_options.append(f)
            facilities = st.radio("Bathroom", facilities_options)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Food**")
        canteen_days = st.slider("Canteen days / week", 0, 5, 3,
            help="Student meal ~100 CZK. Reduces grocery spend.")

        grocery_basket = st.radio(
            "Diet",
            ["Standard", "Vegan"],
            horizontal=True,
            help="Vegan basket replaces meat, dairy and eggs with plant-based alternatives.",
        )

        grocery_store = st.radio(
            "Grocery shopping",
            ["Physical store", "Online delivery", "Average"],
            horizontal=True,
            help="Physical store = Billa/Lidl average. Online = Rohlik/Košík average (~35% pricier).",
        )

        with st.expander("Where are the canteens?"):
            st.markdown("""
| Canteen | Area | Hours (Mon-Thu) |
|---|---|---|
| [Menza Arnosty z Pardubic](https://kam.cuni.cz/KAM-389.html) | Nové Město | 10:45-14:15 |
| [Menza Jednota](https://kam.cuni.cz/KAM-388.html) | Nové Město | 10:45-15:00 |
| [Menza Kajetanka](https://kam.cuni.cz/KAM-392.html) | Praha 6 | 11:00-14:15 |
| [Menza Budec](https://kam.cuni.cz/KAM-391.html) | Vinohrady | 10:45-14:15 |
| [Menza Troja](https://kam.cuni.cz/KAM-396.html) | Trója | 10:45-14:15 |
| [Menza Pravnicka](https://kam.cuni.cz/KAM-387.html) | Staré Město | 11:00-14:15 |
| [Menza Albertov](https://kam.cuni.cz/KAM-390.html) | Albertov | 11:30-15:00 |
| [Menza Malostranska](https://kam.cuni.cz/KAM-769.html) | Malá Strana | 11:00-14:00 |
""")
            st.caption("Closed Sat-Sun. Fri hours shorter. Student meal ~70-100 CZK with ISIC.")

    with c2:
        st.markdown("**Leisure**")
        cinema = st.slider("Cinema / month", 0, 15, 1, help="~180 CZK per visit")
        pub    = st.slider("Pub visits / month", 0, 20, 4, help="~250 CZK per visit")
        cafe   = st.slider("Cafe visits / week", 0, 14, 2, help="~100 CZK per visit")
        gym    = st.checkbox("Gym membership", value=False, help="~1,000 CZK/month")


with right:
    st.subheader("Your Estimated Monthly Costs")

    housing_cost = get_housing_cost(
        housing_type=housing_type,
        zone=zone if housing_type == "Apartment" else None,
        disposition=disposition if housing_type == "Apartment" else None,
        people=people,
        beds=beds if housing_type == "Dorm" else None,
        facilities=facilities if housing_type == "Dorm" else None,
    )
    if housing_cost is None:
        st.warning("No data for this combination. Try different options.")
        st.stop()

    # map UI choices to basket/store params
    basket = "vegan" if grocery_basket == "Vegan" else "standard"
    if grocery_store == "Physical store":
        store = "physical"
    elif grocery_store == "Online delivery":
        store = "online"
    else:
        store = "online"  # average: use online as default, handled in compute_monthly_cost

    breakdown = compute_monthly_cost(
        housing_cost=housing_cost,
        canteen_days=canteen_days,
        basket=basket,
        store=store,
        cinema_per_month=cinema,
        pub_per_month=pub,
        cafe_per_week=cafe,
        gym=gym,
    )

    breakdown_display = {k: v for k, v in breakdown.items() if k != "total"}

    st.metric("Estimated Monthly Total", fmt(breakdown["total"]))

    pie_col, table_col = st.columns([1.2, 1])

    with pie_col:
        labels = [CATEGORY_LABELS.get(k, k) for k in breakdown_display]
        values = list(breakdown_display.values())
        fig = px.pie(
            values=values,
            names=labels,
            hole=0.4,
            color_discrete_sequence=PIE_COLORS,
        )
        fig.update_traces(textposition="outside", textinfo="percent")
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1, y=0.5, font=dict(size=11)),
            margin=dict(t=10, b=10, l=0, r=120),
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width='stretch')

    with table_col:
        table_data = pd.DataFrame({
            "Category": [CATEGORY_LABELS.get(k, k) for k in breakdown_display],
            f"Monthly cost ({currency})": [fmt(v) for v in breakdown_display.values()],
        })
        st.dataframe(table_data, hide_index=True, width='stretch', height=212)

        housing_pct = round(breakdown["housing"] / breakdown["total"] * 100)
        data_source = "scraped from Bezrealitky.cz" if housing_type == "Apartment" else "scraped from rehos.cuni.cz"
        grocery_source = "Rohlik & Košík" if store == "online" else "Billa & Lidl"
        st.caption("Transport: [PID annual student pass](https://pid.cz/tarif-web/stud.php?cat=STU&lt=1&range=P-7&noprg=0&nolt=0&lang=en) — 1,280 Kč/year")
st.divider()


st.subheader("Compare Similar Housing Options")

scenario_df = build_scenario_table(
    people=people,
    canteen_days=canteen_days,
    basket=basket,
    store=store,
    cinema_per_month=cinema,
    pub_per_month=pub,
    cafe_per_week=cafe,
    gym=gym,
)

if housing_type == "Apartment":
    apt_df = scenario_df[scenario_df["type"] == "apartment"].copy()
    current_idx = ROOM_ORDER.get(disposition, 1)

    st.markdown(f"**{disposition} — rent per person by zone**")
    same_disp_rows = sorted(
        [(label, row) for label, row in apt_df.iterrows() if f"Flat {disposition} " in label],
        key=lambda x: next((i for i, z in enumerate(["Center", "Inner city", "Outer/suburbs"]) if z in x[0]), 99)
    )
    if same_disp_rows:
        cols = st.columns(len(same_disp_rows))
        for col, (label, row) in zip(cols, same_disp_rows):
            zone_name = label.replace(f"Flat {disposition} (", "").rstrip(")")
            title = f"{zone_name}{' (yours)' if zone_display in label else ''}"
            if people > 1:
                col.metric(title, fmt(row["housing"]), f"Total: {fmt(row['housing'] * people)}")
            else:
                col.metric(title, fmt(row["housing"]))

    adjacent = [r for r, i in ROOM_ORDER.items() if abs(i - current_idx) == 1]
    if adjacent:
        st.markdown(f"**Smaller / larger options in {zone_display}**")
        adj_cards = []
        for disp in adjacent:
            match = next(
                ((disp, row["housing"]) for label, row in apt_df.iterrows()
                 if f"Flat {disp} " in label and f"({zone_display})" in label),
                None
            )
            if match is None:
                match = next(
                    ((disp, row["housing"]) for label, row in apt_df.iterrows()
                     if f"Flat {disp} " in label),
                    None
                )
            if match:
                adj_cards.append(match)

        if adj_cards:
            cols2 = st.columns(len(adj_cards))
            for col, (disp, rent) in zip(cols2, adj_cards):
                direction = "smaller" if ROOM_ORDER[disp] < current_idx else "larger"
                if people > 1:
                    col.metric(f"{disp} ({direction})", fmt(rent), f"Total: {fmt(rent * people)}", )
                else:
                    col.metric(f"{disp} ({direction})", fmt(rent))

else:
    filtered = scenario_df[scenario_df["type"] == "dorm"].copy()

    # same bed count — own vs shared bathroom
    st.markdown(f"**{beds}-bed room — bathroom options**")
    same_beds = filtered[filtered.index.str.contains(f"{beds}-bed")]
    if not same_beds.empty:
        cols = st.columns(len(same_beds))
        for col, (label, row) in zip(cols, same_beds.iterrows()):
            bath = "own bathroom" if "own" in label else "shared bathroom"
            title = f"{bath}{' (yours)' if (facilities == 'Private') == ('own' in label) else ''}"
            col.metric(title, fmt(row["housing"]))

    # same bathroom type — other bed counts
    bath_str = "own bathroom" if facilities == "Private" else "shared bathroom"
    other_beds = filtered[
        filtered.index.str.contains(bath_str) &
        ~filtered.index.str.contains(f"{beds}-bed")
    ]
    if not other_beds.empty:
        st.markdown(f"**Other room sizes — {bath_str}**")
        cols2 = st.columns(min(len(other_beds), 4))
        for col, (label, row) in zip(cols2, other_beds.iterrows()):
            col.metric(label, fmt(row["housing"]))

