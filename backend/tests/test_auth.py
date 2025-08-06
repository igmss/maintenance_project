import pytest
import json
from unittest.mock import patch, MagicMock
from src.main import app
from src.models.user import User, CustomerProfile, ServiceProviderProfile
from src.utils.auth import generate_token, verify_token, hash_password, verify_password

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            from src.main import db
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        'email': 'test@example.com',
        'phone': '+201234567890',
        'password': 'TestPassword123!',
        'full_name': 'Test User',
        'user_type': 'customer',
        'preferred_language': 'en'
    }

@pytest.fixture
def sample_provider_data():
    """Sample service provider registration data."""
    return {
        'email': 'provider@example.com',
        'phone': '+201234567891',
        'password': 'ProviderPass123!',
        'full_name': 'Test Provider',
        'user_type': 'service_provider',
        'preferred_language': 'ar',
        'business_name': 'Test Service Business',
        'services': ['plumbing', 'electrical'],
        'service_areas': ['cairo', 'giza']
    }

class TestPasswordUtils:
    """Test password hashing and verification utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = 'TestPassword123!'
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Werkzeug hashes are typically long
        assert hashed.startswith('scrypt:')  # Werkzeug uses scrypt by default
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = 'TestPassword123!'
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = 'TestPassword123!'
        wrong_password = 'WrongPassword123!'
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False

class TestTokenUtils:
    """Test JWT token generation and verification."""
    
    def test_generate_token(self):
        """Test JWT token generation."""
        user_id = 123
        token = generate_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_verify_token_valid(self):
        """Test JWT token verification with valid token."""
        user_id = 123
        token = generate_token(user_id)
        
        decoded_user_id = verify_token(token)
        assert decoded_user_id == user_id
    
    def test_verify_token_invalid(self):
        """Test JWT token verification with invalid token."""
        invalid_token = 'invalid.token.here'
        
        decoded_user_id = verify_token(invalid_token)
        assert decoded_user_id is None

class TestAuthRoutes:
    """Test authentication API routes."""
    
    def test_register_customer_success(self, client, sample_user_data):
        """Test successful customer registration."""
        response = client.post('/api/auth/register', 
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == sample_user_data['email']
        assert data['user']['user_type'] == 'customer'
    
    def test_register_provider_success(self, client, sample_provider_data):
        """Test successful service provider registration."""
        response = client.post('/api/auth/register',
                             data=json.dumps(sample_provider_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == sample_provider_data['email']
        assert data['user']['user_type'] == 'service_provider'
    
    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email."""
        # First registration
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Second registration with same email
        response = client.post('/api/auth/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'email already exists' in data['error'].lower()
    
    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email format."""
        sample_user_data['email'] = 'invalid-email'
        
        response = client.post('/api/auth/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'invalid email' in data['error'].lower()
    
    def test_register_weak_password(self, client, sample_user_data):
        """Test registration with weak password."""
        sample_user_data['password'] = '123'
        
        response = client.post('/api/auth/register',
                             data=json.dumps(sample_user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'password' in data['error'].lower()
    
    def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        # First register a user
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Then login
        login_data = {
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == sample_user_data['email']
    
    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'invalid credentials' in data['error'].lower()
    
    def test_login_phone_number(self, client, sample_user_data):
        """Test login with phone number instead of email."""
        # First register a user
        client.post('/api/auth/register',
                   data=json.dumps(sample_user_data),
                   content_type='application/json')
        
        # Then login with phone
        login_data = {
            'email': sample_user_data['phone'],  # Using phone as email field
            'password': sample_user_data['password']
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_profile_access_authenticated(self, client, sample_user_data):
        """Test profile access with valid authentication."""
        # Register and get token
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(sample_user_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Access profile with token
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/profile', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
    
    def test_profile_access_unauthenticated(self, client):
        """Test profile access without authentication."""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'token required' in data['error'].lower()
    
    def test_profile_access_invalid_token(self, client):
        """Test profile access with invalid token."""
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = client.get('/api/auth/profile', headers=headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'invalid token' in data['error'].lower()
    
    def test_profile_update_success(self, client, sample_user_data):
        """Test successful profile update."""
        # Register and get token
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(sample_user_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Update profile
        update_data = {
            'full_name': 'Updated Name',
            'preferred_language': 'ar'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/api/auth/profile',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['user']['full_name'] == 'Updated Name'
        assert data['user']['preferred_language'] == 'ar'

class TestAuthMiddleware:
    """Test authentication middleware and decorators."""
    
    def test_token_required_decorator(self, client, sample_user_data):
        """Test token_required decorator functionality."""
        # Try to access protected endpoint without token
        response = client.get('/api/services')
        assert response.status_code == 401
        
        # Register and get token
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(sample_user_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Access protected endpoint with token
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/services', headers=headers)
        assert response.status_code == 200
    
    def test_role_required_decorator(self, client, sample_provider_data):
        """Test role-based access control."""
        # Register as service provider
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(sample_provider_data),
                                      content_type='application/json')
        
        register_data = json.loads(register_response.data)
        token = register_data['token']
        
        # Try to access provider-only endpoint
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/providers/dashboard', headers=headers)
        assert response.status_code == 200  # Should work for providers
        
        # Try to access admin-only endpoint (should fail)
        response = client.get('/api/admin/users', headers=headers)
        assert response.status_code == 403  # Forbidden for non-admin users

if __name__ == '__main__':
    pytest.main([__file__])

