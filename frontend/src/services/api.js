import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
  getMenu: (id) => api.get(`/restaurants/${id}/menu`),
};

export const reviewAPI = {
  getForRestaurant: (id) => api.get(`/restaurants/${id}/reviews`),
  create: (data) => api.post('/reviews', data),
  update: (id, data) => api.put(`/reviews/${id}`, data),
  delete: (id) => api.delete(`/reviews/${id}`),
};

export const favouriteAPI = {
  list: () => api.get('/favorites'),
  add: (restaurantId) => api.post('/favorites', { restaurant_id: restaurantId }),
  remove: (restaurantId) => api.delete(`/favorites/${restaurantId}`),
  check: (restaurantId) => api.get(`/favorites/check/${restaurantId}`),
};

export const preferencesAPI = {
  get: () => api.get(`/preferences`),
  create: (data) => api.post('/preferences', data),
  update: (data) => api.put(`/preferences`, data),
};

export const chatAPI = {
  send: (data) => api.post('/chat', data),
};

export const historyAPI = {
  get: () => api.get('/history'),
};

export const ownerAPI = {
  getDashboard: () => api.get('/owner/dashboard'),
  getStats: (ownerId) => api.get(`/owner/${ownerId}/stats`),
  getRestaurants: () => api.get(`/owner/restaurants`),
  getReviews: (restaurantId) => api.get(`/owner/restaurants/${restaurantId}/reviews`),
  createRestaurant: (data) => api.post('/owner/restaurants', data)
};

export const adminAPI = {
  getPendingOwners: () => api.get('/admin/owners/pending'),
  approveOwner: (id) => api.put(`/admin/owners/${id}/approve`),
  getPendingRestaurants: () => api.get('/admin/restaurants/pending'),
  updateRestaurantStatus: (id, status) => api.put(`/admin/restaurants/${id}/status`, { status }),
  assignOwner: (id, ownerId) => api.put(`/admin/restaurants/${id}/assign`, { owner_id: ownerId }),
  deassignOwner: (id) => api.put(`/admin/restaurants/${id}/deassign`)
};

export default api;
