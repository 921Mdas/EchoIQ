import React, { useState } from 'react';
import api from './api';
import './App.css';

function App() {
  const [apiResults, setApiResults] = useState({
    root: 'Not fetched yet',
    health: 'Not fetched yet',
    greet: 'Not fetched yet'
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const [root, health, greet] = await Promise.all([
        api.getRoot(),
        api.checkHealth(),
        api.greetUser('John')
      ]);

      setApiResults({
        root: root.data?.message || root.message,
        health: health.data?.status || health.status,
        greet: greet.data?.message || greet.message
      });
    } catch (error) {
      console.error('API Error:', error);
      setApiResults({
        root: 'Error fetching data',
        health: 'Error fetching data',
        greet: 'Error fetching data'
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
      <button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Call API'}
      </button>
      
      <div className="results">
        <h3>API Results from {import.meta.env.DEV ? 'localhost' : 'Render'}:</h3>
        <p><strong>Root:</strong> {apiResults.root}</p>
        <p><strong>Health:</strong> {apiResults.health}</p>
        <p><strong>Greeting:</strong> {apiResults.greet}</p>
      </div>
    </div>
  );
}

export default App;