// API Configuration (aligned with web frontend)
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://maintenance-platform-backend.onrender.com/api',
  ); // Development
  
  static const String prodBaseUrl = String.fromEnvironment(
    'API_PROD_BASE_URL',
    defaultValue: 'https://maintenance-platform-backend.onrender.com/api',
  ); // Production
  
  // Use production URL in release mode
  static String get apiBaseUrl {
    const bool isProduction = bool.fromEnvironment('dart.vm.product');
    return isProduction ? prodBaseUrl : baseUrl;
  }
}

// App Configuration
class AppConfig {
  static const String appName = String.fromEnvironment(
    'APP_NAME',
    defaultValue: 'Maintenance Platform',
  );
  
  static const String appVersion = String.fromEnvironment(
    'APP_VERSION',
    defaultValue: '1.0.0',
  );
  
  static const String supportEmail = String.fromEnvironment(
    'SUPPORT_EMAIL',
    defaultValue: 'support@maintenanceplatform.com',
  );
  
  static const String supportPhone = String.fromEnvironment(
    'SUPPORT_PHONE',
    defaultValue: '+20-XXX-XXX-XXXX',
  );
  
  // Feature Flags
  static const bool enableAnalytics = bool.fromEnvironment(
    'ENABLE_ANALYTICS',
    defaultValue: true,
  );
  
  static const bool enableCrashReporting = bool.fromEnvironment(
    'ENABLE_CRASH_REPORTING',
    defaultValue: true,
  );
  
  static const bool enableLocationTracking = bool.fromEnvironment(
    'ENABLE_LOCATION_TRACKING',
    defaultValue: true,
  );
  
  static const bool enablePushNotifications = bool.fromEnvironment(
    'ENABLE_PUSH_NOTIFICATIONS',
    defaultValue: true,
  );
  
  // Google Maps API Key
  static const String googleMapsApiKey = String.fromEnvironment(
    'GOOGLE_MAPS_API_KEY',
    defaultValue: 'your_google_maps_api_key_here',
  );
  
  // Payment Configuration
  static const String stripePublishableKey = String.fromEnvironment(
    'STRIPE_PUBLISHABLE_KEY',
    defaultValue: 'pk_test_your_stripe_key',
  );
  
  static const String fawryMerchantCode = String.fromEnvironment(
    'FAWRY_MERCHANT_CODE',
    defaultValue: 'your_fawry_merchant_code',
  );
}

// Environment Configuration
enum Environment { development, staging, production }

class EnvironmentConfig {
  static const Environment currentEnvironment = Environment.development;
  
  static bool get isDevelopment => currentEnvironment == Environment.development;
  static bool get isStaging => currentEnvironment == Environment.staging;
  static bool get isProduction => currentEnvironment == Environment.production;
  
  static String get environmentName {
    switch (currentEnvironment) {
      case Environment.development:
        return 'Development';
      case Environment.staging:
        return 'Staging';
      case Environment.production:
        return 'Production';
    }
  }
}

