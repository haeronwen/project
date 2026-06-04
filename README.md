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
project/
├── data/
│   ├── raw/          
│   └── clean/        
├── figures/          
├── source_code/
│   ├── loaders.py    
│   └── cost_model.py 
├── analysis.ipynb    
├── requirements.txt
└── AI_DISCLOSURE.md

## How to run 
1. Instal dependencies: 
```
pip install -r requirements.txt
```
2. Run the cleaning notebooks in `source_code/` (1–4)
3. Run `analysis.ipynb`


---DELETE

# Work in Progress 
!!allow the users to pick free time spending price themselves in the simulation
## Apartments
Rental listings will be scraped from Bezrealitky.cz by first collecting listing URLs from search results pages using BeautifulSoup, then fetching JSON data for each listing. As proof that data can be scraped, `apartments.csv` has been produced with 1,363 listings including price, size, room type, address and district. There were some issues, including some listings outside Prague, extreme price outliers, missing room types and ambiguous zero service charges. These will be adressed during data cleaning. 

## Groceries
A student basket will be scraped from two stores:

- **Lidl.cz** : via their internal search API. `lidl_prices.csv` has been produced as proof of concept, though some items are mismatched due to cheapest-first sorting. This will be improved with more specific search terms.
- **Rohlik.cz** : via their frontend search endpoint. `rohlik_prices.csv` has been produced with mostly correct results. Minor issues include eggs returning a prepared snack and some items priced per single unit rather than standard packaging. These will be fixed with refined search terms.

Tesco was blocked. Albert has no structured online prices.

## Leisure and other costs

Prices for cinema, pubs, cafes, gym memberships and other non-food expenses will be taken from Czech Statistical Office data and other published sources as fixed estimates.

## Dorms 
Dorm prices are scraped from the official university accomodation system `https://rehos.cuni.cz/` by iteration over dormitory IDs and accessing individual dorm detail pages. Data are extracted from HTML tables containing room types and prices. Rows corresponding to newly renovated rooms were removed to ensure consistency of room types.

## Canteen 
Meal prices are collected from the Charles University canteen API `https://kamweb.ruk.cuni.cz/` by querying daily menus for a fixed time period (week April 20-24) . Data are retrieved by JSON API requests containing daily menus for each selected date. Only student prices are included.

## Ideas for interactive aspects
### Apartments 
Students would be able to filtertheir preferred accomodation type by different categoriees, for apartments it would be for example district or number of occupants and if sharing, the rent will be split automatically by the number of people. The simulator will show the average rent for the selected filters alongside the full cost breakdown.

### Groceries 
Students will be able to select a store (Lidl or Rohlik) or view averaged prices across both. A basic cost estimator will calculate a monthly grocery bill based on the standardised basket.

As a more ambitious extension, students could select from a set of common student recipes. The simulator would then generate a shopping list with the cheapest available matching products from the selected store, giving a realistic weekly meal cost estimate.

### Dorms and canteen 
Student that would like cheaper options can chose that they would like to be accomodated in university dorms, and they can chose their preffered location and the type of the room (private, shared by two etc.). Also, they can chose how many days in a week they would like to eat in university canteen. 





