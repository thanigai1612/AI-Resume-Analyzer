import axios from 'axios';

const api = axios.create({
  baseURL: 'baseURL: 'https://ai-resume-analyzer-lc35.onrender.com/api',',
    headers: {
  'Content-Type': 'application/json',
},
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
