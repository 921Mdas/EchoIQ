import axios from 'axios';

// Set base URL based on environment
const baseURL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : 'https://echoiq.onrender.com';

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

export default {
  getRoot() {
    return api.get('/api');
  },
  checkHealth() {
    return api.get('/api/health');
  },
  greetUser(name) {
    return api.get(`/api/greet/${name}`);
  }
};