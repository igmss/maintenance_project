from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User
import re
import jwt
from datetime import datetime, timedelta

def hash_password(password):
    """Hash password using werkzeug"""
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """Verify password against hash"""
    return check_password_hash(password_hash, password)

def generate_token(user_id):
    """Generate JWT token for user"""
    return create_access_token(identity=user_id)

def verify_token(token):
    """Verify JWT token and return user_id"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode the token
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload.get('sub')  # 'sub' is the user_id in JWT
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate Egyptian phone number format"""
    # Egyptian phone numbers: 010/011/012/015 followed by 8 digits
    # Formats: 01012345678, +201012345678, 201012345678
    pattern = r'^(\+20|0020|20)?01[0125][0-9]{8}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def normalize_phone(phone):
    """Normalize phone number to standard format"""
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    
    # Convert to standard format (+201XXXXXXXXX)
    if phone.startswith('+20'):
        return phone
    elif phone.startswith('0020'):
        return phone.replace('0020', '+20')
    elif phone.startswith('20'):
        return '+' + phone
    elif phone.startswith('01'):
        return '+20' + phone[1:]
    else:
        return '+20' + phone

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if current_user.status != 'active':
                return jsonify({'error': 'Account is not active'}), 401
            
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if current_user.user_type != 'admin':
                return jsonify({'error': 'Admin privileges required'}), 403
            
            if current_user.status != 'active':
                return jsonify({'error': 'Account is not active'}), 401
            
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token or insufficient privileges'}), 401
    
    return decorated

def provider_required(f):
    """Decorator to require service provider privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if current_user.user_type != 'service_provider':
                return jsonify({'error': 'Service provider privileges required'}), 403
            
            if current_user.status != 'active':
                return jsonify({'error': 'Account is not active'}), 401
            
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token or insufficient privileges'}), 401
    
    return decorated

def customer_required(f):
    """Decorator to require customer privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if current_user.user_type != 'customer':
                return jsonify({'error': 'Customer privileges required'}), 403
            
            if current_user.status != 'active':
                return jsonify({'error': 'Account is not active'}), 401
            
            return f(current_user=current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token or insufficient privileges'}), 401
    
    return decorated

