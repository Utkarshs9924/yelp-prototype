/**
 * Favorites Slice - Manages user favorites
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchFavorites = createAsyncThunk(
  'favorites/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/favorites');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch favorites');
    }
  }
);

export const addFavorite = createAsyncThunk(
  'favorites/add',
  async (restaurantId, { rejectWithValue }) => {
    try {
      const response = await api.post('/favorites', { restaurant_id: restaurantId });
      return { restaurantId, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to add favorite');
    }
  }
);

export const removeFavorite = createAsyncThunk(
  'favorites/remove',
  async (restaurantId, { rejectWithValue }) => {
    try {
      await api.delete(`/favorites/${restaurantId}`);
      return restaurantId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to remove favorite');
    }
  }
);

export const checkFavorite = createAsyncThunk(
  'favorites/check',
  async (restaurantId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/favorites/check/${restaurantId}`);
      return { restaurantId, isFavorite: response.data.is_favorite };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to check favorite');
    }
  }
);

const initialState = {
  list: [],
  favoriteIds: [],
  loading: false,
  error: null,
};

const favoritesSlice = createSlice({
  name: 'favorites',
  initialState,
  reducers: {
    clearFavorites: (state) => {
      state.list = [];
      state.favoriteIds = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch favorites
      .addCase(fetchFavorites.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFavorites.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
        state.favoriteIds = action.payload.map(fav => fav.restaurant_id);
      })
      .addCase(fetchFavorites.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Add favorite
      .addCase(addFavorite.fulfilled, (state, action) => {
        state.favoriteIds.push(action.payload.restaurantId);
      })
      // Remove favorite
      .addCase(removeFavorite.fulfilled, (state, action) => {
        state.favoriteIds = state.favoriteIds.filter(id => id !== action.payload);
        state.list = state.list.filter(fav => fav.restaurant_id !== action.payload);
      })
      // Check favorite
      .addCase(checkFavorite.fulfilled, (state, action) => {
        if (action.payload.isFavorite && !state.favoriteIds.includes(action.payload.restaurantId)) {
          state.favoriteIds.push(action.payload.restaurantId);
        } else if (!action.payload.isFavorite) {
          state.favoriteIds = state.favoriteIds.filter(id => id !== action.payload.restaurantId);
        }
      });
  },
});

export const { clearFavorites } = favoritesSlice.actions;
export default favoritesSlice.reducer;
