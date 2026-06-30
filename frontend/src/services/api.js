import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Dashboard API
export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/summary'),
  getActivity: () => api.get('/dashboard/activity'),
  getErrors: () => api.get('/dashboard/errors'),
};

// Position API
export const positionAPI = {
  getAll: (params) => api.get('/positions', { params }),
  getById: (id) => api.get(`/positions/${id}`),
  create: (data) => api.post('/positions', data),
  update: (id, data) => api.put(`/positions/${id}`, data),
  delete: (id) => api.delete(`/positions/${id}`),
  pause: (id) => api.post(`/positions/${id}/pause`),
  resume: (id) => api.post(`/positions/${id}/resume`),
  close: (id) => api.post(`/positions/${id}/close`),
};

// Candidate API
export const candidateAPI = {
  getAll: (params) => api.get('/candidates', { params }),
  getById: (id) => api.get(`/candidates/${id}`),
  getByPosition: (positionId, params) => api.get(`/positions/${positionId}/candidates`, { params }),
  update: (id, data) => api.put(`/candidates/${id}`, data),
};

// Pipeline API
export const pipelineAPI = {
  getByPosition: (positionId, params) => api.get(`/positions/${positionId}/pipeline`, { params }),
  update: (id, data) => api.put(`/pipelines/${id}`, data),
  contact: (id) => api.post(`/pipelines/${id}/contact`),
  updateNotes: (id, data) => api.put(`/pipelines/${id}/notes`, data),
};

// Scheduler API
export const schedulerAPI = {
  getJobs: () => api.get('/scheduler/jobs'),
  runNow: (positionId) => api.post(`/scheduler/run/${positionId}`),
  pause: (positionId) => api.post(`/scheduler/pause/${positionId}`),
  resume: (positionId) => api.post(`/scheduler/resume/${positionId}`),
};

// Outreach API
export const outreachAPI = {
  getLogs: (params) => api.get('/outreach/logs', { params }),
  getById: (id) => api.get(`/outreach/${id}`),
};

// System API
export const systemAPI = {
  getConfig: () => api.get('/system/config'),
  updateConfig: (data) => api.put('/system/config', data),
};

export default api;