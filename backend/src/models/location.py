from src.models import db, generate_uuid
from datetime import datetime

class ProviderLocation(db.Model):
    """Real-time service provider location tracking"""
    __tablename__ = 'provider_locations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    provider_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    accuracy = db.Column(db.Numeric(6, 2))  # GPS accuracy in meters
    heading = db.Column(db.Numeric(5, 2))  # Direction in degrees
    speed = db.Column(db.Numeric(5, 2))  # Speed in km/h
    is_online = db.Column(db.Boolean, default=True)
    battery_level = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'heading': float(self.heading) if self.heading else None,
            'speed': float(self.speed) if self.speed else None,
            'is_online': self.is_online,
            'battery_level': self.battery_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class ProviderServiceArea(db.Model):
    """Service areas where providers are willing to work"""
    __tablename__ = 'provider_service_areas'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)
    area_name = db.Column(db.String(100), nullable=False)
    # For simplicity, we'll store area as center point + radius instead of polygon
    center_latitude = db.Column(db.Numeric(10, 8), nullable=False)
    center_longitude = db.Column(db.Numeric(11, 8), nullable=False)
    radius_km = db.Column(db.Numeric(5, 2), nullable=False)  # Service radius in kilometers
    is_primary_area = db.Column(db.Boolean, default=False)
    travel_time_minutes = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'area_name': self.area_name,
            'center_latitude': float(self.center_latitude),
            'center_longitude': float(self.center_longitude),
            'radius_km': float(self.radius_km),
            'is_primary_area': self.is_primary_area,
            'travel_time_minutes': self.travel_time_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BookingLocation(db.Model):
    """Location tracking for active bookings"""
    __tablename__ = 'booking_locations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'), nullable=False)
    provider_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    accuracy = db.Column(db.Numeric(6, 2))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('en_route', 'arrived', 'in_progress', name='location_status'), default='en_route')
    
    # Relationships
    booking = db.relationship('Booking', backref='location_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'provider_id': self.provider_id,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': self.status
        }

class Governorate(db.Model):
    """Egyptian governorates for location management"""
    __tablename__ = 'governorates'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    center_latitude = db.Column(db.Numeric(10, 8))
    center_longitude = db.Column(db.Numeric(11, 8))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cities = db.relationship('City', backref='governorate', lazy='dynamic')
    
    def to_dict(self, language='en'):
        name_field = 'name_ar' if language == 'ar' else 'name_en'
        
        return {
            'id': self.id,
            'name': getattr(self, name_field),
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'code': self.code,
            'center_latitude': float(self.center_latitude) if self.center_latitude else None,
            'center_longitude': float(self.center_longitude) if self.center_longitude else None,
            'is_active': self.is_active,
            'city_count': self.cities.filter_by(is_active=True).count()
        }

class City(db.Model):
    """Cities within governorates"""
    __tablename__ = 'cities'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    governorate_id = db.Column(db.String(36), db.ForeignKey('governorates.id'), nullable=False)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    center_latitude = db.Column(db.Numeric(10, 8))
    center_longitude = db.Column(db.Numeric(11, 8))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, language='en'):
        name_field = 'name_ar' if language == 'ar' else 'name_en'
        
        return {
            'id': self.id,
            'governorate_id': self.governorate_id,
            'name': getattr(self, name_field),
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'center_latitude': float(self.center_latitude) if self.center_latitude else None,
            'center_longitude': float(self.center_longitude) if self.center_longitude else None,
            'is_active': self.is_active,
            'governorate': self.governorate.to_dict(language) if self.governorate else None
        }

class CustomerLocation(db.Model):
    """Customer live location tracking for better service matching"""
    __tablename__ = 'customer_locations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    accuracy = db.Column(db.Numeric(6, 2))  # GPS accuracy in meters
    address_components = db.Column(db.JSON)  # Geocoded address details
    formatted_address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'customer_id': str(self.customer_id),
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'address_components': self.address_components,
            'formatted_address': self.formatted_address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

