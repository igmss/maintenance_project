from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User, CustomerProfile, ServiceProviderProfile
from src.models.location import ProviderLocation, ProviderServiceArea
from src.utils.auth import validate_email, validate_phone, normalize_phone, validate_password, token_required
from src.utils.location import validate_coordinates

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (customer or service provider)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'phone', 'password', 'user_type', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate phone
        if not validate_phone(data['phone']):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Validate password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate user type
        if data['user_type'] not in ['customer', 'service_provider']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Normalize phone number
        normalized_phone = normalize_phone(data['phone'])
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.phone == normalized_phone)
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User with this email or phone already exists'}), 409
        
        # Create new user
        user = User(
            email=data['email'].lower(),
            phone=normalized_phone,
            user_type=data['user_type']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create profile based on user type
        if data['user_type'] == 'customer':
            profile = CustomerProfile(
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                preferred_language=data.get('preferred_language', 'ar')
            )
        elif data['user_type'] == 'admin':
            # Admin users don't need a separate profile, just the user record
            profile = None
        else:  # service_provider
            # Additional validation for service providers
            if 'national_id' not in data or not data['national_id']:
                return jsonify({'error': 'National ID is required for service providers'}), 400
            
            if 'date_of_birth' not in data or not data['date_of_birth']:
                return jsonify({'error': 'Date of birth is required for service providers'}), 400
            
            try:
                dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
            profile = ServiceProviderProfile(
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                national_id=data['national_id'],
                date_of_birth=dob,
                preferred_language=data.get('preferred_language', 'ar'),
                business_name=data.get('business_name', f"{data['first_name']} {data['last_name']}")  # Default business name
            )
        
        db.session.add(profile)
        
        # If this is a service provider and location data is provided, save initial location
        if data['user_type'] == 'service_provider' and 'latitude' in data and 'longitude' in data:
            try:
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                
                if validate_coordinates(latitude, longitude):
                    # Create initial location entry
                    initial_location = ProviderLocation(
                        provider_id=profile.id,
                        latitude=latitude,
                        longitude=longitude,
                        is_online=True,
                        accuracy=data.get('accuracy', 10.0),
                        battery_level=data.get('battery_level', 100)
                    )
                    db.session.add(initial_location)
                    
                    # Create default service area around initial location
                    service_radius = data.get('service_radius', 15.0)
                    service_area = ProviderServiceArea(
                        provider_id=profile.id,
                        area_name=data.get('area_name', 'Primary Service Area'),
                        center_latitude=latitude,
                        center_longitude=longitude,
                        radius_km=service_radius,
                        is_primary_area=True,
                        travel_time_minutes=30
                    )
                    db.session.add(service_area)
                    
                    # Update provider profile with service radius
                    profile.service_radius = int(service_radius)
                    profile.is_available = True
                    
            except (ValueError, TypeError) as e:
                # If location data is invalid, continue without it
                print(f"Invalid location data during registration: {e}")
        
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'profile': profile.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email/phone and password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email_or_phone') or not data.get('password'):
            return jsonify({'error': 'Email/phone and password are required'}), 400
        
        email_or_phone = data['email_or_phone']
        password = data['password']
        
        # Find user by email or phone
        user = None
        if validate_email(email_or_phone):
            user = User.query.filter_by(email=email_or_phone.lower()).first()
        elif validate_phone(email_or_phone):
            normalized_phone = normalize_phone(email_or_phone)
            user = User.query.filter_by(phone=normalized_phone).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user.status == 'suspended':
            return jsonify({'error': 'Account is suspended'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        # Get profile data
        profile = None
        if user.user_type == 'customer' and user.customer_profile:
            profile = user.customer_profile.to_dict()
        elif user.user_type == 'service_provider' and user.provider_profile:
            profile = user.provider_profile.to_dict()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'profile': profile,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.status != 'active':
            return jsonify({'error': 'Invalid user or account not active'}), 401
        
        new_access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    try:
        profile = None
        if current_user.user_type == 'customer' and current_user.customer_profile:
            profile = current_user.customer_profile.to_dict()
        elif current_user.user_type == 'service_provider' and current_user.provider_profile:
            profile = current_user.provider_profile.to_dict()
        
        return jsonify({
            'user': current_user.to_dict(),
            'profile': profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        # Update user fields
        if 'email' in data and data['email'] != current_user.email:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Check if email is already taken
            existing_user = User.query.filter(
                User.email == data['email'].lower(),
                User.id != current_user.id
            ).first()
            
            if existing_user:
                return jsonify({'error': 'Email already taken'}), 409
            
            current_user.email = data['email'].lower()
            current_user.email_verified = False
        
        if 'phone' in data and data['phone'] != current_user.phone:
            if not validate_phone(data['phone']):
                return jsonify({'error': 'Invalid phone format'}), 400
            
            normalized_phone = normalize_phone(data['phone'])
            
            # Check if phone is already taken
            existing_user = User.query.filter(
                User.phone == normalized_phone,
                User.id != current_user.id
            ).first()
            
            if existing_user:
                return jsonify({'error': 'Phone number already taken'}), 409
            
            current_user.phone = normalized_phone
            current_user.phone_verified = False
        
        # Update profile fields
        profile = None
        if current_user.user_type == 'customer' and current_user.customer_profile:
            profile = current_user.customer_profile
            
            if 'first_name' in data:
                profile.first_name = data['first_name']
            if 'last_name' in data:
                profile.last_name = data['last_name']
            if 'preferred_language' in data:
                profile.preferred_language = data['preferred_language']
            if 'notification_preferences' in data:
                profile.notification_preferences = data['notification_preferences']
                
        elif current_user.user_type == 'service_provider' and current_user.provider_profile:
            profile = current_user.provider_profile
            
            if 'first_name' in data:
                profile.first_name = data['first_name']
            if 'last_name' in data:
                profile.last_name = data['last_name']
            if 'preferred_language' in data:
                profile.preferred_language = data['preferred_language']
            if 'is_available' in data:
                profile.is_available = data['is_available']
        
        current_user.updated_at = datetime.utcnow()
        if profile:
            profile.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict(),
            'profile': profile.to_dict() if profile else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not current_user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Set new password
        current_user.set_password(data['new_password'])
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

