import 'dart:async';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'api_service.dart';

class LiveLocationService {
  static final LiveLocationService _instance = LiveLocationService._internal();
  factory LiveLocationService() => _instance;
  LiveLocationService._internal();

  StreamSubscription<Position>? _locationSubscription;
  bool _isTracking = false;
  bool _isOnline = false;

  /// Check and request location permissions
  Future<bool> requestLocationPermission() async {
    // Check if location services are enabled
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('خدمة تحديد المواقع غير مُفعلة. يرجى تفعيلها من الإعدادات.');
    }

    // Check location permission
    LocationPermission permission = await Geolocator.checkPermission();
    
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('تم رفض صلاحية الموقع. يرجى السماح بالوصول للموقع للمتابعة.');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception('تم رفض صلاحية الموقع نهائياً. يرجى تفعيلها من إعدادات التطبيق.');
    }

    return true;
  }

  /// Get current location
  Future<Position> getCurrentLocation() async {
    await requestLocationPermission();
    
    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
      timeLimit: Duration(seconds: 10),
    );
  }

  /// Start live location tracking
  Future<void> startLocationTracking() async {
    if (_isTracking) return;

    await requestLocationPermission();

    const LocationSettings locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // Update every 10 meters
    );

    _locationSubscription = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(
      (Position position) async {
        if (_isOnline) {
          try {
            await _updateLiveLocation(position);
          } catch (e) {
            print('Failed to update live location: $e');
          }
        }
      },
      onError: (error) {
        print('Location tracking error: $error');
      },
    );

    _isTracking = true;
  }

  /// Stop live location tracking
  Future<void> stopLocationTracking() async {
    await _locationSubscription?.cancel();
    _locationSubscription = null;
    _isTracking = false;
  }

  /// Go online with live location
  Future<void> goOnline() async {
    try {
      // Get current location
      Position position = await getCurrentLocation();

      // Update online status with location
      await ApiService().updateOnlineStatus(
        isOnline: true,
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        heading: position.heading,
        speed: position.speed,
      );

      _isOnline = true;

      // Start continuous location tracking
      await startLocationTracking();

    } catch (e) {
      throw Exception('فشل في التشغيل: $e');
    }
  }

  /// Go offline and stop location sharing
  Future<void> goOffline() async {
    try {
      // Update online status to offline
      await ApiService().updateOnlineStatus(isOnline: false);

      _isOnline = false;

      // Stop location tracking
      await stopLocationTracking();

    } catch (e) {
      throw Exception('فشل في إيقاف التشغيل: $e');
    }
  }

  /// Update live location on server
  Future<void> _updateLiveLocation(Position position) async {
    await ApiService().updateLiveLocation(
      latitude: position.latitude,
      longitude: position.longitude,
      accuracy: position.accuracy,
      heading: position.heading,
      speed: position.speed,
    );
  }

  /// Check if currently tracking location
  bool get isTracking => _isTracking;

  /// Check if provider is online
  bool get isOnline => _isOnline;

  /// Get location permission status
  Future<String> getLocationPermissionStatus() async {
    LocationPermission permission = await Geolocator.checkPermission();
    
    switch (permission) {
      case LocationPermission.always:
      case LocationPermission.whileInUse:
        return 'granted';
      case LocationPermission.denied:
        return 'denied';
      case LocationPermission.deniedForever:
        return 'permanently_denied';
      case LocationPermission.unableToDetermine:
        return 'unknown';
    }
  }

  /// Show location permission education dialog
  static String getLocationEducationMessage() {
    return '''
🌍 مشاركة الموقع المباشر

عند تفعيل الخدمة، سيتم:
• مشاركة موقعك المباشر مع العملاء القريبين
• تحديث موقعك تلقائياً أثناء التنقل
• إيقاف المشاركة عند إيقاف الخدمة

🔒 خصوصيتك محمية:
• يتم مشاركة الموقع فقط مع العملاء عند طلب الخدمة
• لا يتم حفظ مسار تنقلك
• يمكنك إيقاف المشاركة في أي وقت
''';
  }
}