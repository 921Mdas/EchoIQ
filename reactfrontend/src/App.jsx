import React, { useState } from 'react';
import api from './api';
import './App.css';

function App() {
  const [apiResults, setApiResults] = useState({
    health: 'Not checked yet',
    dbStatus: 'Not checked yet'
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const [healthResponse, dbResponse] = await Promise.all([
        api.checkHealth(),
        api.checkDbStatus(),
      ]);
   

      console.log(dbResponse)

      setApiResults({
        health: healthResponse.status || 'healthy',
        dbStatus: `Connected to ${dbResponse.details.dbname} (${dbResponse.details.mode})` 

      });
    } catch (error) {
      console.error('API Error:', error);
      setApiResults({
        health: 'Error fetching health',
        dbStatus: 'Error checking database'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="environment-banner">
        {import.meta.env.DEV ? 'Development Mode' : 'Production Mode'}
      </div>
      
      <button 
        onClick={handleSubmit} 
        disabled={isLoading}
        className={`api-button ${isLoading ? 'loading' : ''}`}
      >
        {isLoading ? 'Checking...' : 'Check System Status'}
      </button>
      
      <div className="results">
        <h3>System Status:</h3>
        <div className={`status-card ${apiResults.health === 'healthy' ? 'success' : 'error'}`}>
          <strong>API Health:</strong> {apiResults.health}
        </div>
        <div className={`status-card ${apiResults.dbStatus.includes('Connected') ? 'success' : 'error'}`}>
          <strong>Database:</strong> {apiResults.dbStatus}
        </div>
      </div>
    </div>
  );
}

export default App;