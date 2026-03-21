import { Link } from 'react-router-dom';
import StarRating from './StarRating';

export default function RestaurantCard({ restaurant, variant = 'grid', compact }) {
  const {
    id,
    name,
    cuisine_type,
    city,
    pricing_tier,
    average_rating = 0,
    review_count = 0,
    description,
    photos,
  } = restaurant || {};

  const CUISINE_IMAGE_MAP = {
    'Pizza': '1513104890138-7c749659a591',
    'Mexican': '1565299524944-86dc24727f71',
    'Italian': '1498579150354-977475b7e2b3',
    'Japanese': '1553621042-f6e147245754',
    'Sushi': '1579871494447-9811cf80d66c',
    'Chinese': '1540189549336-e6e99c3679fe',
    'Burger': '1568901346375-23c9450c58cd',
    'Thai': '1559314809-0d155014e29e',
    'Indian': '1585937421606-0d5b1ada5004',
    'Coffee': '1497935586351-b67a49e012bf',
    'Bakery': '1509440159596-0249088772ff',
    'Seafood': '1615141982317-08471384e4f1',
    'Vegan': '1512621776951-a57141f2eefd'
  };

  const GENERIC_IMAGES = [
    '1414235077428-97116960ac16',
    '1504674900247-0877df9cc836',
    '1476224203463-9889505c10ad'
  ];

  const getFallbackImage = () => {
    if (!cuisine_type) return `https://images.unsplash.com/photo-${GENERIC_IMAGES[0]}?auto=format&fit=crop&w=800&q=80`;
    const cType = cuisine_type.toLowerCase();
    
    for (const [key, photoId] of Object.entries(CUISINE_IMAGE_MAP)) {
      if (cType.includes(key.toLowerCase())) {
        return `https://images.unsplash.com/photo-${photoId}?auto=format&fit=crop&w=800&q=80`;
      }
    }
    
    // stable pseudo-random choice from generic based on name length
    const idx = (name?.length || 0) % GENERIC_IMAGES.length;
    return `https://images.unsplash.com/photo-${GENERIC_IMAGES[idx]}?auto=format&fit=crop&w=800&q=80`;
  };

  const imageUrl = photos?.length > 0 ? photos[0] : getFallbackImage();
  const priceDisplay = pricing_tier ? '$'.repeat(Number(pricing_tier) || 1) : null;

  const isList = variant === 'list' || compact;
  const listCompact = compact;

  if (isList) {
    return (
      <Link
        to={`/restaurants/${id}`}
        className={`flex gap-3 bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-100 ${
          listCompact ? 'p-2 gap-2' : 'p-4 gap-4'
        }`}
      >
        <div
          className={`flex-shrink-0 rounded-lg overflow-hidden bg-gray-200 ${
            listCompact ? 'w-12 h-12' : 'w-24 h-24'
          }`}
        >
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.src = 'https://placehold.co/96x96/e5e7eb/9ca3af?text=No+Image';
            }}
          />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-gray-900 truncate ${listCompact ? 'text-sm' : ''}`}>
            {name}
          </h3>
          <p className={`text-gray-600 ${listCompact ? 'text-xs' : 'text-sm'}`}>
            {cuisine_type}
            {city && ` • ${city}`}
          </p>
          <div className={`flex items-center gap-2 ${listCompact ? 'mt-0.5' : 'mt-1'}`}>
            <StarRating rating={Number(average_rating) || 0} size="sm" />
            <span className={`text-gray-500 ${listCompact ? 'text-xs' : 'text-sm'}`}>
              {(Number(average_rating) || 0).toFixed(1)} ({review_count} reviews)
            </span>
            {priceDisplay && (
              <span className={`text-gray-600 ${listCompact ? 'text-xs' : 'text-sm'}`}>
                {priceDisplay}
              </span>
            )}
          </div>
        </div>
      </Link>
    );
  }

  return (
    <Link
      to={`/restaurants/${id}`}
      className="block bg-white rounded-lg shadow hover:shadow-lg transition-all overflow-hidden border border-gray-100 hover:border-red-100"
    >
      <div className="aspect-[4/3] overflow-hidden bg-gray-200">
        <img
          src={imageUrl}
          alt={name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            e.target.src = 'https://placehold.co/400x300/e5e7eb/9ca3af?text=No+Image';
          }}
        />
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 truncate">{name}</h3>
        <p className="text-sm text-gray-600 mt-0.5">
          {cuisine_type}
          {city && ` • ${city}`}
        </p>
        <div className="flex items-center gap-2 mt-2">
          <StarRating rating={Number(average_rating) || 0} size="sm" />
          <span className="text-sm text-gray-500">
            {(Number(average_rating) || 0).toFixed(1)} ({review_count})
          </span>
          {priceDisplay && (
            <span className="text-sm text-gray-600 ml-auto">{priceDisplay}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
