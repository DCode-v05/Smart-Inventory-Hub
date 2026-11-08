# Smart Inventory Hub

**Retail demand forecasting and inventory optimization: predict daily demand from sales history, then work out how much to order and when.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-A30000?style=flat&logo=django&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)

## Overview

Smart Inventory Hub takes historical retail sales data and produces two things a store needs: a forecast of how much of a product will sell, and a plan for how to stock it. The forecasting side is a regression model trained on about 73,000 daily records covering several stores, products, regions and seasons. The inventory side applies standard supply-chain formulas (Economic Order Quantity, Safety Stock and Reorder Point) to that forecast, so a manager can answer "how much do I order, and at what stock level do I reorder?"

It targets the usual inventory squeeze: stockouts lose sales and customers, while overstock ties up cash and adds holding costs. The project forecasts demand first and then sizes orders against a chosen service level.

I built it as a data-science learning project (Nov-Dec 2025). The model training lives in a Jupyter notebook, and the same trained model feeds three front-ends: a Streamlit dashboard, a Django REST API and a React + Vite single-page app. That covers the path from raw CSV to a usable interface, with the analytics shared across all three.

## Key Features

- Demand forecasting from a trained regression model (`best_model.pkl`) on ~73k rows of retail sales data
- Two modeling tracks in the notebook: a standard train/test split (Linear Regression vs Random Forest) and a time-series version using `TimeSeriesSplit` cross-validation with lag and rolling features
- Feature engineering: 3-day and 7-day rolling averages, 1-day and 3-day lags, demand differences, a price × demand interaction term, and label-encoded categoricals (Store, Product, Category, Region, Weather, Seasonality)
- Inventory math built in: EOQ, Safety Stock (service-level / z-score based), Reorder Point, average inventory, turnover ratio and days of supply
- Cost analysis: annual ordering cost vs. annual holding cost and total annual cost, with order frequency
- Adjustable service level (85% to 99%) that maps to the matching z-score for safety stock
- Streamlit dashboard with four pages (Overview KPIs, Demand Forecasting, Inventory Planning and Analytics) and interactive Plotly charts. It currently does not run because of a syntax error, see Getting Started.
- Django REST API exposing `/api/predict/` (run the model) and `/api/inventory/` (run the inventory calculations)
- React + Vite front-end that calls the API, with a 19-field forecasting form and Plotly charts
- A pre-computed `inventory_plan.csv` with a full plan (predicted demand, annual demand, reorder point, safety stock, EOQ, lead time) for 100 SKUs

## How It Works

There are three layers: the model (trained once in the notebook), the analytics (forecast + inventory math), and three interchangeable interfaces on top.

### Data and preprocessing

The input is `retail_store_inventory.csv`, about 73,100 daily rows across 15 columns: `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Inventory Level`, `Units Sold`, `Units Ordered`, `Demand Forecast`, `Price`, `Discount`, `Weather Condition`, `Holiday/Promotion`, `Competitor Pricing` and `Seasonality`. Preprocessing handles missing values and outliers, label-encodes the categorical columns, and scales numeric features with `StandardScaler`.

### Feature engineering

The notebook builds temporal features so the model can pick up trends instead of treating each day on its own:

- Rolling averages over 3-day and 7-day windows
- Lag features (previous day, 3-day lag) and a day-over-day demand difference
- An interaction term combining `Price` and `Demand Forecast`
- Encoded versions of all categorical fields

In the time-series track the feature count grows to 53 (extra rolling min/max/std and percent-change features on `Units Sold`). Feature importance there is dominated by `Demand Forecast` (~0.34), followed by the `Units Sold` difference and percent-change features.

### Model training and evaluation

Training is done two ways for comparison:

- **Standard split:** an 80/20 `train_test_split` on 19 engineered features, training Linear Regression and a Random Forest (`n_estimators=100`). Random Forest wins narrowly and is saved as `best_model.pkl`.
- **Time-series version:** 5-fold `TimeSeriesSplit` cross-validation (no future leakage across folds) on 53 features, with Ridge regression (`alpha=1.0`) as the linear model and a 200-tree Random Forest.

