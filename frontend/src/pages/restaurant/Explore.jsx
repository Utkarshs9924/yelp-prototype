import { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { searchRestaurants } from '../../redux/slices/restaurantsSlice';
import { useAuth } from '../../context/AuthContext';
import RestaurantCard from '../../components/RestaurantCard';
import toast from 'react-hot-toast';

function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null;

  const getPages = () => {
    const pages = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }
    pages.push(1);
    if (page > 3) pages.push('...');
    for (let i = Math.max(2, page - 1); i <= Math.min(totalPages - 1, page + 1); i++) {
      pages.push(i);
    }
    if (page < totalPages - 2) pages.push('...');
    pages.push(totalPages);
    return pages;
  };

  return (
    <div className="pagination">
      <button className="page-btn" onClick={() => onPageChange(page - 1)} disabled={page === 1} aria-label="Previous page">‹</button>
      {getPages().map((p, i) =>
        p === '...' ? (
          <span key={`ellipsis-${i}`} className="page-ellipsis">…</span>
        ) : (
          <button key={p} className={`page-btn ${p === page ? 'active' : ''}`} onClick={() => onPageChange(p)}>{p}</button>
        )
      )}
      <button className="page-btn" onClick={() => onPageChange(page + 1)} disabled={page === totalPages} aria-label="Next page">›</button>
    </div>
  );
}

