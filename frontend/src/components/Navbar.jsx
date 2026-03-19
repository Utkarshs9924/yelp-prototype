import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  FaUser,
  FaHeart,
  FaBars,
  FaTimes,
  FaChevronDown,
  FaCompass,
  FaPlus,
  FaHistory,
  FaCog,
  FaChartLine,
} from 'react-icons/fa';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const isOwner = user?.role === 'owner';

  const handleLogout = () => {
    logout();
    setProfileOpen(false);
    setMobileOpen(false);
    navigate('/');
  };

  const navLinkClass = ({ isActive }) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive ? 'bg-red-700 text-white' : 'text-white hover:bg-red-600'
    }`;

  return (
    <nav className="bg-red-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-bold text-xl">
            <span className="text-white">YelpClone</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-2">
            <NavLink to="/explore" className={navLinkClass}>
              <span className="flex items-center gap-2">
                <FaCompass className="text-sm" /> Explore
              </span>
            </NavLink>
            <NavLink to="/restaurants/add" className={navLinkClass}>
              <span className="flex items-center gap-2">
                <FaPlus className="text-sm" /> Add Restaurant
              </span>
            </NavLink>
            {isOwner && (
              <NavLink to="/owner/dashboard" className={navLinkClass}>
                <span className="flex items-center gap-2">
                  <FaChartLine className="text-sm" /> Owner Dashboard
                </span>
              </NavLink>
            )}

            {user ? (
              <div className="relative ml-2">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-red-700 transition-colors"
                >
                  <FaUser className="text-sm" />
                  <span className="text-sm font-medium">{user.name || user.email}</span>
                  <FaChevronDown className={`text-xs transition-transform ${profileOpen ? 'rotate-180' : ''}`} />
                </button>
                {profileOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setProfileOpen(false)}
                      aria-hidden="true"
                    />
                    <div className="absolute right-0 mt-1 w-48 py-1 bg-white rounded-lg shadow-xl z-20 text-gray-900">
                      <Link
                        to="/profile"
                        onClick={() => setProfileOpen(false)}
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        <span className="flex items-center gap-2">
                          <FaUser /> Profile
                        </span>
                      </Link>
                      <Link
                        to="/preferences"
                        onClick={() => setProfileOpen(false)}
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        <span className="flex items-center gap-2">
                          <FaCog /> Preferences
                        </span>
                      </Link>
                      <Link
                        to="/favourites"
                        onClick={() => setProfileOpen(false)}
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        <span className="flex items-center gap-2">
                          <FaHeart /> Favourites
                        </span>
                      </Link>
                      <Link
                        to="/history"
                        onClick={() => setProfileOpen(false)}
                        className="block px-4 py-2 text-sm hover:bg-gray-100"
                      >
                        <span className="flex items-center gap-2">
                          <FaHistory /> History
                        </span>
                      </Link>
                      <hr className="my-1 border-gray-200" />
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                      >
                        Logout
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2 ml-2">
                <Link
                  to="/login"
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-3 py-2 rounded-md text-sm font-medium bg-white text-red-600 hover:bg-gray-100 transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-md hover:bg-red-700"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-red-500">
            <div className="flex flex-col gap-1">
              <NavLink
                to="/explore"
                onClick={() => setMobileOpen(false)}
                className={navLinkClass}
              >
                <span className="flex items-center gap-2">
                  <FaCompass /> Explore
                </span>
              </NavLink>
              <NavLink
                to="/restaurants/add"
                onClick={() => setMobileOpen(false)}
                className={navLinkClass}
              >
                <span className="flex items-center gap-2">
                  <FaPlus /> Add Restaurant
                </span>
              </NavLink>
              {isOwner && (
                <NavLink
                  to="/owner/dashboard"
                  onClick={() => setMobileOpen(false)}
                  className={navLinkClass}
                >
                  <span className="flex items-center gap-2">
                    <FaChartLine /> Owner Dashboard
                  </span>
                </NavLink>
              )}
              {user ? (
                <>
                  <Link
                    to="/profile"
                    onClick={() => setMobileOpen(false)}
                    className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700 flex items-center gap-2"
                  >
                    <FaUser /> Profile
                  </Link>
                  <Link
                    to="/preferences"
                    onClick={() => setMobileOpen(false)}
                    className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700 flex items-center gap-2"
                  >
                    <FaCog /> Preferences
                  </Link>
                  <Link
                    to="/favourites"
                    onClick={() => setMobileOpen(false)}
                    className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700 flex items-center gap-2"
                  >
                    <FaHeart /> Favourites
                  </Link>
                  <Link
                    to="/history"
                    onClick={() => setMobileOpen(false)}
                    className="px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700 flex items-center gap-2"
                  >
                    <FaHistory /> History
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="text-left px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-red-700"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <div className="flex gap-2 pt-2">
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="flex-1 px-3 py-2 rounded-md text-sm font-medium text-center text-white hover:bg-red-700 border border-white/50"
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    onClick={() => setMobileOpen(false)}
                    className="flex-1 px-3 py-2 rounded-md text-sm font-medium text-center bg-white text-red-600 hover:bg-gray-100"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
