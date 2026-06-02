import streamlit as st
import plotly.express as px
import sys
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from cost_calculator import compute_monthly_cost, build_scenario_table
from source_code.loaders import load_apartments, load_dorms

# ── Constants ─────────────────────────────────────────────────────────────────

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

# Approximate rates from CZK - TODO: replace with live scrape from frankfurter.app
FX_RATES = {
    "CZK": (1.0,   "Kč"),
    "EUR": (0.040, "€"),
    "USD": (0.044, "$"),
    "GBP": (0.035, "£"),
    "PLN": (0.18,  "zł"),
    "HUF": (16.2,  "Ft"),
    "NOK": (0.47,  "kr"),
    "SEK": (0.46,  "kr"),
    "CHF": (0.039, "Fr"),
}

PIE_COLORS = ["#4A7C72", "#C0513A", "#D4A043", "#7B9E87", "#B8956A"]

# ── Helper functions ───────────────────────────────────────────────────────────

def fmt(czk):
    """Convert a CZK amount to the selected display currency and format it."""
    converted = czk * rate
    if currency == "CZK":
        return f"{converted:,.0f} Kč"
    return f"{symbol}{converted:,.0f}"


def get_store_groceries(store):
    """
    Calculate monthly grocery cost from raw store prices.
    store: 'lidl' (physical) or 'rohlik' (online delivery)
    """
    basket = pd.read_csv(Path(__file__).parent / "data/clean/groceries_basket.csv")
    raw = pd.read_csv(Path(__file__).parent / f"data/raw/{store}_prices.csv")

    cheapest = raw.groupby("item")["price"].min().reset_index()
    merged = basket.merge(cheapest, on="item", how="left")
    merged["final_price"] = merged["price"].fillna(merged["unit_price"])
    return float((merged["final_price"] * merged["qty_per_month"]).sum())


# ── Page setup ─────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Prague Student Cost of Living", layout="wide", page_icon="🏰")
st.markdown("""
<style>
    div[data-testid="stMetric"] { background: #f8f9fa; border-radius: 8px; padding: 0.6rem 1rem; }
</style>
""", unsafe_allow_html=True)

title_col, fx_col = st.columns([4, 1])
with title_col:
    st.title("Cost of Living Simulator for Students in Prague")
    st.caption("Estimates your monthly cost of living based on your lifestyle choices.")
with fx_col:
    st.write("")
    st.write("")
    currency = st.selectbox("Display currency", list(FX_RATES.keys()), index=0,
                            help="Exchange rates are approximate.")

rate, symbol = FX_RATES[currency]

st.divider()

# ── Inputs ─────────────────────────────────────────────────────────────────────

left, right = st.columns([1, 1.6])

with left:
    st.subheader("Your Preferences")

    housing_type = st.radio("Accommodation type", ["Apartment", "Dorm"], horizontal=True)

    # default people=1 for dorm path so build_scenario_table always has it
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
        c1, c2 = st.columns(2)
        with c1:
            available_beds = sorted(load_dorms()["beds"].unique().tolist())
            beds = st.selectbox("Beds per room", available_beds)
        with c2:
            dorms_df = load_dorms()
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
        grocery_store = st.radio(
            "Grocery shopping",
            ["Physical store", "Online delivery", "Average"],
            horizontal=True,
            help="Physical store e.g. Lidl, online delivery e.g. Rohlik (~35% pricier)",
        )
        with st.expander("Where are the canteens?"):
            st.markdown("""
| Canteen | Area | Hours (Mon-Thu) |
|---|---|---|
| [Menza Arnosty z Pardubic](https://kam.cuni.cz/KAM-389.html) | Nove Mesto | 10:45-14:15 |
| [Menza Jednota](https://kam.cuni.cz/KAM-388.html) | Nove Mesto | 10:45-15:00 |
| [Menza Kajetanka](https://kam.cuni.cz/KAM-392.html) | Praha 6 | 11:00-14:15 |
| [Menza Budec](https://kam.cuni.cz/KAM-391.html) | Vinohrady | 10:45-14:15 |
| [Menza Troja](https://kam.cuni.cz/KAM-396.html) | Troja | 10:45-14:15 |
| [Menza Pravnicka](https://kam.cuni.cz/KAM-387.html) | Stare Mesto | 11:00-14:15 |
| [Menza Albertov](https://kam.cuni.cz/KAM-390.html) | Albertov | 11:30-15:00 |
| [Menza Malostranska](https://kam.cuni.cz/KAM-769.html) | Mala Strana | 11:00-14:00 |
""")
            st.caption("Closed Sat-Sun. Fri hours shorter. Student meal ~70-100 CZK with ISIC.")

    with c2:
        st.markdown("**Leisure**")
        cinema = st.slider("Cinema / month", 0, 15, 1, help="~180 CZK per visit")
        pub    = st.slider("Pub visits / month", 0, 20, 4, help="~250 CZK per visit")
        cafe   = st.slider("Cafe visits / week", 0, 14, 2, help="~100 CZK per visit")
        gym    = st.checkbox("Gym membership", value=False, help="~1,000 CZK/month")

