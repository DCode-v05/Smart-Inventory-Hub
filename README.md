# Smart Inventory Hub

Forecasts daily product demand from retail sales history, then turns the forecast into inventory numbers: safety stock, reorder point and economic order quantity. The same logic is available as a Streamlit dashboard and as a Django API with a React front end.

## Parts

**Notebook (`Retail_Demand_Forecasting.ipynb`).** Loads `retail_store_inventory.csv` (73,100 daily records across stores, products and regions), cleans and scales it, adds time-series features and compares a Linear Regression with a Random Forest. Both end up at R2 of about 0.993 on the test split (0.9931 and 0.9932), on scaled values. The two scores are almost the same, so I would check the features for leakage before trusting that number (the data has `Demand Forecast` and `Units Sold` correlated at 0.997). The notebook then builds `inventory_plan.csv` (one row per SKU with predicted demand, annual demand, reorder point, safety stock, EOQ and lead time) and pickles the best model.

**Streamlit dashboard (`streamlit_dashboard.py`).** Pages for an overview, demand forecasting, inventory planning and analytics. It reads `inventory_plan.csv` and loads `best_model.pkl`, `feature_scaler.pkl` and `feature_info.pkl` from the folder it runs in.

**Django API (`backend/`).** Two POST endpoints under `/api/`:
- `predict/` takes `{"features": {...}}` and returns the model's prediction, using `backend/model/best_model.pkl` and `feature_info.pkl`.
- `inventory/` takes predicted demand, lead time, service level, unit cost, holding and ordering cost, and returns safety stock, reorder point, EOQ, inventory turnover, days of supply and annual costs.

**React front end (`frontend/`).** A Vite app with Home, Forecasting, Inventory and About pages that calls the API through axios (base URL from `VITE_API_BASE`, default `http://127.0.0.1:8000`) and draws charts with Plotly.

## Running it

```bash
pip install -r backend/requirements.txt
```

API:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Front end:

```bash
cd frontend
npm install
npm run dev
```

Dashboard (also needs `pip install streamlit plotly`):

```bash
streamlit run streamlit_dashboard.py
```

The dashboard looks for the pickle files in the current directory, but the repo keeps them in `backend/model/` and `feature_scaler.pkl` is not committed. Run the notebook to regenerate them, or copy them next to the script.

## Notes

- `backend/db.sqlite3` is not tracked; `migrate` creates it.
- `*.pkl` files are stored with Git LFS (`.gitattributes`).
- `settings.py` is set up for local use: `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, all CORS origins allowed, and a placeholder secret key unless `DJANGO_SECRET_KEY` is set.

## Layout

```
Retail_Demand_Forecasting.ipynb
streamlit_dashboard.py
retail_store_inventory.csv
inventory_plan.csv
backend/     Django project (project/), API app (api/), model/
frontend/    React + Vite app
```
