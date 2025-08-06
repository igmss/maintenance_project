from src.models import db, generate_uuid
from datetime import datetime

class ServiceCategory(db.Model):
    """Service category model"""
    __tablename__ = 'service_categories'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    color_code = db.Column(db.String(7), default='#007bff')
    is_active = db.Column(db.Boolean, default=True)
    is_emergency_available = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='category', lazy='dynamic')
    
    def to_dict(self, language='en'):
        name_field = 'name_ar' if language == 'ar' else 'name_en'
        desc_field = 'description_ar' if language == 'ar' else 'description_en'
        
        return {
            'id': self.id,
            'name': getattr(self, name_field),
            'description': getattr(self, desc_field),
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'description_ar': self.description_ar,
            'description_en': self.description_en,
            'icon_url': self.icon_url,
            'color_code': self.color_code,
            'is_active': self.is_active,
            'is_emergency_available': self.is_emergency_available,
            'sort_order': self.sort_order,
            'service_count': self.services.filter_by(is_active=True).count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Service(db.Model):
    """Individual service model"""
    __tablename__ = 'services'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    category_id = db.Column(db.String(36), db.ForeignKey('service_categories.id'), nullable=False)
    name_ar = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    description_ar = db.Column(db.Text)
    description_en = db.Column(db.Text)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    price_unit = db.Column(db.String(20), default='fixed')
    estimated_duration = db.Column(db.Integer)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    is_emergency_service = db.Column(db.Boolean, default=False)
    emergency_surcharge_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    requires_materials = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider_services = db.relationship('ProviderService', backref='service', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='service', lazy='dynamic')
    
    def to_dict(self, language='en'):
        name_field = 'name_ar' if language == 'ar' else 'name_en'
        desc_field = 'description_ar' if language == 'ar' else 'description_en'
        
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': getattr(self, name_field),
            'description': getattr(self, desc_field),
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'description_ar': self.description_ar,
            'description_en': self.description_en,
            'base_price': float(self.base_price),
            'price_unit': self.price_unit,
            'estimated_duration': self.estimated_duration,
            'is_active': self.is_active,
            'is_emergency_service': self.is_emergency_service,
            'emergency_surcharge_percentage': float(self.emergency_surcharge_percentage),
            'requires_materials': self.requires_materials,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProviderService(db.Model):
    """Service provider skills and service offerings"""
    __tablename__ = 'provider_services'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    custom_price = db.Column(db.Numeric(10, 2))  # Override base price if needed
    is_available = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    experience_years = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('provider_id', 'service_id', name='unique_provider_service'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'service_id': self.service_id,
            'custom_price': float(self.custom_price) if self.custom_price else None,
            'is_available': self.is_available,
            'is_active': self.is_active,
            'experience_years': self.experience_years,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'service': self.service.to_dict() if self.service else None
        }

class Booking(db.Model):
    """Service booking model"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer_profiles.id'), nullable=False)
    provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'))
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    booking_status = db.Column(db.Enum('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'disputed', 
                                      name='booking_status'), default='pending')
    scheduled_date = db.Column(db.DateTime, nullable=False)
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    estimated_duration = db.Column(db.Integer)  # in minutes
    actual_duration = db.Column(db.Integer)  # in minutes
    
    # Service address (JSON)
    service_address = db.Column(db.JSON, nullable=False)
    special_instructions = db.Column(db.Text)
    
    # Pricing
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    platform_commission = db.Column(db.Numeric(10, 2), nullable=False)
    provider_earnings = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment
    payment_status = db.Column(db.Enum('pending', 'paid', 'refunded', 'disputed', name='payment_status'), 
                              default='pending')
    payment_method = db.Column(db.Enum('cash', 'card', 'wallet', 'bank_transfer', name='payment_methods'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    status_history = db.relationship('BookingStatusHistory', backref='booking', cascade='all, delete-orphan')
    reviews = db.relationship('BookingReview', backref='booking', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'provider_id': self.provider_id,
            'service_id': self.service_id,
            'booking_status': self.booking_status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'service_address': self.service_address,
            'special_instructions': self.special_instructions,
            'total_amount': float(self.total_amount),
            'platform_commission': float(self.platform_commission),
            'provider_earnings': float(self.provider_earnings),
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer': self.customer.to_dict() if self.customer else None,
            'provider': self.provider.to_dict() if self.provider else None,
            'service': self.service.to_dict() if self.service else None
        }

class BookingStatusHistory(db.Model):
    """Booking status change history for audit trail"""
    __tablename__ = 'booking_status_history'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'), nullable=False)
    previous_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    change_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'previous_status': self.previous_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'change_reason': self.change_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BookingReview(db.Model):
    """Customer review and rating for completed bookings"""
    __tablename__ = 'booking_reviews'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer_profiles.id'), nullable=False)
    provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    review_photos = db.Column(db.JSON)  # Array of photo URLs
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'provider_id': self.provider_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_photos': self.review_photos,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'customer_name': f"{self.booking.customer.first_name} {self.booking.customer.last_name}" if self.booking and self.booking.customer else None
        }

