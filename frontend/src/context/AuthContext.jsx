import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const savedUser = localStorage.getItem('user');
      const savedToken = localStorage.getItem('token');

      const isValidUser = savedUser && savedUser !== 'undefined' && savedUser !== 'null';
      const isValidToken = savedToken && savedToken !== 'undefined' && savedToken !== 'null';

      if (isValidUser && isValidToken) {
        const parsedUser = JSON.parse(savedUser);
        setUser(parsedUser);
        setToken(savedToken);

        // Refresh full profile from API to get latest data including profile_picture
        api.get(`/users/${parsedUser.id}`)
          .then(({ data }) => {
            const merged = { ...parsedUser, ...data };
            localStorage.setItem('user', JSON.stringify(merged));
            setUser(merged);
          })
          .catch(() => {});
      } else {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    } catch (e) {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
    setLoading(false);
  }, []);

  const login = async (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    setToken(token);

    // Fetch full profile immediately after login to get profile_picture etc.
    try {
      const { data } = await api.get(`/users/${userData.id}`);
      const merged = { ...userData, ...data };
      localStorage.setItem('user', JSON.stringify(merged));
      setUser(merged);
    } catch (e) {}
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setToken(null);
  };

  const updateUser = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);