import { useState, useEffect } from 'react';
import { preferencesAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CUISINES = ['Italian', 'Chinese', 'Mexican', 'Indian', 'Japanese', 'American', 'Thai', 'Korean', 'French', 'Mediterranean'];
const PRICE_RANGES = ['$', '$$', '$$$', '$$$$'];
const DIETARY = ['Vegetarian', 'Vegan', 'Halal', 'Gluten-Free', 'Kosher', 'Dairy-Free', 'Nut-Free'];
const AMBIANCE = ['Casual', 'Fine Dining', 'Family-Friendly', 'Romantic', 'Outdoor', 'Pet-Friendly', 'Bar/Lounge'];
const SORT_OPTIONS = ['Rating', 'Distance', 'Popularity', 'Price'];

function parseList(val) {
  if (Array.isArray(val)) return val;
  if (typeof val === 'string') {
    try {
      const parsed = JSON.parse(val);
      return Array.isArray(parsed) ? parsed : val.split(',').map((s) => s.trim()).filter(Boolean);
    } catch {
      return val.split(',').map((s) => s.trim()).filter(Boolean);
    }
  }
  return [];
}

function toList(arr) {
  return Array.isArray(arr) ? arr : [];
}

export default function Preferences() {
  const [form, setForm] = useState({
    cuisine_preferences: [],
    price_range: '',
    preferred_locations: '',
    search_radius: 10,
    dietary_needs: [],
    ambiance_preferences: [],
    sort_preference: 'Rating',
  });
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    preferencesAPI
      .get()
      .then(({ data }) => {
        setForm({
          cuisine_preferences: parseList(data.cuisine_preferences),
          price_range: data.price_range || '',
          preferred_locations: Array.isArray(data.preferred_locations)
            ? data.preferred_locations.join(', ')
            : typeof data.preferred_locations === 'string'
              ? data.preferred_locations
              : '',
          search_radius: data.search_radius ?? 10,
          dietary_needs: parseList(data.dietary_needs),
          ambiance_preferences: parseList(data.ambiance_preferences),
          sort_preference: data.sort_preference || 'Rating',
        });
      })
      .catch(() => toast.error('Failed to load preferences'))
      .finally(() => setFetching(false));
  }, []);

  const toggleArray = (field, value) => {
    setForm((prev) => {
      const arr = toList(prev[field]);
      const next = arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value];
      return { ...prev, [field]: next };
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    const num = e.target.type === 'number' ? Number(value) : value;
    setForm((prev) => ({ ...prev, [name]: num }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        preferred_locations: form.preferred_locations
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      };
      await preferencesAPI.update(payload);
      toast.success('Preferences saved');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="animate-pulse bg-gray-200 h-8 w-48 rounded mb-6" />
        <div className="animate-pulse bg-gray-200 h-64 rounded" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">AI Assistant Preferences</h1>
      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine preferences</label>
          <div className="flex flex-wrap gap-2">
            {CUISINES.map((c) => (
              <label key={c} className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.cuisine_preferences.includes(c)}
                  onChange={() => toggleArray('cuisine_preferences', c)}
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                />
                <span className="text-sm">{c}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Price range</label>
          <div className="flex flex-wrap gap-4">
            {PRICE_RANGES.map((p) => (
              <label key={p} className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="price_range"
                  value={p}
                  checked={form.price_range === p}
                  onChange={handleChange}
                  className="border-gray-300 text-red-600 focus:ring-red-500"
                />
                <span className="text-sm">{p}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="preferred_locations" className="block text-sm font-medium text-gray-700 mb-1">
            Preferred locations
          </label>
          <input
            id="preferred_locations"
            name="preferred_locations"
            type="text"
            value={form.preferred_locations}
            onChange={handleChange}
            placeholder="City1, City2, Neighborhood..."
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
          />
        </div>

        <div>
          <label htmlFor="search_radius" className="block text-sm font-medium text-gray-700 mb-1">
            Search radius (miles)
          </label>
          <input
            id="search_radius"
            name="search_radius"
            type="number"
            min={1}
            max={100}
            value={form.search_radius}
            onChange={handleChange}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Dietary needs</label>
          <div className="flex flex-wrap gap-2">
            {DIETARY.map((d) => (
              <label key={d} className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.dietary_needs.includes(d)}
                  onChange={() => toggleArray('dietary_needs', d)}
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                />
                <span className="text-sm">{d}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ambiance preferences</label>
          <div className="flex flex-wrap gap-2">
            {AMBIANCE.map((a) => (
              <label key={a} className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.ambiance_preferences.includes(a)}
                  onChange={() => toggleArray('ambiance_preferences', a)}
                  className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                />
                <span className="text-sm">{a}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="sort_preference" className="block text-sm font-medium text-gray-700 mb-1">
            Sort preference
          </label>
          <select
            id="sort_preference"
            name="sort_preference"
            value={form.sort_preference}
            onChange={handleChange}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none bg-white"
          >
            {SORT_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition disabled:opacity-60"
        >
          {loading ? 'Saving...' : 'Save preferences'}
        </button>
      </form>
    </div>
  );
}
