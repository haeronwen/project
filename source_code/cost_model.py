import pandas as pd
from source_code.loaders import (
    load_apartments,
    load_apartments_clean,
    load_dorms,
    load_canteen,
    load_groceries_basket,
    load_groceries_full,
    get_groceries_monthly,
    TRANSPORT_MONTHLY,
    LEISURE_MONTHLY
)

# Load canteen once at module level 
canteen = load_canteen().set_index("days_per_week")["monthly_cost"]


# ============================================
# CANTEEN COST FUNCTION
# ============================================

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
    
    if days_per_week not in canteen.index:
        raise ValueError(f"Invalid days_per_week: {days_per_week}. Must be 0-5.")
    
    return float(canteen.loc[days_per_week])


# MONTHLY COST COMPUTATION

def compute_monthly_cost(
        housing_cost: float,
        canteen_days: int = 5,
        groceries: float = None,
        transport: float = TRANSPORT_MONTHLY,
        leisure: float = LEISURE_MONTHLY) -> dict:
    """
    Compute itemized monthly cost of living for a Prague student.
    
    Combines housing, food (canteen + groceries), transport, and leisure 
    into a detailed cost breakdown.
    
    Args:
        housing_cost (float): monthly housing cost in CZK
        canteen_days (int, 0-5): number of days per week eating at canteen
        groceries (float, optional): monthly grocery budget in CZK
                                   If None, uses standard basket from data
        transport (float, optional): monthly transport cost
                                   Default: PID student monthly pass (~107 CZK)
        leisure (float, optional): monthly leisure budget
                                  Default: 2000 CZK (estimated for cinema, pub, gym, etc.)
    
    Returns:
        dict: breakdown with keys:
            - housing: float
            - canteen: float
            - groceries: float
            - transport: float
            - leisure: float
            - total: float (sum of all components)
    """
    # Fallback to standard grocery basket if not provided
    if groceries is None:
        groceries = get_groceries_monthly(basket="standard", store="online")

    # Build itemized breakdown
    breakdown = {
        "housing": housing_cost,
        "canteen": get_canteen_cost(canteen_days),
        "groceries": groceries,
        "transport": transport,
        "leisure": leisure
    }
    
    # Add total as sum of all components
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


# COMPARISON FUNCTIONS

def compare_scenarios(scenario1: dict, scenario2: dict) -> dict:
    """
    Compare two living scenarios side-by-side.
    
    Args:
        scenario1, scenario2 (dict): output from compute_monthly_cost()
    
    Returns:
        dict: comparison metrics
    """
    total_diff = scenario2["total"] - scenario1["total"]
    pct_diff = (total_diff / scenario1["total"]) * 100
    
    return {
        "scenario1_total": scenario1["total"],
        "scenario2_total": scenario2["total"],
        "difference": total_diff,
        "percent_difference": pct_diff,
        "breakdown_diffs": {
            key: scenario2[key] - scenario1[key]
            for key in ["housing", "canteen", "groceries", "transport", "leisure"]
        }
    }


def get_affordable_options(max_budget: float, canteen_days: int = 5) -> pd.DataFrame:
    """
    Filter scenario table to show only options within a budget.
    
    Args:
        max_budget (float): maximum monthly budget in CZK
        canteen_days (int): canteen usage frequency
    
    Returns:
        pd.DataFrame: filtered scenarios sorted by total cost
    """
    df = build_scenario_table(canteen_days=canteen_days)
    return df[df["total"] <= max_budget].sort_values("total")

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