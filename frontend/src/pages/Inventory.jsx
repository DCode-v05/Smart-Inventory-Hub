import React, {useState} from 'react'
import Plot from 'react-plotly.js'
import api from '../api'

export default function Inventory(){
  // Check for predicted demand from forecasting page
  const [hasPredictedDemand, setHasPredictedDemand] = useState(false)
  const [predictionSource, setPredictionSource] = useState(null)
  
  const [formData, setFormData] = useState(() => {
    // Check localStorage for predicted demand
    const savedDemand = localStorage.getItem('predictedDemand')
    const savedSource = localStorage.getItem('predictionSource')
    
    if (savedDemand && savedSource) {
      setHasPredictedDemand(true)
      setPredictionSource(JSON.parse(savedSource))
    }
    
    return {
      predicted_demand: savedDemand ? parseFloat(savedDemand) : 25,
      lead_time_days: 7,
      service_level: 0.95,
      unit_cost: 10.0,
      holding_cost_rate: 0.25,
      ordering_cost: 50,
      demand_std_dev: savedDemand ? parseFloat(savedDemand) * 0.2 : 5.0  // 20% variability by default
    }
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('input')

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }))
  }

  async function calculateMetrics(){
    setLoading(true)
    setError(null)
    try{
      const res = await api.post('/api/inventory/', formData)
      setResult(res.data)
    }catch(e){ 
      setError(e?.response?.data?.error || e.message || 'Calculation failed')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    // Clear localStorage data
    localStorage.removeItem('predictedDemand')
    localStorage.removeItem('predictionSource')
    
    // Reset prediction state
    setHasPredictedDemand(false)
    setPredictionSource(null)
    
    // Reset form data
    setFormData({
      predicted_demand: 25,
      lead_time_days: 7,
      service_level: 0.95,
      unit_cost: 10.0,
      holding_cost_rate: 0.25,
      ordering_cost: 50,
      demand_std_dev: 5.0
    })
    setResult(null)
    setError(null)
  }

  // Generate ABC analysis data
  const generateABCData = () => {
    return [
      {category: 'A-Items', percentage: 20, value: 80, count: 150},
      {category: 'B-Items', percentage: 30, value: 15, count: 225},
      {category: 'C-Items', percentage: 50, value: 5, count: 375}
    ]
  }

  // Generate stock simulation data
  const generateStockSimulation = () => {
    const days = Array.from({length: 30}, (_, i) => i + 1)
    const eoq = result?.eoq || 50
    const reorderPoint = result?.rop || 40
    let currentStock = 100
    
    return days.map(day => {
      // Simulate daily demand with variability
      const dailyDemand = Math.max(0, formData.predicted_demand + (Math.random() - 0.5) * 10)
      currentStock -= dailyDemand
      
      // Reorder when below reorder point
      if (currentStock <= reorderPoint && day % 7 === 0) {
        currentStock += eoq
      }
      
      return {
        day,
        stock: Math.max(0, currentStock),
        reorderPoint,
        demand: dailyDemand
      }
    })
  }

  // Generate cost breakdown data
  const generateCostBreakdown = () => {
    const annualDemand = formData.predicted_demand * 365
    const holdingCost = (formData.unit_cost * formData.holding_cost_rate * (result?.eoq || 50)) / 2
    const orderingCost = (annualDemand / (result?.eoq || 50)) * formData.ordering_cost
    const stockoutCost = formData.unit_cost * 0.1 * 5 // Estimated stockout cost
    
    return [
      {category: 'Holding Cost', amount: holdingCost, percentage: holdingCost / (holdingCost + orderingCost + stockoutCost) * 100},
      {category: 'Ordering Cost', amount: orderingCost, percentage: orderingCost / (holdingCost + orderingCost + stockoutCost) * 100},
      {category: 'Stockout Cost', amount: stockoutCost, percentage: stockoutCost / (holdingCost + orderingCost + stockoutCost) * 100}
    ]
  }

  const abcData = generateABCData()
  const stockSimulation = generateStockSimulation()
  const costBreakdown = generateCostBreakdown()

  return (
    <>
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'input' ? 'active' : ''}`}
          onClick={() => setActiveTab('input')}
        >
          Inventory Optimization
        </button>
        <button 
          className={`tab ${activeTab === 'visualizations' ? 'active' : ''}`}
          onClick={() => setActiveTab('visualizations')}
        >
          Inventory Analytics
        </button>
      </div>

      {activeTab === 'input' && (
        <div className="card">
          <h3>Inventory Planning</h3>
          <p>Calculate optimal inventory metrics based on predicted demand and business parameters.</p>
          
          {hasPredictedDemand && predictionSource && (
            <div style={{
              background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
              border: '1px solid #10b981',
              borderRadius: '12px',
              padding: '1rem',
              marginBottom: '2rem'
            }}>
              <h4 style={{color: '#047857', margin: '0 0 0.5rem 0', fontSize: '1rem'}}>
                Using Predicted Demand from Forecasting
              </h4>
              <div style={{color: '#065f46', fontSize: '0.9rem', lineHeight: '1.4'}}>
                <strong>Predicted Demand:</strong> {predictionSource.value.toFixed(2)} units/day<br/>
                <strong>Prediction Time:</strong> {new Date(predictionSource.timestamp).toLocaleString()}<br/>
                <strong>Annual Demand:</strong> {(predictionSource.value * 365).toFixed(0)} units/year
              </div>
              <button 
                style={{
                  marginTop: '0.5rem',
                  background: 'transparent',
                  border: '1px solid #059669',
                  color: '#059669',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  cursor: 'pointer'
                }}
                onClick={() => {
                  localStorage.removeItem('predictedDemand')
                  localStorage.removeItem('predictionSource')
                  setHasPredictedDemand(false)
                  setPredictionSource(null)
                  setFormData(prev => ({...prev, predicted_demand: 25}))
                }}
              >
                Use Manual Input Instead
              </button>
            </div>
          )}
          
          <div className="form-grid">
            <div className="form-group">
              <label>Predicted Demand (units/day)</label>
              <input 
                type="number" 
                value={formData.predicted_demand} 
                onChange={e => handleInputChange('predicted_demand', e.target.value)}
                placeholder="Daily demand forecast"
                min="0"
                step="0.1"
              />
            </div>
            
            <div className="form-group">
              <label>Demand Variability (Std Dev)</label>
              <input 
                type="number" 
                value={formData.demand_std_dev} 
                onChange={e => handleInputChange('demand_std_dev', e.target.value)}
                placeholder="Standard deviation of demand"
                min="0.1"
                step="0.1"
              />
              <small style={{color: '#6b7280', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block'}}>
                Higher values indicate more unpredictable demand
              </small>
            </div>
            
            <div className="form-group">
              <label>Lead Time (days)</label>
              <input 
                type="number" 
                value={formData.lead_time_days} 
                onChange={e => handleInputChange('lead_time_days', e.target.value)}
                placeholder="Supplier lead time"
                min="1"
              />
            </div>
            
            <div className="form-group">
              <label>Service Level (%)</label>
              <select 
                value={formData.service_level} 
                onChange={e => handleInputChange('service_level', e.target.value)}
              >
                <option value={0.90}>90% (Z=1.28)</option>
                <option value={0.95}>95% (Z=1.65)</option>
                <option value={0.99}>99% (Z=2.33)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Unit Cost ($)</label>
              <input 
                type="number" 
                value={formData.unit_cost} 
                onChange={e => handleInputChange('unit_cost', e.target.value)}
                placeholder="Cost per unit"
                min="0"
                step="0.01"
              />
            </div>
            
            <div className="form-group">
              <label>Holding Cost Rate (%/year)</label>
              <input 
                type="number" 
                value={formData.holding_cost_rate} 
                onChange={e => handleInputChange('holding_cost_rate', e.target.value)}
                placeholder="0.25 = 25%"
                min="0"
                max="1"
                step="0.01"
              />
            </div>
            
            <div className="form-group">
              <label>Ordering Cost ($)</label>
              <input 
                type="number" 
                value={formData.ordering_cost} 
                onChange={e => handleInputChange('ordering_cost', e.target.value)}
                placeholder="Cost per order"
                min="0"
              />
            </div>
          </div>

          <div className="input-row">
            <button className="button" onClick={calculateMetrics} disabled={loading}>
              {loading ? 'Calculating...' : 'Calculate Metrics'}
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
              <h4>Inventory Optimization Results</h4>
              
              <div className="metrics-grid">
                <div className="metric-card">
                  <h5>Reorder Point (ROP)</h5>
                  <div className="metric-value">{result.rop?.toFixed(0)} units</div>
                  <p>Order when inventory reaches this level</p>
                </div>
                
                <div className="metric-card">
                  <h5>Economic Order Quantity (EOQ)</h5>
                  <div className="metric-value">{result.eoq?.toFixed(0)} units</div>
                  <p>Optimal order quantity to minimize costs</p>
                </div>
                
                <div className="metric-card">
                  <h5>Safety Stock</h5>
                  <div className="metric-value">{result.safety_stock?.toFixed(0)} units</div>
                  <p>Buffer stock for demand variability</p>
                </div>
                
                <div className="metric-card">
                  <h5>Total Annual Cost</h5>
                  <div className="metric-value">${result.total_annual_cost?.toFixed(2)}</div>
                  <p>Holding + Ordering costs per year</p>
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <h5>Average Inventory</h5>
                  <div className="metric-value">{result.avg_inventory?.toFixed(0)} units</div>
                  <p>Average stock level maintained</p>
                </div>
                
                <div className="metric-card">
                  <h5>Inventory Turnover</h5>
                  <div className="metric-value">{result.inventory_turnover?.toFixed(1)}x</div>
                  <p>How many times inventory is sold per year</p>
                </div>
                
                <div className="metric-card">
                  <h5>Days Supply</h5>
                  <div className="metric-value">{result.days_supply?.toFixed(0)} days</div>
                  <p>Days of demand covered by average inventory</p>
                </div>
                
                <div className="metric-card">
                  <h5>Annual Demand</h5>
                  <div className="metric-value">{result.annual_demand?.toFixed(0)} units</div>
                  <p>Total yearly demand projection</p>
                </div>
              </div>

              <div className="policy-summary">
                <h5>📋 Inventory Policy Summary</h5>
                <div className="policy-grid">
                  <div>
                    <strong>When to order:</strong> When inventory level drops to {result.rop?.toFixed(0)} units
                  </div>
                  <div>
                    <strong>How much to order:</strong> {result.eoq?.toFixed(0)} units each time
                  </div>
                  <div>
                    <strong>Order frequency:</strong> Every {result.order_frequency_days?.toFixed(0)} days
                  </div>
                  <div>
                    <strong>Service level:</strong> {(result.service_level_used * 100).toFixed(0)}% fill rate target
                  </div>
                </div>
              </div>

              <div style={{
                background: 'rgba(59, 130, 246, 0.05)',
                border: '1px solid rgba(59, 130, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginTop: '1.5rem'
              }}>
                <h5 style={{color: '#2563eb', marginBottom: '1rem', fontSize: '1.1rem', fontWeight: '700'}}>
                  Cost Breakdown Analysis
                </h5>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem'}}>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px'}}>
                    <strong>Annual Ordering Cost:</strong><br/>
                    <span style={{color: '#2563eb', fontWeight: '700'}}>${result.annual_ordering_cost?.toFixed(2)}</span>
                  </div>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px'}}>
                    <strong>Annual Holding Cost:</strong><br/>
                    <span style={{color: '#7c3aed', fontWeight: '700'}}>${result.annual_holding_cost?.toFixed(2)}</span>
                  </div>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px'}}>
                    <strong>Total Annual Cost:</strong><br/>
                    <span style={{color: '#059669', fontWeight: '700'}}>${result.total_annual_cost?.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div style={{
                background: 'rgba(16, 185, 129, 0.05)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem',
                marginTop: '1.5rem'
              }}>
                <h5 style={{color: '#059669', marginBottom: '1rem', fontSize: '1.1rem', fontWeight: '700'}}>
                  Key Insights & Recommendations
                </h5>
                <div style={{display: 'grid', gap: '0.75rem'}}>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px', fontSize: '0.9rem'}}>
                    <strong>Inventory Efficiency:</strong> {result.inventory_turnover > 6 ? 
                      '✅ Good turnover ratio - inventory is moving efficiently' : 
                      '⚠️ Consider strategies to increase inventory velocity'}
                  </div>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px', fontSize: '0.9rem'}}>
                    <strong>Cost Optimization:</strong> EOQ balances ordering frequency with holding costs for minimum total cost
                  </div>
                  <div style={{padding: '0.75rem', background: 'white', borderRadius: '8px', fontSize: '0.9rem'}}>
                    <strong>Risk Management:</strong> Safety stock provides {(result.service_level_used * 100).toFixed(0)}% protection against stockouts during lead time
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'visualizations' && (
        <div>
          <div className="viz-grid">
            <div className="viz-container">
              <h4>📊 ABC Inventory Analysis</h4>
              <Plot
                data={[{
                  x: abcData.map(d => d.category),
                  y: abcData.map(d => d.value),
                  type: 'bar',
                  marker: {color: ['#ef4444', '#f59e0b', '#10b981']},
                  name: 'Value %'
                }]}
                layout={{
                  title: 'ABC Analysis - Value Contribution',
                  xaxis: {title: 'Item Category'},
                  yaxis: {title: 'Value Contribution (%)'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>📈 Stock Level Simulation (30 Days)</h4>
              <Plot
                data={[
                  {
                    x: stockSimulation.map(d => d.day),
                    y: stockSimulation.map(d => d.stock),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Stock Level',
                    line: {color: '#3b82f6'}
                  },
                  {
                    x: stockSimulation.map(d => d.day),
                    y: stockSimulation.map(d => d.reorderPoint),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Reorder Point',
                    line: {color: '#ef4444', dash: 'dash'}
                  }
                ]}
                layout={{
                  title: 'Inventory Level Over Time',
                  xaxis: {title: 'Day'},
                  yaxis: {title: 'Stock Units'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>Cost Breakdown Analysis</h4>
              <Plot
                data={[{
                  values: costBreakdown.map(d => d.amount),
                  labels: costBreakdown.map(d => d.category),
                  type: 'pie',
                  marker: {colors: ['#8b5cf6', '#06b6d4', '#f59e0b']},
                  textinfo: 'label+percent'
                }]}
                layout={{
                  title: 'Annual Inventory Costs',
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 60}
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>

            <div className="viz-container">
              <h4>📊 EOQ vs Order Quantity Analysis</h4>
              <Plot
                data={[{
                  x: [25, 50, 75, 100, 125, 150],
                  y: [180, 120, 95, 85, 90, 110],
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Total Cost',
                  line: {color: '#059669'},
                  marker: {size: 8}
                }]}
                layout={{
                  title: 'Order Quantity vs Total Cost',
                  xaxis: {title: 'Order Quantity'},
                  yaxis: {title: 'Total Cost ($)'},
                  height: 350,
                  margin: {t: 40, b: 40, l: 60, r: 20},
                  annotations: [{
                    x: result?.eoq || 75,
                    y: 85,
                    text: 'Optimal EOQ',
                    showarrow: true,
                    arrowcolor: '#ef4444'
                  }]
                }}
                config={{displayModeBar: false}}
                style={{width: '100%', height: '100%'}}
              />
            </div>
          </div>

          <div className="card">
            <h3>� Inventory Performance Metrics</h3>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '16px'}}>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#059669', margin: 0}}>15.2</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Inventory Turnover</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#dc2626', margin: 0}}>{(formData.service_level * 100).toFixed(1)}%</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Service Level</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#2563eb', margin: 0}}>{Math.ceil((result?.eoq || 50) / formData.predicted_demand)} days</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Days Supply (EOQ)</p>
              </div>
              <div style={{textAlign: 'center', padding: '16px', background: '#f8fafc', borderRadius: '8px'}}>
                <h4 style={{color: '#7c3aed', margin: 0}}>${(formData.unit_cost * formData.holding_cost_rate * 100).toFixed(0)}</h4>
                <p style={{margin: '4px 0', fontSize: '14px'}}>Monthly Holding Cost</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Inventory Optimization Recommendations</h3>
            <div style={{display: 'grid', gap: '12px', marginTop: '16px'}}>
              <div style={{padding: '12px', background: '#f0fdf4', borderLeft: '4px solid #059669', borderRadius: '4px'}}>
                <strong>Optimize Order Frequency:</strong> Current EOQ suggests ordering every {result ? Math.ceil(result.eoq / formData.predicted_demand) : 'N/A'} days to minimize costs.
              </div>
              <div style={{padding: '12px', background: '#fef3c7', borderLeft: '4px solid #f59e0b', borderRadius: '4px'}}>
                <strong>Review Safety Stock:</strong> Consider increasing safety stock during high-demand seasons or uncertain supply periods.
              </div>
              <div style={{padding: '12px', background: '#dbeafe', borderLeft: '4px solid #3b82f6', borderRadius: '4px'}}>
                <strong>ABC Classification:</strong> Focus on A-items (high value) for tighter inventory control and frequent monitoring.
              </div>
              <div style={{padding: '12px', background: '#fce7f3', borderLeft: '4px solid #ec4899', borderRadius: '4px'}}>
                <strong>Technology Integration:</strong> Consider automated reordering systems to trigger orders at optimal reorder points.
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}