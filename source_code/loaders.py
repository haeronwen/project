import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "clean"

TRANSPORT_MONTHLY = 1280 / 12
LEISURE_MONTHLY = 2000


# HOUSING LOADERS

def load_apartments() -> pd.DataFrame:
    """Load apartments with monthly cost (for scenarios)"""
    try:
        return pd.read_csv(DATA_DIR / "apartment_monthly_cost.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'apartment_monthly_cost.csv'}")


def load_apartment_district_stats() -> pd.DataFrame:
    """Load apartment statistics aggregated by district (for housing analysis)"""
    try:
        return pd.read_csv(DATA_DIR / "apartment_district_stats.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'apartment_district_stats.csv'}")


def load_apartments_clean() -> pd.DataFrame:
    """Load detailed apartments data (for deep analysis)"""
    try:
        return pd.read_csv(DATA_DIR / "apartments_clean.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'apartments_clean.csv'}")

def load_apartments_app() -> pd.DataFrame:
    """Load full 9-disposition apartment data for the app"""
    return pd.read_csv(DATA_DIR / "apartment_monthly_cost_app.csv")

def load_dorms() -> pd.DataFrame:
    """Load dorm statistics (for baseline comparison)"""
    try:
        return pd.read_csv(DATA_DIR / "dorm_stats.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'dorm_stats.csv'}")


# FOOD LOADERS

def load_canteen() -> pd.DataFrame:
    """Load canteen cost lookup table (days_per_week -> monthly_cost)"""
    try:
        return pd.read_csv(DATA_DIR / "canteen_costs.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'canteen_costs.csv'}")


def load_groceries_basket() -> pd.DataFrame:
    """Load groceries basket breakdown (item-by-item costs)"""
    try:
        return pd.read_csv(DATA_DIR / "groceries_basket.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'groceries_basket.csv'}")


def load_groceries_full() -> pd.DataFrame:
    """Load raw grocery data from all stores (for detailed analysis)"""
    try:
        return pd.read_csv(DATA_DIR / "groceries_full.csv")
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing data file: {DATA_DIR / 'groceries_full.csv'}")
    
def get_groceries_monthly(basket: str = "standard", store: str = "online") -> float:
    """Return monthly grocery cost for a given basket and store type for app"""
    filepath = DATA_DIR / "grocery_monthly.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    df = pd.read_csv(filepath)
    row = df[(df["basket"] == basket) & (df["store"] == store)]
    if len(row) == 0:
        raise ValueError(f"No grocery data for basket='{basket}', store='{store}'")
    return float(row["monthly"].values[0])