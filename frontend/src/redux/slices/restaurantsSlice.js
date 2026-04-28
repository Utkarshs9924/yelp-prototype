/**
 * Restaurants Slice - Manages restaurant data
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchRestaurants = createAsyncThunk(
  'restaurants/fetchAll',
  async ({ page = 1, limit = 30 } = {}, { rejectWithValue }) => {
    try {
      const response = await api.get(`/restaurants?page=${page}&limit=${limit}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch restaurants');
    }
  }
);

export const fetchRestaurantDetails = createAsyncThunk(
  'restaurants/fetchDetails',
  async (restaurantId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/restaurants/${restaurantId}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch restaurant');
    }
  }
);

export const searchRestaurants = createAsyncThunk(
  'restaurants/search',
  async (
    { query, cuisine, city, zip_code, pricing_tier, amenities, page = 1, limit = 30 } = {},
    { rejectWithValue }
  ) => {
    try {
      const params = { page, limit };
      if (query) params.name = query;
      if (cuisine) params.cuisine = cuisine;
      if (city) params.city = city;
      if (zip_code) params.zip_code = zip_code;
      if (pricing_tier) params.pricing_tier = pricing_tier;
      if (amenities) params.amenities = amenities;

      const response = await api.get('/restaurants/search', { params });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Search failed');
    }
  }
);

const initialState = {
  list: [],
  currentRestaurant: null,
  total: 0,
  page: 1,
  limit: 30,
  totalPages: 1,
  loading: false,
  error: null,
  searching: false,
};

const restaurantsSlice = createSlice({
  name: 'restaurants',
  initialState,
  reducers: {
    clearCurrentRestaurant: (state) => {
      state.currentRestaurant = null;
    },
    clearSearchResults: (state) => {
      state.list = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all restaurants
      .addCase(fetchRestaurants.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRestaurants.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.restaurants || [];
        state.total = action.payload.total || 0;
        state.page = action.payload.page || 1;
        state.totalPages = action.payload.total_pages || 1;
      })
      .addCase(fetchRestaurants.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch restaurant details
      .addCase(fetchRestaurantDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRestaurantDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.currentRestaurant = action.payload;
      })
      .addCase(fetchRestaurantDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Search restaurants
      .addCase(searchRestaurants.pending, (state) => {
        state.searching = true;
        state.error = null;
      })
      .addCase(searchRestaurants.fulfilled, (state, action) => {
        state.searching = false;
        state.list = action.payload.restaurants || [];
        state.total = action.payload.total || 0;
        state.page = action.payload.page || 1;
        state.totalPages = action.payload.total_pages || 1;
      })
      .addCase(searchRestaurants.rejected, (state, action) => {
        state.searching = false;
        state.error = action.payload;
      });
  },
});

export const { clearCurrentRestaurant, clearSearchResults } = restaurantsSlice.actions;
export default restaurantsSlice.reducer;