# ── Results ────────────────────────────────────────────────────────────────────

with right:
    st.subheader("Your Estimated Monthly Costs")

    apartments = load_apartments()
    dorms_df = load_dorms()

    if housing_type == "Apartment":
        row = apartments[
            (apartments["zone"] == zone) &
            (apartments["disposition_clean"] == disposition)
        ]
        if len(row) == 0:
            st.warning("No data for this combination. Try a different zone or room type.")
            st.stop()
        housing_cost = float(row["avg_rent"].values[0]) / people
    else:
        facilities_val = "Yes" if facilities == "Private" else "No"
        row = dorms_df[(dorms_df["beds"] == beds) & (dorms_df["facilities"] == facilities_val)]
        if len(row) == 0:
            st.warning(f"No data for {beds}-bed rooms with {facilities.lower()} bathroom.")
            st.stop()
        housing_cost = float(row["avg_cost"].values[0])

    if grocery_store == "Physical store":
        groceries = get_store_groceries("lidl")
    elif grocery_store == "Online delivery":
        groceries = get_store_groceries("rohlik")
    else:
        groceries = None

    breakdown = compute_monthly_cost(
        housing_cost=housing_cost,
        canteen_days=canteen_days,
        groceries=groceries,
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
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        table_data = pd.DataFrame({
            "Category": [CATEGORY_LABELS.get(k, k) for k in breakdown_display],
            f"Monthly cost ({currency})": [fmt(v) for v in breakdown_display.values()],
        })
        st.dataframe(table_data, hide_index=True, use_container_width=True, height=212)

        housing_pct = round(breakdown["housing"] / breakdown["total"] * 100)
        data_source = "scraped from Bezrealitky.cz" if housing_type == "Apartment" else "scraped from rehos.cuni.cz"
        st.caption(
            f"Housing is {housing_pct}% of total ({data_source}). "
            f"Groceries from Lidl and Rohlik price data. "
            f"Transport = PID student pass. Leisure is user estimate."
        )
        st.text_input("🔗 Share this configuration", value="", placeholder="URL sharing coming soon...", disabled=True)

st.divider()

# ── Compare Similar Housing Options ───────────────────────────────────────────

st.subheader("Compare Similar Housing Options")

scenario_df = build_scenario_table(
    people=people,
    canteen_days=canteen_days,
    cinema_per_month=cinema,
    pub_per_month=pub,
    cafe_per_week=cafe,
    gym=gym,
)

if housing_type == "Apartment":
    apt_df = scenario_df[scenario_df["type"] == "apartment"].copy()
    current_idx = ROOM_ORDER.get(disposition, 1)

    # Same room type across all zones
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
            col.metric(title, fmt(row["housing"]))

    # Smaller / larger options in the same zone
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
                col.metric(f"{disp} ({direction})", fmt(rent))

else:
    filtered = scenario_df[scenario_df["type"] == "dorm"].copy()
    st.markdown("**All dorm options — rent comparison**")
    cols = st.columns(min(len(filtered), 4))
    for col, (label, row) in zip(cols, filtered.iterrows()):
        col.metric(label, fmt(row["housing"]))