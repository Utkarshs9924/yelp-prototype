import { useState } from 'react';
import { FaStar, FaStarHalfAlt, FaRegStar } from 'react-icons/fa';

const sizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-xl',
};

export default function StarRating({ rating = 0, onRate, size = 'md' }) {
  const [hoverRating, setHoverRating] = useState(null);
  const isInteractive = typeof onRate === 'function';
  const displayRating = hoverRating ?? rating;

  const renderStar = (index) => {
    const value = index + 1;
    const filled = displayRating >= value;
    const half = displayRating >= value - 0.5 && displayRating < value;

    const StarIcon = filled ? FaStar : half ? FaStarHalfAlt : FaRegStar;

    const star = (
      <StarIcon
        className={`text-amber-400 ${sizeClasses[size]} ${isInteractive ? 'cursor-pointer' : ''}`}
        onMouseEnter={isInteractive ? () => setHoverRating(value) : undefined}
        onMouseLeave={isInteractive ? () => setHoverRating(null) : undefined}
        onClick={
          isInteractive
            ? (e) => {
                e.preventDefault();
                onRate(value);
              }
            : undefined
        }
      />
    );

    return <span key={index}>{star}</span>;
  };

  return (
    <div className="flex items-center gap-0.5" role={isInteractive ? 'slider' : undefined}>
      {[0, 1, 2, 3, 4].map(renderStar)}
    </div>
  );
}
