import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export const authAPI = {
  signup: (data) => api.post('/signup', data),
  login: (data) => api.post('/login', data),
};

export const userAPI = {
  getProfile: (userId) => api.get(`/users/${userId}`),
  updateProfile: (userId, data) => api.put(`/users/${userId}`, data),
};

export const restaurantAPI = {
  list: () => api.get('/restaurants'),
  search: (params) => api.get('/restaurants/search', { params }),
  get: (id) => api.get(`/restaurants/${id}`),
  create: (data) => api.post('/restaurants', data),
};

export const reviewAPI = {
  getForRestaurant: (id) => api.get(`/restaurants/${id}/reviews`),
  create: (data) => api.post('/reviews', data),
  update: (id, data) => api.put(`/reviews/${id}`, data),
  delete: (id) => api.delete(`/reviews/${id}`),
};

export const favouriteAPI = {
  list: (userId) => api.get(`/favorites/${userId}`),
  add: (data) => api.post('/favorites', data),
  remove: (id) => api.delete(`/favorites/${id}`),
};

export const preferencesAPI = {
  get: (userId) => api.get(`/preferences/${userId}`),
  create: (data) => api.post('/preferences', data),
  update: (userId, data) => api.put(`/preferences/${userId}`, data),
};

export const chatAPI = {
  send: (data) => api.post('/chat', data),
};

export const historyAPI = {
  get: (userId) => api.get(`/history/${userId}`),
};

export const ownerAPI = {
  getStats: (ownerId) => api.get(`/owner/${ownerId}/stats`),
  getRestaurants: (ownerId) => api.get(`/owner/${ownerId}/restaurants`),
  getReviews: (ownerId) => api.get(`/owner/${ownerId}/reviews`),
};

export default api;
