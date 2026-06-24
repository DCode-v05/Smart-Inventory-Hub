# Smart Inventory Hub

**Retail demand forecasting and inventory optimization — predict daily demand from sales history, then compute how much to order and when.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-A30000?style=flat&logo=django&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)

## Overview

Smart Inventory Hub takes historical retail sales data and turns it into two things a store actually needs: a forecast of how much of a product will sell, and a plan for how to stock it. The forecasting side is a regression model trained on roughly 73,000 daily records covering multiple stores, products, regions, and seasons. The inventory side applies standard supply-chain math — Economic Order Quantity (EOQ), Safety Stock, and Reorder Point — on top of that forecast so a manager can answer "how much do I order, and at what stock level do I reorder?"

The problem it targets is the usual inventory squeeze: stockouts lose sales and customers, while overstock ties up cash and racks up holding costs. The project sits between those two failure modes by forecasting demand first and then sizing orders against a chosen service level.

I built it as a data-science learning project (Nov–Dec 2025). The model training lives in a Jupyter notebook, and the same trained model is wired into three different front-ends: a Streamlit dashboard, a Django REST API, and a React + Vite single-page app. That gives the repo a full path from raw CSV to a usable interface, with the analytics layer reusable across all three.

## Key Features

- Demand forecasting from a trained regression model (`best_model.pkl`) on ~73k rows of retail sales data
- Two modeling tracks in the notebook: a standard train/test split (Linear Regression vs Random Forest) and a time-series adaptation using `TimeSeriesSplit` cross-validation with lag/rolling features
- Feature engineering: 3-day and 7-day rolling averages, 1-day and 3-day lags, demand differences, a price × demand interaction term, and label-encoded categoricals (Store, Product, Category, Region, Weather, Seasonality)
- Inventory math built in: EOQ, Safety Stock (service-level / z-score based), Reorder Point, average inventory, turnover ratio, and days of supply
- Cost analysis: annual ordering cost vs. annual holding cost and total annual cost, with order frequency
- Adjustable service level (85% to 99%) that maps to the right z-score for safety stock
- Streamlit dashboard with four pages — Overview KPIs, Demand Forecasting, Inventory Planning, and Analytics — with interactive Plotly charts
- Django REST API exposing `/api/predict/` (run the model) and `/api/inventory/` (run the inventory calculations) for programmatic use
- React + Vite front-end that calls the API, with a 19-field forecasting form and Plotly visualizations
- A pre-computed `inventory_plan.csv` with a full plan (predicted demand, annual demand, reorder point, safety stock, EOQ, lead time) for 100 SKUs, exportable from the dashboard

## How It Works

There are three layers: the model (trained once in the notebook), the analytics (forecast + inventory math), and three interchangeable interfaces over them.

### Data and preprocessing

The input is `retail_store_inventory.csv` — about 73,100 daily rows across 15 columns: `Date`, `Store ID`, `Product ID`, `Category`, `Region`, `Inventory Level`, `Units Sold`, `Units Ordered`, `Demand Forecast`, `Price`, `Discount`, `Weather Condition`, `Holiday/Promotion`, `Competitor Pricing`, and `Seasonality`. Preprocessing handles missing values and outliers, label-encodes the categorical columns, and scales numeric features with `StandardScaler`.

### Feature engineering

The notebook builds temporal features so the model can pick up trends instead of treating each day as independent:

- Rolling averages over 3-day and 7-day windows
- Lag features (previous day, 3-day lag) and a day-over-day demand difference
- An interaction term combining `Price` and `Demand Forecast`
- Encoded versions of all categorical fields

In the time-series track the feature count grows to 53 (additional rolling min/max/std and percent-change features on `Units Sold`), and feature importance there is dominated by `Demand Forecast` (~0.34), followed by the `Units Sold` difference and percent-change features.

### Model training and evaluation

Training is done two ways for comparison:

- **Standard split** — an 80/20 `train_test_split` on 19 engineered features, training Linear Regression and a Random Forest (`n_estimators=100`). Random Forest wins narrowly and is saved as `best_model.pkl`.
- **Time-series adaptation** — a proper `TimeSeriesSplit` 5-fold cross-validation (no future leakage across folds) on 53 features, with Ridge regression (`alpha=1.0`) for the linear model and a 200-tree Random Forest.

The model picked at the end of the standard track is serialized to `best_model.pkl`, alongside `feature_scaler.pkl` (the `StandardScaler`) and `feature_info.pkl` (the ordered feature columns the API and dashboard use to build a prediction row).

### Inventory optimization

Once demand is predicted, the analytics layer turns it into an order plan:

- **Safety Stock** = `z * demand_std_dev * sqrt(lead_time)`, where the z-score comes from the chosen service level (e.g. 1.645 at 95%)
- **Reorder Point** = `predicted_demand * lead_time + safety_stock`
- **EOQ** = `sqrt(2 * annual_demand * ordering_cost / (unit_cost * holding_cost_rate))`
- Plus average inventory, turnover, days of supply, annual ordering/holding/total cost, and order frequency

