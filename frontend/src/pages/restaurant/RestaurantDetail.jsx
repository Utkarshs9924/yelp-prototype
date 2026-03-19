import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FaHeart, FaRegHeart, FaMapMarkerAlt, FaPhone, FaEnvelope, FaGlobe, FaEdit, FaTrash } from 'react-icons/fa';
import { restaurantAPI, reviewAPI, favouriteAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import StarRating from '../../components/StarRating';
import toast from 'react-hot-toast';

export default function RestaurantDetail() {
  const { restaurant_id } = useParams();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [isFavourite, setIsFavourite] = useState(false);
  const [loading, setLoading] = useState(true);
  const [favLoading, setFavLoading] = useState(false);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editingReviewId, setEditingReviewId] = useState(null);
  const [editComment, setEditComment] = useState('');

  const userReview = reviews.find((r) => r.user_id === user?.id || r.user?.id === user?.id);

  const fetchRestaurant = useCallback(async () => {
    if (!restaurant_id) return;
    try {
      const { data } = await restaurantAPI.get(restaurant_id);
      setRestaurant(data);
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
    } catch (err) {
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

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await Promise.all([fetchRestaurant(), fetchReviews(), checkFavourite()]);
      setLoading(false);
    };
    load();
  }, [fetchRestaurant, fetchReviews, checkFavourite]);

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
      await reviewAPI.create({
        restaurant_id: Number(restaurant_id),
        rating: reviewRating,
        comment: reviewComment.trim() || undefined,
      });
      toast.success('Review submitted!');
      setReviewRating(0);
      setReviewComment('');
      fetchReviews();
      fetchRestaurant();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to submit review');
    } finally {
      setSubmitting(false);
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
  const priceDisplay = restaurant.pricing_tier
    ? '$'.repeat(Number(restaurant.pricing_tier) || 1)
    : null;
  const amenities = restaurant.amenities
    ? (typeof restaurant.amenities === 'string'
        ? restaurant.amenities.split(/[,\n]/).map((a) => a.trim()).filter(Boolean)
        : Array.isArray(restaurant.amenities)
          ? restaurant.amenities
          : [])
    : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          {/* Photos Gallery */}
          {photos.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1">
              {photos.slice(0, 6).map((url, i) => (
                <div key={i} className="aspect-[4/3] overflow-hidden">
                  <img
                    src={url}
                    alt={`${restaurant.name} ${i + 1}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://placehold.co/400x300/e5e7eb/9ca3af?text=No+Image';
                    }}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="aspect-[21/9] bg-gray-200 flex items-center justify-center">
              <img
                src="https://placehold.co/800x300/e5e7eb/9ca3af?text=No+Photos"
                alt={restaurant.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          <div className="p-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{restaurant.name}</h1>
                  {priceDisplay && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-sm font-medium">
                      {priceDisplay}
                    </span>
                  )}
                  {restaurant.cuisine_type && (
                    <span className="px-2 py-0.5 bg-red-50 text-red-700 rounded text-sm">
                      {restaurant.cuisine_type}
                    </span>
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
                {isFavourite ? (
                  <FaHeart className="text-red-600" size={20} />
                ) : (
                  <FaRegHeart className="text-gray-500" size={20} />
                )}
                <span>{isFavourite ? 'Favourited' : 'Favourite'}</span>
              </button>
            </div>

            {/* Contact & Info */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {restaurant.address && (
                <div className="flex items-start gap-2">
                  <FaMapMarkerAlt className="text-red-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">
                    {[restaurant.address, restaurant.city, restaurant.state, restaurant.zip_code]
                      .filter(Boolean)
                      .join(', ')}
                  </span>
                </div>
              )}
              {restaurant.phone && (
                <div className="flex items-center gap-2">
                  <FaPhone className="text-red-600 flex-shrink-0" />
                  <a href={`tel:${restaurant.phone}`} className="text-red-600 hover:underline">
                    {restaurant.phone}
                  </a>
                </div>
              )}
              {restaurant.email && (
                <div className="flex items-center gap-2">
                  <FaEnvelope className="text-red-600 flex-shrink-0" />
                  <a href={`mailto:${restaurant.email}`} className="text-red-600 hover:underline">
                    {restaurant.email}
                  </a>
                </div>
              )}
              {restaurant.website && (
                <div className="flex items-center gap-2">
                  <FaGlobe className="text-red-600 flex-shrink-0" />
                  <a
                    href={restaurant.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-red-600 hover:underline"
                  >
                    Website
                  </a>
                </div>
              )}
            </div>

            {restaurant.description && (
              <p className="mt-4 text-gray-600">{restaurant.description}</p>
            )}

            {restaurant.hours_of_operation && (
              <div className="mt-4">
                <h3 className="font-semibold text-gray-900 mb-1">Hours</h3>
                <pre className="text-sm text-gray-600 whitespace-pre-wrap font-sans">
                  {restaurant.hours_of_operation}
                </pre>
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
                    <span
                      key={i}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Reviews Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Reviews</h2>

          {/* Write Review (if logged in, no existing review) */}
          {user && !userReview && (
            <form onSubmit={handleSubmitReview} className="mb-8 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-3">Write a Review</h3>
              <div className="flex items-center gap-2 mb-3">
                <StarRating
                  rating={reviewRating}
                  onRate={setReviewRating}
                  size="lg"
                />
                <span className="text-sm text-gray-600">Your rating</span>
              </div>
              <textarea
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                placeholder="Share your experience..."
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 mb-3"
              />
              <button
                type="submit"
                disabled={submitting || reviewRating < 1}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
            </form>
          )}

          {!user && (
            <p className="mb-6 text-gray-500 text-sm">
              <Link to="/login" className="text-red-600 hover:underline">Log in</Link> to write a review.
            </p>
          )}

          {/* Reviews List */}
          <div className="space-y-4">
            {reviews.length === 0 ? (
              <p className="text-gray-500">No reviews yet. Be the first to review!</p>
            ) : (
              reviews.map((review) => {
                const isOwn = review.user_id === user?.id || review.user?.id === user?.id;
                const isEditing = editingReviewId === review.id;

                return (
                  <div
                    key={review.id}
                    className="p-4 border border-gray-100 rounded-lg hover:bg-gray-50/50"
                  >
                    {isEditing ? (
                      <form onSubmit={handleUpdateReview}>
                        <textarea
                          value={editComment}
                          onChange={(e) => setEditComment(e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-2"
                        />
                        <div className="flex gap-2">
                          <button
                            type="submit"
                            disabled={submitting}
                            className="px-3 py-1 bg-red-600 text-white rounded text-sm"
                          >
                            Save
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setEditingReviewId(null);
                              setEditComment('');
                            }}
                            className="px-3 py-1 border border-gray-300 rounded text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </form>
                    ) : (
                      <>
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">
                              {review.user?.name ?? review.user_name ?? 'Anonymous'}
                            </span>
                            <StarRating rating={review.rating ?? 0} size="sm" />
                          </div>
                          {isOwn && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  setEditingReviewId(review.id);
                                  setEditComment(review.comment ?? '');
                                }}
                                className="text-gray-500 hover:text-red-600 p-1"
                                title="Edit"
                              >
                                <FaEdit size={14} />
                              </button>
                              <button
                                onClick={() => handleDeleteReview(review.id)}
                                disabled={submitting}
                                className="text-gray-500 hover:text-red-600 p-1"
                                title="Delete"
                              >
                                <FaTrash size={14} />
                              </button>
                            </div>
                          )}
                        </div>
                        {review.comment && (
                          <p className="mt-1 text-gray-600 text-sm">{review.comment}</p>
                        )}
                        <p className="mt-1 text-xs text-gray-400">
                          {review.created_at
                            ? new Date(review.created_at).toLocaleDateString()
                            : ''}
                        </p>
                      </>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
