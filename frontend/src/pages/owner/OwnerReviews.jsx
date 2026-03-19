import { useState, useEffect, useMemo } from 'react';
import { ownerAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import StarRating from '../../components/StarRating';
import { FaSpinner } from 'react-icons/fa';

export default function OwnerReviews() {
  const { token } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loadingRestaurants, setLoadingRestaurants] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [ratingFilter, setRatingFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    setLoadingRestaurants(true);
    ownerAPI
      .getRestaurants()
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data?.restaurants ?? [];
        if (!cancelled) {
          setRestaurants(list);
          if (list.length > 0 && !selectedId) setSelectedId(list[0].id);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoadingRestaurants(false);
      });
    return () => { cancelled = true; };
  }, [token]);

  useEffect(() => {
    if (!selectedId || !token) {
      setReviews([]);
      return;
    }
    let cancelled = false;
    setLoadingReviews(true);
    ownerAPI
      .getReviews(selectedId)
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data?.reviews ?? [];
        if (!cancelled) setReviews(list);
      })
      .catch(() => {
        if (!cancelled) setReviews([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingReviews(false);
      });
    return () => { cancelled = true; };
  }, [selectedId, token]);

  const filteredAndSorted = useMemo(() => {
    let list = [...reviews];
    if (ratingFilter !== 'all') {
      const star = Number(ratingFilter);
      list = list.filter((r) => Math.round(r.rating) === star);
    }
    list.sort((a, b) => {
      if (sortBy === 'date') {
        const da = new Date(a.created_at || 0).getTime();
        const db = new Date(b.created_at || 0).getTime();
        return db - da;
      }
      return (b.rating ?? 0) - (a.rating ?? 0);
    });
    return list;
  }, [reviews, ratingFilter, sortBy]);

  const selectedRestaurant = restaurants.find((r) => r.id === selectedId);

  if (loadingRestaurants) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <FaSpinner className="animate-spin text-5xl text-red-600" aria-label="Loading" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Reviews Dashboard</h1>

      {restaurants.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center text-gray-500">
          You have no restaurants. Add a restaurant to view reviews.
        </div>
      ) : (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select restaurant
            </label>
            <select
              value={selectedId ?? ''}
              onChange={(e) => setSelectedId(e.target.value ? Number(e.target.value) : null)}
              className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
            >
              <option value="">— Select —</option>
              {restaurants.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>

          {selectedId && (
            <>
              <div className="flex flex-wrap items-center gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">
                    Filter by rating
                  </label>
                  <select
                    value={ratingFilter}
                    onChange={(e) => setRatingFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-sm"
                  >
                    <option value="all">All ratings</option>
                    <option value="5">5 stars</option>
                    <option value="4">4 stars</option>
                    <option value="3">3 stars</option>
                    <option value="2">2 stars</option>
                    <option value="1">1 star</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Sort by</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none text-sm"
                  >
                    <option value="date">Date (newest first)</option>
                    <option value="rating">Rating (highest first)</option>
                  </select>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-4 border-b border-gray-100 bg-gray-50">
                  <h2 className="font-semibold text-gray-900">
                    {selectedRestaurant?.name ?? 'Restaurant'} — Reviews
                  </h2>
                </div>
                <div className="p-4">
                  {loadingReviews ? (
                    <div className="flex items-center justify-center py-12">
                      <FaSpinner className="animate-spin text-4xl text-red-600" />
                    </div>
                  ) : filteredAndSorted.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No reviews to display.</p>
                  ) : (
                    <div className="space-y-4">
                      {filteredAndSorted.map((rev) => (
                        <div
                          key={rev.id}
                          className="p-4 rounded-lg border border-gray-100 bg-gray-50/50"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <StarRating rating={rev.rating ?? 0} size="sm" />
                              <span className="font-medium text-gray-900">
                                {rev.user_name ?? 'Anonymous'}
                              </span>
                            </div>
                            <span className="text-sm text-gray-500">
                              {rev.created_at
                                ? new Date(rev.created_at).toLocaleDateString(undefined, {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric',
                                  })
                                : ''}
                            </span>
                          </div>
                          <p className="text-gray-700">{rev.comment || '—'}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
