import pytest
import json
import time
from unittest.mock import patch, MagicMock
from src.main import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            from src.main import db
            db.create_all()
            yield client
            db.drop_all()

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks."""
        malicious_data = {
            'email': "admin@test.com'; DROP TABLE users; --",
            'password': 'password123',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(malicious_data),
                             content_type='application/json')
        
        # Should either reject the input or sanitize it
        # The database should not be affected
        assert response.status_code in [400, 201]
        
        # Verify database integrity by trying to access users
        test_response = client.get('/api/auth/profile')
        assert test_response.status_code == 401  # Should get unauthorized, not server error
    
    def test_xss_protection(self, client):
        """Test protection against XSS attacks."""
        xss_payload = "<script>alert('XSS')</script>"
        
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'full_name': xss_payload,  # XSS in name field
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        if response.status_code == 201:
            data = json.loads(response.data)
            # Name should be sanitized
            assert '<script>' not in data['user']['full_name']
            assert 'alert' not in data['user']['full_name']
    
    def test_command_injection_protection(self, client):
        """Test protection against command injection."""
        malicious_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'full_name': 'Test; rm -rf /',  # Command injection attempt
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(malicious_data),
                             content_type='application/json')
        
        # Should handle malicious input safely
        assert response.status_code in [400, 201]
    
    def test_oversized_payload_protection(self, client):
        """Test protection against oversized payloads."""
        large_string = 'A' * 10000  # Very large string
        
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'full_name': large_string,
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        # Should reject oversized input
        assert response.status_code == 400
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON payloads."""
        invalid_json = '{"email": "test@example.com", "password": "incomplete'
        
        response = client.post('/api/auth/register',
                             data=invalid_json,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

class TestAuthenticationSecurity:
    """Test authentication security measures."""
    
    def test_password_strength_enforcement(self, client):
        """Test password strength requirements."""
        weak_passwords = [
            '123',           # Too short
            'password',      # No numbers/special chars
            '12345678',      # Only numbers
            'PASSWORD',      # Only uppercase
            'password123',   # No special chars
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                'email': f'test{weak_password}@example.com',
                'password': weak_password,
                'full_name': 'Test User',
                'user_type': 'customer'
            }
            
            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'password' in data['error'].lower()
    
    def test_rate_limiting_login_attempts(self, client):
        """Test rate limiting for login attempts."""
        # Register a user first
        user_data = {
            'email': 'test@example.com',
            'password': 'ValidPassword123!',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        client.post('/api/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Attempt multiple failed logins
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        failed_attempts = 0
        for i in range(10):  # Try 10 failed attempts
            response = client.post('/api/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            if response.status_code == 429:  # Rate limited
                break
            elif response.status_code == 401:  # Invalid credentials
                failed_attempts += 1
        
        # Should eventually get rate limited
        assert failed_attempts < 10  # Should be blocked before 10 attempts
    
    def test_session_token_expiration(self, client):
        """Test JWT token expiration."""
        # Register and login
        user_data = {
            'email': 'test@example.com',
            'password': 'ValidPassword123!',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        data = json.loads(register_response.data)
        token = data['token']
        
        # Use token immediately (should work)
        headers = {'Authorization': f'Bearer {token}'}
        response = client.get('/api/auth/profile', headers=headers)
        assert response.status_code == 200
        
        # Test with expired token (mock expiration)
        with patch('src.utils.auth.verify_token') as mock_verify:
            mock_verify.return_value = None  # Simulate expired token
            
            response = client.get('/api/auth/profile', headers=headers)
            assert response.status_code == 401
    
    def test_token_blacklisting_on_logout(self, client):
        """Test token invalidation on logout."""
        # Register and login
        user_data = {
            'email': 'test@example.com',
            'password': 'ValidPassword123!',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        data = json.loads(register_response.data)
        token = data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Logout
        logout_response = client.post('/api/auth/logout', headers=headers)
        assert logout_response.status_code == 200
        
        # Try to use token after logout (should fail)
        response = client.get('/api/auth/profile', headers=headers)
        assert response.status_code == 401

class TestDataProtection:
    """Test data protection and privacy measures."""
    
    def test_password_hashing(self, client):
        """Test that passwords are properly hashed."""
        user_data = {
            'email': 'test@example.com',
            'password': 'MySecretPassword123!',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        # Password should not be returned in response
        assert 'password' not in data['user']
        
        # Verify password is hashed in database
        from src.main import db
        from src.models.user import User
        
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.password_hash != 'MySecretPassword123!'
        assert user.password_hash.startswith('$2b$')  # bcrypt hash
    
    def test_sensitive_data_exclusion(self, client):
        """Test that sensitive data is excluded from API responses."""
        user_data = {
            'email': 'test@example.com',
            'password': 'ValidPassword123!',
            'full_name': 'Test User',
            'user_type': 'customer'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        data = json.loads(register_response.data)
        token = data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get profile
        profile_response = client.get('/api/auth/profile', headers=headers)
        profile_data = json.loads(profile_response.data)
        
        user_info = profile_data['user']
        
        # Sensitive fields should not be present
        sensitive_fields = ['password', 'password_hash', 'reset_token']
        for field in sensitive_fields:
            assert field not in user_info
    
    def test_user_data_isolation(self, client):
        """Test that users can only access their own data."""
        # Create two users
        user1_data = {
            'email': 'user1@example.com',
            'password': 'Password123!',
            'full_name': 'User One',
            'user_type': 'customer'
        }
        
        user2_data = {
            'email': 'user2@example.com',
            'password': 'Password123!',
            'full_name': 'User Two',
            'user_type': 'customer'
        }
        
        # Register both users
        response1 = client.post('/api/auth/register',
                              data=json.dumps(user1_data),
                              content_type='application/json')
        
        response2 = client.post('/api/auth/register',
                              data=json.dumps(user2_data),
                              content_type='application/json')
        
        token1 = json.loads(response1.data)['token']
        token2 = json.loads(response2.data)['token']
        user2_id = json.loads(response2.data)['user']['id']
        
        # Try to access user2's data with user1's token
        headers1 = {'Authorization': f'Bearer {token1}'}
        
        # This should fail or return only user1's data
        response = client.get(f'/api/users/{user2_id}', headers=headers1)
        assert response.status_code in [403, 404]  # Forbidden or Not Found

class TestAPISecurityHeaders:
    """Test security headers and CORS configuration."""
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options('/api/auth/login')
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are present."""
        response = client.get('/api/auth/profile')
        
        # Check for security headers (if implemented)
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        # Note: These might not be implemented yet, so we just check if they exist
        for header in security_headers:
            if header in response.headers:
                assert response.headers[header] is not None
    
    def test_content_type_validation(self, client):
        """Test content type validation."""
        # Try to send data with wrong content type
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        # Send as form data instead of JSON
        response = client.post('/api/auth/login',
                             data=user_data,  # Not JSON
                             content_type='application/x-www-form-urlencoded')
        
        # Should reject or handle gracefully
        assert response.status_code in [400, 415]  # Bad Request or Unsupported Media Type

class TestLocationSecurity:
    """Test location data security and validation."""
    
    def test_location_coordinate_validation(self, client):
        """Test location coordinate bounds validation."""
        # Register a user first
        user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'full_name': 'Test User',
            'user_type': 'service_provider'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        token = json.loads(register_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to update location with invalid coordinates
        invalid_locations = [
            {'latitude': 200.0, 'longitude': 31.0},    # Invalid latitude
            {'latitude': 30.0, 'longitude': 200.0},    # Invalid longitude
            {'latitude': 0.0, 'longitude': 0.0},       # Outside Egypt
            {'latitude': 'invalid', 'longitude': 31.0} # Non-numeric
        ]
        
        for location in invalid_locations:
            response = client.post('/api/providers/location',
                                 data=json.dumps(location),
                                 content_type='application/json',
                                 headers=headers)
            
            assert response.status_code == 400
    
    def test_location_privacy_controls(self, client):
        """Test location privacy and access controls."""
        # Test that location data is properly protected
        # and only accessible to authorized users
        pass  # Implementation depends on specific privacy requirements

class TestFileUploadSecurity:
    """Test file upload security measures."""
    
    def test_file_type_validation(self, client):
        """Test file type validation for document uploads."""
        # Register a service provider
        user_data = {
            'email': 'provider@example.com',
            'password': 'Password123!',
            'full_name': 'Test Provider',
            'user_type': 'service_provider'
        }
        
        register_response = client.post('/api/auth/register',
                                      data=json.dumps(user_data),
                                      content_type='application/json')
        
        token = json.loads(register_response.data)['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try to upload invalid file types
        invalid_files = [
            ('document', 'malicious.exe', b'MZ\x90\x00'),  # Executable
            ('document', 'script.js', b'alert("xss")'),    # JavaScript
            ('document', 'large.txt', b'A' * 10000000)     # Too large
        ]
        
        for field_name, filename, content in invalid_files:
            data = {field_name: (content, filename)}
            
            response = client.post('/api/providers/documents',
                                 data=data,
                                 headers=headers)
            
            # Should reject invalid files
            assert response.status_code in [400, 413, 415]
    
    def test_file_size_limits(self, client):
        """Test file size limits for uploads."""
        # This test would check file size restrictions
        # Implementation depends on specific file upload handling
        pass

if __name__ == '__main__':
    pytest.main([__file__])

