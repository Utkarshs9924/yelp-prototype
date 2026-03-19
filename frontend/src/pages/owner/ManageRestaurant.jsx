import { useState, useEffect } from 'react';
import { ownerAPI, restaurantAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';
import { FaSpinner, FaEdit, FaSave, FaTimes, FaCamera } from 'react-icons/fa';
import StarRating from '../../components/StarRating';

const EDIT_FIELDS = [
  { key: 'name', label: 'Name', type: 'text' },
  { key: 'cuisine_type', label: 'Cuisine Type', type: 'text' },
  { key: 'description', label: 'Description', type: 'textarea' },
  { key: 'address', label: 'Address', type: 'text' },
  { key: 'city', label: 'City', type: 'text' },
  { key: 'state', label: 'State', type: 'text' },
  { key: 'zip_code', label: 'ZIP Code', type: 'text' },
  { key: 'phone', label: 'Phone', type: 'text' },
  { key: 'email', label: 'Email', type: 'email' },
  { key: 'website', label: 'Website', type: 'url' },
  { key: 'hours_of_operation', label: 'Hours of Operation', type: 'textarea' },
  { key: 'pricing_tier', label: 'Pricing Tier (1–4)', type: 'text' },
  { key: 'amenities', label: 'Amenities', type: 'textarea' },
  { key: 'ambiance', label: 'Ambiance', type: 'textarea' },
];

export default function ManageRestaurant() {
  const { token } = useAuth();
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(null);
  const [photoFile, setPhotoFile] = useState(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    setLoading(true);
    ownerAPI
      .getRestaurants()
      .then(({ data }) => {
        if (!cancelled) setRestaurants(Array.isArray(data) ? data : data?.restaurants ?? []);
      })
      .catch(() => {
        if (!cancelled) toast.error('Failed to load restaurants');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [token]);

  const startEdit = (r) => {
    setEditingId(r.id);
    setForm({
      name: r.name ?? '',
      cuisine_type: r.cuisine_type ?? '',
      description: r.description ?? '',
      address: r.address ?? '',
      city: r.city ?? '',
      state: r.state ?? '',
      zip_code: r.zip_code ?? '',
      phone: r.phone ?? '',
      email: r.email ?? '',
      website: r.website ?? '',
      hours_of_operation: r.hours_of_operation ?? '',
      pricing_tier: r.pricing_tier ?? '',
      amenities: r.amenities ?? '',
      ambiance: r.ambiance ?? '',
    });
    setPhotoFile(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({});
    setPhotoFile(null);
  };

  const updateField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    if (!editingId) return;
    setSaving(true);
    try {
      await restaurantAPI.update(editingId, form);
      setRestaurants((prev) =>
        prev.map((r) => (r.id === editingId ? { ...r, ...form } : r))
      );
      toast.success('Restaurant updated');
      cancelEdit();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update restaurant');
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoUpload = async () => {
    if (!editingId || !photoFile) {
      toast.error('Select a photo first');
      return;
    }
    setUploading(editingId);
    try {
      await restaurantAPI.uploadPhoto(editingId, photoFile);
      toast.success('Photo uploaded');
      setPhotoFile(null);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to upload photo');
    } finally {
      setUploading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <FaSpinner className="animate-spin text-5xl text-red-600" aria-label="Loading" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Manage Restaurants</h1>

      {restaurants.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center text-gray-500">
          You have no restaurants yet.
        </div>
      ) : (
        <div className="space-y-6">
          {restaurants.map((r) => (
            <div
              key={r.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
            >
              {editingId === r.id ? (
                <div className="p-6 space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Edit: {r.name}</h2>
                    <div className="flex gap-2">
                      <button
                        onClick={cancelEdit}
                        className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
                      >
                        <FaTimes /> Cancel
                      </button>
                      <button
                        onClick={handleSave}
                        disabled={saving}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition flex items-center gap-2 disabled:opacity-60"
                      >
                        <FaSave /> {saving ? 'Saving...' : 'Save'}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {EDIT_FIELDS.map(({ key, label, type }) => (
                      <div
                        key={key}
                        className={type === 'textarea' ? 'sm:col-span-2' : ''}
                      >
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {label}
                        </label>
                        {type === 'textarea' ? (
                          <textarea
                            value={form[key] ?? ''}
                            onChange={(e) => updateField(key, e.target.value)}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                          />
                        ) : (
                          <input
                            type={type}
                            value={form[key] ?? ''}
                            onChange={(e) => updateField(key, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                          />
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="pt-4 border-t border-gray-100">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Photo upload</h3>
                    <div className="flex flex-wrap items-center gap-3">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setPhotoFile(e.target.files?.[0] || null)}
                        className="text-sm"
                      />
                      <button
                        onClick={handlePhotoUpload}
                        disabled={!photoFile || uploading === r.id}
                        className="px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white rounded-lg transition flex items-center gap-2 disabled:opacity-60"
                      >
                        <FaCamera />
                        {uploading === r.id ? 'Uploading...' : 'Upload photo'}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-5 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold text-gray-900">{r.name}</h2>
                    <p className="text-sm text-gray-600">{r.cuisine_type}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <StarRating rating={r.average_rating ?? 0} size="sm" />
                      <span className="text-sm text-gray-500">
                        {(r.average_rating ?? 0).toFixed(1)} · {r.review_count ?? 0} reviews
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => startEdit(r)}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition flex items-center gap-2"
                  >
                    <FaEdit /> Edit
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
