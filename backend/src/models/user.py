from src.models import db, generate_uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

class User(db.Model):
    """Base user model for all user types"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('customer', 'service_provider', 'admin', name='user_types'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'suspended', 'pending_verification', name='user_status'), 
                      default='pending_verification')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    customer_profile = db.relationship('CustomerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    provider_profile = db.relationship('ServiceProviderProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified
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
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    profile_image_url = db.Column(db.Text)
    verification_status = db.Column(db.Enum('pending', 'verified', 'rejected', 'suspended', name='verification_status'), 
                                   default='pending')
    background_check_status = db.Column(db.Enum('pending', 'clear', 'flagged', name='background_check_status'), 
                                       default='pending')
    average_rating = db.Column(db.Numeric(3, 2), default=0.00)
    total_jobs_completed = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    is_available = db.Column(db.Boolean, default=True)
    preferred_language = db.Column(db.String(5), default='ar')
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
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'national_id': self.national_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'profile_image_url': self.profile_image_url,
            'verification_status': self.verification_status,
            'background_check_status': self.background_check_status,
            'average_rating': float(self.average_rating) if self.average_rating else 0.0,
            'total_jobs_completed': self.total_jobs_completed,
            'total_earnings': float(self.total_earnings) if self.total_earnings else 0.0,
            'is_available': self.is_available,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerAddress(db.Model):
    """Customer address model"""
    __tablename__ = 'customer_addresses'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    customer_id = db.Column(db.String(36), db.ForeignKey('customer_profiles.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)  # Home, Work, etc.
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    governorate = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'title': self.title,
            'street': self.street,
            'city': self.city,
            'governorate': self.governorate,
            'postal_code': self.postal_code,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'is_default': self.is_default,
            'full_address': f"{self.street}, {self.city}, {self.governorate}"
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

