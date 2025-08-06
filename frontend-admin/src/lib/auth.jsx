import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from './api';

export const AUTH_STORAGE_KEY = 'admin_token';
export const USER_STORAGE_KEY = 'admin_user';

class AuthService {
  constructor() {
    this.token = localStorage.getItem(AUTH_STORAGE_KEY);
    this.user = JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || 'null');
  }

  async login(credentials) {
    try {
      // Real backend authentication for admin
      const response = await apiClient.login({
        email_or_phone: credentials.email,  // Send correct parameter name
        password: credentials.password
      });
      
      // Check if user is admin
      if (response.user && response.user.user_type === 'admin') {
        this.setAuth(response.access_token, response.user);
        return { success: true, user: response.user };
      } else {
        return { success: false, error: 'Access denied. Admin privileges required.' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message || 'Login failed' };
    }
  }

  async logout() {
    this.clearAuth();
  }

  setAuth(token, user) {
    this.token = token;
    this.user = user;
    
    localStorage.setItem(AUTH_STORAGE_KEY, token);
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    
    apiClient.setToken(token);
  }

  clearAuth() {
    this.token = null;
    this.user = null;
    
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    
    apiClient.setToken(null);
  }

  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  getUser() {
    return this.user;
  }

  getToken() {
    return this.token;
  }
}

export const authService = new AuthService();

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authService.getUser());
  const [loading, setLoading] = useState(false);

  const login = async (credentials) => {
    setLoading(true);
    const result = await authService.login(credentials);
    
    if (result.success) {
      setUser(result.user);
    }
    
    setLoading(false);
    return result;
  };

  const logout = async () => {
    setLoading(true);
    await authService.logout();
    setUser(null);
    setLoading(false);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: authService.isAuthenticated(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default authService;

