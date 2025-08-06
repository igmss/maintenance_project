const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('admin_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('admin_token', token);
    } else {
      localStorage.removeItem('admin_token');
    }
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'API request failed');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentication
  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  async logout() {
    this.setToken(null);
  }

  // Dashboard Stats
  async getDashboardStats() {
    return this.request('/admin/dashboard/stats');
  }

  // User Management
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/users${queryString ? `?${queryString}` : ''}`);
  }

  async getUserById(id) {
    return this.request(`/admin/users/${id}`);
  }

  async updateUser(id, data) {
    return this.request(`/admin/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteUser(id) {
    return this.request(`/admin/users/${id}`, {
      method: 'DELETE',
    });
  }

  // Service Provider Management
  async getProviders(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/providers${queryString ? `?${queryString}` : ''}`);
  }

  async getProviderById(id) {
    return this.request(`/admin/providers/${id}`);
  }

  async verifyProvider(id, data) {
    return this.request(`/admin/providers/${id}/verify`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async rejectProvider(id, data) {
    return this.request(`/admin/providers/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Booking Management
  async getBookings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/bookings${queryString ? `?${queryString}` : ''}`);
  }

  async getBookingById(id) {
    return this.request(`/admin/bookings/${id}`);
  }

  async updateBookingStatus(id, status) {
    return this.request(`/admin/bookings/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  }

  // Service Management
  async getServices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/services${queryString ? `?${queryString}` : ''}`);
  }

  async createService(data) {
    return this.request('/admin/services', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateService(id, data) {
    return this.request(`/admin/services/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteService(id) {
    return this.request(`/admin/services/${id}`, {
      method: 'DELETE',
    });
  }

  // Analytics
  async getAnalytics(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/analytics${queryString ? `?${queryString}` : ''}`);
  }

  // Reports
  async getReports(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/reports${queryString ? `?${queryString}` : ''}`);
  }

  async exportReport(type, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/reports/export/${type}${queryString ? `?${queryString}` : ''}`);
  }

  // System Settings
  async getSettings() {
    return this.request('/admin/settings');
  }

  async updateSettings(data) {
    return this.request('/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Notifications
  async getNotifications(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/notifications${queryString ? `?${queryString}` : ''}`);
  }

  async sendNotification(data) {
    return this.request('/admin/notifications/send', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Financial Management
  async getTransactions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/transactions${queryString ? `?${queryString}` : ''}`);
  }

  async getRevenue(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/revenue${queryString ? `?${queryString}` : ''}`);
  }

  async getPayouts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/payouts${queryString ? `?${queryString}` : ''}`);
  }

  async processPayouts(data) {
    return this.request('/admin/payouts/process', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();
export default apiClient;

