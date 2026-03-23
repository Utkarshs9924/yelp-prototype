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
  const CUISINE_IMAGE_MAP = {
    'Pizza': '1513104890138-7c749659a591',
    'Mexican': '1504674900247-0877df9cc836',
    'Italian': '1501339847302-ac426a4a7cbb',
    'Japanese': '1580822184713-fc5400e7fe10',
    'Sushi': '1579871494447-9811cf80d66c',
    'Chinese': '1540189549336-e6e99c3679fe',
    'Burger': '1561758033-d89a9ad46330',
    'Thai': '1559314809-0d155014e29e',
    'Indian': '1517248135467-4c7edcad34c4',
    'American': '1550966871-3ed3cdb5ed0c',
    'Fast Food': '1561758033-d89a9ad46330',
    'Coffee': '1495474472287-4d71bcdd2085',
    'Cafe': '1501339847302-ac426a4a7cbb',
    'Bakery': '1509440159596-0249088772ff',
    'Seafood': '1476224203463-9889505c10ad',
    'Vegan': '1512621776951-a57141f2eefd',
    'Steakhouse': '1558030006-450675393462',
    'Bar': '1514362545857-3bc16c4c7d1b',
    'Grill': '1555939594-58d7cb561ad1',
    'Pub': '1514362545857-3bc16c4c7d1b'
  };

  // 🎲 Generic fallback IDs
  const GENERIC_IMAGES = [
    '1546069901-ba9599a7e63c',
    '1519708227418-c8fd9a32b7a2',
    '1493770348161-369560ae357d'
  ];

  // 🧠 smart fallback logic
  const getCuisineImage = () => {
    const type = cuisine_type || '';
    const nameStr = name || '';
    const combined = `${type} ${nameStr}`.toLowerCase();

    // Check mapping
    for (const [key, id] of Object.entries(CUISINE_IMAGE_MAP)) {
      if (combined.includes(key.toLowerCase())) {
        return `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=800&q=80`;
      }
    }

    // Pick random generic
    const randomId = GENERIC_IMAGES[Math.floor(Math.random() * GENERIC_IMAGES.length)];
    return `https://images.unsplash.com/photo-${randomId}?auto=format&fit=crop&w=800&q=80`;
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