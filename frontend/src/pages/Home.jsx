import React from 'react'

export default function Home({navigateToPage}) {
  return (
    <>
      <div className="hero">
        <h2>Welcome to the Retail Forecasting Hub</h2>
        <p>
          Transform your inventory management with AI-powered demand forecasting and intelligent planning tools. 
          Make data-driven decisions to optimize stock levels, reduce costs, and improve customer satisfaction.
        </p>
      </div>

      <div className="content-section">
        <h3>Core Features</h3>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Demand Forecasting</h3>
            <p>Advanced ML models predict future demand using 19+ market and product features</p>
          </div>
          
          <div className="feature-card">
            <h3>Inventory Planning</h3>
            <p>Calculate optimal reorder points, EOQ, and safety stock levels automatically</p>
          </div>
          
          <div className="feature-card">
            <h3>Visual Analytics</h3>
            <p>Interactive charts and insights for demand patterns and inventory optimization</p>
          </div>
          
          <div className="feature-card">
            <h3>Cost Optimization</h3>
            <p>Minimize holding and ordering costs while maintaining service levels</p>
          </div>
        </div>
      </div>
      
      <div className="content-section">
        <h3>Quick Start Guide</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '20px'}}>
          <div>
            <h4>1. Demand Forecasting</h4>
            <p>Navigate to the Demand Forecasting page and input your product characteristics:</p>
            <ul>
              <li>Inventory levels and current orders</li>
              <li>Pricing and discount information</li>
              <li>Market conditions and seasonality</li>
              <li>Historical demand patterns</li>
            </ul>
            <button 
              className="button" 
              style={{marginTop: '1rem', width: '100%'}}
              onClick={() => navigateToPage && navigateToPage('forecast')}
            >
              Start Forecasting
            </button>
          </div>
          
          <div>
            <h4>2. Inventory Planning</h4>
            <p>Use predicted demand to calculate optimal inventory metrics:</p>
            <ul>
              <li>Set your service level targets</li>
              <li>Input cost parameters</li>
              <li>Get ROP, EOQ, and safety stock recommendations</li>
              <li>View actionable inventory policies</li>
            </ul>
            <button 
              className="button" 
              style={{marginTop: '1rem', width: '100%'}}
              onClick={() => navigateToPage && navigateToPage('inventory')}
            >
              Plan Inventory
            </button>
          </div>
        </div>
      </div>
      
      <div className="benefits">
        <h2>Proven Results</h2>
        <div className="benefits-grid">
          <div className="benefit-item">
            <div className="metric">↓ 25%</div>
            <div className="label">Inventory Holding Costs</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↓ 15%</div>
            <div className="label">Stockout Incidents</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↑ 95%</div>
            <div className="label">Service Level Achievement</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↑ 30%</div>
            <div className="label">Forecast Accuracy</div>
          </div>
        </div>
      </div>
    </>
  )
}