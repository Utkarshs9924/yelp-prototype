import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <main>
        <Routes>
          <Route path="/" element={<div className="text-center py-20 text-2xl">Yelp Prototype - Coming Soon</div>} />
        </Routes>
      </main>
    </div>
  );
}
