import pandas as pd

df = pd.read_csv('data/clean/apartments_clean.csv')

# keep only relevant dispositions
keep = ['GARSONIERA', '1+KK', '1+1', '2+KK', '2+1', '3+KK', '3+1', '4+KK', '4+1']
df = df[df['disposition_clean'].isin(keep)]

# average total rent per (zone, disposition) — no people assumption
result = df.groupby(['zone', 'disposition_clean']).agg(
    avg_rent=('full_cost', 'mean'),
    n=('full_cost', 'count')
).reset_index()

result.to_csv('data/clean/apartment_monthly_cost.csv', index=False)
print(result)