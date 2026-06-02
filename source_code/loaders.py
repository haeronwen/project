import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "clean"

TRANSPORT_MONTHLY = 1280 / 12


def load_apartments() -> pd.DataFrame:
    filepath = DATA_DIR / "apartment_monthly_cost.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_dorms() -> pd.DataFrame:
    filepath = DATA_DIR / "dorm_stats.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_canteen() -> pd.DataFrame:
    filepath = DATA_DIR / "canteen_costs.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def get_groceries_monthly(basket: str = "standard", store: str = "online") -> float:
    """
    Return monthly grocery cost for a given basket and store type.
    basket: 'standard' or 'vegan'
    store:  'online' (Rohlik + Košík avg) or 'physical' (Billa + Lidl avg)
    """
    filepath = DATA_DIR / "grocery_monthly.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    df = pd.read_csv(filepath)
    row = df[(df["basket"] == basket) & (df["store"] == store)]
    if len(row) == 0:
        raise ValueError(f"No grocery data for basket='{basket}', store='{store}'")
    return float(row["monthly"].values[0])
