from flask import Blueprint, jsonify, request
from src.models.user import User, CustomerProfile, ServiceProviderProfile, db
from src.utils.auth import validate_email, validate_phone, normalize_phone, validate_password
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user with proper validation and error handling"""
    try:
        data = request.get_json()
        
        # Validate request data exists
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
            return jsonify({'error': 'Invalid user type. Must be customer or service_provider'}), 400
        
        # Normalize phone number
        normalized_phone = normalize_phone(data['phone'])
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == data['email'].lower()) | (User.phone == normalized_phone)
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
        else:  # service_provider
            # Additional validation for service providers
            if 'business_name' not in data or not data['business_name']:
                return jsonify({'error': 'Business name is required for service providers'}), 400
            
            profile = ServiceProviderProfile(
                user_id=user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                business_name=data['business_name'],
                business_description=data.get('business_description', ''),
                years_of_experience=data.get('years_of_experience', 0),
                hourly_rate=data.get('hourly_rate'),
                service_radius=data.get('service_radius', 10),
                commission_rate=data.get('commission_rate', 15.00)
            )
        
        db.session.add(profile)
        db.session.commit()
        
        # Return success response with user data
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log the error for debugging
        print(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Internal server error occurred while creating user'}), 500

@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict())
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == data['email'].lower(), User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Email already taken by another user'}), 409
            user.email = data['email'].lower()
        
        if 'phone' in data:
            if not validate_phone(data['phone']):
                return jsonify({'error': 'Invalid phone number format'}), 400
            normalized_phone = normalize_phone(data['phone'])
            # Check if phone is already taken by another user
            existing_user = User.query.filter(User.phone == normalized_phone, User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Phone number already taken by another user'}), 409
            user.phone = normalized_phone
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        # Update password if provided
        if 'password' in data:
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'error': message}), 400
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
