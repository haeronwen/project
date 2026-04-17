# project
Student cost of living
1.data 
bydlení-sreality, kolej;
strava - obchody;
transport;
menza;
zábava - kafe

2. interaktivní prvky
výběr kolej x byt


# Work in Progress - Bára

## Apartments
Rental listings will be scraped from Bezrealitky.cz by first collecting listing URLs from search results pages using BeautifulSoup, then fetching JSON data for each listing. As proof that data can be scraped, `apartments.csv` has been produced with 1,363 listings including price, size, room type, address and district. There were some issues, including some listings outside Prague, extreme price outliers, missing room types and ambiguous zero service charges. These will be adressed during data cleaning. 

## Groceries
A student basket will be scraped from two stores:

- **Lidl.cz** : via their internal search API. `lidl_prices.csv` has been produced as proof of concept, though some items are mismatched due to cheapest-first sorting. This will be improved with more specific search terms.
- **Rohlik.cz** : via their frontend search endpoint. `rohlik_prices.csv` has been produced with mostly correct results. Minor issues include eggs returning a prepared snack and some items priced per single unit rather than standard packaging. These will be fixed with refined search terms.

Tesco was blocked. Albert has no structured online prices.

## Leisure and other costs

Prices for cinema, pubs, cafes, gym memberships and other non-food expenses will be taken from Czech Statistical Office data and other published sources as fixed estimates.

## Ideas for interactive aspects
### Apartments
Students would be able to filtertheir preferred accomodation type by different categoriees, for apartments it would be for example district or number of occupants and if sharing, the rent will be split automatically by the number of people. The simulator will show the average rent for the selected filters alongside the full cost breakdown.

### Groceries
Students will be able to select a store (Lidl or Rohlik) or view averaged prices across both. A basic cost estimator will calculate a monthly grocery bill based on the standardised basket.

As a more ambitious extension, students could select from a set of common student recipes. The simulator would then generate a shopping list with the cheapest available matching products from the selected store, giving a realistic weekly meal cost estimate.


