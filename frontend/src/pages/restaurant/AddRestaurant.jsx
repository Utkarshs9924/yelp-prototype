import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { restaurantAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CUISINE_OPTIONS = [
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

const AMBIANCE_OPTIONS = [
  'Casual',
  'Upscale',
  'Romantic',
  'Family-friendly',
  'Trendy',
  'Cozy',
  'Lively',
  'Quiet',
];

const PRICING_OPTIONS = [
  { value: '1', label: '$' },
  { value: '2', label: '$$' },
  { value: '3', label: '$$$' },
  { value: '4', label: '$$$$' },
];

const initialForm = {
  name: '',
  cuisine_type: '',
  description: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  phone: '',
  email: '',
  website: '',
  hours_of_operation: '',
  pricing_tier: '',
  amenities: '',
  ambiance: '',
};

export default function AddRestaurant() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      toast.error('Restaurant name is required');
      return;
    }

    setLoading(true);
    try {
      const payload = { ...form };
      Object.keys(payload).forEach((k) => {
        if (payload[k] === '') payload[k] = undefined;
      });
      if (payload.amenities) {
        payload.amenities = payload.amenities
          .split(/[,\n]/)
          .map((a) => a.trim())
          .filter(Boolean);
      }

      const { data } = await restaurantAPI.create(payload);
      toast.success('Restaurant created successfully!');
      navigate(`/restaurants/${data.id ?? data.restaurant?.id ?? data}`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create restaurant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="bg-red-600 text-white px-6 py-4">
            <h1 className="text-2xl font-bold">Add a Restaurant</h1>
            <p className="text-red-100 text-sm mt-1">Share your favourite spot with the community</p>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-8">
            {/* Basic Info */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Basic Information
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Restaurant Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="name"
                    type="text"
                    value={form.name}
                    onChange={(e) => update('name', e.target.value)}
                    required
                    placeholder="e.g. Joe's Pizza"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div>
                  <label htmlFor="cuisine_type" className="block text-sm font-medium text-gray-700 mb-1">
                    Cuisine Type
                  </label>
                  <select
                    id="cuisine_type"
                    value={form.cuisine_type}
                    onChange={(e) => update('cuisine_type', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 bg-white"
                  >
                    <option value="">Select cuisine</option>
                    {CUISINE_OPTIONS.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    value={form.description}
                    onChange={(e) => update('description', e.target.value)}
                    rows={4}
                    placeholder="Tell us about this restaurant..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div>
                  <label htmlFor="pricing_tier" className="block text-sm font-medium text-gray-700 mb-1">
                    Price Tier
                  </label>
                  <select
                    id="pricing_tier"
                    value={form.pricing_tier}
                    onChange={(e) => update('pricing_tier', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 bg-white"
                  >
                    <option value="">Select price range</option>
                    {PRICING_OPTIONS.map((p) => (
                      <option key={p.value} value={p.value}>
                        {p.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="ambiance" className="block text-sm font-medium text-gray-700 mb-1">
                    Ambiance
                  </label>
                  <select
                    id="ambiance"
                    value={form.ambiance}
                    onChange={(e) => update('ambiance', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 bg-white"
                  >
                    <option value="">Select ambiance</option>
                    {AMBIANCE_OPTIONS.map((a) => (
                      <option key={a} value={a}>
                        {a}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            {/* Location */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Location
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
                    Address
                  </label>
                  <input
                    id="address"
                    type="text"
                    value={form.address}
                    onChange={(e) => update('address', e.target.value)}
                    placeholder="123 Main St"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                      City
                    </label>
                    <input
                      id="city"
                      type="text"
                      value={form.city}
                      onChange={(e) => update('city', e.target.value)}
                      placeholder="San Francisco"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
                      State
                    </label>
                    <input
                      id="state"
                      type="text"
                      value={form.state}
                      onChange={(e) => update('state', e.target.value)}
                      placeholder="CA"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-1">
                      Zip Code
                    </label>
                    <input
                      id="zip_code"
                      type="text"
                      value={form.zip_code}
                      onChange={(e) => update('zip_code', e.target.value)}
                      placeholder="94102"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                    />
                  </div>
                </div>
              </div>
            </section>

            {/* Contact */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Contact
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    id="phone"
                    type="tel"
                    value={form.phone}
                    onChange={(e) => update('phone', e.target.value)}
                    placeholder="(555) 123-4567"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={form.email}
                    onChange={(e) => update('email', e.target.value)}
                    placeholder="contact@restaurant.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div>
                  <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-1">
                    Website
                  </label>
                  <input
                    id="website"
                    type="url"
                    value={form.website}
                    onChange={(e) => update('website', e.target.value)}
                    placeholder="https://www.restaurant.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
              </div>
            </section>

            {/* Hours & Amenities */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Hours & Amenities
              </h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="hours_of_operation" className="block text-sm font-medium text-gray-700 mb-1">
                    Hours of Operation
                  </label>
                  <textarea
                    id="hours_of_operation"
                    value={form.hours_of_operation}
                    onChange={(e) => update('hours_of_operation', e.target.value)}
                    rows={4}
                    placeholder="Mon-Fri: 11am-10pm&#10;Sat-Sun: 10am-11pm"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
                <div>
                  <label htmlFor="amenities" className="block text-sm font-medium text-gray-700 mb-1">
                    Amenities
                  </label>
                  <textarea
                    id="amenities"
                    value={form.amenities}
                    onChange={(e) => update('amenities', e.target.value)}
                    rows={3}
                    placeholder="Outdoor seating, Takeout, Delivery, Reservations (comma or newline separated)"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                </div>
              </div>
            </section>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 px-4 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Creating...' : 'Create Restaurant'}
              </button>
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
