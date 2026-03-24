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

  // 🎯 Verified Cuisine-based image mapping
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

  // 🧠 smart fallback logic
  const getCuisineImage = () => {
    const type = cuisine_type || '';
    const nameStr = name || '';
    const combined = `${type} ${nameStr}`.toLowerCase();

    // Check mapping
    for (const [key, asset] of Object.entries(CUISINE_ASSET_MAP)) {
      if (combined.includes(key.toLowerCase())) {
        return `${ADLS_BASE}/${asset}`;
      }
    }

    return ULTIMATE_FALLBACK;
  };

  // ✅ final image logic
  const imageUrl = photos?.length > 0 
    ? photos[0] 
    : getCuisineImage();

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
              e.target.src = getCuisineImage(); // 🔄 fallback if broken
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
            e.target.src = getCuisineImage(); // 🔄 fallback if broken
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