The model picked at the end of the standard track is saved as `best_model.pkl`, alongside `feature_scaler.pkl` (the `StandardScaler`) and `feature_info.pkl` (the ordered feature columns the API and dashboard use to build a prediction row).

### Inventory optimization

Once demand is predicted, the analytics layer turns it into an order plan:

- **Safety Stock** = `z * demand_std_dev * sqrt(lead_time)`, where the z-score comes from the chosen service level (e.g. 1.645 at 95%)
- **Reorder Point** = `predicted_demand * lead_time + safety_stock`
- **EOQ** = `sqrt(2 * annual_demand * ordering_cost / (unit_cost * holding_cost_rate))`
- Plus average inventory, turnover, days of supply, annual ordering/holding/total cost and order frequency

The same logic is in both the Streamlit app and the Django `inventory` view, so the numbers match across interfaces. The notebook also uses it to build `inventory_plan.csv`.

### Interfaces

**Streamlit dashboard** (`streamlit_dashboard.py`) loads the pickled model and `inventory_plan.csv`, caches them, and serves four pages from a sidebar: Overview (SKU count, average daily demand, total annual demand, turnover, inventory value, plus interactive distribution, correlation, comparison and time-series charts), Demand Forecasting (input form to live prediction), Inventory Planning (EOQ / ROP / safety-stock calculators with service-level control and a cost breakdown) and Analytics. It reads the three pickle files from the folder it runs in.

**Django REST API** (`backend/`) loads the model artifacts from `backend/model/` with `joblib` and exposes two POST endpoints. `/api/predict/` accepts `{ "features": { ... } }`, reorders the features per `feature_info.pkl`, applies the scaler if present, and returns the prediction. `/api/inventory/` accepts the demand and cost parameters and returns the full set of inventory metrics. It uses Django REST Framework with `django-cors-headers` and SQLite.

**React + Vite front-end** (`frontend/`) is a single-page app with simple state-based routing across Home, About, Demand Forecasting and Inventory Planning. The Forecasting page renders a 19-field form (inventory level, units ordered, price, discount, promotion flag, competitor pricing, the rolling/lag features and encoded categoricals), posts to `/api/predict/` through an axios client (`api.js`), keeps the last 10 predictions in history, and draws charts with `react-plotly.js`.

## Results / Highlights

- Random Forest on the standard 80/20 split: **R² 0.9932**, MAE 0.0146, RMSE 0.0172 (Linear Regression was essentially tied at R² 0.9931). These are on scaled values, and two models landing this close makes me suspect leakage: `Demand Forecast` and `Units Sold` are correlated at 0.997, so check the features before trusting the number.
- Time-series track (5-fold `TimeSeriesSplit`, 53 features): Random Forest R² 0.9941 (MAE 0.0124, RMSE 0.0159). The linear model reported R² 1.0000, which points to leakage and is not a real headline number.
- Trained on ~73,100 daily records (15 raw columns) spanning several stores, products, regions and seasons
- Pre-computed inventory plan covering 100 SKUs with EOQ, safety stock, reorder point and lead time per SKU
- Top time-series feature: `Demand Forecast` at ~0.34 importance, ahead of the `Units Sold` difference and percent-change features

## Tech Stack

- **Languages:** Python 3, JavaScript (JSX), with CSS/HTML for the front-end
- **Data / ML:** pandas, NumPy, scikit-learn (Random Forest, Linear/Ridge regression, `StandardScaler`, `TimeSeriesSplit`), joblib/pickle
- **Visualization:** Plotly (Express + Graph Objects), `react-plotly.js`, matplotlib (in the notebook)
- **Dashboard / API / UI:** Streamlit, Django + Django REST Framework, `django-cors-headers`, React 18 + Vite, axios
- **Other:** Jupyter Notebook for training, SQLite for the Django backend

## Getting Started

### Prerequisites

- Python 3.x
- Node.js (for the React front-end)
- `pip` for Python dependencies

### Installation

```bash
git clone https://github.com/DCode-v05/Smart-Inventory-Hub.git
cd Smart-Inventory-Hub
```

The backend pins its own dependencies, and the Streamlit dashboard needs `streamlit` and `plotly` on top:

