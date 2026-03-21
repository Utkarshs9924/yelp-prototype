import { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function AdminDashboard() {
  const [pendingOwners, setPendingOwners] = useState([]);
  const [pendingRestaurants, setPendingRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [ownersRes, restRes] = await Promise.all([
        adminAPI.getPendingOwners(),
        adminAPI.getPendingRestaurants()
      ]);
      setPendingOwners(ownersRes.data);
      setPendingRestaurants(restRes.data);
    } catch (err) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const approveOwner = async (id) => {
    try {
      await adminAPI.approveOwner(id);
      toast.success('Owner approved');
      fetchData();
    } catch (err) {
      toast.error('Failed to approve owner');
    }
  };

  const updateRestaurantStatus = async (id, status) => {
    try {
      await adminAPI.updateRestaurantStatus(id, status);
      toast.success(`Restaurant ${status}`);
      fetchData();
    } catch (err) {
      toast.error('Failed to update restaurant');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-900">Admin Control Panel</h1>
      
      <div className="mb-12">
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Pending Owner Approvals</h2>
        {pendingOwners.length === 0 ? (
          <p className="text-gray-500">No pending owners.</p>
        ) : (
          <div className="grid gap-4">
            {pendingOwners.map(owner => (
              <div key={owner.id} className="bg-white p-4 rounded-lg shadow border flex justify-between items-center transition hover:shadow-md">
                <div>
                  <p className="font-bold text-lg text-gray-900">{owner.name}</p>
                  <p className="text-sm text-gray-500">{owner.email}</p>
                  <p className="text-xs text-gray-400 mt-1">Submitted: {new Date(owner.created_at).toLocaleDateString()}</p>
                </div>
                <button 
                  onClick={() => approveOwner(owner.id)} 
                  className="bg-green-600 hover:bg-green-700 transition text-white px-5 py-2.5 rounded-lg shadow-sm font-medium"
                >
                  Approve Profile
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4 border-b pb-2">Pending Restaurant Approvals</h2>
        {pendingRestaurants.length === 0 ? (
          <p className="text-gray-500">No pending restaurants.</p>
        ) : (
          <div className="grid gap-4">
            {pendingRestaurants.map(rest => (
              <div key={rest.id} className="bg-white p-5 rounded-lg shadow border flex justify-between items-center transition hover:shadow-md">
                <div>
                  <p className="font-bold text-xl text-gray-900">{rest.name}</p>
                  <p className="text-sm text-gray-600">{rest.address}, {rest.city}</p>
                  <p className="text-xs text-blue-600 mt-1 font-medium bg-blue-50 w-fit px-2 py-1 rounded">Submitted by Owner ID: {rest.owner_id}</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => updateRestaurantStatus(rest.id, 'approved')} 
                    className="bg-green-600 hover:bg-green-700 transition text-white px-5 py-2 rounded-lg font-medium shadow-sm"
                  >
                    Approve
                  </button>
                  <button 
                    onClick={() => updateRestaurantStatus(rest.id, 'rejected')} 
                    className="bg-red-600 hover:bg-red-700 transition text-white px-5 py-2 rounded-lg font-medium shadow-sm"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
