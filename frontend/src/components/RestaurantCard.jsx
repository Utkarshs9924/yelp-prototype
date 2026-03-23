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

  // 🔥 Cuisine-based image pools (multiple per category)
  const CUISINE_IMAGES = {
    pizza: [
      "https://images.unsplash.com/photo-1513104890138-7c749659a591",
      "https://images.unsplash.com/photo-1548365328-5b849b7d9b7b",
      "https://images.unsplash.com/photo-1601924582975-7e6b64e3c52f"
    ],
    mexican: [
      "https://images.unsplash.com/photo-1565299585323-38d6b0865b47",
      "https://images.unsplash.com/photo-1600891964599-f61ba0e24092"
    ],
    italian: [
      "https://images.unsplash.com/photo-1498579150354-977475b7e2b3",
      "https://images.unsplash.com/photo-1608756687911-aa1599ab3bd9"
    ],
    japanese: [
      "https://images.unsplash.com/photo-1553621042-f6e147245754",
      "https://images.unsplash.com/photo-1563612116625-3012372fccce"
    ],
    sushi: [
      "https://images.unsplash.com/photo-1579871494447-9811cf80d66c",
      "https://images.unsplash.com/photo-1553621042-f6e147245754"
    ],
    chinese: [
      "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
      "https://images.unsplash.com/photo-1585032226651-759b368d7246"
    ],
    burger: [
      "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
      "https://images.unsplash.com/photo-1550547660-d9450f859349"
    ],
    thai: [
      "https://images.unsplash.com/photo-1559314809-0d155014e29e",
      "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d"
    ],
    indian: [
      "https://images.unsplash.com/photo-1585937421606-0d5b1ada5004",
      "https://images.unsplash.com/photo-1601050690597-df0568f70950"
    ],
    coffee: [
      "https://images.unsplash.com/photo-1497935586351-b67a49e012bf",
      "https://images.unsplash.com/photo-1509042239860-f550ce710b93"
    ],
    bakery: [
      "https://images.unsplash.com/photo-1509440159596-0249088772ff",
      "https://images.unsplash.com/photo-1608198093002-ad4e005484ec"
    ],
    seafood: [
      "https://images.unsplash.com/photo-1615141982317-08471384e4f1",
      "https://images.unsplash.com/photo-1559847844-5315695dadae"
    ],
    vegan: [
      "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
      "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
    ]
  };

  // 🎲 Generic fallback images
  const GENERIC_IMAGES = [
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
    "https://images.unsplash.com/photo-1498654896293-37aacf113fd9",
    "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327",
    "https://images.unsplash.com/photo-1467003909585-2f8a72700288"
  ];

  // 🎲 helper to pick random from array
  const getRandomFromArray = (arr) => {
    const idx = Math.floor(Math.random() * arr.length);
    return `${arr[idx]}?auto=format&fit=crop&w=800&q=80`;
  };

  // 🧠 smart fallback (cuisine + random)
  const getCuisineImage = () => {
    const text = `${cuisine_type || ''} ${name || ''}`.toLowerCase();

    for (const key of Object.keys(CUISINE_IMAGES)) {
      if (text.includes(key)) {
        return getRandomFromArray(CUISINE_IMAGES[key]);
      }
    }

    return getRandomFromArray(GENERIC_IMAGES);
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