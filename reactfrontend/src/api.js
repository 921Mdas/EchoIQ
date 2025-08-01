import axios from 'axios';

// Set base URL based on environment
const baseURL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : 'https://echoiq.onrender.com';

const api = axios.create({
  baseURL,
  timeout: 30000, // 30 seconds timeout
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Unified error handler
const handleError = (error, endpoint) => {
  let errorDetails = {
    endpoint,
    status: error.response?.status || 'No response',
    message: error.message,
    config: {
      url: error.config?.url,
      method: error.config?.method
    }
  };

  console.error('API Error:', errorDetails);
  
  // Transform specific error types
  if (error.code === 'ECONNABORTED') {
    throw { ...errorDetails, message: 'Request timeout' };
  }
  if (!error.response) {
    throw { ...errorDetails, message: 'Network error - backend may be down' };
  }
  
  throw errorDetails;
};

export default {
  async getRoot() {
    try {
      const response = await api.get('/api');
      return response.data;
    } catch (error) {
      return handleError(error, '/api');
    }
  },

  async checkHealth() {
    try {
      const response = await api.get('/api/health');
      return response.data;
    } catch (error) {
      return handleError(error, '/api/health');
    }
  },

  async greetUser(name) {
    try {
      const response = await api.get(`/api/greet/${encodeURIComponent(name)}`);
      return response.data;
    } catch (error) {
      return handleError(error, `/api/greet/${name}`);
    }
  }
};