```bash
# backend dependencies
pip install -r backend/requirements.txt

# extra packages for the Streamlit dashboard
pip install streamlit plotly
```

### Running

**Django API:**

```bash
cd backend
python manage.py migrate
python manage.py runserver
# API at http://127.0.0.1:8000/api/predict/  and  /api/inventory/
```

`backend/db.sqlite3` is not tracked, so `migrate` creates it. `settings.py` is set up for local use: `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, all CORS origins allowed, and a placeholder secret key unless `DJANGO_SECRET_KEY` is set.

**React front-end:**

```bash
cd frontend
npm install
npm run dev
# set VITE_API_BASE if the API isn't on http://127.0.0.1:8000
```

**Streamlit dashboard:**

```bash
streamlit run streamlit_dashboard.py
```

Known issue: `streamlit_dashboard.py` does not currently parse. Several calls have a corrupted argument, for example `st.plotly_chart(fig, width=" stretch\)` on lines 180, 187, 213, 225, 233, 268, 350, 454 and 556, which should read `width="stretch"`. Fix those before running it. The API and front end are not affected.

The dashboard also looks for `best_model.pkl`, `feature_scaler.pkl` and `feature_info.pkl` in the current directory, but the repo keeps the first and last in `backend/model/` and `feature_scaler.pkl` is not committed. Run the notebook to regenerate them, or copy them next to the script. The `*.pkl` files are stored with Git LFS (`.gitattributes`).

**Notebook** (to retrain or inspect the pipeline):

```bash
jupyter notebook Retail_Demand_Forecasting.ipynb
```

## Usage

1. **Forecast demand.** On the Streamlit Demand Forecasting page (or via `POST /api/predict/` with a `features` object), enter the product and market values (inventory level, price, discount, promotion flag, competitor pricing and the rolling/lag demand fields) to get a predicted daily demand.
2. **Plan the order.** Feed that demand into Inventory Planning along with lead time, unit cost, ordering cost, holding cost rate and a target service level. The app returns EOQ (how much to order), Reorder Point (when to order) and Safety Stock (the buffer), plus turnover, days of supply and a cost breakdown.
3. **Review the dashboard.** The Overview page gives portfolio-level KPIs and interactive charts across all SKUs, and Analytics adds trend and stock-level simulation views.
4. **Export.** The Inventory Planning page can export the computed plan as a CSV (`inventory_plan.csv` format) for downstream use.

For the API directly:

```bash
curl -X POST http://127.0.0.1:8000/api/inventory/ \
  -H "Content-Type: application/json" \
  -d '{"predicted_demand": 25, "lead_time_days": 7, "service_level": 0.95, "unit_cost": 10, "ordering_cost": 50, "holding_cost_rate": 0.25}'
```

## Project Structure

```
Smart-Inventory-Hub/
├── Retail_Demand_Forecasting.ipynb   # Training pipeline: EDA, feature engineering, model comparison
├── streamlit_dashboard.py            # Streamlit app: Overview, Forecasting, Planning, Analytics
├── retail_store_inventory.csv        # Raw dataset (~73k rows, 15 columns)
├── inventory_plan.csv                # Pre-computed plan for 100 SKUs
├── .gitattributes                    # Git LFS rule for *.pkl
├── backend/                          # Django REST API
│   ├── api/
│   │   ├── views.py                  # predict() and inventory() endpoints
│   │   └── urls.py                   # /api/predict/, /api/inventory/
│   ├── model/                        # best_model.pkl, feature_info.pkl (loaded via joblib)
│   ├── project/settings.py           # DRF + CORS + SQLite config
│   ├── manage.py
│   └── requirements.txt
└── frontend/                         # React + Vite SPA
    ├── src/
    │   ├── App.jsx                   # Page routing (Home / About / Forecasting / Inventory)
    │   ├── api.js                    # axios client (VITE_API_BASE)
    │   └── pages/                    # Home, About, Forecasting, Inventory
    ├── package.json
    └── vite.config.js
```

> Note: the notebook writes `best_model.pkl`, `feature_scaler.pkl` and `feature_info.pkl` to the repo root, but those root copies are not committed. The repo only has `best_model.pkl` and `feature_info.pkl`, under `backend/model/`.

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
