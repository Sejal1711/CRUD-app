import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({ baseURL: BASE_URL });

// Attach JWT to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const register = (data) => client.post('/auth/register', data);
export const login    = (data) => client.post('/auth/login', data);
export const getMe    = ()     => client.get('/auth/me');

// Tasks
export const getTasks   = (params) => client.get('/tasks', { params });
export const getTask    = (id)     => client.get(`/tasks/${id}`);
export const createTask = (data)   => client.post('/tasks', data);
export const updateTask = (id, data) => client.patch(`/tasks/${id}`, data);
export const deleteTask = (id)     => client.delete(`/tasks/${id}`);
export const getStats   = ()       => client.get('/tasks/stats');

// Users (admin)
export const getUsers    = (params)      => client.get('/users', { params });
export const updateRole  = (id, data)    => client.patch(`/users/${id}/role`, data);
export const deleteUser  = (id)          => client.delete(`/users/${id}`);
export const updateProfile = (id, data)  => client.patch(`/users/${id}`, data);
