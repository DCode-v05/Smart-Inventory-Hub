import os
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Try to lazy-load model artifacts from backend/model/
MODEL = None
SCALER = None
FEATURE_INFO = None

try:
    import joblib
    model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'best_model.pkl')
    scaler_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'feature_scaler.pkl')
    feature_info_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'feature_info.pkl')
    if os.path.exists(model_path):
        MODEL = joblib.load(model_path)
    if os.path.exists(scaler_path):
        SCALER = joblib.load(scaler_path)
    if os.path.exists(feature_info_path):
        FEATURE_INFO = joblib.load(feature_info_path)
except Exception:
    MODEL = None
    SCALER = None
    FEATURE_INFO = None

@api_view(['POST'])
def predict(request):
    """Accepts JSON: { features: { feature_name: value, ... } }"""
    data = request.data or {}
    features = data.get('features') or {}
    # If model loaded and feature_info available, attempt prediction
    if MODEL is None:
        return Response({'prediction': None, 'model': 'no model available'})
    try:
        import pandas as pd
        # Build DataFrame in correct feature order if possible
        if FEATURE_INFO and 'feature_columns' in FEATURE_INFO:
            cols = FEATURE_INFO['feature_columns']
            row = [features.get(c, 0) for c in cols]
            X = pd.DataFrame([row], columns=cols)
        else:
            X = pd.DataFrame([features])
        if SCALER is not None:
            X = SCALER.transform(X)
        pred = MODEL.predict(X)
        return Response({'prediction': float(pred[0]), 'model': str(type(MODEL))})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def inventory(request):
    """Enhanced inventory calculation with detailed metrics like the Streamlit app"""
    d = request.data
    try:
        # Input parameters
        predicted_demand = float(d.get('predicted_demand', 0))
        lead_time_days = float(d.get('lead_time_days', 0))
        service_level = float(d.get('service_level', 0.95))
        unit_cost = float(d.get('unit_cost', 10))
        holding_cost_rate = float(d.get('holding_cost_rate', 0.25))
        ordering_cost = float(d.get('ordering_cost', 50))
        
        # Additional parameters with defaults
        demand_std_dev = float(d.get('demand_std_dev', predicted_demand * 0.2))  # 20% variability
        
        import math
        
        # Z-score based on service level (matching Streamlit app)
        z_scores = {
            0.85: 1.04, 0.90: 1.28, 0.95: 1.645, 
            0.98: 2.05, 0.99: 2.33
        }
        # Find closest service level
        closest_sl = min(z_scores.keys(), key=lambda x: abs(x - service_level))
        z_score = z_scores[closest_sl]
        
        # 1. Safety Stock calculation
        safety_stock = z_score * demand_std_dev * math.sqrt(max(lead_time_days, 1))
        
        # 2. Reorder Point calculation  
        rop = (predicted_demand * lead_time_days) + safety_stock
        
        # 3. Economic Order Quantity (EOQ) calculation
        annual_demand = predicted_demand * 365
        if holding_cost_rate * unit_cost <= 0:
            eoq = 0
        else:
            eoq = math.sqrt((2 * annual_demand * ordering_cost) / (unit_cost * holding_cost_rate))
        
        # 4. Additional metrics (like Streamlit app)
        avg_inventory = (eoq / 2) + safety_stock if eoq > 0 else safety_stock
        inventory_turnover = annual_demand / avg_inventory if avg_inventory > 0 else 0
        days_supply = avg_inventory / predicted_demand if predicted_demand > 0 else 0
        
        # 5. Cost analysis
        annual_ordering_cost = (annual_demand / eoq * ordering_cost) if eoq > 0 else 0
        annual_holding_cost = avg_inventory * unit_cost * holding_cost_rate
        total_annual_cost = annual_ordering_cost + annual_holding_cost
        
        # 6. Order frequency  
        order_frequency_days = eoq / predicted_demand if predicted_demand > 0 else 0
        
        return Response({
            # Basic metrics
            'rop': rop,
            'eoq': eoq, 
            'safety_stock': safety_stock,
            
            # Additional insights
            'avg_inventory': avg_inventory,
            'inventory_turnover': inventory_turnover,
            'days_supply': days_supply,
            'annual_demand': annual_demand,
            
            # Cost breakdown
            'annual_ordering_cost': annual_ordering_cost,
            'annual_holding_cost': annual_holding_cost,
            'total_annual_cost': total_annual_cost,
            
            # Operational metrics
            'order_frequency_days': order_frequency_days,
            'service_level_used': closest_sl,
            'z_score_used': z_score,
            
            # Input echo for validation
            'inputs': {
                'predicted_demand': predicted_demand,
                'lead_time_days': lead_time_days,
                'service_level': service_level,
                'unit_cost': unit_cost,
                'holding_cost_rate': holding_cost_rate,
                'ordering_cost': ordering_cost,
                'demand_std_dev': demand_std_dev
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)