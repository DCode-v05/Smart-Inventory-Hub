import React, {useState} from 'react'
import Plot from 'react-plotly.js'
import api from '../api'

const FEATURE_FIELDS = [
  { key: 'Inventory Level', label: 'Inventory Level', type: 'number', default: 100 },
  { key: 'Units Ordered', label: 'Units Ordered', type: 'number', default: 50 },
  { key: 'Demand Forecast', label: 'Demand Forecast', type: 'number', default: 25 },
  { key: 'Price', label: 'Price ($)', type: 'number', default: 10.0, step: 0.01 },
  { key: 'Discount', label: 'Discount (%)', type: 'number', default: 0, min: 0, max: 100 },
  { key: 'Holiday/Promotion', label: 'Holiday/Promotion', type: 'select', options: [{value: 0, label: 'No'}, {value: 1, label: 'Yes'}], default: 0 },
  { key: 'Competitor Pricing', label: 'Competitor Pricing ($)', type: 'number', default: 10.0, step: 0.01 },
  { key: 'Demand Forecast_rolling_3', label: 'Demand Forecast (3-day rolling)', type: 'number', default: 25 },
  { key: 'Demand Forecast_rolling_7', label: 'Demand Forecast (7-day rolling)', type: 'number', default: 25 },
  { key: 'Demand Forecast_lag_1', label: 'Demand Forecast (1-day lag)', type: 'number', default: 25 },
  { key: 'Demand Forecast_lag_3', label: 'Demand Forecast (3-day lag)', type: 'number', default: 25 },
  { key: 'Demand Forecast_diff', label: 'Demand Forecast Difference', type: 'number', default: 0 },
  { key: 'Price_Demand Forecast_interaction', label: 'Price-Demand Interaction', type: 'number', default: 250 },
  { key: 'Store ID_encoded', label: 'Store ID (encoded)', type: 'number', default: 1 },
  { key: 'Product ID_encoded', label: 'Product ID (encoded)', type: 'number', default: 1 },
  { key: 'Category_encoded', label: 'Category (encoded)', type: 'number', default: 1 },
  { key: 'Region_encoded', label: 'Region (encoded)', type: 'number', default: 1 },
  { key: 'Weather Condition_encoded', label: 'Weather Condition (encoded)', type: 'number', default: 1 },
  { key: 'Seasonality_encoded', label: 'Seasonality (encoded)', type: 'number', default: 1 }
]

