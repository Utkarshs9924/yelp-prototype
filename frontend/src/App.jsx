import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import ChatBot from './components/ChatBot';
import ProtectedRoute from './components/ProtectedRoute';
import Explore from './pages/restaurant/Explore';
import RestaurantDetail from './pages/restaurant/RestaurantDetail';
import AddRestaurant from './pages/restaurant/AddRestaurant';
import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';
import Profile from './pages/user/Profile';
import Preferences from './pages/user/Preferences';
import Favourites from './pages/user/Favourites';
import History from './pages/user/History';
import OwnerDashboard from './pages/owner/OwnerDashboard';
import ManageRestaurant from './pages/owner/ManageRestaurant';
import OwnerReviews from './pages/owner/OwnerReviews';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Toaster position="top-right" />
      <main>
        <Routes>
          <Route path="/" element={<Explore />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/restaurants/:restaurant_id" element={<RestaurantDetail />} />
          <Route path="/restaurants/add" element={<ProtectedRoute><AddRestaurant /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/preferences" element={<ProtectedRoute><Preferences /></ProtectedRoute>} />
          <Route path="/favourites" element={<ProtectedRoute><Favourites /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
          <Route path="/owner/dashboard" element={<ProtectedRoute><OwnerDashboard /></ProtectedRoute>} />
          <Route path="/owner/restaurants" element={<ProtectedRoute><ManageRestaurant /></ProtectedRoute>} />
          <Route path="/owner/reviews" element={<ProtectedRoute><OwnerReviews /></ProtectedRoute>} />
        </Routes>
      </main>
      <ChatBot />
    </div>
  );
}
