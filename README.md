# Smart Inventory Hub

## Project Description
The **Smart Inventory Hub** is an **AI-Powered Demand Forecasting & Inventory Optimization** system designed for the retail sector. By analyzing historical sales data, market conditions, and product parameters, the system predicts future demand and provides actionable inventory recommendations. The solution is deployed as an interactive **Streamlit dashboard**, enabling inventory managers to visualize data, forecast demand, and calculate optimal inventory parameters like **Economic Order Quantity (EOQ)**, **Safety Stock**, and **Reorder Points**.

---

## Project Details

### Problem Statement
Retailers often struggle to maintain optimal inventory levels. **Stockouts** lead to lost sales and customer dissatisfaction, while **overstocking** ties up capital and increases holding costs. This project addresses these challenges by using machine learning to forecast demand accurately and applying scientific inventory management principles to optimize stock levels.

### Data Preprocessing
- **Feature Engineering:**
  - Created rolling averages (3-day, 7-day) to capture trends.
  - Generated lag features (Previous Day, 3-Day Lag) for temporal dependencies.
  - Calculated interaction terms (e.g., Price × Demand Forecast).
  - Encoded categorical variables: Store ID, Product ID, Category, Region, etc.
- **Scaling:** Applied feature scaling using `StandardScaler` (saved as `feature_scaler.pkl`).
- **Data Cleaning:** Handled missing values and outliers in the `retail_store_inventory.csv` dataset.

### Model Training & Evaluation
- **Models Used:**
  - Validated multiple regression models (likely including Random Forest or Gradient Boosting) to predict daily demand.
  - The best performing model is saved as `best_model.pkl`.
- **Key Metrics:**
  - Mean Absolute Error (MAE)
  - R-squared (R²) Score
- **Features Used:**
  - Inventory Level, Units Ordered, Price, Discount, Holiday/Promotion.
  - Competitor Pricing, Weather Condition, Seasonality.
  - Historical demand patterns (Rolling averages, Lags).

### Web Application Features
The **Streamlit Dashboard** (`streamlit_dashboard.py`) includes:

1.  **Overview**:
    - Real-time KPIs: Total SKUs, Avg Daily Demand, Turnover Ratio, Inventory Value.
    - Interactive Charts: Demand Distribution, Reorder Point vs. Demand Correlation.
2.  **Demand Forecasting**:
    - Input form for product and market parameters.
    - Real-time demand prediction using the trained ML model.
    - Insights on Annual Demand and Days Supply.
3.  **Inventory Planning**:
    - Calculators for **Safety Stock**, **Reorder Point (ROP)**, and **EOQ**.
    - Service Level adjustment (85% - 99%).
    - Cost Analysis: Ordering Cost vs. Holding Cost.
4.  **Advanced Analytics**:
    - Demand Trend Analysis (Seasonality, Variability).
    - Stock Level Simulation over time.
    - Financial insights and visual recommendations.

---

## Tech Stack
- **Languages:** Python 3.x, JavaScript (for React frontend)
- **Data Science:** pandas, numpy, scikit-learn
- **Visualization:** Plotly, matplotlib
- **Web Application:** Streamlit (Dashboard), React + Vite (Frontend), Django (Backend API)
- **Tools:** Jupyter Notebook

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/Smart-Inventory-Hub.git
cd Smart-Inventory-Hub
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
*Note: Ensure you include libraries like `streamlit`, `pandas`, `numpy`, `plotly`, `scikit-learn` in your environment.*

### 3. Run the Application

**To launch the Main Dashboard (Streamlit):**
```bash
streamlit run streamlit_dashboard.py
```

**To explore the Data Analysis (Jupyter):**
```bash
jupyter notebook Retail_Demand_Forecasting.ipynb
```

---

## Usage
1.  **Dashboard Overview**: Check high-level metrics to identify stock health (High vs. Low turnover).
2.  **Forecast Demand**: Go to the "Demand Forecasting" page, enter current product metrics (Price, Inventory, Competitor Price), and get a daily demand prediction.
3.  **Plan Inventory**: Use the predicted demand in the "Inventory Planning" page to calculate how much to order (EOQ) and when to order (Reorder Point) to maintain your desired Service Level.
4.  **Download Plan**: Export the calculated inventory plan as a CSV file for execution.

---

## Project Structure
```
Smart-Inventory-Hub/
│
├── streamlit_dashboard.py      # Main Streamlit Dashboard application
├── Retail_Demand_Forecasting.ipynb # Data Science & Model Training Notebook
├── best_model.pkl              # Trained ML Model
├── feature_scaler.pkl          # Feature Scaler object
├── feature_info.pkl            # Metadata about features
├── retail_store_inventory.csv  # Raw dataset
├── inventory_plan.csv          # Generated inventory plan data
├── backend/                    # Django Backend (API)
│   ├── requirements.txt        # Python dependencies
│   ├── manage.py
│   └── ...
├── frontend/                   # React Frontend
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md                   # Project Documentation
```

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
