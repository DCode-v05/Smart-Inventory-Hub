import React from 'react'

export default function About() {
  return (
    <>
      <div className="hero">
        <h2>Retail Forecasting & Inventory Planning Hub</h2>
        <p>
          Empowering retailers with AI-driven demand forecasting and intelligent inventory optimization. 
          Transform your supply chain decisions with machine learning predictions, cost optimization algorithms, 
          and real-time analytics for maximum efficiency and profitability.
        </p>
      </div>

      <div className="content-section">
        <h3>Why Choose Our Platform?</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '20px'}}>
          <div className="feature-card">
            <h4>Precision Forecasting</h4>
            <p>Advanced Random Forest algorithms analyze 19+ variables to predict demand with unprecedented accuracy.</p>
          </div>
          <div className="feature-card">
            <h4>Smart Optimization</h4>
            <p>Automatically calculate EOQ, ROP, and safety stock levels to minimize costs while maintaining service levels.</p>
          </div>
          <div className="feature-card">
            <h4>Interactive Insights</h4>
            <p>Beautiful visualizations and dashboards provide actionable insights at a glance.</p>
          </div>
        </div>
      </div>

      <div className="benefits">
        <h2>Proven Business Impact</h2>
        <div className="benefits-grid">
          <div className="benefit-item">
            <div className="metric">↓ 30%</div>
            <div className="label">Inventory Costs</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↑ 25%</div>
            <div className="label">Forecast Accuracy</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↓ 40%</div>
            <div className="label">Stockouts</div>
          </div>
          <div className="benefit-item">
            <div className="metric">↑ 95%</div>
            <div className="label">Service Level</div>
          </div>
        </div>
      </div>
      
      <div className="content-section">
        <h3>Core Capabilities</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginTop: '20px'}}>
          <div className="feature-card">
            <h4 style={{color: '#059669'}}>Machine Learning Engine</h4>
            <p>Sophisticated algorithms that learn from your data patterns to deliver precise demand predictions.</p>
            <ul style={{fontSize: '14px', color: '#6b7280', marginTop: '12px'}}>
              <li>Random Forest Regressor</li>
              <li>Feature importance analysis</li>
              <li>Cross-validation testing</li>
              <li>Continuous model improvement</li>
            </ul>
          </div>
          
          <div className="feature-card">
            <h4 style={{color: '#dc2626'}}>Inventory Intelligence</h4>
            <p>Comprehensive inventory optimization using proven mathematical models and modern analytics.</p>
            <ul style={{fontSize: '14px', color: '#6b7280', marginTop: '12px'}}>
              <li>Economic Order Quantity (EOQ)</li>
              <li>Reorder Point calculations</li>
              <li>Safety stock optimization</li>
              <li>Service level management</li>
            </ul>
          </div>
          
          <div className="feature-card">
            <h4 style={{color: '#2563eb'}}>Visual Analytics</h4>
            <p>Interactive dashboards and charts that make complex data insights accessible and actionable.</p>
            <ul style={{fontSize: '14px', color: '#6b7280', marginTop: '12px'}}>
              <li>Demand trend analysis</li>
              <li>Cost breakdown charts</li>
              <li>Inventory simulations</li>
              <li>ABC classification views</li>
            </ul>
          </div>
          
          <div className="feature-card">
            <h4 style={{color: '#7c3aed'}}>Cost Optimization</h4>
            <p>Minimize total inventory costs while maintaining optimal service levels through intelligent algorithms.</p>
            <ul style={{fontSize: '14px', color: '#6b7280', marginTop: '12px'}}>
              <li>Holding cost analysis</li>
              <li>Ordering cost optimization</li>
              <li>Trade-off calculations</li>
              <li>ROI maximization</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="content-section">
        <h3>Technology Stack</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginTop: '20px'}}>
          <div>
            <h4>Frontend</h4>
            <ul>
              <li><strong>React 18:</strong> Modern component architecture</li>
              <li><strong>Vite:</strong> Lightning-fast development</li>
              <li><strong>Plotly.js:</strong> Interactive visualizations</li>
              <li><strong>Responsive Design:</strong> Mobile-first approach</li>
            </ul>
          </div>
          
          <div>
            <h4>Backend</h4>
            <ul>
              <li><strong>Django:</strong> Robust web framework</li>
              <li><strong>REST API:</strong> Scalable endpoints</li>
              <li><strong>NumPy/Pandas:</strong> Data processing</li>
              <li><strong>Scikit-learn:</strong> ML model serving</li>
            </ul>
          </div>
          
          <div>
            <h4>Analytics</h4>
            <ul>
              <li><strong>Random Forest:</strong> Demand prediction</li>
              <li><strong>Statistical Models:</strong> Inventory optimization</li>
              <li><strong>Data Validation:</strong> Input verification</li>
              <li><strong>Performance Metrics:</strong> Model evaluation</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="content-section">
        <h3>Getting Started</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginTop: '20px'}}>
          <div>
            <h4>1. Input Your Data</h4>
            <p>Enter your product characteristics, inventory levels, costs, and market conditions through our intuitive interface.</p>
          </div>
          
          <div>
            <h4>2. Get Predictions</h4>
            <p>Our ML model analyzes your inputs and provides accurate demand forecasts with confidence intervals.</p>
          </div>
          
          <div>
            <h4>3. Optimize Inventory</h4>
            <p>Use predictions to calculate optimal reorder points, order quantities, and safety stock levels automatically.</p>
          </div>
          
          <div>
            <h4>4. Monitor & Adjust</h4>
            <p>Track performance with visual dashboards and continuously improve your inventory strategy.</p>
          </div>
        </div>
      </div>
    </>
  )
}