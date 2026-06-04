# Student Cost of Living in Prague
## Data Processing in Python 
Anna Chodurková, Barbora Motyková

## Goal
Analyse and compare monthly living consts for students in Prague across different housing, food and lifestyle choices.

### Data Sources
- Apartments - scraped from Bezrealitky.cz
- Dorms - scraped from Charles University accommodation system rehos.cuni.cz
- Canteen - scraped from Charles University canteen API kamweb.ruk.cuni.cz, week of April 20–24
- Groceries - scraped from Billa, Lidl, Košík, Rohlík 
- Transport - PID student yearly pass (pid.cz)
- Leisure - manually estimated 

## Project structure 
```
project/
├── data/
│   ├── raw/                ← scraped CSVs
│   └── clean/              ← processed CSVs
├── figures/
├── source_code/
│   ├── scraping notebooks (groceries, apartments, dorms, menza)
│   ├── cleaning notebooks (1–4)
│   ├── data_prep_app.ipynb ← additional data preparation for the app
│   ├── loaders.py
│   ├── cost_model.py       ← for analysis
│   └── cost_calculator.py  ← for app
├── analysis.ipynb
├── app.py
├── requirements.txt
└── AI_DISCLOSURE.md
```

## How to run 
1. Install dependencies: 
```
pip install -r requirements.txt
```
2. Optionally re-run scraping notebooks in `source_code/` to collect fresh data   
    note: `menza.ipynb` cannot be re-run to reproduce the original data as it was scraped for a specific week (April 20–24 2025) and the canteen API only serves current menus. Raw data is already included in `data/raw/`
3. Run the cleaning notebooks in `source_code/` (1–4)
4. Run `data_prep_app.ipynb` to generate additional app-specific clean files
5. Run `analysis.ipynb`
6. Run `app.py` locally (optional) since https://praguestudentcosts.streamlit.app/ 



