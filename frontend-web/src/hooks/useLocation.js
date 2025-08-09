import { useState, useEffect, useCallback } from 'react';
import apiClient from '../lib/api';

export const useLocation = () => {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [watching, setWatching] = useState(false);
  const [watchId, setWatchId] = useState(null);

  // Get current position once
  const getCurrentLocation = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const position = await new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error('Geolocation is not supported by this browser'));
          return;
        }

        navigator.geolocation.getCurrentPosition(
          resolve,
          reject,
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000, // 1 minute
          }
        );
      });

      const locationData = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString(),
      };

      setLocation(locationData);
      return locationData;
    } catch (err) {
      const errorMessage = err.code 
        ? getGeolocationErrorMessage(err.code)
        : err.message;
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Start watching position changes
  const startWatching = useCallback(async () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    if (watching) {
      return; // Already watching
    }

    setWatching(true);
    setError(null);

    const id = navigator.geolocation.watchPosition(
      async (position) => {
        const locationData = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date().toISOString(),
        };

        setLocation(locationData);

        // Update customer location on server
        try {
          await apiClient.updateCustomerLocation(locationData);
        } catch (err) {
          console.error('Failed to update customer location:', err);
        }
      },
      (err) => {
        const errorMessage = getGeolocationErrorMessage(err.code);
        setError(errorMessage);
        console.error('Location watch error:', errorMessage);
      },
      {
        enableHighAccuracy: true,
        timeout: 30000,
        maximumAge: 30000, // 30 seconds
      }
    );

    setWatchId(id);
  }, [watching]);

  // Stop watching position changes
  const stopWatching = useCallback(() => {
    if (watchId) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
    }
    setWatching(false);
  }, [watchId]);

  // Share location with server
  const shareLocation = useCallback(async (locationData) => {
    try {
      const response = await apiClient.updateCustomerLocation(locationData || location);
      return response;
    } catch (err) {
      setError('Failed to share location');
      throw err;
    }
  }, [location]);

  // Get nearby providers
  const getNearbyProviders = useCallback(async (serviceId, customLocation = null) => {
    const loc = customLocation || location;
    if (!loc || !serviceId) {
      throw new Error('Location and service ID are required');
    }

    try {
      const response = await apiClient.getNearbyProviders({
        service_id: serviceId,
        latitude: loc.latitude,
        longitude: loc.longitude,
        max_distance_km: 25,
      });
      return response;
    } catch (err) {
      setError('Failed to get nearby providers');
      throw err;
    }
  }, [location]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (watchId) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, [watchId]);

  return {
    location,
    loading,
    error,
    watching,
    getCurrentLocation,
    startWatching,
    stopWatching,
    shareLocation,
    getNearbyProviders,
  };
};

const getGeolocationErrorMessage = (code) => {
  switch (code) {
    case 1:
      return 'تم رفض الوصول إلى الموقع. يرجى السماح بالوصول للموقع في إعدادات المتصفح.';
    case 2:
      return 'الموقع غير متاح. يرجى التحقق من إعدادات GPS.';
    case 3:
      return 'انتهت مهلة الحصول على الموقع. يرجى المحاولة مرة أخرى.';
    default:
      return 'حدث خطأ في الحصول على الموقع.';
  }
};

export default useLocation;