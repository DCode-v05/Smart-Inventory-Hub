import React, {useState} from 'react'
import Home from './pages/Home'
import About from './pages/About'
import Forecasting from './pages/Forecasting'
import Inventory from './pages/Inventory'

export default function App(){
  const [page, setPage] = useState('home')
  
  const renderPage = () => {
    switch(page) {
      case 'home': return <Home navigateToPage={setPage} />
      case 'about': return <About />
      case 'forecast': return <Forecasting navigateToPage={setPage} />
      case 'inventory': return <Inventory />
      default: return <Home navigateToPage={setPage} />
    }
  }
  
  return (
    <div className="app">
      <div className="main-header">
        <h1>Retail Forecasting and Inventory Planning Hub</h1>
        <nav className="nav-bar">
          <button 
            className={`nav-button ${page === 'home' ? 'active' : ''}`}
            onClick={() => setPage('home')}
          >
            Home
          </button>
          <button 
            className={`nav-button ${page === 'about' ? 'active' : ''}`}
            onClick={() => setPage('about')}
          >
            About
          </button>
          <button 
            className={`nav-button ${page === 'forecast' ? 'active' : ''}`}
            onClick={() => setPage('forecast')}
          >
            Demand Forecasting
          </button>
          <button 
            className={`nav-button ${page === 'inventory' ? 'active' : ''}`}
            onClick={() => setPage('inventory')}
          >
            Inventory Planning
          </button>
        </nav>
      </div>

      <div className="page-content">
        {renderPage()}
      </div>
    </div>
  )
}