export default function Explore() {
  const { user } = useAuth();
  const dispatch = useDispatch();
  const { list: restaurants, total, totalPages, page, searching: loading } = useSelector(
    (state) => state.restaurants
  );

  const [search, setSearch] = useState('');
  const [cityZip, setCityZip] = useState('');
  const [searchMode, setSearchMode] = useState('standard');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedPrice, setSelectedPrice] = useState('');
  const [selectedAmenities, setSelectedAmenities] = useState([]);

  const fetchRestaurants = useCallback((pageNum = 1) => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    const val = cityZip.trim();
    dispatch(searchRestaurants({
      query: search.trim() || undefined,
      cuisine: selectedCuisine || undefined,
      city: val && !/^\d+$/.test(val) ? val : undefined,
      zip_code: val && /^\d+$/.test(val) ? val : undefined,
      pricing_tier: selectedPrice || undefined,
      amenities: selectedAmenities.length > 0 ? selectedAmenities.join(',') : undefined,
      page: pageNum,
      limit: 30,
    }));
  }, [dispatch, search, cityZip, selectedCuisine, selectedPrice, selectedAmenities]);

  useEffect(() => {
    fetchRestaurants(1);
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRestaurants(1);
  };

  const handleAiClick = () => {
    if (!user) {
      toast('Please log in or create an account to use the AI Assistant ✨', {
        icon: '🔒',
        duration: 3000,
        position: 'bottom-center',
      });
      return;
    }
    setSearchMode('ai');
    window.dispatchEvent(new CustomEvent('open-chatbot'));
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

        .explore-root {
          font-family: 'DM Sans', sans-serif;
          min-height: 100vh;
          background: #faf9f7;
        }

        .hero {
          position: relative;
          background: #c0392b;
          overflow: hidden;
          padding: 32px 24px 48px;
        }

        .hero::before {
          content: '';
          position: absolute;
          inset: 0;
          background:
            radial-gradient(ellipse 70% 60% at 20% 40%, rgba(255,120,60,0.35) 0%, transparent 70%),
            radial-gradient(ellipse 50% 50% at 80% 20%, rgba(180,20,10,0.45) 0%, transparent 60%),
            linear-gradient(160deg, #d44535 0%, #b03020 60%, #8b1a0e 100%);
          pointer-events: none;
        }

        .hero::after {
          content: '';
          position: absolute;
          inset: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
          background-size: 200px 200px;
          opacity: 0.4;
          pointer-events: none;
        }

        .hero-inner {
          position: relative;
          z-index: 1;
          max-width: 860px;
          margin: 0 auto;
          text-align: center;
        }

        .hero-title {
          font-family: 'Playfair Display', serif;
          font-size: clamp(24px, 4vw, 40px);
          font-weight: 800;
          color: #fff;
          line-height: 1.1;
          letter-spacing: -0.02em;
          margin: 0 0 8px;
        }

        .hero-title em { font-style: italic; color: #ffcbbf; }

        .hero-sub {
          color: rgba(255,255,255,0.72);
          font-size: 14px;
          margin: 0 0 18px;
          line-height: 1.5;
        }

        .mode-toggle {
          display: inline-flex;
          background: rgba(0,0,0,0.25);
          border-radius: 100px;
          padding: 4px;
          gap: 4px;
          margin-bottom: 20px;
        }

        .mode-btn {
          padding: 9px 22px;
          border-radius: 100px;
          border: none;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          color: rgba(255,255,255,0.75);
          background: transparent;
        }

        .mode-btn.active {
          background: #fff;
          color: #c0392b;
          box-shadow: 0 2px 12px rgba(0,0,0,0.2);
        }

        .mode-btn:not(.active):hover {
          color: #fff;
          background: rgba(255,255,255,0.12);
        }

        .search-card {
          background: #fff;
          border-radius: 18px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.22), 0 4px 16px rgba(0,0,0,0.12);
          display: flex;
          align-items: center;
          overflow: hidden;
          border: 1px solid rgba(255,255,255,0.9);
        }

        .search-input {
          flex: 1;
          padding: 14px 18px;
          font-family: 'DM Sans', sans-serif;
          font-size: 15px;
          color: #1a1a1a;
          border: none;
          outline: none;
          background: transparent;
        }

        .search-input::placeholder { color: #aaa; }

        .search-divider { width: 1px; height: 28px; background: #e5e5e5; flex-shrink: 0; }

        .search-btn {
          background: linear-gradient(135deg, #d44535, #b03020);
          color: #fff;
          border: none;
          padding: 14px 28px;
          font-family: 'DM Sans', sans-serif;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.15s;
          letter-spacing: 0.02em;
          white-space: nowrap;
        }

        .search-btn:hover { opacity: 0.88; }

        .wave { display: block; width: 100%; margin-top: -2px; }

        .results-section { max-width: 1200px; margin: 0 auto; padding: 20px 24px 60px; }

        .results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px; }

        .results-count { font-size: 14px; color: #888; font-weight: 500; }
        .results-count strong { color: #1a1a1a; font-weight: 700; }

        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }

        .skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }

        .skeleton-card { border-radius: 16px; overflow: hidden; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }

        .skeleton-img {
          height: 200px;
          background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
          background-size: 400% 100%;
          animation: shimmer 1.4s infinite;
        }

        .skeleton-body { padding: 16px; }

        .skeleton-line {
          height: 14px;
          border-radius: 8px;
          background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
          background-size: 400% 100%;
          animation: shimmer 1.4s infinite;
          margin-bottom: 10px;
        }

        .skeleton-line.short { width: 60%; }

        @keyframes shimmer {
          0% { background-position: 100% 0; }
          100% { background-position: -100% 0; }
        }

        .pagination { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 48px; flex-wrap: wrap; }

        .page-btn {
          min-width: 38px;
          height: 38px;
          padding: 0 10px;
          border-radius: 10px;
          border: 1.5px solid #e5e0d8;
          background: #fff;
          color: #444;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .page-btn:hover:not(:disabled) { border-color: #c0392b; color: #c0392b; background: #fff5f4; }
        .page-btn.active { background: #c0392b; border-color: #c0392b; color: #fff; box-shadow: 0 2px 8px rgba(192,57,43,0.35); }
        .page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
        .page-ellipsis { color: #aaa; font-size: 16px; padding: 0 2px; user-select: none; }

        @media (max-width: 600px) {
          .search-card { flex-direction: column; border-radius: 14px; }
          .search-input { width: 100%; border-bottom: 1px solid #eee; }
          .search-divider { display: none; }
          .search-btn { width: 100%; padding: 16px; }
          .filters-row { flex-direction: column; align-items: stretch; }
          .price-filters, .amenity-filters { justify-content: center; }
        }

        .filters-row {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 24px;
          flex-wrap: wrap;
          justify-content: center;
        }

        .filter-select {
          background: rgba(255,255,255,0.15);
          border: 1.5px solid rgba(255,255,255,0.3);
          border-radius: 10px;
          padding: 8px 16px;
          color: #fff;
          font-family: 'DM Sans', sans-serif;
          font-size: 14px;
          outline: none;
          cursor: pointer;
          transition: all 0.2s;
        }

        .filter-select option { color: #333; }
        .filter-select:hover { background: rgba(255,255,255,0.25); }

        .price-filters, .amenity-filters { display: flex; gap: 8px; flex-wrap: wrap; }

        .price-btn, .amenity-btn {
          background: rgba(255,255,255,0.1);
          border: 1.5px solid rgba(255,255,255,0.2);
          border-radius: 10px;
          padding: 8px 14px;
          color: #fff;
          font-family: 'DM Sans', sans-serif;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .price-btn:hover, .amenity-btn:hover { background: rgba(255,255,255,0.2); }
        .price-btn.active, .amenity-btn.active {
          background: #fff;
          color: #c0392b;
          border-color: #fff;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
      `}</style>

      <div className="explore-root">
        <div className="hero">
          <div className="hero-inner">
            <h1 className="hero-title">
              Discover your next <em>favourite</em> restaurant
            </h1>

            <p className="hero-sub">
              Search by name, cuisine, keywords, city or zip code
            </p>

            <div className="mode-toggle">
              <button
                className={`mode-btn ${searchMode === 'standard' ? 'active' : ''}`}
                onClick={() => { setSearchMode('standard'); fetchRestaurants(1); }}
              >
                Standard Search
              </button>
              <button
                className={`mode-btn ${searchMode === 'ai' ? 'active' : ''}`}
                onClick={handleAiClick}
              >
                ✨ Ask AI Assistant
              </button>
            </div>

            <form onSubmit={handleSearchSubmit}>
              <div className="search-card">
                <input
                  className="search-input"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="🔍  Name, cuisine, or keyword…"
                />
                <div className="search-divider" />
                <input
                  className="search-input"
                  style={{ maxWidth: 200 }}
                  value={cityZip}
                  onChange={(e) => setCityZip(e.target.value)}
                  placeholder="📍  City or zip"
                />
                <button type="submit" className="search-btn">Search</button>
              </div>
            </form>

            <div className="filters-row">
              <select
                className="filter-select"
                value={selectedCuisine}
                onChange={(e) => { setSelectedCuisine(e.target.value); fetchRestaurants(1); }}
              >
                <option value="">All Cuisines</option>
                <option value="American">American</option>
                <option value="Chinese">Chinese</option>
                <option value="Indian">Indian</option>
                <option value="Italian">Italian</option>
                <option value="Japanese">Japanese</option>
                <option value="Mexican">Mexican</option>
                <option value="Pizza">Pizza</option>
                <option value="Seafood">Seafood</option>
                <option value="Thai">Thai</option>
                <option value="Steakhouse">Steakhouse</option>
              </select>

              <div className="price-filters">
                {['1', '2', '3', '4'].map(tier => (
                  <button
                    key={tier}
                    className={`price-btn ${selectedPrice === tier ? 'active' : ''}`}
                    onClick={() => {
                      const next = selectedPrice === tier ? '' : tier;
                      setSelectedPrice(next);
                      fetchRestaurants(1);
                    }}
                  >
                    {'$'.repeat(parseInt(tier))}
                  </button>
                ))}
              </div>

              <div className="amenity-filters">
                {['Free Wi-Fi', 'Outdoor Seating', 'Dine-in', 'Takeout'].map(amenity => (
                  <button
                    key={amenity}
                    className={`amenity-btn ${selectedAmenities.includes(amenity) ? 'active' : ''}`}
                    onClick={() => {
                      const next = selectedAmenities.includes(amenity)
                        ? selectedAmenities.filter(a => a !== amenity)
                        : [...selectedAmenities, amenity];
                      setSelectedAmenities(next);
                      fetchRestaurants(1);
                    }}
                  >
                    {amenity}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <svg className="wave" viewBox="0 0 1440 40" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ background: '#b03020' }}>
          <path d="M0 40 C360 0 1080 0 1440 40 L1440 40 L0 40 Z" fill="#faf9f7"/>
        </svg>

        <div className="results-section">
          <div className="results-header">
            <p className="results-count">
              Found <strong>{total}</strong> restaurants
              {totalPages > 1 && (
                <span> — page <strong>{page}</strong> of <strong>{totalPages}</strong></span>
              )}
            </p>
          </div>

          {loading ? (
            <div className="skeleton-grid">
              {Array.from({ length: 6 }).map((_, i) => (
                <div className="skeleton-card" key={i}>
                  <div className="skeleton-img" style={{ animationDelay: `${i * 0.1}s` }} />
                  <div className="skeleton-body">
                    <div className="skeleton-line" style={{ animationDelay: `${i * 0.1 + 0.1}s` }} />
                    <div className="skeleton-line short" style={{ animationDelay: `${i * 0.1 + 0.2}s` }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <div className="results-grid">
                {restaurants.map(r => (
                  <RestaurantCard key={r.id} restaurant={r} />
                ))}
              </div>
              <Pagination
                page={page}
                totalPages={totalPages}
                onPageChange={(p) => fetchRestaurants(p)}
              />
            </>
          )}
        </div>
      </div>
    </>
  );
}