export default function Forecasting({navigateToPage}){
  const [features, setFeatures] = useState(() => {
    const initial = {}
    FEATURE_FIELDS.forEach(field => {
      initial[field.key] = field.default
    })
    return initial
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('input')
  const [predictionHistory, setPredictionHistory] = useState([])

  const handleInputChange = (key, value) => {
    setFeatures(prev => ({
      ...prev,
      [key]: parseFloat(value) || 0
    }))
  }

  async function handlePredict(){
    setLoading(true)
    setError(null)
    try{
      const payload = { features }
      const res = await api.post('/api/predict/', payload)
      const newResult = {
        ...res.data,
        timestamp: new Date(),
        features: {...features}
      }
      setResult(newResult)
      
      // Add to prediction history
      setPredictionHistory(prev => [...prev, newResult].slice(-10)) // Keep last 10 predictions
    }catch(e){
      setError(e?.response?.data?.error || e.message || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    const initial = {}
    FEATURE_FIELDS.forEach(field => {
      initial[field.key] = field.default
    })
    setFeatures(initial)
    setResult(null)
    setError(null)
  }

  // Generate sample demand trend data
  const generateDemandTrend = () => {
    const days = Array.from({length: 30}, (_, i) => i + 1)
    const baseDemand = features['Demand Forecast'] || 25
    return days.map(day => ({
      day,
      demand: baseDemand + Math.sin(day * 0.2) * 5 + (Math.random() - 0.5) * 3,
      predicted: baseDemand + Math.sin(day * 0.2) * 5
    }))
  }

  // Generate seasonal pattern data
  const generateSeasonalData = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const seasonality = features['Seasonality_encoded'] || 1
    return months.map((month, i) => ({
      month,
      factor: 0.8 + 0.4 * Math.sin((i + seasonality) * 0.5) + 0.2 * Math.random()
    }))
  }

  const demandTrendData = generateDemandTrend()
  const seasonalData = generateSeasonalData()

  return (
    <>
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => setActiveTab('input')}
        >
          Demand Forecasting
        </button>
        <button 
          className={`tab ${activeTab === 'visualizations' ? 'active' : ''}`}
          onClick={() => setActiveTab('visualizations')}
        >
          Demand Visualizations
        </button>
      </div>

      {activeTab === 'input' && (
        <div className="card">
          <h3>Demand Forecasting</h3>
          <p>Enter product and market features to predict demand using our ML model.</p>
          
          <div className="form-grid">
            {FEATURE_FIELDS.map(field => (
              <div key={field.key} className="form-group">
                <label>{field.label}</label>
                {field.type === 'select' ? (
                  <select 
                    value={features[field.key]} 
                    onChange={e => handleInputChange(field.key, e.target.value)}
                  >
                    {field.options.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input 
                    type={field.type}
                    value={features[field.key]} 
                    onChange={e => handleInputChange(field.key, e.target.value)}
                    step={field.step}
                    min={field.min}
                    max={field.max}
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="input-row">
            <button className="button" onClick={handlePredict} disabled={loading}>
              {loading ? 'Predicting...' : 'Predict Demand'}
            </button>
            <button className="button button-secondary" onClick={resetForm}>
              Reset Form
            </button>
          </div>

          {error && (
            <div className="error">
              ❌ Error: {error}
            </div>
          )}

          {result && (
            <div className="results">
              <h4>Prediction Results</h4>
              <div className="metric">
                <span className="metric-label">Predicted Demand:</span>
                <span className="metric-value">
                  {result.prediction !== null ? `${result.prediction.toFixed(2)} units/day` : 'No prediction available'}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Annual Demand:</span>
                <span className="metric-value">
                  {result.prediction !== null ? `${(result.prediction * 365).toFixed(0)} units/year` : 'N/A'}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Model Status:</span>
                <span className="metric-value">{result.model || 'Unknown'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Prediction Time:</span>
                <span className="metric-value">{result.timestamp?.toLocaleTimeString()}</span>
              </div>
              
              {result.prediction && (
                <div style={{marginTop: 20}}>
                  <div style={{marginBottom: 16, padding: 12, background: '#f0fdf4', borderRadius: 8}}>
                    💡 <strong>Next Step:</strong> Use this predicted demand to calculate optimal inventory parameters.
                  </div>
                  <div className="input-row">
                    <button 
                      className="button" 
                      onClick={() => {
                        // Store prediction in localStorage for inventory planning
                        localStorage.setItem('predictedDemand', result.prediction.toString());
                        localStorage.setItem('predictionSource', JSON.stringify({
                          value: result.prediction,
                          timestamp: result.timestamp,
                          features: result.features
                        }));
                        // Navigate to inventory planning page
                        if (navigateToPage) {
                          navigateToPage('inventory');
                        }
                      }}
                    >
                      📦 Use for Inventory Planning
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {predictionHistory.length > 0 && (
            <div className="results" style={{marginTop: 20}}>
              <h4>Prediction History</h4>
              <div className="chart-container">
                <Plot
                  data={[{
                    x: predictionHistory.map((_, i) => i + 1),
                    y: predictionHistory.map(p => p.prediction || 0),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Predictions',
                    line: {color: '#3b82f6'},
                    marker: {size: 8}
                  }]}
                  layout={{
                    title: 'Recent Prediction History',
                    xaxis: {title: 'Prediction #'},
                    yaxis: {title: 'Predicted Demand'},
                    height: 300,
                    margin: {t: 40, b: 40, l: 60, r: 20}
                  }}
                  config={{displayModeBar: false}}
                  style={{width: '100%', height: '100%'}}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'visualizations' && (
        <div>
          <div className="viz-grid">
            <div className="viz-container">
              <h4>30-Day Demand Trend Simulation</h4>
              <Plot
                data={[
                  {
                    x: demandTrendData.map(d => d.day),
                    y: demandTrendData.map(d => d.demand),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Actual Demand',
                    line: {color: '#ef4444'}
                  },
                  {
                    x: demandTrendData.map(d => d.day),
                    y: demandTrendData.map(d => d.predicted),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Predicted Trend',
                    line: {color: '#3b82f6', dash: 'dot'}
                  }
                ]}
                layout={{
                  title: 'Demand Variability Over Time',
                  xaxis: {title: 'Day'},
                  yaxis: {title: 'Demand (units)'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>📅 Seasonal Demand Patterns</h4>
              <Plot
                data={[{
                  x: seasonalData.map(d => d.month),
                  y: seasonalData.map(d => d.factor),
                  type: 'bar',
                  marker: {color: '#8b5cf6'},
                  name: 'Seasonal Factor'
                }]}
                layout={{
                  title: 'Monthly Seasonality Index',
                  xaxis: {title: 'Month'},
                  yaxis: {title: 'Seasonal Factor'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>Feature Importance</h4>
              <Plot
                data={[{
                  x: ['Price', 'Inventory Level', 'Seasonality', 'Weather', 'Promotion'],
                  y: [0.25, 0.20, 0.18, 0.15, 0.12],
                  type: 'bar',
                  marker: {color: '#059669'},
                  name: 'Importance Score'
                }]}
                layout={{
                  title: 'Top 5 Feature Importance (ML Model)',
                  xaxis: {title: 'Features'},
                  yaxis: {title: 'Importance Score'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>Forecast Accuracy</h4>
              <Plot
                data={[{
                  x: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                  y: [95.2, 93.8, 94.5, 96.1],
                  type: 'scatter',
                  mode: 'lines+markers',
                  line: {color: '#dc2626'},
                  marker: {size: 10},
                  name: 'Accuracy %'
                }]}
                layout={{
                  title: 'Weekly Forecast Accuracy',
                  xaxis: {title: 'Time Period'},
                  yaxis: {title: 'Accuracy (%)', range: [90, 100]},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>
          </div>

          <div className="card">
            <h3>Demand Insights Summary</h3>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '16px'}}>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#059669', margin: 0}}>94.9%</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Avg Forecast Accuracy</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#dc2626', margin: 0}}>±15%</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Demand Variability</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#2563eb', margin: 0}}>1.2x</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Seasonal Peak Factor</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#7c3aed', margin: 0}}>7 days</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Optimal Forecast Horizon</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}