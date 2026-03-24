import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FaHeart, FaRegHeart, FaMapMarkerAlt, FaPhone, FaEnvelope, FaGlobe, FaEdit, FaTrash, FaUtensils, FaCamera, FaTimesCircle, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { restaurantAPI, reviewAPI, favouriteAPI, photoAPI } from '../../services/api';
import { useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import StarRating from '../../components/StarRating';
import toast from 'react-hot-toast';

// ✅ Verified IDs — same as RestaurantCard.jsx which already works
const ADLS_BASE = 'https://yelpclonephotos.blob.core.windows.net/restaurant-photos';

const CUISINE_ASSET_MAP = {
  'Pizza': 'traditional_pasta_review_photo_3_1774302771097.png',
  'Mexican': 'tacos_platter_review_photo_4_1774302786282.png',
  'Italian': 'traditional_pasta_review_photo_3_1774302771097.png',
  'Japanese': 'sushi_platter_review_photo_2_1774302757257.png',
  'Sushi': 'sushi_platter_review_photo_2_1774302757257.png',
  'Chinese': 'dim_sum_review_photo_6_1774302824990.png',
  'Thai': 'dim_sum_review_photo_6_1774302824990.png',
  'Burger': 'gourmet_burger_review_photo_1_1774302742382.png',
  'Thai': 'dim_sum_review_photo_6_1774302824990.png',
  'Indian': 'indian_curry_review_photo_8_1774302851319.png',
  'Seafood': 'sushi_platter_review_photo_2_1774302757257.png',
  'American': 'gourmet_burger_review_photo_1_1774302742382.png',
  'Fast Food': 'gourmet_burger_review_photo_1_1774302742382.png',
  'Chicken': 'fried_chicken_review_photo_9_1774302865083.png',
  'Steakhouse': 'steak_dinner_review_photo_5_1774302802504.png',
  'Bakery': 'avocado_toast_review_photo_7_1774302837757.png',
  'Dessert': 'chocolate_lava_cake_review_photo_10_1774302875701.png',
  'Cafe': 'avocado_toast_review_photo_7_1774302837757.png',
  'Coffee': 'avocado_toast_review_photo_7_1774302837757.png',
  'Bar': 'steak_dinner_review_photo_5_1774302802504.png',
  'Pub': 'steak_dinner_review_photo_5_1774302802504.png'
};

const ULTIMATE_FALLBACK = `${ADLS_BASE}/gourmet_burger_review_photo_1_1774302742382.png`;

function getFallbackImage(cuisineType, name) {
  const combined = `${cuisineType || ''} ${name || ''}`.toLowerCase();
  for (const [key, asset] of Object.entries(CUISINE_ASSET_MAP)) {
    if (combined.includes(key.toLowerCase())) {
      return `${ADLS_BASE}/${asset}`;
    }
  }
  return ULTIMATE_FALLBACK;
}

export default function RestaurantDetail() {
  const { restaurant_id } = useParams();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [isFavourite, setIsFavourite] = useState(false);
  const [loading, setLoading] = useState(true);
  const [favLoading, setFavLoading] = useState(false);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editComment, setEditComment] = useState('');
  const [activeTab, setActiveTab] = useState('menu');
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [userPhotos, setUserPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [reviewFile, setReviewFile] = useState(null);
  const fileInputRef = useRef(null);
  const reviewPhotoRef = useRef(null);

  const canDeletePhotos = user && (user.role === 'admin' || user.role === 'business_owner');
  const userReview = reviews.find((r) => r.user_id === user?.id || r.user?.id === user?.id);
  
  const handlePrevPhoto = (e) => {
    e.stopPropagation();
    if (!selectedPhoto || userPhotos.length <= 1) return;
    const currentIndex = userPhotos.findIndex(p => p.photo_url === selectedPhoto.photo_url);
    const newIndex = (currentIndex - 1 + userPhotos.length) % userPhotos.length;
    setSelectedPhoto(userPhotos[newIndex]);
  };

  const handleNextPhoto = (e) => {
    e.stopPropagation();
    if (!selectedPhoto || userPhotos.length <= 1) return;
    const currentIndex = userPhotos.findIndex(p => p.photo_url === selectedPhoto.photo_url);
    const newIndex = (currentIndex + 1) % userPhotos.length;
    setSelectedPhoto(userPhotos[newIndex]);
  };

  const fetchRestaurant = useCallback(async () => {
    if (!restaurant_id) return;
    try {
      const { data } = await restaurantAPI.get(restaurant_id);
      setRestaurant(data);
      // Synchronize user photos for navigation
      setUserPhotos(data.user_photos || []);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Restaurant not found');
      navigate('/');
    }
  }, [restaurant_id, navigate]);

  const fetchReviews = useCallback(async () => {
    if (!restaurant_id) return;
    try {
      const { data } = await reviewAPI.getForRestaurant(restaurant_id);
      setReviews(Array.isArray(data) ? data : data?.reviews ?? []);
    } catch {
      setReviews([]);
    }
  }, [restaurant_id]);

  const checkFavourite = useCallback(async () => {
    if (!restaurant_id || !token) return;
    try {
      const { data } = await favouriteAPI.check(restaurant_id);
      setIsFavourite(data?.is_favourite ?? data ?? false);
    } catch {
      setIsFavourite(false);
    }
  }, [restaurant_id, token]);

  const fetchMenu = useCallback(async () => {
    if (!restaurant_id) return;
    try {
      const { data } = await restaurantAPI.getMenu(restaurant_id);
      setMenuItems(Array.isArray(data) ? data : []);
    } catch {
      setMenuItems([]);
    }
  }, [restaurant_id]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, []);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await Promise.all([fetchRestaurant(), fetchReviews(), checkFavourite(), fetchMenu()]);
      setLoading(false);
    };
    load();
  }, [fetchRestaurant, fetchReviews, checkFavourite, fetchMenu]);

  const toggleFavourite = async () => {
    if (!token) {
      toast.error('Please log in to add favourites');
      navigate('/login');
      return;
    }
    setFavLoading(true);
    try {
      if (isFavourite) {
        await favouriteAPI.remove(restaurant_id);
        setIsFavourite(false);
        toast.success('Removed from favourites');
      } else {
        await favouriteAPI.add(restaurant_id);
        setIsFavourite(true);
        toast.success('Added to favourites');
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update favourite');
    } finally {
      setFavLoading(false);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!token) {
      toast.error('Please log in to write a review');
      navigate('/login');
      return;
    }
    if (reviewRating < 1) {
      toast.error('Please select a rating');
      return;
    }
    setSubmitting(true);
    try {
      let photo_url = null;
      if (reviewFile) {
        const { data: uploadRes } = await reviewAPI.uploadPhoto(reviewFile);
        photo_url = uploadRes.photo_url;
      }
      await reviewAPI.create({
        restaurant_id: Number(restaurant_id),
        rating: reviewRating,
        comment: reviewComment.trim() || undefined,
        photo_url,
      });
      toast.success('Review submitted!');
      setReviewRating(0);
      setReviewComment('');
      setReviewFile(null);
      fetchReviews();
      fetchRestaurant();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClaim = async () => {
    if (!window.confirm('Are you the authorized owner of this business? Your claim will be reviewed by an administrator.')) return;
    try {
      const { data } = await restaurantAPI.claim(restaurant_id);
      toast.success(data.message);
      fetchRestaurant();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to claim restaurant');
    }
  };

  const handleUpdateReview = async (e) => {
    e.preventDefault();
    if (!editingReviewId || !editComment.trim()) return;
    setSubmitting(true);
    try {
      await reviewAPI.update(editingReviewId, { comment: editComment.trim() });
      toast.success('Review updated');
      setEditingReviewId(null);
      setEditComment('');
      fetchReviews();
      fetchRestaurant();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update review');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Delete this review?')) return;
    setSubmitting(true);
    try {
      await reviewAPI.delete(reviewId);
      toast.success('Review deleted');
      fetchReviews();
      fetchRestaurant();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to delete review');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !restaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  const photos = restaurant.photos ?? [];
  const userPhotosList = restaurant.user_photos ?? [];
  const priceDisplay = restaurant.pricing_tier ? '$'.repeat(Number(restaurant.pricing_tier) || 1) : null;
  const amenities = restaurant.amenities
    ? (typeof restaurant.amenities === 'string'
        ? restaurant.amenities.split(/[,\n]/).map((a) => a.trim()).filter(Boolean)
        : Array.isArray(restaurant.amenities) ? restaurant.amenities : [])
    : [];

  const heroFallback = getFallbackImage(restaurant.cuisine_type, restaurant.name);

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-6">
        <header className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-6">

          {/* ── Hero Image (Simplified) ── */}
          <div className="aspect-[21/9] overflow-hidden bg-gray-100 relative">
            <img
              src={photos.length > 0 ? photos[0] : heroFallback}
              alt={restaurant.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                if (e.target.src !== ULTIMATE_FALLBACK) {
                  e.target.src = ULTIMATE_FALLBACK;
                }
              }}
            />
            {photos.length > 1 && (
              <div className="absolute bottom-4 right-4 bg-black/60 text-white px-3 py-1.5 rounded-lg text-sm font-medium backdrop-blur-sm">
                1 / {photos.length} Photos
              </div>
            )}
          </div>

          {/* Upload Photo */}
          {user && (
            <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex items-center gap-3">
              <input
                type="file"
                ref={fileInputRef}
                accept="image/jpeg,image/png,image/webp,image/gif"
                className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  setUploading(true);
                  try {
                    await photoAPI.upload(restaurant_id, file);
                    toast.success('Photo uploaded! 📸');
                    fetchRestaurant();
                  } catch (err) {
                    toast.error(err.response?.data?.detail || 'Failed to upload photo');
                  } finally {
                    setUploading(false);
                    e.target.value = '';
                  }
                }}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 text-sm font-medium"
              >
                <FaCamera size={14} />
                {uploading ? 'Uploading...' : 'Add Photo'}
              </button>
              <span className="text-xs text-gray-400">JPEG, PNG, WebP, GIF • Max 10MB</span>
            </div>
          )}

          <div className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{restaurant.name}</h1>
                  {priceDisplay && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-sm font-medium">{priceDisplay}</span>
                  )}
                  {restaurant.cuisine_type && (
                    <span className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-sm">{restaurant.cuisine_type}</span>
                  )}
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <StarRating rating={restaurant.average_rating ?? 0} size="lg" />
                  <span className="text-gray-600">
                    {(restaurant.average_rating ?? 0).toFixed(1)} ({restaurant.review_count ?? reviews.length} reviews)
                  </span>
                </div>
              </div>

              <button
                onClick={toggleFavourite}
                disabled={favLoading}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 hover:border-red-300 hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                {isFavourite ? <FaHeart className="text-red-600" size={20} /> : <FaRegHeart className="text-gray-500" size={20} />}
                <span>{isFavourite ? 'Favourited' : 'Favourite'}</span>
              </button>

              {user?.role === 'owner' && !restaurant.owner_id && (
                <button
                  onClick={handleClaim}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
                >
                  Claim this Business
                </button>
              )}
            </div>

            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {restaurant.address && (
                <div className="flex items-start gap-2">
                  <FaMapMarkerAlt className="text-red-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">
                    {[restaurant.address, restaurant.city, restaurant.state, restaurant.zip_code].filter(Boolean).join(', ')}
                  </span>
                </div>
              )}
              {restaurant.phone && (
                <div className="flex items-center gap-2">
                  <FaPhone className="text-red-600 flex-shrink-0" />
                  <a href={`tel:${restaurant.phone}`} className="text-red-600 hover:underline">{restaurant.phone}</a>
                </div>
              )}
              {restaurant.email && (
                <div className="flex items-center gap-2">
                  <FaEnvelope className="text-red-600 flex-shrink-0" />
                  <a href={`mailto:${restaurant.email}`} className="text-red-600 hover:underline">{restaurant.email}</a>
                </div>
              )}
              {restaurant.website && (
                <div className="flex items-center gap-2">
                  <FaGlobe className="text-red-600 flex-shrink-0" />
                  <a href={restaurant.website} target="_blank" rel="noopener noreferrer" className="text-red-600 hover:underline">Website</a>
                </div>
              )}
            </div>

            {restaurant.description && <p className="mt-4 text-gray-600">{restaurant.description}</p>}

            {restaurant.hours_of_operation && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-1">Hours</h3>
                <pre className="text-sm text-gray-600 whitespace-pre-wrap font-sans">{restaurant.hours_of_operation}</pre>
              </div>
            )}

            {restaurant.ambiance && (
              <p className="mt-2 text-sm text-gray-600">
                <span className="font-medium">Ambiance:</span> {restaurant.ambiance}
              </p>
            )}

            {amenities.length > 0 && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-2">Amenities</h3>
                <div className="flex flex-wrap gap-2">
                  {amenities.map((a, i) => (
                    <span key={i} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">{a}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('menu')}
              className={`flex-1 flex items-center justify-center gap-2 py-4 px-6 text-sm font-semibold transition-colors ${
                activeTab === 'menu' ? 'text-red-600 border-b-2 border-red-600 bg-red-50/50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FaUtensils size={16} /> Menu ({menuItems.length} items)
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`flex-1 flex items-center justify-center gap-2 py-4 px-6 text-sm font-semibold transition-colors ${
                activeTab === 'reviews' ? 'text-red-600 border-b-2 border-red-600 bg-red-50/50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              ⭐ Reviews ({reviews.length})
            </button>
            <button
              onClick={() => setActiveTab('photos')}
              className={`flex-1 flex items-center justify-center gap-2 py-4 px-6 text-sm font-semibold transition-colors ${
                activeTab === 'photos' ? 'text-red-600 border-b-2 border-red-600 bg-red-50/50' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FaCamera size={16} /> Photos ({userPhotosList.length + photos.length})
            </button>
          </div>

          <div className="p-6">
            {/* Menu Tab */}
            {activeTab === 'menu' && (
              <div>
                {menuItems.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No menu available for this restaurant.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {menuItems.map((item) => (
                      <div key={item.id} className="flex justify-between items-start p-4 rounded-lg border border-gray-100 hover:border-red-200 hover:bg-red-50/30 transition-colors">
                        <div className="flex-1 pr-4">
                          <h4 className="font-semibold text-gray-900">{item.name}</h4>
                          {item.description && <p className="text-sm text-gray-500 mt-1 leading-relaxed">{item.description}</p>}
                        </div>
                        <span className="text-red-600 font-bold text-lg whitespace-nowrap">${parseFloat(item.price).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {/* Photos Tab */}
            {activeTab === 'photos' && (
              <div>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                  {/* Official Photos */}
                  {photos.map((url, i) => (
                    <div key={`official-${i}`} className="aspect-square rounded-lg overflow-hidden border border-gray-100 group relative">
                      <img src={url} alt="Official" className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform" onClick={() => window.open(url, '_blank')} />
                      {canDeletePhotos && (
                        <button
                          onClick={async () => {
                            const photoId = restaurant.photo_ids?.[i];
                            if (!photoId) return;
                            if (!window.confirm('Delete official photo?')) return;
                            try {
                              await photoAPI.delete(photoId);
                              toast.success('Photo deleted');
                              fetchRestaurant();
                            } catch (err) {
                              toast.error('Failed to delete');
                            }
                          }}
                          className="absolute top-1 right-1 bg-black/50 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <FaTimesCircle size={14} />
                        </button>
                      )}
                    </div>
                  ))}
                  {/* User Photos */}
                  {userPhotosList.map((p, i) => (
                    <div key={`user-${i}`} className="aspect-square rounded-lg overflow-hidden border border-gray-100 group relative">
                      <img 
                        src={p.photo_url} 
                        alt={p.caption} 
                        className="w-full h-full object-cover cursor-pointer hover:scale-105 transition-transform" 
                        onClick={() => setSelectedPhoto(p)} 
                      />
                      <div className="absolute bottom-0 left-0 right-0 bg-black/40 text-white text-[10px] p-1 truncate opacity-0 group-hover:opacity-100 transition-opacity">
                        {p.caption || 'User Photo'}
                      </div>
                    </div>
                  ))}
                </div>
                {photos.length === 0 && userPhotosList.length === 0 && (
                  <p className="text-gray-500 text-center py-8">No photos yet.</p>
                )}

                {/* Photo Context Modal */}
                {selectedPhoto && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={() => setSelectedPhoto(null)}>
                    <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col md:flex-row shadow-2xl" onClick={e => e.stopPropagation()}>
                      <div className="flex-1 bg-gray-900 flex items-center justify-center p-2 relative group">
                        {userPhotosList.length > 1 && (
                          <>
                            <button 
                              onClick={handlePrevPhoto}
                              className="absolute left-4 p-3 rounded-full bg-white/20 text-white hover:bg-white/40 transition-all z-20 backdrop-blur-md border border-white/30 active:scale-90"
                              title="Previous Photo"
                            >
                              <FaChevronLeft size={24} />
                            </button>
                            <button 
                              onClick={handleNextPhoto}
                              className="absolute right-4 p-3 rounded-full bg-white/20 text-white hover:bg-white/40 transition-all z-20 backdrop-blur-md border border-white/30 active:scale-90"
                              title="Next Photo"
                            >
                              <FaChevronRight size={24} />
                            </button>
                          </>
                        )}
                        <img src={selectedPhoto.photo_url} alt="Review" className="max-w-full max-h-[70vh] object-contain" />
                      </div>
                      <div className="w-full md:w-80 p-6 flex flex-col border-l border-gray-100 bg-gray-50/50">
                        <div className="flex justify-between items-start mb-6">
                            <h3 className="text-xl font-bold text-gray-900">Review Context</h3>
                            <button onClick={() => setSelectedPhoto(null)} className="text-gray-400 hover:text-gray-600 transition-colors">
                                <FaTimesCircle size={24} />
                            </button>
                        </div>
                        
                        {selectedPhoto.user_name ? (
                          <>
                            <div className="mb-4">
                                <span className="text-sm font-bold text-gray-500 uppercase tracking-wider">Posted by</span>
                                <div className="flex items-center gap-3">
                                    <p className="text-lg font-semibold text-gray-900">{selectedPhoto.user_name}</p>
                                    <StarRating rating={selectedPhoto.rating || 0} size="sm" />
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                <span className="text-sm font-bold text-gray-500 uppercase tracking-wider block mb-2">Review</span>
                                <p className="text-gray-700 italic leading-relaxed">
                                    "{selectedPhoto.comment || "No comment provided."}"
                                </p>
                            </div>
                          </>
                        ) : (
                          <div className="flex-1 flex items-center justify-center">
                            <p className="text-gray-500 italic">Official restaurant photo</p>
                          </div>
                        )}
                        
                        <div className="mt-auto pt-6 border-t border-gray-200">
                           <button 
                            onClick={() => {
                                setSelectedPhoto(null);
                                setActiveTab('reviews');
                                // Could add scroll logic here if needed
                            }}
                            className="w-full bg-red-600 text-white rounded-xl py-3 font-bold hover:bg-red-700 transition-all shadow-md active:scale-95"
                           >
                            View All Reviews
                           </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Reviews Tab */}
            {activeTab === 'reviews' && (
              <div>
                {user && !userReview && (
                  <form onSubmit={handleSubmitReview} className="mb-8 p-4 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-3">Write a Review</h3>
                    <div className="flex items-center gap-2 mb-3">
                      <StarRating rating={reviewRating} onRate={setReviewRating} size="lg" />
                      <span className="text-sm text-gray-600">Your rating</span>
                    </div>
                    <textarea
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      placeholder="Share your experience..."
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 mb-3"
                    />
                    <div className="flex items-center gap-4 mb-4">
                      <input type="file" ref={reviewPhotoRef} onChange={(e) => setReviewFile(e.target.files[0])} className="hidden" accept="image/*" />
                      <button type="button" onClick={() => reviewPhotoRef.current.click()} className="flex items-center gap-2 px-3 py-1.5 border border-gray-300 rounded-md text-sm hover:bg-gray-100">
                        <FaCamera className="text-gray-500" />
                        {reviewFile ? 'Change Photo' : 'Attach Photo'}
                      </button>
                      {reviewFile && <span className="text-xs text-gray-500 truncate max-w-[200px]">{reviewFile.name}</span>}
                    </div>
                    <button type="submit" disabled={submitting || reviewRating < 1} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed">
                      {submitting ? 'Submitting...' : 'Submit Review'}
                    </button>
                  </form>
                )}

                {!user && (
                  <p className="mb-6 text-gray-500 text-sm">
                    <Link to="/login" className="text-red-600 hover:underline">Log in</Link> to write a review.
                  </p>
                )}

                <div className="space-y-4">
                  {reviews.length === 0 ? (
                    <p className="text-gray-500">No reviews yet. Be the first to review!</p>
                  ) : (
                    reviews.map((review) => {
                      const canManageReview = 
                        user?.role === 'admin' || 
                        (user?.role === 'owner' && restaurant?.owner_id === user?.id);
                      
                      const isEditing = editingReviewId === review.id;
                      return (
                        <article key={review.id} className="p-4 border border-gray-100 rounded-lg hover:bg-gray-50/50">
                          {isEditing ? (
                            <form onSubmit={handleUpdateReview}>
                              <textarea value={editComment} onChange={(e) => setEditComment(e.target.value)} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-2" />
                              <div className="flex gap-2">
                                <button type="submit" disabled={submitting} className="px-3 py-1 bg-red-600 text-white rounded text-sm">Save</button>
                                <button type="button" onClick={() => { setEditingReviewId(null); setEditComment(''); }} className="px-3 py-1 border border-gray-300 rounded text-sm">Cancel</button>
                              </div>
                            </form>
                          ) : (
                            <>
                              <div className="flex items-center justify-between gap-2">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-gray-900">{review.user?.name ?? review.user_name ?? 'Anonymous'}</span>
                                  <StarRating rating={review.rating ?? 0} size="sm" />
                                </div>
                                {canManageReview && (
                                  <div className="flex gap-2">
                                    <button onClick={() => { setEditingReviewId(review.id); setEditComment(review.comment ?? ''); }} className="text-gray-500 hover:text-red-600 p-1" title="Edit"><FaEdit size={14} /></button>
                                    <button onClick={() => handleDeleteReview(review.id)} disabled={submitting} className="text-gray-500 hover:text-red-600 p-1" title="Delete"><FaTrash size={14} /></button>
                                  </div>
                                )}
                              </div>
                              {review.photo_url ? (
                                <div className="mt-3 flex gap-4 bg-white p-3 rounded-xl border border-gray-100 shadow-sm">
                                  <div className="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer hover:opacity-90 transition-opacity"
                                       onClick={() => setSelectedPhoto({ 
                                           photo_url: review.photo_url, 
                                           user_name: review.user?.name ?? review.user_name ?? 'Anonymous', 
                                           comment: review.comment,
                                           rating: review.rating
                                       })}
                                  >
                                    <img src={review.photo_url} alt="Review media" className="w-full h-full object-cover" />
                                  </div>
                                  <div className="flex-1">
                                    <p className="text-gray-700 text-sm leading-relaxed">{review.comment}</p>
                                  </div>
                                </div>
                              ) : (
                                review.comment && <p className="mt-2 text-gray-700 text-sm leading-relaxed">{review.comment}</p>
                              )}
                              <p className="mt-3 text-[10px] text-gray-400 font-medium uppercase tracking-wider">{review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</p>
                            </>
                          )}
                        </article>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}