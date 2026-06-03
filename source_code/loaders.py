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


def get_groceries_monthly(basket: str = "standard", store: str = "online") -> float:
    """
    Return monthly grocery cost for a given basket and store type.
    
    Args:
    basket: "standard" or "vegan" or "budget"
    store:  "online" (Rohlik + Košík avg) or "physical" (Billa + Lidl avg) or "cheapest"
    
    Returns:
    float: monthly cost in CZK
    
    If no custom file exists, calculates from groceries_basket.csv
    """
    filepath = DATA_DIR / "grocery_monthly.csv"
    
    # Try loading pre-calculated table
    if filepath.exists():
        df = pd.read_csv(filepath)
        row = df[(df["basket"] == basket) & (df["store"] == store)]
        if len(row) > 0:
            return float(row["monthly"].values[0])
    
    # Fallback: calculate from basket if only 'standard' requested
    if basket == "standard":
        basket_df = load_groceries_basket()
        return float(basket_df["monthly_cost"].sum())
    
    raise ValueError(f"No grocery data for basket='{basket}', store='{store}'")

