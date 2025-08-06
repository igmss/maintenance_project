from src.models import db, generate_uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

class User(db.Model):
    """Base user model for all user types"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    phone_verified_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    provider_profile = db.relationship('ServiceProviderProfile', foreign_keys='ServiceProviderProfile.user_id', backref='user', uselist=False, cascade='all, delete-orphan')
    verified_providers = db.relationship('ServiceProviderProfile', foreign_keys='ServiceProviderProfile.verified_by', backref='verifier', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'status': self.status,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None,
            'phone_verified_at': self.phone_verified_at.isoformat() if self.phone_verified_at else None
        }

class CustomerProfile(db.Model):
    """Customer profile model"""
    __tablename__ = 'customer_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender_types'))
    profile_image_url = db.Column(db.Text)
    preferred_language = db.Column(db.String(5), default='ar')
    notification_preferences = db.Column(db.JSON, default={'push': True, 'sms': True, 'email': True})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')
    addresses = db.relationship('CustomerAddress', backref='customer', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'profile_image_url': self.profile_image_url,
            'preferred_language': self.preferred_language,
            'notification_preferences': self.notification_preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ServiceProviderProfile(db.Model):
    """Service provider profile model"""
    __tablename__ = 'service_provider_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    business_license = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    profile_image_url = db.Column(db.Text)
    bio_ar = db.Column(db.Text)
    bio_en = db.Column(db.Text)
    business_description = db.Column(db.Text)
    years_of_experience = db.Column(db.Integer, default=0)
    verification_status = db.Column(db.String(20), default='pending')
    verification_date = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    is_available = db.Column(db.Boolean, default=True)
    average_rating = db.Column(db.Numeric(3, 2), default=0.00)
    rating = db.Column(db.Numeric(3, 2), default=0.00)
    total_reviews = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    total_completed_jobs = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Numeric(12, 2), default=0.00)
    commission_rate = db.Column(db.Numeric(5, 2), default=15.00)
    service_radius = db.Column(db.Integer, default=10)
    hourly_rate = db.Column(db.Numeric(10, 2))
    emergency_rate_multiplier = db.Column(db.Numeric(3, 2), default=1.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('ProviderService', backref='provider', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='provider', lazy='dynamic')
    locations = db.relationship('ProviderLocation', backref='provider', cascade='all, delete-orphan')
    service_areas = db.relationship('ProviderServiceArea', backref='provider', cascade='all, delete-orphan')
    documents = db.relationship('ProviderDocument', backref='provider', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'business_license': self.business_license,
            'tax_id': self.tax_id,
            'profile_image_url': self.profile_image_url,
            'bio_ar': self.bio_ar,
            'bio_en': self.bio_en,
            'business_description': self.business_description,
            'years_of_experience': self.years_of_experience,
            'verification_status': self.verification_status,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_notes': self.verification_notes,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'verified_by': self.verified_by,
            'is_available': self.is_available,
            'average_rating': float(self.average_rating) if self.average_rating else 0.0,
            'rating': float(self.rating) if self.rating else 0.0,
            'total_reviews': self.total_reviews,
            'total_bookings': self.total_bookings,
            'total_completed_jobs': self.total_completed_jobs,
            'total_earnings': float(self.total_earnings) if self.total_earnings else 0.0,
            'commission_rate': float(self.commission_rate) if self.commission_rate else 15.0,
            'service_radius': self.service_radius,
            'hourly_rate': float(self.hourly_rate) if self.hourly_rate else None,
            'emergency_rate_multiplier': float(self.emergency_rate_multiplier) if self.emergency_rate_multiplier else 1.5,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerAddress(db.Model):
    """Customer address model"""
    __tablename__ = 'customer_addresses'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer_profiles.id'), nullable=False)
    address_type = db.Column(db.String(20), default='home')
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    governorate = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'address_type': self.address_type,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'governorate': self.governorate,
            'postal_code': self.postal_code,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'is_default': self.is_default,
            'full_address': f"{self.address_line1}, {self.city}, {self.governorate}",
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProviderDocument(db.Model):
    """Service provider document model for verification"""
    __tablename__ = 'provider_documents'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)
    document_type = db.Column(db.Enum('national_id', 'certificate', 'license', 'insurance', 'background_check', 
                                     name='document_types'), nullable=False)
    document_url = db.Column(db.Text, nullable=False)
    verification_status = db.Column(db.Enum('pending', 'approved', 'rejected', name='doc_verification_status'), 
                                   default='pending')
    verified_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'document_type': self.document_type,
            'document_url': self.document_url,
            'verification_status': self.verification_status,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