This same logic is implemented in both the Streamlit app and the Django `inventory` view, so the numbers match across interfaces.

### Interfaces

**Streamlit dashboard** (`streamlit_dashboard.py`) loads the pickled model and `inventory_plan.csv`, caches them, and serves four pages from a sidebar: Overview (SKU count, average daily demand, total annual demand, turnover, inventory value, plus interactive distribution/correlation/comparison/time-series charts), Demand Forecasting (input form → live prediction), Inventory Planning (EOQ / ROP / safety-stock calculators with service-level control and cost breakdown), and Analytics.

**Django REST API** (`backend/`) lazy-loads the model artifacts from `backend/model/` with `joblib` and exposes two POST endpoints. `/api/predict/` accepts `{ "features": { ... } }`, reorders the features per `feature_info.pkl`, applies the scaler if present, and returns the prediction. `/api/inventory/` accepts the demand and cost parameters and returns the full set of inventory metrics. It uses Django REST Framework with `django-cors-headers` (CORS open for local dev) and SQLite.

**React + Vite front-end** (`frontend/`) is a single-page app with simple state-based routing across Home, About, Demand Forecasting, and Inventory Planning. The Forecasting page renders a 19-field form (inventory level, units ordered, price, discount, promotion flag, competitor pricing, the rolling/lag features, and encoded categoricals), posts to `/api/predict/` via an axios client (`api.js`), keeps the last 10 predictions in history, and draws charts with `react-plotly.js`.

## Results / Highlights

- Random Forest on the standard 80/20 split: **R² 0.9932**, MAE 0.0146, RMSE 0.0172 (Linear Regression was essentially tied at R² 0.9931)
- Time-series track (5-fold `TimeSeriesSplit`, 53 features): Random Forest R² 0.9941 (MAE 0.0124, RMSE 0.0159); the linear model reported R² 1.0000, which is a leakage red flag, not a real headline number — see Notes
- Trained on ~73,100 daily records (15 raw columns) spanning multiple stores, products, regions, and seasons
- Pre-computed inventory plan covering 100 SKUs with EOQ, safety stock, reorder point, and lead time per SKU
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

The Streamlit dashboard needs `streamlit`, `pandas`, `numpy`, `plotly`, and `scikit-learn`. The backend pins its own dependencies:

```bash
# backend dependencies
pip install -r backend/requirements.txt

# extra packages for the Streamlit dashboard
pip install streamlit plotly
```

### Running

**Streamlit dashboard** (loads the model and `inventory_plan.csv` from the repo root):

```bash
streamlit run streamlit_dashboard.py
```

**Django API:**

```bash
cd backend
python manage.py migrate
python manage.py runserver
# API at http://127.0.0.1:8000/api/predict/  and  /api/inventory/
```

**React front-end:**

```bash
cd frontend
npm install
npm run dev
# set VITE_API_BASE if the API isn't on http://127.0.0.1:8000
```

**Notebook** (to retrain or inspect the pipeline):

```bash
jupyter notebook Retail_Demand_Forecasting.ipynb
```

## Usage

1. **Forecast demand.** On the Streamlit Demand Forecasting page (or via `POST /api/predict/` with a `features` object), enter the product and market values — inventory level, price, discount, promotion flag, competitor pricing, and the rolling/lag demand fields — to get a predicted daily demand.
2. **Plan the order.** Feed that demand into Inventory Planning along with lead time, unit cost, ordering cost, holding cost rate, and a target service level. The app returns EOQ (how much to order), Reorder Point (when to order), and Safety Stock (the buffer), plus turnover, days of supply, and a cost breakdown.
3. **Review the dashboard.** The Overview page gives portfolio-level KPIs and interactive charts across all SKUs; Analytics adds trend and stock-level simulation views.
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
├── streamlit_dashboard.py            # Streamlit app — Overview, Forecasting, Planning, Analytics
├── retail_store_inventory.csv        # Raw dataset (~73k rows, 15 columns)
├── inventory_plan.csv                # Pre-computed plan for 100 SKUs
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

> Note: `best_model.pkl`, `feature_scaler.pkl`, and `feature_info.pkl` are produced by the notebook at the repo root; the Django backend keeps its own copies under `backend/model/`.

---

## Contact

**Portfolio:** [Denistan](https://www.denistan.me)<br>
**LinkedIn:** [Denistan](https://www.linkedin.com/in/denistanb)<br>
**GitHub:** [DCode-v05](https://github.com/DCode-v05)<br>
**LeetCode:** [Denistan_B](https://leetcode.com/u/Denistan_B)<br>
**Email:** [denistanb05@gmail.com](mailto:denistanb05@gmail.com)

Made with ❤️ by **Denistan B**
