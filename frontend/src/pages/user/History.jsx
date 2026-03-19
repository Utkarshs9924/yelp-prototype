import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { historyAPI } from '../../services/api';
import StarRating from '../../components/StarRating';
import toast from 'react-hot-toast';
import { FaStar, FaUtensils, FaHistory } from 'react-icons/fa';

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function History() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    historyAPI
      .get()
      .then(({ data }) => setItems(data?.history ?? data ?? []))
      .catch(() => toast.error('Failed to load history'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <FaHistory className="text-red-600" />
        History
      </h1>
      {items.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center text-gray-500">
          <FaHistory className="mx-auto text-4xl text-gray-300 mb-4" />
          <p>No history yet.</p>
        </div>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div className="space-y-0">
            {items.map((item, i) => {
              const type = item.type || item.action_type || 'review';
              const isReview = type === 'review' || type === 'Review';
              const restaurantId = item.restaurant_id ?? item.restaurant?.id;
              const restaurantName = item.restaurant?.name ?? item.restaurant_name ?? 'Unknown';
              const rating = item.rating ?? item.stars;
              const date = item.created_at ?? item.date ?? item.timestamp;

              return (
                <div key={item.id ?? i} className="relative flex gap-4 pb-6 pl-2">
                  <div className="absolute left-3 w-5 h-5 rounded-full bg-red-600 flex items-center justify-center shrink-0 z-10">
                    {isReview ? (
                      <FaStar className="text-white text-xs" />
                    ) : (
                      <FaUtensils className="text-white text-xs" />
                    )}
                  </div>
                  <div className="ml-6 flex-1 bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <Link
                        to={`/restaurants/${restaurantId}`}
                        className="font-semibold text-gray-900 hover:text-red-600 transition"
                      >
                        {restaurantName}
                      </Link>
                      <span className="text-sm text-gray-500">{formatDate(date)}</span>
                    </div>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500 uppercase">
                        {isReview ? 'Review' : 'Restaurant added'}
                      </span>
                      {isReview && rating != null && (
                        <StarRating rating={rating} size="sm" />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
