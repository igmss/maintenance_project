// API client for maintenance platform backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://maintenance-platform-backend.onrender.com/api';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  getToken() {
    return this.token || localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    const config = {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    // Handle FormData for file uploads
    if (options.isFormData && config.body instanceof FormData) {
      // Don't set Content-Type for FormData - browser will set it automatically with boundary
      // Don't stringify FormData
    } else {
      // Set JSON content type for regular requests
      config.headers['Content-Type'] = 'application/json';
      
      if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
      }
    }

    try {
      const response = await fetch(url, config);
      
      // Handle token expiration
      if (response.status === 401) {
        this.setToken(null);
        window.location.href = '/login';
        return;
      }

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Non-JSON response:', text);
        throw new Error(`Server returned non-JSON response: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Expose baseURL for building absolute links when backend returns relative paths
  get baseURLWithoutApi() {
    return this.baseURL.replace(/\/api$/, '');
  }

  // Authentication endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: userData,
    });
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: credentials,
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  async logout() {
    this.setToken(null);
    localStorage.clear();
  }

  async getProfile() {
    return this.request('/auth/profile');
  }

  async updateProfile(profileData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: profileData,
    });
  }

  async changePassword(passwordData) {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: passwordData,
    });
  }

  // Service endpoints
  async getServiceCategories(language = 'en') {
    return this.request(`/services/categories?lang=${language}`);
  }

  async getCategoryServices(categoryId, language = 'en') {
    return this.request(`/services/categories/${categoryId}/services?lang=${language}`);
  }

  async getService(serviceId, language = 'en') {
    return this.request(`/services/${serviceId}?lang=${language}`);
  }

  async searchProviders(searchData) {
    return this.request('/services/search', {
      method: 'POST',
      body: searchData,
    });
  }

  async createBooking(bookingData) {
    return this.request('/services/bookings', {
      method: 'POST',
      body: bookingData,
    });
  }

  async getBookings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/services/bookings${queryString ? `?${queryString}` : ''}`);
  }

  async getBooking(bookingId) {
    return this.request(`/services/bookings/${bookingId}`);
  }

  async updateBookingStatus(bookingId, statusData) {
    return this.request(`/services/bookings/${bookingId}/status`, {
      method: 'PUT',
      body: statusData,
    });
  }

  async createReview(bookingId, reviewData) {
    return this.request(`/services/bookings/${bookingId}/review`, {
      method: 'POST',
      body: reviewData,
    });
  }

  // Provider endpoints
  async getProviderProfile() {
    return this.request('/providers/profile');
  }

  // Customer location APIs
  async updateCustomerLocation(locationData) {
    return this.request('/customers/location', {
      method: 'POST',
      body: locationData,
    });
  }

  async getCustomerLocation() {
    return this.request('/customers/location');
  }

  async getNearbyProviders(searchData) {
    return this.request('/customers/nearby-providers', {
      method: 'POST',
      body: searchData,
    });
  }

  async getPublicProviderProfile(providerId) {
    return this.request(`/providers/${providerId}`);
  }

  async addProviderService(serviceData) {
    return this.request('/providers/services', {
      method: 'POST',
      body: serviceData,
    });
  }

  async updateProviderService(serviceId, serviceData) {
    return this.request(`/providers/services/${serviceId}`, {
      method: 'PUT',
      body: serviceData,
    });
  }

  async updateLocation(locationData) {
    return this.request('/providers/location', {
      method: 'POST',
      body: locationData,
    });
  }

  // Get online providers near customer location
  async getOnlineProviders(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.latitude) queryParams.append('latitude', params.latitude);
    if (params.longitude) queryParams.append('longitude', params.longitude);
    if (params.radius) queryParams.append('radius', params.radius);
    if (params.service_id) queryParams.append('service_id', params.service_id);
    
    return this.request(`/providers/online?${queryParams}`);
  }

    // Update provider online status with live location
  async updateOnlineStatus(isOnline, location = null) {
    const body = { is_online: isOnline };
    
    if (isOnline && location) {
      body.latitude = location.latitude;
      body.longitude = location.longitude;
      body.accuracy = location.accuracy;
      body.heading = location.heading;
      body.speed = location.speed;
    }

    return this.request('/providers/status', {
      method: 'POST',
      body: body,
    });
  }

  // Update live location while online (continuous tracking)
  async updateLiveLocation(location) {
    return this.request('/providers/live-location', {
      method: 'POST',
      body: {
        latitude: location.latitude,
        longitude: location.longitude,
        accuracy: location.accuracy,
        heading: location.heading,
        speed: location.speed
      }
    });
  }

  async updateAvailability(availabilityData) {
    return this.request('/providers/availability', {
      method: 'PUT',
      body: availabilityData,
    });
  }

  // Service area methods removed - now using live location instead

  async uploadDocument(documentData) {
    return this.request('/providers/documents', {
      method: 'POST',
      body: documentData,
    });
  }

  // Admin endpoints
  async getDashboardStats() {
    return this.request('/admin/dashboard/stats');
  }

  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/users${queryString ? `?${queryString}` : ''}`);
  }

  async updateUserStatus(userId, statusData) {
    return this.request(`/admin/users/${userId}/status`, {
      method: 'PUT',
      body: statusData,
    });
  }

  async getProviders(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/providers${queryString ? `?${queryString}` : ''}`);
  }

  async updateProviderVerification(providerId, data) {
    return this.request(`/admin/providers/${providerId}/verification`, {
      method: 'PUT',
      body: data,
    });
  }

  async getAdminServices(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/services${queryString ? `?${queryString}` : ''}`);
  }

  async createAdminService(data) {
    return this.request('/admin/services', {
      method: 'POST',
      body: data,
    });
  }

  async updateAdminService(id, data) {
    return this.request(`/admin/services/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async getAnalytics(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/analytics${queryString ? `?${queryString}` : ''}`);
  }

  async getAllBookings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/admin/bookings${queryString ? `?${queryString}` : ''}`);
  }

  async createServiceCategory(categoryData) {
    return this.request('/admin/services/categories', {
      method: 'POST',
      body: categoryData,
    });
  }

  async getRevenueAnalytics(days = 30) {
    return this.request(`/admin/analytics/revenue?days=${days}`);
  }

  async getSystemSettings() {
    return this.request('/admin/system/settings');
  }

  // Document verification methods
  async uploadProviderDocument(formData) {
    return this.request('/providers/documents/upload', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
  }

  async getVerificationQueue(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/providers/verification-queue${queryString ? `?${queryString}` : ''}`);
  }

  async verifyProvider(providerId, action, reason = null) {
    return this.request(`/providers/${providerId}/verify`, {
      method: 'POST',
      body: { action, reason }
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();
export default apiClient;

