import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const uploadLogs = async (formData) => {
  const res = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const investigateThreat = async (payload) => {
  const res = await api.post('/api/investigate', payload);
  return res.data;
};

export const getIncidents = async (params = {}) => {
  const res = await api.get('/api/incidents', { params });
  return res.data;
};

export const getIncidentById = async (incidentId) => {
  const res = await api.get(`/api/incidents/${incidentId}`);
  return res.data;
};

export const submitFeedback = async (incidentId, feedback) => {
  const res = await api.post(`/api/incidents/${incidentId}/feedback`, feedback);
  return res.data;
};

export const searchMemory = async (query, limit = 10) => {
  const res = await api.get('/api/memory/search', { params: { query, limit } });
  return res.data;
};

export const reflectMemory = async (query, context = '') => {
  const res = await api.post('/api/memory/reflect', { query, context });
  return res.data;
};

export const listRecentMemories = async (limit = 20) => {
  const res = await api.get('/api/memory/list', { params: { limit } });
  return res.data;
};

export const getMemoryHealth = async () => {
  const res = await api.get('/api/memory/health');
  return res.data;
};

export const getAnalytics = async () => {
  const res = await api.get('/api/analytics');
  return res.data;
};

export default api;
