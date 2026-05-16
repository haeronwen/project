import pandas as pd
from pathlib import Path 

DATA_DIR=Path(__file__).parent.parent/"data"/"clean"

#manually researched constants
TRANSPORT_MONTHLY=1280/12
LEISURE_MONTHLY=2000

def load_apartments()->pd.DataFrame:
    """
    load cleaned apartment rent data
    columns: zone, disposition_clean, avg_rent, people, avg_rent_per_person
    """
    return pd.read_csv(DATA_DIR/"apartment_monthly_cost.csv")

def load_dorms()->pd.DataFrame:
    """
    load cleaned dorm pricing data
    columns: beds, facilities, avg_cost, count
    """
    return pd.read_csv(DATA_DIR/"dorm_stats.csv")

def load_canteen()->pd.DataFrame:
    """
    load canteen monthly cost by days per week
    columns: days_per_weel, monthly_cost
    """
    return pd.read_csv(DATA_DIR/"canteen_costs.csv")

def load_groceries_basket()->pd.DataFrame:
    """
    load cheapest grocery basket with per-item monthly costs
    columns: item, unit_price, qty_per_month, monthly_cost
    """
    return pd.read_csv(DATA_DIR/"groceries_basket.csv")

def get_groceries_monthly()->float:
    """
    return total monthly grocery cost from the basket 
    """
    return load_groceries_basket()["monthly_cost"].sum()

