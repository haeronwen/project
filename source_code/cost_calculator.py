import pandas as pd
from source_code.loaders import (
    load_apartments,
    load_dorms,
    load_canteen,
    get_groceries_monthly,
    TRANSPORT_MONTHLY
)

# Leisure prices based on Prague estimates
CINEMA_PRICE = 180
PUB_PRICE = 250
CAFE_PRICE = 100
GYM_MONTHLY = 1000
WEEKS_PER_MONTH = 4.33

ZONE_LABELS = {
    "center": "Center",
    "inner_city": "Inner city",
    "outer_or_suburbs": "Outer/suburbs"
}

canteen = load_canteen().set_index("days_per_week")["monthly_cost"]


def get_canteen_cost(days_per_week: int) -> float:
    """Monthly canteen cost for 0-5 days/week. Returns 0 if days_per_week is 0."""
    if days_per_week == 0:
        return 0
    return float(canteen.loc[days_per_week])


def compute_leisure_cost(
        cinema_per_month: int = 1,
        pub_per_month: int = 4,
        cafe_per_week: int = 2,
        gym: bool = False) -> float:
    """Total monthly leisure cost. Prices: cinema 180, pub 250, cafe 100, gym 1000 CZK."""
    return (
        cinema_per_month * CINEMA_PRICE
        + pub_per_month * PUB_PRICE
        + cafe_per_week * WEEKS_PER_MONTH * CAFE_PRICE
        + (GYM_MONTHLY if gym else 0)
    )


def compute_monthly_cost(
        housing_cost: float,
        canteen_days: int = 5,
        groceries: float = None,
        transport: float = TRANSPORT_MONTHLY,
        cinema_per_month: int = 1,
        pub_per_month: int = 4,
        cafe_per_week: int = 2,
        gym: bool = False) -> dict:
    """Itemised monthly cost breakdown. Grocery spend reduced proportionally with canteen days."""
    if groceries is None:
        groceries = get_groceries_monthly()

    grocery_reduction = (canteen_days / 5) * 0.4
    adjusted_groceries = groceries * (1 - grocery_reduction)

    breakdown = {
        "housing": housing_cost,
        "canteen": get_canteen_cost(canteen_days),
        "groceries": adjusted_groceries,
        "transport": transport,
        "leisure": compute_leisure_cost(cinema_per_month, pub_per_month, cafe_per_week, gym),
    }
    breakdown["total"] = sum(breakdown.values())
    return breakdown


def build_scenario_table(
        people: int = 1,
        canteen_days: int = 5,
        cinema_per_month: int = 1,
        pub_per_month: int = 4,
        cafe_per_week: int = 2,
        gym: bool = False) -> pd.DataFrame:
    """Comparison table of monthly costs across all housing options.

    For apartments, avg_rent is divided by `people` so the comparison
    always reflects the per-person cost consistent with the user's sharing setting.
    """
    dorms = load_dorms()
    apartments = load_apartments()
    rows = []

    for _, row in dorms.iterrows():
        facilities = "own bathroom" if row["facilities"] == "Yes" else "shared bathroom"
        cost = compute_monthly_cost(
            housing_cost=row["avg_cost"],
            canteen_days=canteen_days,
            cinema_per_month=cinema_per_month,
            pub_per_month=pub_per_month,
            cafe_per_week=cafe_per_week,
            gym=gym,
        )
        cost["label"] = f"Dorm {row['beds']}-bed ({facilities})"
        cost["type"] = "dorm"
        rows.append(cost)

    for _, row in apartments.iterrows():
        zone_label = ZONE_LABELS.get(row["zone"], row["zone"])
        cost = compute_monthly_cost(
            housing_cost=row["avg_rent"] / people,
            canteen_days=canteen_days,
            cinema_per_month=cinema_per_month,
            pub_per_month=pub_per_month,
            cafe_per_week=cafe_per_week,
            gym=gym,
        )
        cost["label"] = f"Flat {row['disposition_clean']} ({zone_label})"
        cost["type"] = "apartment"
        rows.append(cost)

    return pd.DataFrame(rows).set_index("label")