import { useState, useEffect, useCallback } from 'react';
import { FaSearch, FaFilter } from 'react-icons/fa';
import { restaurantAPI, chatAPI } from '../../services/api';
import RestaurantCard from '../../components/RestaurantCard';
import toast from 'react-hot-toast';

const CUISINE_OPTIONS = [
  'All Cuisines',
  'American',
  'Italian',
  'Mexican',
  'Chinese',
  'Japanese',
  'Indian',
  'Thai',
  'French',
  'Mediterranean',
  'Korean',
  'Vietnamese',
  'Greek',
  'Spanish',
  'Other',
];

const PRICE_OPTIONS = [
  { value: '', label: 'Any Price' },
  { value: '1', label: '$' },
  { value: '2', label: '$$' },
  { value: '3', label: '$$$' },
  { value: '4', label: '$$$$' },
];

export default function Explore() {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [cuisine, setCuisine] = useState('All Cuisines');
  const [priceRange, setPriceRange] = useState('');
  const [cityZip, setCityZip] = useState('');
  const [searchMode, setSearchMode] = useState('standard');
  const [aiSearch, setAiSearch] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const fetchRestaurants = useCallback(async (pageNum = 1) => {
    setLoading(true);
    try {
      const params = { page: pageNum, limit: 30 };

      if (search.trim()) params.name = search.trim();
      if (cuisine && cuisine !== 'All Cuisines') params.cuisine = cuisine;
      if (priceRange) params.pricing_tier = priceRange;

      if (cityZip.trim()) {
        const val = cityZip.trim();
        if (/^\d+$/.test(val)) params.zip_code = val;
        else params.city = val;
      }

      const { data } = await restaurantAPI.search(params);

      setRestaurants(data?.restaurants || []);
      setTotal(data?.total || 0);
      setTotalPages(data?.total_pages || 1);
      setPage(pageNum);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load restaurants');
      setRestaurants([]);
      setTotal(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  }, [search, cuisine, priceRange, cityZip]);

  useEffect(() => {
    fetchRestaurants(1);
  }, [cuisine, priceRange, cityZip]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants(1);
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchRestaurants(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">

      {/* HERO */}
      <div className="bg-gradient-to-b from-red-600 to-red-700 text-white relative pb-20">
        <div className="max-w-6xl mx-auto px-4 pt-12 sm:pt-16">

          <h1 className="text-3xl sm:text-4xl font-bold text-center mb-2">
            Find the Best Restaurants
          </h1>

          <p className="text-red-100 text-center mb-8 max-w-xl mx-auto">
            Search by name, cuisine, keywords, city or zip code
          </p>

          {/* Toggle */}
          <div className="flex justify-center gap-4 mb-6">
            <button
              onClick={() => { setSearchMode('standard'); fetchRestaurants(1); }}
              className={`px-5 py-2 rounded-full font-semibold ${
                searchMode === 'standard'
                  ? 'bg-white text-red-600'
                  : 'bg-red-700/50 text-white'
              }`}
            >
              Standard Search
            </button>

            <button
              onClick={() => setSearchMode('ai')}
              className={`px-5 py-2 rounded-full font-semibold ${
                searchMode === 'ai'
                  ? 'bg-white text-red-600'
                  : 'bg-red-700/50 text-white'
              }`}
            >
              ✨ Ask AI Assistant
            </button>
          </div>
        </div>

        {/* SEARCH BAR */}
        <form onSubmit={handleSearchSubmit} className="absolute left-1/2 -translate-x-1/2 bottom-0 w-full px-4">
          <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-2xl p-4 flex gap-3">

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Restaurant name..."
              className="flex-1 px-4 py-3 border rounded-lg"
            />

            <input
              value={cityZip}
              onChange={(e) => setCityZip(e.target.value)}
              placeholder="City or zip"
              className="flex-1 px-4 py-3 border rounded-lg"
            />

            <button className="px-6 py-3 bg-red-600 text-white rounded-lg">
              Search
            </button>

          </div>
        </form>
      </div>

      {/* RESULTS */}
      <div className="max-w-6xl mx-auto px-4 pt-20">

        <div className="text-sm text-gray-500 mb-4">
          Found {total} restaurants
        </div>

        {loading ? (
          <div className="text-center py-10">Loading...</div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
              {restaurants.map(r => (
                <RestaurantCard key={r.id} restaurant={r} />
              ))}
            </div>

            {/* PAGINATION */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2">
                <button onClick={() => handlePageChange(page - 1)}>Prev</button>

                {[...Array(totalPages)].map((_, i) => {
                  const p = i + 1;
                  return (
                    <button
                      key={p}
                      onClick={() => handlePageChange(p)}
                      className={page === p ? 'font-bold' : ''}
                    >
                      {p}
                    </button>
                  );
                })}

                <button onClick={() => handlePageChange(page + 1)}>Next</button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}