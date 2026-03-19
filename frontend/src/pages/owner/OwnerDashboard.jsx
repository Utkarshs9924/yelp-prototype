import { useState, useEffect } from 'react';
import { FaStore, FaComments, FaStar } from 'react-icons/fa';
import { ownerAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import StarRating from '../../components/StarRating';
import toast from 'react-hot-toast';

export default function OwnerDashboard() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const { data } = await ownerAPI.getDashboard();
        setDashboard(data);
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">No dashboard data available.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Owner Dashboard</h1>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
              <FaStore className="text-red-600" size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Restaurants</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.total_restaurants}</p>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <FaComments className="text-blue-600" size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Reviews</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.total_reviews}</p>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center">
              <FaStar className="text-yellow-500" size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Overall Avg Rating</p>
              <p className="text-2xl font-bold text-gray-900">{dashboard.overall_average_rating}</p>
            </div>
          </div>
        </div>

        {/* Restaurant Stats */}
        <div className="space-y-6">
          {dashboard.restaurants?.map((r) => (
            <div key={r.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
                <h2 className="text-lg font-semibold text-gray-900">{r.name}</h2>
                <div className="flex items-center gap-3">
                  <StarRating rating={r.average_rating} size="sm" />
                  <span className="text-sm text-gray-500">
                    {r.average_rating.toFixed(1)} ({r.review_count} reviews)
                  </span>
                </div>
              </div>

              {/* Rating Distribution */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Rating Distribution</h3>
                <div className="space-y-1">
                  {[5, 4, 3, 2, 1].map((star) => {
                    const count = r.rating_distribution?.[star] || 0;
                    const total = r.review_count || 1;
                    const pct = Math.round((count / total) * 100);
                    return (
                      <div key={star} className="flex items-center gap-2 text-sm">
                        <span className="w-8 text-right text-gray-600">{star}★</span>
                        <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-red-500 rounded-full transition-all"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="w-10 text-right text-gray-500">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Recent Reviews */}
              {r.recent_reviews?.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Reviews</h3>
                  <div className="space-y-2">
                    {r.recent_reviews.map((rev) => (
                      <div key={rev.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm text-gray-900">{rev.user_name}</span>
                          <StarRating rating={rev.rating} size="sm" />
                        </div>
                        {rev.comment && (
                          <p className="text-sm text-gray-600">{rev.comment}</p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          {rev.created_at ? new Date(rev.created_at).toLocaleDateString() : ''}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {(!dashboard.restaurants || dashboard.restaurants.length === 0) && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
              <p className="text-gray-500">No restaurants found. Claim or add a restaurant to get started.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
