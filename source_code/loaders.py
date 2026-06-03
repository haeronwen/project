import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent/ "data" / "clean"

TRANSPORT_MONTHLY = 1280 / 12
LEISURE_MONTHLY = 2000


# HOUSING LOADERS


def load_apartments() -> pd.DataFrame:
    """
    Load apartments with monthly cost (for scenarios/comparisons)
    """
    filepath = DATA_DIR / "apartment_monthly_cost.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_apartment_district_stats() -> pd.DataFrame:
    """Load apartment statistics aggregated by district (for housing analysis)"""
    filepath = DATA_DIR / "apartment_district_stats.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_apartments_clean() -> pd.DataFrame:
    """Load detailed apartments data (for deep analysis)"""
    filepath = DATA_DIR / "apartments_clean.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)



def load_dorms() -> pd.DataFrame:
    """Load dorm statistics (for baseline comparison)"""
    filepath = DATA_DIR / "dorm_stats.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)

# FOOD LOADERS

def load_canteen() -> pd.DataFrame:
    """Load canteen cost lookup table (days_per_week -> monthly_cost)"""
    filepath = DATA_DIR / "canteen_costs.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_groceries_basket() -> pd.DataFrame:
    """Load groceries basket breakdown (item-by-item costs)"""
    filepath = DATA_DIR / "groceries_basket.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)


def load_groceries_full() -> pd.DataFrame:
    """Load raw grocery data from all stores (for detailed analysis/optimization)"""
    filepath = DATA_DIR / "groceries_full.csv"
    if not filepath.exists():
        raise FileNotFoundError(f"Missing data file: {filepath}")
    return pd.read_csv(filepath)
