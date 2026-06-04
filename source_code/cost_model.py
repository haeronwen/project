import pandas as pd
from source_code.loaders import (
    load_apartments,
    load_dorms,
    load_canteen,
    load_groceries_basket,
    TRANSPORT_MONTHLY,
    LEISURE_MONTHLY
)

# Load canteen once at module level 
canteen = load_canteen().set_index("days_per_week")["monthly_cost"]


# CANTEEN COST FUNCTION

def get_canteen_cost(days_per_week: int) -> float:
    """
    Return monthly canteen cost for a given number of days per week.
    
    Uses canteen_costs.csv which contains pre-calculated costs for each frequency.
    Returns 0 if days_per_week is 0 (no canteen usage).
    
    Args:  
        days_per_week: int (0-5) - number of days per week eating at canteen
    
    Returns: 
        float: monthly cost in CZK
    
    Raises:
        ValueError: if days_per_week not in 0-5
    """
    if days_per_week == 0:
        return 0
    
    try:
        return float(canteen.loc[days_per_week])
    except KeyError:
        raise ValueError(f"Invalid days_per_week: {days_per_week}. Must be 0-5.")


# MONTHLY COST COMPUTATION

def compute_monthly_cost(
        housing_cost: float,
        canteen_days: int = 5,
        groceries: float = None,
        transport: float = TRANSPORT_MONTHLY,
        leisure: float = LEISURE_MONTHLY,
        lunch_share: float = 0.4) -> dict:

    full_grocery_basket = load_groceries_basket()["monthly_cost"].sum()
    
    if groceries is None:
        # Scale down groceries based on how many lunches canteen covers
        home_lunch_cost = full_grocery_basket * lunch_share
        other_food_cost = full_grocery_basket * (1 - lunch_share)
        home_lunch_remaining = home_lunch_cost * (5 - canteen_days) / 5
        groceries = other_food_cost + home_lunch_remaining

    canteen_cost = get_canteen_cost(canteen_days)

    breakdown = {
        "housing": housing_cost,
        "canteen": canteen_cost,
        "groceries": groceries,
        "transport": transport,
        "leisure": leisure
    }
    breakdown["total"] = sum(breakdown.values())
    return breakdown


# SCENARIO BUILDING

def build_scenario_table(canteen_days: int = 5) -> pd.DataFrame:
    """
    Build a comprehensive comparison table of monthly costs across all housing options.
    
    Iterates over all dorm configurations and apartment types from cleaned data,
    computes monthly cost for each using compute_monthly_cost(), and returns
    a single DataFrame for comparison and visualization.
    
    Args:
        canteen_days (int, 0-5): default canteen usage frequency
                                Can be changed per scenario
    
    Returns:
        pd.DataFrame: indexed by housing label with columns:
            - housing: float (just the housing cost)
            - canteen: float
            - groceries: float
            - transport: float
            - leisure: float
            - total: float (full monthly cost)
            - type: str ('dorm' or 'apartment')
    """
    dorms = load_dorms()
    apartments = load_apartments()
    rows = []

    # DORM SCENARIOS 
    for idx, row in dorms.iterrows():
        # Format facilities description
        facilities = "own facilities" if row["facilities"] == "Yes" else "shared facilities"
        
        # Compute full cost breakdown
        cost = compute_monthly_cost(row["avg_cost"], canteen_days=canteen_days)
        
        # Add metadata
        cost["label"] = f"Dorm {row['beds']}-bed ({facilities})"
        cost["type"] = "dorm"
        
        rows.append(cost)

    # APARTMENT SCENARIOS 
    for idx, row in apartments.iterrows():
        # Compute full cost breakdown (avg_rent_per_person = shared apartment)
        cost = compute_monthly_cost(row["avg_rent_per_person"], canteen_days=canteen_days)
        
        # Add metadata
        cost["label"] = f"Flat {row['disposition_clean']} {row['zone']}"
        cost["type"] = "apartment"
        
        rows.append(cost)

    # Return as DataFrame indexed by label for easy lookup
    df = pd.DataFrame(rows).set_index("label")
    
    return df

# INSIGHTS 

def get_cost_insights() -> dict:
    """
    Extract key insights from all scenarios.
    
    Returns:
        dict: statistics about living costs
    """
    df = build_scenario_table(canteen_days=5)
    
    dorms = df[df["type"] == "dorm"]
    apartments = df[df["type"] == "apartment"]
    
    return {
        "cheapest_option": {
            "name": df["total"].idxmin(),
            "cost": df["total"].min()
        },
        "most_expensive_option": {
            "name": df["total"].idxmax(),
            "cost": df["total"].max()
        },
        "dorm_average": dorms["total"].mean(),
        "apartment_average": apartments["total"].mean(),
        "housing_dominance": (df["housing"].mean() / df["total"].mean()) * 100,
        "cost_ratio": df["total"].max() / df["total"].min()
    }