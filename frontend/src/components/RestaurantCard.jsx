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

  const imageUrl = photos?.[0] || '/placeholder-restaurant.jpg';
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
            <StarRating rating={average_rating} size="sm" />
            <span className={`text-gray-500 ${listCompact ? 'text-xs' : 'text-sm'}`}>
              {average_rating.toFixed(1)} ({review_count} reviews)
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
          <StarRating rating={average_rating} size="sm" />
          <span className="text-sm text-gray-500">
            {average_rating.toFixed(1)} ({review_count})
          </span>
          {priceDisplay && (
            <span className="text-sm text-gray-600 ml-auto">{priceDisplay}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
