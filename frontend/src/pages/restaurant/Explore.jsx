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
  const [search, setSearch] = useState('');
  const [cuisine, setCuisine] = useState('All Cuisines');
  const [priceRange, setPriceRange] = useState('');
  const [cityZip, setCityZip] = useState('');
  const [searchMode, setSearchMode] = useState('standard');
  const [aiSearch, setAiSearch] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const fetchRestaurants = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search.trim()) {
        params.name = search.trim();
      }
      if (cuisine && cuisine !== 'All Cuisines') params.cuisine = cuisine;
      if (priceRange) params.pricing_tier = priceRange;
      if (cityZip.trim()) {
        const val = cityZip.trim();
        if (/^\d+$/.test(val)) params.zip_code = val;
        else params.city = val;
      }

      const { data } = await restaurantAPI.search(params);
      setRestaurants(Array.isArray(data) ? data : data?.restaurants ?? data?.results ?? []);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load restaurants');
      setRestaurants([]);
    } finally {
      setLoading(false);
    }
  }, [search, cuisine, priceRange, cityZip]);

  useEffect(() => {
    fetchRestaurants();
  }, [fetchRestaurants]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants();
  };

  const handleAiSearchSubmit = async (e) => {
    e.preventDefault();
    if (!aiSearch.trim()) return;
    
    setAiLoading(true);
    setAiResponse('');
    try {
      const { data } = await chatAPI.send({
        message: aiSearch,
        conversation_history: []
      });
      setAiResponse(data.response);
      setRestaurants(data.restaurants || []);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to get AI response');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-red-600 to-red-700 text-white">
        <div className="max-w-6xl mx-auto px-4 py-12 sm:py-16">
          <h1 className="text-3xl sm:text-4xl font-bold text-center mb-2">
            Find the best restaurants
          </h1>
          <p className="text-red-100 text-center mb-8 max-w-xl mx-auto">
            Search by name, cuisine, keywords, city or zip code
          </p>

          <div className="flex justify-center gap-4 mb-6">
            <button 
              type="button"
              onClick={() => { setSearchMode('standard'); fetchRestaurants(); }} 
              className={`px-5 py-2 rounded-full font-semibold transition-all ${searchMode === 'standard' ? 'bg-white text-red-600 shadow-md' : 'bg-red-700/50 text-white hover:bg-red-600'}`}
            >
              Standard Search
            </button>
            <button 
              type="button"
              onClick={() => setSearchMode('ai')} 
              className={`px-5 py-2 rounded-full font-semibold transition-all ${searchMode === 'ai' ? 'bg-white text-red-600 shadow-md' : 'bg-red-700/50 text-white hover:bg-red-600'}`}
            >
              ✨ Ask AI Assistant
            </button>
          </div>

          {searchMode === 'standard' ? (
            <form onSubmit={handleSearchSubmit} className="max-w-2xl mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="flex-1 relative">
                  <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Restaurant name, cuisine, keywords..."
                    className="w-full pl-11 pr-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50"
                  />
                </div>
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={cityZip}
                    onChange={(e) => setCityZip(e.target.value)}
                    placeholder="City or zip code"
                    className="w-full px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white/50"
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-3 bg-white text-red-600 font-semibold rounded-lg hover:bg-red-50 transition-colors shadow-md"
                >
                  Search
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleAiSearchSubmit} className="max-w-2xl mx-auto relative animate-fade-in">
              <input
                type="text"
                value={aiSearch}
                onChange={(e) => setAiSearch(e.target.value)}
                placeholder="Ex: 'I'm vegan and want something casual' or 'Romantic italian spot'"
                className="w-full px-6 py-4 rounded-xl text-gray-900 placeholder-gray-500 text-lg shadow-xl focus:outline-none focus:ring-4 focus:ring-red-300"
                disabled={aiLoading}
              />
              <button
                type="submit"
                disabled={aiLoading || !aiSearch.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-red-600 to-red-500 text-white rounded-lg hover:from-red-700 hover:to-red-600 disabled:opacity-70 transition-all font-medium shadow-md flex items-center gap-2"
              >
                {aiLoading ? 'Thinking...' : 'Ask AI'}
              </button>
            </form>
          )}
        </div>
      </div>
      


      {/* Filters & Content */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Filter Bar */}
        {searchMode === 'standard' && (
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-red-300 hover:bg-red-50 transition-colors sm:hidden"
            >
              <FaFilter size={16} />
              Filters
            </button>

            <div
              className={`flex flex-col sm:flex-row gap-4 ${showFilters ? 'flex' : 'hidden sm:flex'}`}
            >
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-wrap">
                <div>
                  <label className="sr-only">Cuisine</label>
                  <select
                    value={cuisine}
                    onChange={(e) => setCuisine(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  >
                    {CUISINE_OPTIONS.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Price:</span>
                  <div className="flex gap-1">
                    {PRICE_OPTIONS.filter((p) => p.value).map((p) => (
                      <button
                        key={p.value}
                        type="button"
                        onClick={() => setPriceRange(priceRange === p.value ? '' : p.value)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                          priceRange === p.value
                            ? 'bg-red-600 text-white'
                            : 'bg-white border border-gray-300 text-gray-700 hover:border-red-300 hover:bg-red-50'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI Response Alert */}
        {searchMode === 'ai' && aiResponse && (
          <div className="mb-6 animate-fade-in">
            <div className="bg-blue-50 border border-blue-200 p-5 rounded-xl shadow-sm">
              <div className="flex items-start gap-4">
                <span className="text-2xl mt-0.5">✨</span>
                <p className="text-blue-900 whitespace-pre-wrap leading-relaxed text-lg font-medium">{aiResponse}</p>
              </div>
            </div>
          </div>
        )}

        {/* Restaurant Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="bg-white rounded-lg shadow overflow-hidden animate-pulse"
              >
                <div className="aspect-[4/3] bg-gray-200" />
                <div className="p-4 space-y-3">
                  <div className="h-5 bg-gray-200 rounded w-3/4" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                  <div className="h-4 bg-gray-200 rounded w-1/3" />
                </div>
              </div>
            ))}
          </div>
        ) : restaurants.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-gray-100">
            <p className="text-gray-500 text-lg">No restaurants found</p>
            <p className="text-gray-400 text-sm mt-1">
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
