import pandas as pd
from source_code.loaders import (
    load_apartments,
    load_dorms,
    load_canteen,
    get_groceries_monthly,
    TRANSPORT_MONTHLY,
    LEISURE_MONTHLY
)

#load canteen lookup once at module level
canteen=load_canteen().set_index("days_per_week")["monthly_cost"]

def get_canteen_cost(days_per_week:int)->float:
    """
    return monthly canteen cost for a given number of days (0-5)
    uses canteen_costs.csv which contains the monthly cost for each frequency
    returns 0 if days_per_week is 0

    parameters:
    days_per_wek: int 
    """
    if days_per_week==0:
        return 0
    return float(canteen.loc[days_per_week])

def compute_monthly_cost(
        housing_cost:float,
        canteen_days:int=5,
        groceries: float=None,
        transport:float=TRANSPORT_MONTHLY,
        leisure:float=LEISURE_MONTHLY)->dict:
    """
    compute itemised monthly cost of living for a Prague student 
    combines housing, food (canteen+groceries), transport and leisure into a full monthly breakdown
    """
    #fall back to cheapest basket from data if groceries not provided
    if groceries is None:
        groceries=get_groceries_monthly()

    #sum all cost components into a breakdown dict
    breakdown={
        "housing":housing_cost,
        "canteen":get_canteen_cost(canteen_days),
        "groceries":groceries,
        "transport":transport,
        "leisure":leisure
    }
    
    #add total as sum of all components 
    breakdown["total"]=sum(breakdown.values())
    return breakdown 

def build_scenario_table(canteen_days:int=5)->pd.DataFrame:
    """
    build a comparison table of monthly costs across all housing options
    iterates over all dorm configurations and apartment types from the cleaned data, computes monthly cost for each using compute_monthly_cost()
    returns a signle DataFrame for comparison and cisualisation 
    """
    dorms=load_dorms()
    apartments=load_apartments()
    rows=[]

    #monthly cost for each dorm type
    for id,row in dorms.iterrows():
        facilities="own facilities" if row["facilities"]=="Yes" else "shared facilities"
        cost=compute_monthly_cost(row["avg_cost"],canteen_days=canteen_days)
        cost["label"]=f"Dorm {row['beds']}-bed ({facilities})"
        cost["type"]="dorm"
        rows.append(cost)

    #monthly cost for each apartment type (cost per person - assuming sharing)
    for id,row in apartments.iterrows():
        cost= compute_monthly_cost(row["avg_rent_per_person"],canteen_days=canteen_days)
        cost["label"]=f"Flat {row['disposition_clean']} {row['zone']}"
        cost["type"]="apartment"
        rows.append(cost)

    return pd.DataFrame(rows).set_index("label")







