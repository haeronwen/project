# AI DISCLOSURE
Tools Used: Claude

Troubleshooting:   
- identify the causes and undersand what was going wrong, for example why our `analysis.ipynb` could not import from `loaders.py`
- find the source of inconsistent values in notebooks 
- module caching - explained `importlib.reload()` and Jupyter's module caching behaviour as the reason why the notebook kept showing old values
- resolving import errors between app.py, cost_calculator.py and loaders.py
- debugging grocery scraper filter issues (wrong products passing through)
- diagnosing outlier prices inflating basket costs
- app layout, FX rate integration and chart formatting in Streamlit

Consulting:
- how to apply EAFP instead of LBYL pattern consistently in data loaders
- project structure to keep app and analysis pipelines compatible
- git workflow and coordination between analysis and app source codes
- additional features: diet/store selectors, soup option, dorm comparison section

Grammar:
- README and markdown cells proofreading 