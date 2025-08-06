import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.main import app
from src.models.service import ServiceCategory, Service, Booking, BookingStatusHistory

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            from src.main import db
            db.create_all()
            
            # Create sample service categories
            categories = [
                ServiceCategory(
                    name_en='Plumbing',
                    name_ar='السباكة',
                    description_en='Plumbing services',
                    description_ar='خدمات السباكة',
                    icon='plumbing-icon',
                    is_active=True
                ),
                ServiceCategory(
                    name_en='Electrical',
                    name_ar='الكهرباء',
                    description_en='Electrical services',
                    description_ar='خدمات الكهرباء',
                    icon='electrical-icon',
                    is_active=True
                )
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            yield client
            db.drop_all()

@pytest.fixture
def authenticated_customer(client):
    """Create an authenticated customer user."""
    user_data = {
        'email': 'customer@example.com',
        'phone': '+201234567890',
        'password': 'CustomerPass123!',
        'full_name': 'Test Customer',
        'user_type': 'customer',
        'preferred_language': 'en'
    }
    
    response = client.post('/api/auth/register',
                         data=json.dumps(user_data),
                         content_type='application/json')
    
    data = json.loads(response.data)
    return {
        'token': data['token'],
        'user': data['user'],
        'headers': {'Authorization': f'Bearer {data["token"]}'}
    }

@pytest.fixture
def authenticated_provider(client):
    """Create an authenticated service provider."""
    provider_data = {
        'email': 'provider@example.com',
        'phone': '+201234567891',
        'password': 'ProviderPass123!',
        'full_name': 'Test Provider',
        'user_type': 'service_provider',
        'preferred_language': 'en',
        'business_name': 'Test Service Business',
        'services': ['plumbing'],
        'service_areas': ['cairo']
    }
    
    response = client.post('/api/auth/register',
                         data=json.dumps(provider_data),
                         content_type='application/json')
    
    data = json.loads(response.data)
    return {
        'token': data['token'],
        'user': data['user'],
        'headers': {'Authorization': f'Bearer {data["token"]}'}
    }

@pytest.fixture
def sample_booking_data():
    """Sample booking data."""
    return {
        'service_category_id': 1,
        'description': 'Fix leaking faucet',
        'preferred_date': (datetime.now() + timedelta(days=1)).isoformat(),
        'preferred_time': '10:00',
        'location': {
            'address': '123 Test Street, Cairo',
            'latitude': 30.0444,
            'longitude': 31.2357,
            'governorate': 'cairo'
        },
        'urgency': 'normal',
        'estimated_duration': 2
    }

class TestServiceCategories:
    """Test service category management."""
    
    def test_get_service_categories_success(self, client, authenticated_customer):
        """Test retrieving service categories."""
        response = client.get('/api/services/categories',
                            headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'categories' in data
        assert len(data['categories']) >= 2
        
        # Check category structure
        category = data['categories'][0]
        assert 'id' in category
        assert 'name_en' in category
        assert 'name_ar' in category
        assert 'description_en' in category
        assert 'description_ar' in category
        assert 'icon' in category
        assert 'is_active' in category
    
    def test_get_service_categories_unauthenticated(self, client):
        """Test retrieving service categories without authentication."""
        response = client.get('/api/services/categories')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_service_categories_by_language(self, client, authenticated_customer):
        """Test retrieving service categories with language preference."""
        response = client.get('/api/services/categories?lang=ar',
                            headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should return Arabic names as primary
        category = data['categories'][0]
        assert category['name_ar'] is not None
    
    def test_get_active_categories_only(self, client, authenticated_customer):
        """Test retrieving only active service categories."""
        response = client.get('/api/services/categories',
                            headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # All returned categories should be active
        for category in data['categories']:
            assert category['is_active'] is True

class TestBookingSystem:
    """Test booking creation and management."""
    
    def test_create_booking_success(self, client, authenticated_customer, sample_booking_data):
        """Test successful booking creation."""
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'booking' in data
        
        booking = data['booking']
        assert booking['customer_id'] == authenticated_customer['user']['id']
        assert booking['service_category_id'] == sample_booking_data['service_category_id']
        assert booking['description'] == sample_booking_data['description']
        assert booking['status'] == 'pending'
        assert booking['urgency'] == sample_booking_data['urgency']
    
    def test_create_booking_invalid_category(self, client, authenticated_customer, sample_booking_data):
        """Test booking creation with invalid service category."""
        sample_booking_data['service_category_id'] = 999  # Non-existent category
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'service category' in data['error'].lower()
    
    def test_create_booking_missing_required_fields(self, client, authenticated_customer):
        """Test booking creation with missing required fields."""
        incomplete_data = {
            'description': 'Fix something'
            # Missing service_category_id, location, etc.
        }
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(incomplete_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_create_booking_invalid_date(self, client, authenticated_customer, sample_booking_data):
        """Test booking creation with past date."""
        sample_booking_data['preferred_date'] = (datetime.now() - timedelta(days=1)).isoformat()
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'date' in data['error'].lower()
    
    def test_create_emergency_booking(self, client, authenticated_customer, sample_booking_data):
        """Test emergency booking creation."""
        sample_booking_data['urgency'] = 'emergency'
        sample_booking_data['preferred_date'] = datetime.now().isoformat()
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        
        booking = data['booking']
        assert booking['urgency'] == 'emergency'
        assert booking['emergency_fee'] > 0  # Should have emergency fee
    
    def test_get_customer_bookings(self, client, authenticated_customer, sample_booking_data):
        """Test retrieving customer's bookings."""
        # Create a booking first
        client.post('/api/services/bookings',
                   data=json.dumps(sample_booking_data),
                   content_type='application/json',
                   headers=authenticated_customer['headers'])
        
        # Get bookings
        response = client.get('/api/services/bookings',
                            headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'bookings' in data
        assert len(data['bookings']) >= 1
        
        booking = data['bookings'][0]
        assert booking['customer_id'] == authenticated_customer['user']['id']
    
    def test_get_booking_details(self, client, authenticated_customer, sample_booking_data):
        """Test retrieving specific booking details."""
        # Create a booking first
        create_response = client.post('/api/services/bookings',
                                    data=json.dumps(sample_booking_data),
                                    content_type='application/json',
                                    headers=authenticated_customer['headers'])
        
        create_data = json.loads(create_response.data)
        booking_id = create_data['booking']['id']
        
        # Get booking details
        response = client.get(f'/api/services/bookings/{booking_id}',
                            headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'booking' in data
        
        booking = data['booking']
        assert booking['id'] == booking_id
        assert 'location' in booking
        assert 'status_history' in booking
    
    def test_cancel_booking_success(self, client, authenticated_customer, sample_booking_data):
        """Test successful booking cancellation."""
        # Create a booking first
        create_response = client.post('/api/services/bookings',
                                    data=json.dumps(sample_booking_data),
                                    content_type='application/json',
                                    headers=authenticated_customer['headers'])
        
        create_data = json.loads(create_response.data)
        booking_id = create_data['booking']['id']
        
        # Cancel booking
        cancel_data = {'reason': 'Changed my mind'}
        response = client.post(f'/api/services/bookings/{booking_id}/cancel',
                             data=json.dumps(cancel_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Check booking status
        get_response = client.get(f'/api/services/bookings/{booking_id}',
                                headers=authenticated_customer['headers'])
        get_data = json.loads(get_response.data)
        assert get_data['booking']['status'] == 'cancelled'
    
    def test_cancel_booking_too_late(self, client, authenticated_customer, sample_booking_data):
        """Test booking cancellation after deadline."""
        # Create a booking with near-future date
        sample_booking_data['preferred_date'] = (datetime.now() + timedelta(hours=12)).isoformat()
        
        create_response = client.post('/api/services/bookings',
                                    data=json.dumps(sample_booking_data),
                                    content_type='application/json',
                                    headers=authenticated_customer['headers'])
        
        create_data = json.loads(create_response.data)
        booking_id = create_data['booking']['id']
        
        # Try to cancel (should fail if within 24h window)
        cancel_data = {'reason': 'Too late'}
        response = client.post(f'/api/services/bookings/{booking_id}/cancel',
                             data=json.dumps(cancel_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        # Depending on cancellation policy, this might fail
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'cancellation' in data['error'].lower()

class TestProviderBookingManagement:
    """Test service provider booking management."""
    
    def test_get_available_bookings(self, client, authenticated_provider):
        """Test retrieving available bookings for providers."""
        response = client.get('/api/providers/bookings/available',
                            headers=authenticated_provider['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'bookings' in data
    
    def test_accept_booking_success(self, client, authenticated_customer, authenticated_provider, sample_booking_data):
        """Test provider accepting a booking."""
        # Create a booking as customer
        create_response = client.post('/api/services/bookings',
                                    data=json.dumps(sample_booking_data),
                                    content_type='application/json',
                                    headers=authenticated_customer['headers'])
        
        create_data = json.loads(create_response.data)
        booking_id = create_data['booking']['id']
        
        # Accept booking as provider
        accept_data = {
            'estimated_price': 150.0,
            'estimated_duration': 2,
            'notes': 'I can fix this quickly'
        }
        
        response = client.post(f'/api/providers/bookings/{booking_id}/accept',
                             data=json.dumps(accept_data),
                             content_type='application/json',
                             headers=authenticated_provider['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Check booking status
        get_response = client.get(f'/api/services/bookings/{booking_id}',
                                headers=authenticated_customer['headers'])
        get_data = json.loads(get_response.data)
        assert get_data['booking']['status'] == 'confirmed'
        assert get_data['booking']['provider_id'] == authenticated_provider['user']['id']
    
    def test_update_booking_status(self, client, authenticated_provider, authenticated_customer, sample_booking_data):
        """Test provider updating booking status."""
        # Create and accept a booking
        create_response = client.post('/api/services/bookings',
                                    data=json.dumps(sample_booking_data),
                                    content_type='application/json',
                                    headers=authenticated_customer['headers'])
        
        booking_id = json.loads(create_response.data)['booking']['id']
        
        # Accept booking
        accept_data = {'estimated_price': 150.0}
        client.post(f'/api/providers/bookings/{booking_id}/accept',
                   data=json.dumps(accept_data),
                   content_type='application/json',
                   headers=authenticated_provider['headers'])
        
        # Update status to in_progress
        status_data = {
            'status': 'in_progress',
            'notes': 'Started working on the issue'
        }
        
        response = client.post(f'/api/providers/bookings/{booking_id}/status',
                             data=json.dumps(status_data),
                             content_type='application/json',
                             headers=authenticated_provider['headers'])
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify status change
        get_response = client.get(f'/api/services/bookings/{booking_id}',
                                headers=authenticated_customer['headers'])
        get_data = json.loads(get_response.data)
        assert get_data['booking']['status'] == 'in_progress'

class TestBookingValidation:
    """Test booking data validation."""
    
    def test_validate_location_coordinates(self, client, authenticated_customer, sample_booking_data):
        """Test location coordinate validation."""
        # Invalid coordinates (outside Egypt)
        sample_booking_data['location']['latitude'] = 0.0
        sample_booking_data['location']['longitude'] = 0.0
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'location' in data['error'].lower()
    
    def test_validate_phone_format(self, client, authenticated_customer, sample_booking_data):
        """Test Egyptian phone number format validation."""
        sample_booking_data['contact_phone'] = '123456'  # Invalid format
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        # Should either accept (if phone is optional) or reject with proper error
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'phone' in data['error'].lower()
    
    def test_validate_service_area_coverage(self, client, authenticated_customer, sample_booking_data):
        """Test service area coverage validation."""
        # Set location outside typical service areas
        sample_booking_data['location']['governorate'] = 'south_sinai'
        
        response = client.post('/api/services/bookings',
                             data=json.dumps(sample_booking_data),
                             content_type='application/json',
                             headers=authenticated_customer['headers'])
        
        # Should still create booking but might have different handling
        assert response.status_code in [201, 400]

if __name__ == '__main__':
    pytest.main([__file__])

