import { useState, useEffect } from 'react';
import { favouriteAPI } from '../../services/api';
import RestaurantCard from '../../components/RestaurantCard';
import toast from 'react-hot-toast';
import { FaHeart } from 'react-icons/fa';

export default function Favourites() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    favouriteAPI
      .list()
      .then(({ data }) => setItems(data?.favourites ?? data ?? []))
      .catch(() => toast.error('Failed to load favourites'))
      .finally(() => setLoading(false));
  };

  useEffect(() => load(), []);

  const handleRemove = async (id) => {
    try {
      await favouriteAPI.remove(id);
      setItems((prev) => prev.filter((f) => (f.restaurant?.id ?? f.id) !== id));
      toast.success('Removed from favourites');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to remove');
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="animate-pulse grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-gray-200 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <FaHeart className="text-red-600" />
        Favourites
      </h1>
      {items.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center text-gray-500">
          <FaHeart className="mx-auto text-4xl text-gray-300 mb-4" />
          <p>No favourites yet. Explore restaurants and add some!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((fav) => (
            <RestaurantCard
              key={fav.restaurant?.id ?? fav.id ?? fav}
              restaurant={fav}
              showRemove
              onRemove={handleRemove}
            />
          ))}
        </div>
      )}
    </div>
  );
}
