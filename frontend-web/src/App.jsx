import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './lib/auth.jsx';
import { Toaster } from '@/components/ui/sonner';

// Import pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CustomerDashboard from './pages/CustomerDashboard';
import ProviderDashboard from './pages/ProviderDashboard';
import AdminDashboard from './pages/AdminDashboard';
import BookingPage from './pages/BookingPage';
import ProfilePage from './pages/ProfilePage';
import ServicesPage from './pages/ServicesPage';
import BookingsPage from './pages/BookingsPage';
import AddServicePage from './pages/AddServicePage';
import ServiceAreasPage from './pages/ServiceAreasPage';
import VerificationPage from './pages/VerificationPage';

import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children, requiredUserType = null }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredUserType && user?.user_type !== requiredUserType) {
    // Redirect to appropriate dashboard based on user type
    const redirectPath = {
      customer: '/dashboard',
      service_provider: '/provider-dashboard',
      admin: '/admin-dashboard'
    }[user?.user_type] || '/';
    
    return <Navigate to={redirectPath} replace />;
  }

  return children;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    // Redirect to appropriate dashboard based on user type
    const redirectPath = {
      customer: '/dashboard',
      service_provider: '/provider-dashboard',
      admin: '/admin-dashboard'
    }[user?.user_type] || '/dashboard';
    
    return <Navigate to={redirectPath} replace />;
  }

  return children;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } 
      />
      <Route 
        path="/register" 
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        } 
      />

      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute requiredUserType="customer">
            <CustomerDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/provider-dashboard" 
        element={
          <ProtectedRoute requiredUserType="service_provider">
            <ProviderDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/admin-dashboard" 
        element={
          <ProtectedRoute requiredUserType="admin">
            <AdminDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/booking/:serviceId" 
        element={
          <ProtectedRoute requiredUserType="customer">
            <BookingPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/profile" 
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } 
      />

      {/* Customer Routes */}
      <Route 
        path="/services" 
        element={
          <ProtectedRoute requiredUserType="customer">
            <ServicesPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/bookings" 
        element={
          <ProtectedRoute>
            <BookingsPage />
          </ProtectedRoute>
        } 
      />

      {/* Provider Routes */}
      <Route 
        path="/services/add" 
        element={
          <ProtectedRoute requiredUserType="service_provider">
            <AddServicePage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/service-areas" 
        element={
          <ProtectedRoute requiredUserType="service_provider">
            <ServiceAreasPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/verification" 
        element={
          <ProtectedRoute requiredUserType="service_provider">
            <VerificationPage />
          </ProtectedRoute>
        } 
      />

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-background">
          <AppRoutes />
          <Toaster position="top-right" />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

