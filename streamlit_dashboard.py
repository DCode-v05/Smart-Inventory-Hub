
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
import warnings

# Suppress specific numpy warnings for division operations
warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value encountered in divide')

st.set_page_config(
    page_title="Smart Inventory Hub",
    page_icon="📊",
    layout="wide"
)

# Load models and data
@st.cache_resource
def load_models():
    with open('best_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    try:
        with open('feature_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
    except:
        scaler = None
    
    with open('feature_info.pkl', 'rb') as f:
        feature_info = pickle.load(f)
    
    return model, scaler, feature_info

@st.cache_data
def load_inventory_plan():
    return pd.read_csv('inventory_plan.csv')

# Main dashboard
def main():
    st.title("📊 Smart Inventory Hub")
    st.markdown("*AI-Powered Demand Forecasting & Inventory Optimization*")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox("Choose a page:", 
                               ["Overview", "Demand Forecasting", "Inventory Planning", "Analytics"])
    
    # Load data
    model, scaler, feature_info = load_models()
    inventory_plan = load_inventory_plan()
    
    if page == "Overview":
        show_overview(inventory_plan)
    elif page == "Demand Forecasting":
        show_forecasting(model, scaler, feature_info)
    elif page == "Inventory Planning":
        show_inventory_planning(inventory_plan)
    else:
        show_analytics(inventory_plan)

def show_overview(inventory_plan):
    st.header("📊 Dashboard Overview")
    st.markdown("*Welcome to your intelligent inventory management system*")
    
    # Enhanced KPIs with calculations
    avg_inventory = (inventory_plan['EOQ'] / 2) + inventory_plan['Safety_Stock']
    turnover_ratio = inventory_plan['Annual_Demand'] / avg_inventory
    total_inventory_value = avg_inventory.sum() * 10  # Assuming $10 unit cost
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📦 Total SKUs", f"{len(inventory_plan):,}")
    
    with col2:
        avg_demand = inventory_plan['Predicted_Demand'].mean()
        st.metric("📈 Avg Daily Demand", f"{avg_demand:.2f}")
    
    with col3:
        total_annual_demand = inventory_plan['Annual_Demand'].sum()
        st.metric("📊 Total Annual Demand", f"{total_annual_demand:,.0f}")
    
    with col4:
        avg_turnover = turnover_ratio.mean()
        st.metric("🔄 Avg Turnover", f"{avg_turnover:.1f}x", 
                 delta="Healthy" if avg_turnover > 6 else "Review")
    
    with col5:
        st.metric("💰 Inventory Value", f"${total_inventory_value:,.0f}")
    
    # Interactive filters for charts
    st.write("---")
    st.subheader("🎛️ Interactive Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox("📊 Chart Type", 
                                 ["Distribution", "Correlation", "Comparison", "Time Series Simulation"])
    with col2:
        color_by = st.selectbox("🎨 Color By", 
                               ["Lead_Time_Days", "EOQ_Category", "Demand_Category", "None"])
    with col3:
        show_outliers = st.checkbox("🔍 Highlight Outliers", value=False)
    
    # Create categories for coloring
    inventory_display = inventory_plan.copy()
    
    # EOQ Categories - handle case where all EOQs are similar
    eoq_unique_values = inventory_display['EOQ'].nunique()
    if eoq_unique_values > 3:
        eoq_quantiles = inventory_display['EOQ'].quantile([0.33, 0.66])
        inventory_display['EOQ_Category'] = pd.cut(inventory_display['EOQ'], 
                                                  bins=[-np.inf, eoq_quantiles.iloc[0], eoq_quantiles.iloc[1], np.inf],
                                                  labels=['Low EOQ', 'Medium EOQ', 'High EOQ'])
    else:
        # If all EOQs are similar, create simple categories
        inventory_display['EOQ_Category'] = 'Standard EOQ'
    
    # Demand Categories
    demand_unique_values = inventory_display['Predicted_Demand'].nunique()
    if demand_unique_values > 3:
        demand_quantiles = inventory_display['Predicted_Demand'].quantile([0.33, 0.66])
        inventory_display['Demand_Category'] = pd.cut(inventory_display['Predicted_Demand'],
                                                     bins=[-np.inf, demand_quantiles.iloc[0], demand_quantiles.iloc[1], np.inf],
                                                     labels=['Low Demand', 'Medium Demand', 'High Demand'])
    else:
        # Create categories based on actual values
        min_demand = inventory_display['Predicted_Demand'].min()
        max_demand = inventory_display['Predicted_Demand'].max()
        mid_demand = (min_demand + max_demand) / 2
        
        inventory_display['Demand_Category'] = inventory_display['Predicted_Demand'].apply(
            lambda x: 'Low Demand' if x < mid_demand else 'High Demand'
        )
    
    # Handle outliers
    if show_outliers:
        # Calculate outliers using IQR method
        Q1 = inventory_display['Predicted_Demand'].quantile(0.25)
        Q3 = inventory_display['Predicted_Demand'].quantile(0.75)
        IQR = Q3 - Q1
        outlier_condition = (inventory_display['Predicted_Demand'] < (Q1 - 1.5 * IQR)) | (inventory_display['Predicted_Demand'] > (Q3 + 1.5 * IQR))
        inventory_display['Is_Outlier'] = outlier_condition
    
    # Generate charts based on selection
    col1, col2 = st.columns(2)
    
    with col1:
        if chart_type == "Distribution":
            if color_by != "None":
                fig = px.histogram(inventory_display, x='Predicted_Demand', 
                                 color=color_by,
                                 title="📊 Demand Distribution by Category",
                                 nbins=20)
            else:
                fig = px.histogram(inventory_display, x='Predicted_Demand', 
                                 title="📊 Demand Distribution",
                                 nbins=20)
            
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, width="stretch")
            
        elif chart_type == "Correlation":
            color_col = color_by if color_by != "None" else None
            fig = px.scatter(inventory_display, x='Predicted_Demand', y='Reorder_Point',
                           color=color_col,
                           size='EOQ',
                           hover_data=['SKU_ID', 'Safety_Stock'],
                           title="🎯 Reorder Point vs Demand Correlation")
            
            if show_outliers and 'Is_Outlier' in inventory_display.columns:
                outliers = inventory_display[inventory_display['Is_Outlier']]
                fig.add_scatter(x=outliers['Predicted_Demand'], y=outliers['Reorder_Point'],
                              mode='markers', marker=dict(color='red', size=10, symbol='x'),
                              name='Outliers')
            
            st.plotly_chart(fig, width=" stretch\)
            
        elif chart_type == "Comparison":
            # Box plot comparison
            fig = px.box(inventory_display, x='Lead_Time_Days', y='Predicted_Demand',
                        color='Lead_Time_Days',
                        title="📦 Demand Distribution by Lead Time")
            st.plotly_chart(fig, width=" stretch\)
            
        else:  # Time Series Simulation
            # Simulate demand over time for top 10 SKUs
            top_skus = inventory_display.nlargest(10, 'Predicted_Demand')
            
            # Create simulated time series
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            sim_data = []
            
            for _, sku in top_skus.iterrows():
                for date in dates:
                    # Add some random variation to simulate realistic demand
                    daily_demand = sku['Predicted_Demand'] * (1 + np.random.normal(0, 0.1))
                    sim_data.append({
                        'Date': date,
                        'SKU_ID': sku['SKU_ID'],
                        'Simulated_Demand': max(0, daily_demand),
                        'Reorder_Point': sku['Reorder_Point']
                    })
            
            sim_df = pd.DataFrame(sim_data)
            
            fig = px.line(sim_df, x='Date', y='Simulated_Demand', 
                         color='SKU_ID',
                         title="📈 30-Day Demand Simulation (Top 10 SKUs)")
            st.plotly_chart(fig, width=" stretch\)
    
    with col2:
        # Second chart based on selection
        if chart_type in ["Distribution", "Correlation"]:
            # EOQ vs Safety Stock analysis
            color_col = color_by if color_by != "None" else None
            fig = px.scatter(inventory_display, x='EOQ', y='Safety_Stock',
                           color=color_col,
                           size='Predicted_Demand',
                           hover_data=['SKU_ID', 'Reorder_Point'],
                           title="📈 EOQ vs Safety Stock Analysis")
            st.plotly_chart(fig, width=" stretch\)
            
        elif chart_type == "Comparison":
            # Turnover analysis
            inventory_display['Turnover'] = inventory_display['Annual_Demand'] / avg_inventory
            fig = px.histogram(inventory_display, x='Turnover',
                             color='Lead_Time_Days',
                             title="🔄 Inventory Turnover Distribution")
            st.plotly_chart(fig, width=" stretch\)
            
        else:  # Time Series
            # Inventory level simulation
            inventory_sim = []
            current_inventory = top_skus['EOQ'].iloc[0]  # Start with EOQ for first SKU
            sku_data = top_skus.iloc[0]
            
            for i, date in enumerate(dates):
                daily_demand = max(0, sku_data['Predicted_Demand'] * (1 + np.random.normal(0, 0.1)))
                current_inventory -= daily_demand
                
                # Reorder when hitting ROP
                if current_inventory <= sku_data['Reorder_Point']:
                    current_inventory += sku_data['EOQ']
                
                inventory_sim.append({
                    'Date': date,
                    'Inventory_Level': max(0, current_inventory),
                    'Reorder_Point': sku_data['Reorder_Point'],
                    'Safety_Stock': sku_data['Safety_Stock']
                })
            
            inv_sim_df = pd.DataFrame(inventory_sim)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=inv_sim_df['Date'], y=inv_sim_df['Inventory_Level'],
                                   mode='lines+markers', name='Inventory Level'))
            fig.add_trace(go.Scatter(x=inv_sim_df['Date'], y=inv_sim_df['Reorder_Point'],
                                   mode='lines', name='Reorder Point', line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=inv_sim_df['Date'], y=inv_sim_df['Safety_Stock'],
                                   mode='lines', name='Safety Stock', line=dict(dash='dot')))
            
            fig.update_layout(title="📦 Inventory Level Simulation (Sample SKU)",
                            xaxis_title="Date", yaxis_title="Units")
            st.plotly_chart(fig, width=" stretch\)
    
    # Quick insights and recommendations
    st.write("---")
    st.subheader("🔍 Quick Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🎯 Performance Metrics:**")
        high_turnover = len(inventory_display[turnover_ratio > 12])
        low_turnover = len(inventory_display[turnover_ratio < 4])
        
        st.write(f"• High Turnover SKUs: {high_turnover} ({high_turnover/len(inventory_display)*100:.1f}%)")
        st.write(f"• Low Turnover SKUs: {low_turnover} ({low_turnover/len(inventory_display)*100:.1f}%)")
        st.write(f"• Optimal Range SKUs: {len(inventory_display) - high_turnover - low_turnover}")
    
    with col2:
        st.write("**💰 Financial Impact:**")
        total_holding_cost = total_inventory_value * 0.25  # 25% holding cost
        annual_ordering_cost = (inventory_display['Annual_Demand'] / inventory_display['EOQ']).sum() * 50  # $50 per order
        
        st.write(f"• Est. Annual Holding Cost: ${total_holding_cost:,.0f}")
        st.write(f"• Est. Annual Ordering Cost: ${annual_ordering_cost:,.0f}")
        st.write(f"• **Total Inventory Cost: ${total_holding_cost + annual_ordering_cost:,.0f}**")
    
    with col3:
        st.write("**⚡ Recommendations:**")
        if avg_turnover < 6:
            st.write("• 🔽 Consider reducing inventory levels")
        elif avg_turnover > 12:
            st.write("• 🔼 Consider increasing safety stock")
        else:
            st.write("• ✅ Inventory levels appear optimal")
        
        if low_turnover > len(inventory_display) * 0.2:
            st.write("• 📊 Review slow-moving items")
        
        st.write("• 🎯 Focus on demand forecasting accuracy")

def show_forecasting(model, scaler, feature_info):
    st.header("🎯 Demand Forecasting")
    st.write("Enter product and market parameters to predict daily demand")
    
    # Single streamlined input form
    with st.form("demand_prediction_form"):
        st.subheader("📝 Product Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Basic Parameters:**")
            inventory_level = st.number_input("Current Inventory Level", value=100.0, min_value=0.0)
            units_ordered = st.number_input("Units Ordered", value=50.0, min_value=0.0)
            demand_forecast = st.number_input("Initial Demand Forecast", value=25.0, min_value=0.0)
            price = st.number_input("Product Price ($)", value=15.0, min_value=0.0)
            discount = st.number_input("Discount Rate", value=0.1, min_value=0.0, max_value=1.0, step=0.01)
        
        with col2:
            st.write("**Market Conditions:**")
            holiday_promotion = st.selectbox("Holiday/Promotion", ["No (0)", "Yes (1)"])
            competitor_pricing = st.number_input("Competitor Price ($)", value=14.0, min_value=0.0)
            
            st.write("**Location & Category:**")
            store_id = st.selectbox("Store ID", range(0, 10))
            product_id = st.selectbox("Product ID", range(0, 20))
            category = st.selectbox("Category", range(0, 5))
            region = st.selectbox("Region", range(0, 4))
        
        with col3:
            st.write("**External Factors:**")
            weather_condition = st.selectbox("Weather Condition", range(0, 3))
            seasonality = st.selectbox("Seasonality", range(0, 4))
            
            st.write("**Historical Data:**")
            rolling_3 = st.number_input("3-Day Rolling Average", value=22.0, min_value=0.0)
            rolling_7 = st.number_input("7-Day Rolling Average", value=23.0, min_value=0.0)
            lag_1 = st.number_input("Previous Day Demand", value=23.0, min_value=0.0)
            lag_3 = st.number_input("3-Day Lag Demand", value=22.0, min_value=0.0)
            demand_diff = st.number_input("Demand Difference", value=1.0)
        
        # Predict button
        predict_btn = st.form_submit_button("🔮 Predict Demand", width=" stretch\)
        
        if predict_btn:
            # Prepare input data in the correct order
            holiday_val = 1 if "Yes" in holiday_promotion else 0
            price_demand_interaction = price * demand_forecast
            
            # Create feature array in the exact order expected by the model
            feature_values = [
                inventory_level,      # Inventory Level
                units_ordered,        # Units Ordered  
                demand_forecast,      # Demand Forecast
                price,               # Price
                discount,            # Discount
                holiday_val,         # Holiday/Promotion
                competitor_pricing,  # Competitor Pricing
                rolling_3,           # Demand Forecast_rolling_3
                rolling_7,           # Demand Forecast_rolling_7
                lag_1,               # Demand Forecast_lag_1
                lag_3,               # Demand Forecast_lag_3
                demand_diff,         # Demand Forecast_diff
                price_demand_interaction,  # Price_Demand Forecast_interaction
                store_id,            # Store ID_encoded
                product_id,          # Product ID_encoded
                category,            # Category_encoded
                region,              # Region_encoded
                weather_condition,   # Weather Condition_encoded
                seasonality          # Seasonality_encoded
            ]
            
            input_data = np.array([feature_values])
            
            # Apply scaling if available
            if scaler:
                input_data = scaler.transform(input_data)
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Display result
            st.success("✅ Prediction Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Predicted Daily Demand", f"{prediction:.2f} units")
            with col2:
                annual_demand = prediction * 365
                st.metric("📊 Annual Demand", f"{annual_demand:.0f} units")
            with col3:
                if prediction > 0:
                    days_supply = inventory_level / prediction
                    st.metric("📅 Current Days Supply", f"{days_supply:.0f} days")
                else:
                    st.metric("📅 Current Days Supply", "N/A")
            
            # Store prediction in session state for inventory planning
            st.session_state['predicted_demand'] = prediction
            st.session_state['annual_demand'] = annual_demand
            
            st.info("💡 **Next Step:** Go to 'Inventory Planning' page to calculate optimal inventory parameters based on this demand prediction!")

def show_inventory_planning(inventory_plan):
    st.header("📦 Inventory Planning Calculator")
    st.write("Calculate optimal inventory parameters based on demand prediction")
    
    # Check if we have a demand prediction from the forecasting page
    if 'predicted_demand' in st.session_state:
        st.success(f"✅ Using predicted demand: {st.session_state['predicted_demand']:.2f} units/day")
        default_demand = st.session_state['predicted_demand']
    else:
        st.info("💡 **Tip:** First go to 'Demand Forecasting' page to predict demand, or enter demand manually below.")
        default_demand = 10.0
    
    # Simple input form for inventory calculations
    with st.form("inventory_planning_form"):
        st.subheader("📝 Product & Cost Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Demand Information:**")
            daily_demand = st.number_input("Daily Demand (units)", value=default_demand, min_value=0.1, step=0.1)
            demand_std_dev = st.number_input("Demand Variability (Std Dev)", value=2.0, min_value=0.1, step=0.1,
                                           help="Standard deviation of daily demand - higher values indicate more unpredictable demand")
            
            st.write("**Lead Time & Service:**")
            lead_time = st.number_input("Lead Time (days)", value=7, min_value=1, max_value=365,
                                      help="Time between placing an order and receiving it")
            service_level = st.selectbox("Service Level (%)", [85, 90, 95, 98, 99], index=2,
                                       help="Probability of not running out of stock during lead time")
        
        with col2:
            st.write("**Cost Information:**")
            ordering_cost = st.number_input("Ordering Cost ($)", value=50.0, min_value=0.1,
                                          help="Fixed cost of placing one order (setup, paperwork, etc.)")
            unit_cost = st.number_input("Unit Cost ($)", value=10.0, min_value=0.01,
                                      help="Cost to purchase/produce one unit")
            holding_cost_rate = st.number_input("Holding Cost Rate (%/year)", value=25.0, min_value=0.1) / 100
            
            st.write("**Product Information:**")
            product_name = st.text_input("Product Name (optional)", value="Product A")
            sku_id = st.text_input("SKU ID (optional)", value="SKU-001")
        
        # Calculate button
        calculate_btn = st.form_submit_button("🧮 Calculate Inventory Parameters", width=" stretch\)
        
        if calculate_btn:
            # Inventory calculations
            z_scores = {85: 1.04, 90: 1.28, 95: 1.645, 98: 2.05, 99: 2.33}
            z_score = z_scores[service_level]
            
            # 1. Safety Stock calculation
            safety_stock = z_score * demand_std_dev * np.sqrt(lead_time)
            
            # 2. Reorder Point calculation
            reorder_point = (daily_demand * lead_time) + safety_stock
            
            # 3. Economic Order Quantity (EOQ) calculation
            annual_demand = daily_demand * 365
            eoq = np.sqrt((2 * annual_demand * ordering_cost) / (unit_cost * holding_cost_rate))
            
            # Display main results
            st.success("✅ Inventory Parameters Calculated!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🛡️ Safety Stock", f"{safety_stock:.1f} units", 
                         delta=f"{service_level}% service level")
            with col2:
                st.metric("🔄 Reorder Point", f"{reorder_point:.1f} units",
                         delta=f"{lead_time} days lead time")
            with col3:
                st.metric("📦 Economic Order Quantity", f"{eoq:.0f} units",
                         delta=f"Optimal order size")
            
            # Additional insights
            st.write("---")
            st.subheader("📊 Additional Insights")
            
            # Calculate additional metrics
            avg_inventory = (eoq / 2) + safety_stock
            inventory_turnover = annual_demand / avg_inventory if avg_inventory > 0 else 0
            days_supply = avg_inventory / daily_demand
            
            # Cost analysis
            annual_ordering_cost = (annual_demand / eoq) * ordering_cost
            annual_holding_cost = avg_inventory * unit_cost * holding_cost_rate
            total_annual_cost = annual_ordering_cost + annual_holding_cost
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📈 Performance Metrics:**")
                st.write(f"• Annual Demand: {annual_demand:.0f} units")
                st.write(f"• Average Inventory: {avg_inventory:.0f} units")
                st.write(f"• Inventory Turnover: {inventory_turnover:.1f}x/year")
                st.write(f"• Days of Supply: {days_supply:.0f} days")
            
            with col2:
                st.write("**💰 Cost Analysis:**")
                st.write(f"• Annual Ordering Cost: ${annual_ordering_cost:.2f}")
                st.write(f"• Annual Holding Cost: ${annual_holding_cost:.2f}")
                st.write(f"• **Total Annual Cost: ${total_annual_cost:.2f}**")
                st.write(f"• Cost per Unit Sold: ${total_annual_cost/annual_demand:.3f}")
            
            with col3:
                st.write("**⚡ Recommendations:**")
                if inventory_turnover > 12:
                    st.write("🔥 High turnover - Very efficient")
                elif inventory_turnover > 6:
                    st.write("✅ Good turnover ratio")
                elif inventory_turnover > 4:
                    st.write("⚠️ Moderate turnover")
                else:
                    st.write("🐌 Low turnover - Review demand")
                
                reorder_frequency = 365 / (annual_demand / eoq)
                st.write(f"📅 Reorder every {reorder_frequency:.0f} days")
                
                if days_supply > 30:
                    st.write("📦 Consider reducing inventory")
                elif days_supply < 7:
                    st.write("⚠️ Low inventory buffer")
                else:
                    st.write("👍 Balanced inventory level")
            
            # Summary table
            st.write("---")
            st.subheader("📋 Inventory Planning Summary")
            
            summary_data = {
                'Parameter': [
                    'Product Name', 'SKU ID', 'Daily Demand', 'Annual Demand',
                    'Safety Stock', 'Reorder Point', 'Economic Order Quantity',
                    'Average Inventory', 'Service Level', 'Lead Time',
                    'Total Annual Cost', 'Inventory Turnover'
                ],
                'Value': [
                    product_name, sku_id, f"{daily_demand:.1f} units", f"{annual_demand:.0f} units",
                    f"{safety_stock:.1f} units", f"{reorder_point:.1f} units", f"{eoq:.0f} units",
                    f"{avg_inventory:.0f} units", f"{service_level}%", f"{lead_time} days",
                    f"${total_annual_cost:.2f}", f"{inventory_turnover:.1f}x/year"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, width=" stretch\, hide_index=True)
            
            # Store data in session state for download outside the form
            st.session_state['inventory_summary'] = summary_df
            st.session_state['sku_id'] = sku_id
    
    # Download button outside the form
    if 'inventory_summary' in st.session_state:
        csv_data = st.session_state['inventory_summary'].to_csv(index=False)
        st.download_button(
            label="📥 Download Inventory Plan Summary",
            data=csv_data,
            file_name=f"inventory_plan_{st.session_state['sku_id']}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Quick reference section
    st.write("---")
    st.subheader("📚 Quick Reference")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📖 Formula Explanations:**")
        st.write("• **Safety Stock** = Z-score × Demand Std Dev × √Lead Time")
        st.write("• **Reorder Point** = (Daily Demand × Lead Time) + Safety Stock")
        st.write("• **EOQ** = √(2 × Annual Demand × Ordering Cost / (Unit Cost × Holding Rate))")
        
    with col2:
        st.write("**🎯 Service Level Z-scores:**")
        z_score_ref = pd.DataFrame({
            'Service Level': ['85%', '90%', '95%', '98%', '99%'],
            'Z-score': [1.04, 1.28, 1.645, 2.05, 2.33],
            'Stockout Risk': ['15%', '10%', '5%', '2%', '1%']
        })
        st.dataframe(z_score_ref, hide_index=True)

def show_analytics(inventory_plan):
    st.header("� Advanced Analytics")
    st.markdown("*Deep insights for data-driven inventory decisions*")
    
    # Calculate additional metrics for analysis
    avg_inventory = (inventory_plan['EOQ'] / 2) + inventory_plan['Safety_Stock']
    turnover = inventory_plan['Annual_Demand'] / avg_inventory
    inventory_plan_enhanced = inventory_plan.copy()
    inventory_plan_enhanced['Avg_Inventory'] = avg_inventory
    inventory_plan_enhanced['Turnover_Ratio'] = turnover
    inventory_plan_enhanced['Days_Supply'] = avg_inventory / inventory_plan['Predicted_Demand']
    inventory_plan_enhanced['Total_Annual_Cost'] = (inventory_plan['Annual_Demand'] / inventory_plan['EOQ'] * 50) + (avg_inventory * 10 * 0.25)
    inventory_plan_enhanced['Inventory_Value'] = avg_inventory * 10  # Assuming $10 unit cost
    
    # Create tabs for different analytical views
    tab1, tab2, tab3 = st.tabs(["🎯 Demand Forecasting", "📦 Inventory Management", "💰 Financial Insights"])
    
    with tab1:
        st.subheader("🎯 Demand Forecasting Analysis")
        
        # Generate synthetic time series data for demonstration
        np.random.seed(42)  # For reproducible results
        dates = pd.date_range(start='2024-01-01', periods=365, freq='D')
        
        # Select top 5 SKUs for detailed analysis
        top_5_skus = inventory_plan_enhanced.nlargest(5, 'Annual_Demand')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Plot 9: Demand Trend Analysis
            demand_trends = []
            for _, sku in top_5_skus.iterrows():
                base_demand = sku['Predicted_Demand']
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * np.arange(365) / 365)  # Yearly seasonality
                trend_factor = 1 + 0.002 * np.arange(365)  # Slight upward trend
                noise = np.random.normal(0, 0.1, 365)
                
                daily_demands = base_demand * seasonal_factor * trend_factor * (1 + noise)
                daily_demands = np.maximum(daily_demands, 0)  # Ensure non-negative
                
                for i, demand in enumerate(daily_demands):
                    demand_trends.append({
                        'Date': dates[i],
                        'SKU_ID': sku['SKU_ID'],
                        'Daily_Demand': demand,
                        'Baseline_Demand': base_demand
                    })
            
            demand_df = pd.DataFrame(demand_trends)
            
            fig10 = px.line(demand_df, x='Date', y='Daily_Demand', color='SKU_ID',
                           title="📈 Demand Trends Over Time (Top 5 SKUs)")
            fig10.update_layout(xaxis_title="Date", yaxis_title="Daily Demand")
            st.plotly_chart(fig10, width=" stretch\)
            
            # Plot 10: Forecast Accuracy Analysis
            # Simulate forecast vs actual data
            forecast_analysis = []
            for _, sku in top_5_skus.iterrows():
                actual = sku['Predicted_Demand']
                forecast_error = np.random.normal(0, 0.15)  # 15% standard deviation
                forecasted = actual * (1 + forecast_error)
                
                forecast_analysis.append({
                    'SKU_ID': sku['SKU_ID'],
                    'Actual_Demand': actual,
                    'Forecasted_Demand': forecasted,
                    'Absolute_Error': abs(actual - forecasted),
                    'Percentage_Error': abs((actual - forecasted) / actual) * 100
                })
            
            forecast_df = pd.DataFrame(forecast_analysis)
            
            fig11 = px.scatter(forecast_df, x='Actual_Demand', y='Forecasted_Demand',
                             size='Absolute_Error', hover_data=['SKU_ID', 'Percentage_Error'],
                             title="🎯 Forecast Accuracy: Actual vs Predicted")
            
            # Add perfect forecast line
            max_demand = max(forecast_df['Actual_Demand'].max(), forecast_df['Forecasted_Demand'].max())
            fig11.add_shape(type="line", x0=0, y0=0, x1=max_demand, y1=max_demand,
                           line=dict(dash="dash", color="red"), name="Perfect Forecast")
            st.plotly_chart(fig11, width=" stretch\)
        
        with col2:
            # Plot 11: Demand Variability Analysis
            demand_variability = []
            for _, sku in inventory_plan_enhanced.iterrows():
                # Simulate monthly demand for each SKU
                monthly_demands = np.random.normal(sku['Predicted_Demand'] * 30, 
                                                 sku['Predicted_Demand'] * 3, 12)
                monthly_demands = np.maximum(monthly_demands, 0)
                
                cv = np.std(monthly_demands) / np.mean(monthly_demands)  # Coefficient of variation
                demand_variability.append({
                    'SKU_ID': sku['SKU_ID'],
                    'Mean_Monthly_Demand': np.mean(monthly_demands),
                    'Std_Monthly_Demand': np.std(monthly_demands),
                    'Coefficient_of_Variation': cv,
                    'Predictability': 'High' if cv < 0.2 else 'Medium' if cv < 0.5 else 'Low'
                })
            
            variability_df = pd.DataFrame(demand_variability)
            
            fig12 = px.scatter(variability_df, x='Mean_Monthly_Demand', y='Coefficient_of_Variation',
                             color='Predictability', size='Std_Monthly_Demand',
                             title="📊 Demand Variability Analysis",
                             hover_data=['SKU_ID'])
            
            # Add reference lines for predictability zones
            fig12.add_hline(y=0.2, line_dash="dot", annotation_text="High Predictability Threshold")
            fig12.add_hline(y=0.5, line_dash="dot", annotation_text="Medium Predictability Threshold")
            st.plotly_chart(fig12, width=" stretch\)
            
            # Plot 12: Seasonal Decomposition
            # Create seasonal pattern analysis
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            seasonal_factors = [0.9, 0.85, 1.1, 1.2, 1.3, 1.4, 1.5, 1.4, 1.2, 1.1, 0.9, 0.8]  # Holiday/seasonal pattern
            
            seasonal_data = []
            for i, month in enumerate(months):
                avg_seasonal_demand = inventory_plan_enhanced['Predicted_Demand'].mean() * seasonal_factors[i]
                seasonal_data.append({
                    'Month': month,
                    'Seasonal_Factor': seasonal_factors[i],
                    'Avg_Demand': avg_seasonal_demand
                })
            
            seasonal_df = pd.DataFrame(seasonal_data)
            
            fig13 = go.Figure()
            fig13.add_trace(go.Bar(x=seasonal_df['Month'], y=seasonal_df['Avg_Demand'],
                                  name='Average Demand', marker_color='lightblue'))
            fig13.add_trace(go.Scatter(x=seasonal_df['Month'], y=seasonal_df['Seasonal_Factor'],
                                     mode='lines+markers', name='Seasonal Factor',
                                     yaxis='y2', line=dict(color='red', width=3)))
            
            fig13.update_layout(
                title="📅 Seasonal Demand Patterns",
                xaxis_title="Month",
                yaxis=dict(title="Average Demand", side="left"),
                yaxis2=dict(title="Seasonal Factor", side="right", overlaying="y"),
                legend=dict(x=0.7, y=0.9)
            )
            st.plotly_chart(fig13, width=" stretch\)
    
    with tab2:
        st.subheader("📦 Inventory Management Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Plot 13: Stock Level Simulation
            # Simulate inventory levels over time for a sample SKU
            sample_sku = inventory_plan_enhanced.iloc[0]
            simulation_days = 90
            
            inventory_simulation = []
            current_stock = sample_sku['EOQ']  # Start with full EOQ
            
            for day in range(simulation_days):
                # Daily demand with some randomness
                daily_demand = max(0, np.random.normal(sample_sku['Predicted_Demand'], 
                                                     sample_sku['Predicted_Demand'] * 0.2))
                current_stock -= daily_demand
                
                # Reorder when hitting ROP
                if current_stock <= sample_sku['Reorder_Point']:
                    current_stock += sample_sku['EOQ']
                
                inventory_simulation.append({
                    'Day': day + 1,
                    'Stock_Level': max(0, current_stock),
                    'Reorder_Point': sample_sku['Reorder_Point'],
                    'Safety_Stock': sample_sku['Safety_Stock']
                })
            
            sim_df = pd.DataFrame(inventory_simulation)
            
            fig14 = go.Figure()
            fig14.add_trace(go.Scatter(x=sim_df['Day'], y=sim_df['Stock_Level'],
                                     mode='lines', name='Stock Level', line=dict(color='blue', width=2)))
            fig14.add_trace(go.Scatter(x=sim_df['Day'], y=sim_df['Reorder_Point'],
                                     mode='lines', name='Reorder Point', line=dict(color='red', dash='dash')))
            fig14.add_trace(go.Scatter(x=sim_df['Day'], y=sim_df['Safety_Stock'],
                                     mode='lines', name='Safety Stock', line=dict(color='orange', dash='dot')))
            
            fig14.update_layout(title=f"📊 Stock Level Simulation - {sample_sku['SKU_ID']}",
                              xaxis_title="Days", yaxis_title="Units")
            st.plotly_chart(fig14, width=" stretch\)
            
            # Plot 14: EOQ Optimization Analysis
            # Show how EOQ changes with different parameters
            eoq_analysis = []
            cost_multipliers = np.linspace(0.5, 2.0, 20)
            
            for multiplier in cost_multipliers:
                new_ordering_cost = 50 * multiplier
                new_eoq = np.sqrt((2 * sample_sku['Annual_Demand'] * new_ordering_cost) / (10 * 0.25))
                total_cost = (sample_sku['Annual_Demand'] / new_eoq * new_ordering_cost) + ((new_eoq / 2) * 10 * 0.25)
                
                eoq_analysis.append({
                    'Cost_Multiplier': multiplier,
                    'Ordering_Cost': new_ordering_cost,
                    'EOQ': new_eoq,
                    'Total_Cost': total_cost
                })
            
            eoq_df = pd.DataFrame(eoq_analysis)
            
            fig15 = make_subplots(specs=[[{"secondary_y": True}]])
            fig15.add_trace(go.Scatter(x=eoq_df['Cost_Multiplier'], y=eoq_df['EOQ'],
                                     mode='lines+markers', name='EOQ'), secondary_y=False)
            fig15.add_trace(go.Scatter(x=eoq_df['Cost_Multiplier'], y=eoq_df['Total_Cost'],
                                     mode='lines+markers', name='Total Cost', line=dict(color='red')), secondary_y=True)
            
            fig15.update_layout(title="⚖️ EOQ Sensitivity to Ordering Costs")
            fig15.update_xaxes(title_text="Ordering Cost Multiplier")
            fig15.update_yaxes(title_text="EOQ (Units)", secondary_y=False)
            fig15.update_yaxes(title_text="Total Annual Cost ($)", secondary_y=True)
            st.plotly_chart(fig15, width=" stretch\)
        
        with col2:
            # Plot 15: Service Level vs Cost Analysis
            service_levels = [85, 90, 95, 98, 99, 99.5]
            z_scores = [1.04, 1.28, 1.645, 2.05, 2.33, 2.58]
            
            service_analysis = []
            for sl, z in zip(service_levels, z_scores):
                avg_safety_stock = z * 0.2 * np.sqrt(7)  # Assuming std dev = 0.2, lead time = 7
                total_safety_stock = avg_safety_stock * len(inventory_plan_enhanced)
                holding_cost = total_safety_stock * 10 * 0.25  # Unit cost * holding rate
                
                service_analysis.append({
                    'Service_Level': sl,
                    'Avg_Safety_Stock': avg_safety_stock,
                    'Total_Safety_Stock': total_safety_stock,
                    'Annual_Holding_Cost': holding_cost
                })
            
            service_df = pd.DataFrame(service_analysis)
            
            fig16 = make_subplots(specs=[[{"secondary_y": True}]])
            fig16.add_trace(go.Scatter(x=service_df['Service_Level'], y=service_df['Total_Safety_Stock'],
                                     mode='lines+markers', name='Total Safety Stock'), secondary_y=False)
            fig16.add_trace(go.Scatter(x=service_df['Service_Level'], y=service_df['Annual_Holding_Cost'],
                                     mode='lines+markers', name='Holding Cost', line=dict(color='red')), secondary_y=True)
            
            fig16.update_layout(title="📊 Service Level vs Inventory Cost Trade-off")
            fig16.update_xaxes(title_text="Service Level (%)")
            fig16.update_yaxes(title_text="Total Safety Stock (Units)", secondary_y=False)
            fig16.update_yaxes(title_text="Annual Holding Cost ($)", secondary_y=True)
            st.plotly_chart(fig16, width=" stretch\)
            
            # Plot 16: ABC Classification Analysis
            # Classify items based on annual demand value
            inventory_plan_enhanced['Annual_Value'] = inventory_plan_enhanced['Annual_Demand'] * 10  # Assuming unit cost $10
            inventory_sorted_abc = inventory_plan_enhanced.sort_values('Annual_Value', ascending=False).reset_index(drop=True)
            inventory_sorted_abc['Cumulative_Value'] = inventory_sorted_abc['Annual_Value'].cumsum()
            inventory_sorted_abc['Cumulative_Percentage'] = (inventory_sorted_abc['Cumulative_Value'] / inventory_sorted_abc['Annual_Value'].sum()) * 100
            
            # Define ABC categories
            inventory_sorted_abc['ABC_Category'] = 'C'
            inventory_sorted_abc.loc[inventory_sorted_abc['Cumulative_Percentage'] <= 80, 'ABC_Category'] = 'A'
            inventory_sorted_abc.loc[(inventory_sorted_abc['Cumulative_Percentage'] > 80) & 
                                   (inventory_sorted_abc['Cumulative_Percentage'] <= 95), 'ABC_Category'] = 'B'
            
            abc_summary = inventory_sorted_abc.groupby('ABC_Category').agg({
                'SKU_ID': 'count',
                'Annual_Value': 'sum'
            }).reset_index()
            abc_summary.columns = ['Category', 'SKU_Count', 'Total_Value']
            abc_summary['Value_Percentage'] = (abc_summary['Total_Value'] / abc_summary['Total_Value'].sum()) * 100
            
            fig17 = px.pie(abc_summary, values='SKU_Count', names='Category',
                          title="🎯 ABC Classification: SKU Distribution",
                          color_discrete_map={'A': 'red', 'B': 'orange', 'C': 'lightblue'})
            st.plotly_chart(fig17, width=" stretch\)
            
            # Display ABC summary table
            st.write("**ABC Analysis Summary:**")
            abc_display = abc_summary.copy()
            abc_display['Total_Value'] = abc_display['Total_Value'].apply(lambda x: f"${x:,.0f}")
            abc_display['Value_Percentage'] = abc_display['Value_Percentage'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(abc_display, width=" stretch\)
    
    with tab3:
        st.subheader("Financial & Cost Analysis")
        
        # 4 additional financial plots
        col1, col2 = st.columns(2)
        
        with col1:
            # Plot 5: Cost Breakdown Analysis
            ordering_cost = (inventory_plan_enhanced['Annual_Demand'] / inventory_plan_enhanced['EOQ']) * 50
            holding_cost = inventory_plan_enhanced['Avg_Inventory'] * 10 * 0.25
            
            cost_comparison = pd.DataFrame({
                'SKU_ID': inventory_plan_enhanced['SKU_ID'],
                'Ordering_Cost': ordering_cost,
                'Holding_Cost': holding_cost,
                'Total_Cost': ordering_cost + holding_cost
            })
            
            fig6 = px.scatter(cost_comparison, x='Ordering_Cost', y='Holding_Cost',
                            size='Total_Cost', hover_data=['SKU_ID'],
                            title="💰 Ordering vs Holding Costs (Bubble Size = Total Cost)")
            fig6.add_shape(type="line", x0=0, y0=0, x1=cost_comparison['Ordering_Cost'].max(), 
                          y1=cost_comparison['Ordering_Cost'].max(), line=dict(dash="dash", color="gray"))
            st.plotly_chart(fig6, width=" stretch\)
            
            # Plot 6: Inventory Value Distribution
            fig7 = px.histogram(inventory_plan_enhanced, x='Inventory_Value',
                              title="💎 Inventory Value Distribution",
                              nbins=25, color_discrete_sequence=['lightblue'])
            fig7.add_vline(x=inventory_plan_enhanced['Inventory_Value'].mean(), 
                          line_dash="dash", line_color="red",
                          annotation_text=f"Mean: ${inventory_plan_enhanced['Inventory_Value'].mean():.0f}")
            st.plotly_chart(fig7, width=" stretch\)
        
        with col2:
            # Plot 7: ROI Analysis (Turnover vs Cost Efficiency)
            cost_per_unit_sold = inventory_plan_enhanced['Total_Annual_Cost'] / inventory_plan_enhanced['Annual_Demand']
            inventory_plan_enhanced['Cost_Efficiency'] = 1 / cost_per_unit_sold  # Higher is better
            
            fig8 = px.scatter(inventory_plan_enhanced, x='Turnover_Ratio', y='Cost_Efficiency',
                            color='Lead_Time_Days', size='Annual_Demand',
                            title="📊 ROI Analysis: Turnover vs Cost Efficiency",
                            hover_data=['SKU_ID'])
            
            # Add quadrant lines
            median_turnover = inventory_plan_enhanced['Turnover_Ratio'].median()
            median_efficiency = inventory_plan_enhanced['Cost_Efficiency'].median()
            fig8.add_vline(x=median_turnover, line_dash="dot", line_color="gray")
            fig8.add_hline(y=median_efficiency, line_dash="dot", line_color="gray")
            
            # Add quadrant labels
            fig8.add_annotation(x=median_turnover*1.5, y=median_efficiency*1.5, text="High Performance", 
                              showarrow=False, bgcolor="lightgreen", opacity=0.7)
            fig8.add_annotation(x=median_turnover*0.5, y=median_efficiency*0.5, text="Needs Attention", 
                              showarrow=False, bgcolor="lightcoral", opacity=0.7)
            
            st.plotly_chart(fig8, width=" stretch\)
            
            # Plot 8: Lead Time vs Total Cost Analysis
            fig9 = px.violin(inventory_plan_enhanced, x='Lead_Time_Days', y='Total_Annual_Cost',
                           title="🎻 Cost Distribution by Lead Time",
                           box=True, points="all")
            st.plotly_chart(fig9, width=" stretch\)
    
    # Summary insights section
    st.write("---")
    st.subheader("🧠 AI-Powered Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📊 Statistical Summary:**")
        high_value_skus = len(inventory_plan_enhanced[inventory_plan_enhanced['Inventory_Value'] > inventory_plan_enhanced['Inventory_Value'].quantile(0.8)])
        
        # Create a simple pareto calculation
        inventory_sorted_simple = inventory_plan_enhanced.sort_values('Annual_Demand', ascending=False)
        top_20_percent_count = int(len(inventory_sorted_simple) * 0.2)
        pareto_20_demand = inventory_sorted_simple.head(top_20_percent_count)['Annual_Demand'].sum()
        pareto_percentage = (pareto_20_demand / inventory_plan_enhanced['Annual_Demand'].sum()) * 100
        
        st.write(f"• High-value SKUs (top 20%): {high_value_skus}")
        st.write(f"• Pareto efficiency: {pareto_percentage:.1f}% demand from top 20% SKUs")
        st.write(f"• Average inventory turnover: {turnover.mean():.1f}x")
        st.write(f"• Total inventory value: ${inventory_plan_enhanced['Inventory_Value'].sum():,.0f}")
    
    with col2:
        st.write("**💡 Optimization Opportunities:**")
        low_efficiency = len(inventory_plan_enhanced[inventory_plan_enhanced['Cost_Efficiency'] < inventory_plan_enhanced['Cost_Efficiency'].median()])
        high_days_supply = len(inventory_plan_enhanced[inventory_plan_enhanced['Days_Supply'] > 30])
        
        st.write(f"• Low cost efficiency SKUs: {low_efficiency}")
        st.write(f"• Excess inventory (>30 days): {high_days_supply}")
        if pareto_percentage < 70:
            st.write("• ⚠️ Consider ABC analysis for better focus")
        else:
            st.write("• ✅ Good demand concentration")
        
        if turnover.mean() < 6:
            st.write("• 🔽 Overall turnover below optimal")
        else:
            st.write("• ✅ Healthy inventory turnover")
    
    with col3:
        st.write("**🎯 Strategic Recommendations:**")
        
        # Lead time analysis
        lead_time_corr = inventory_plan_enhanced['Lead_Time_Days'].corr(inventory_plan_enhanced['Total_Annual_Cost'])
        if abs(lead_time_corr) > 0.3:
            st.write("• 📈 Lead time significantly impacts costs")
        else:
            st.write("• ✅ Lead time costs are well managed")
        
        # Efficiency quadrant analysis
        high_perf_skus = len(inventory_plan_enhanced[
            (inventory_plan_enhanced['Turnover_Ratio'] > median_turnover) & 
            (inventory_plan_enhanced['Cost_Efficiency'] > median_efficiency)
        ])
        
        st.write(f"• High-performance SKUs: {high_perf_skus}/{len(inventory_plan_enhanced)}")
        
        if high_perf_skus / len(inventory_plan_enhanced) > 0.5:
            st.write("• 🌟 Strong overall performance")
        else:
            st.write("• 🎯 Focus on efficiency improvements")

if __name__ == "__main__":
    main()
