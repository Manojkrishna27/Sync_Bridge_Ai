import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
        } catch (error) {
          console.error("Failed to load user session", error);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    localStorage.setItem('access_token', res.data.access_token);
    const userRes = await api.get('/auth/me');
    setUser(userRes.data);
    return res;
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch(e) {}
    localStorage.removeItem('access_token');
    setUser(null);
  };

  const hasPermission = (permission) => {
    if (!user || !user.role || !user.role.permissions) return false;
    return user.role.permissions.some(p => p.name === permission);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
