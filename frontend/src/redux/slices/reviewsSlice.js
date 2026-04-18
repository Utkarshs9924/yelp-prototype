/**
 * Reviews Slice - Manages review data
 */
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunks
export const fetchReviews = createAsyncThunk(
  'reviews/fetchAll',
  async (restaurantId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/restaurants/${restaurantId}/reviews`);
      return response.data.reviews;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch reviews');
    }
  }
);

export const createReview = createAsyncThunk(
  'reviews/create',
  async ({ restaurantId, userId, rating, comment }, { rejectWithValue }) => {
    try {
      const response = await api.post('/reviews', {
        restaurant_id: restaurantId,
        user_id: userId,
        rating,
        comment,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create review');
    }
  }
);

export const updateReview = createAsyncThunk(
  'reviews/update',
  async ({ reviewId, restaurantId, userId, rating, comment }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/reviews/${reviewId}`, {
        restaurant_id: restaurantId,
        user_id: userId,
        rating,
        comment,
      });
      return { reviewId, rating, comment };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update review');
    }
  }
);

export const deleteReview = createAsyncThunk(
  'reviews/delete',
  async ({ reviewId, restaurantId }, { rejectWithValue }) => {
    try {
      await api.delete(`/reviews/${reviewId}?restaurant_id=${restaurantId}`);
      return reviewId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete review');
    }
  }
);

const initialState = {
  list: [],
  loading: false,
  error: null,
  submitting: false,
};

const reviewsSlice = createSlice({
  name: 'reviews',
  initialState,
  reducers: {
    clearReviews: (state) => {
      state.list = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch reviews
      .addCase(fetchReviews.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchReviews.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchReviews.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create review
      .addCase(createReview.pending, (state) => {
        state.submitting = true;
        state.error = null;
      })
      .addCase(createReview.fulfilled, (state) => {
        state.submitting = false;
      })
      .addCase(createReview.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      })
      // Update review
      .addCase(updateReview.pending, (state) => {
        state.submitting = true;
        state.error = null;
      })
      .addCase(updateReview.fulfilled, (state, action) => {
        state.submitting = false;
        const index = state.list.findIndex(r => r.id === action.payload.reviewId);
        if (index !== -1) {
          state.list[index].rating = action.payload.rating;
          state.list[index].comment = action.payload.comment;
        }
      })
      .addCase(updateReview.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      })
      // Delete review
      .addCase(deleteReview.pending, (state) => {
        state.submitting = true;
        state.error = null;
      })
      .addCase(deleteReview.fulfilled, (state, action) => {
        state.submitting = false;
        state.list = state.list.filter(r => r.id !== action.payload);
      })
      .addCase(deleteReview.rejected, (state, action) => {
        state.submitting = false;
        state.error = action.payload;
      });
  },
});

export const { clearReviews } = reviewsSlice.actions;
export default reviewsSlice.reducer;
