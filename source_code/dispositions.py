import pandas as pd

df = pd.read_csv('data/clean/apartments_clean.csv')

# keep only relevant dispositions
keep = ['GARSONIERA', '1+KK', '1+1', '2+KK', '2+1', '3+KK', '3+1', '4+KK', '4+1']
df = df[df['disposition_clean'].isin(keep)]

# number of people per disposition
people_map = {
    'GARSONIERA': 1, '1+KK': 1, '1+1': 1,
    '2+KK': 2, '2+1': 2,
    '3+KK': 3, '3+1': 3,
    '4+KK': 4, '4+1': 4
}
df['people'] = df['disposition_clean'].map(people_map)

result = df.groupby(['zone', 'disposition_clean', 'people']).agg(
    avg_rent=('full_cost', 'mean')
).reset_index()

result['avg_rent_per_person'] = result['avg_rent'] / result['people']

result.to_csv('data/clean/apartment_monthly_cost.csv', index=False)