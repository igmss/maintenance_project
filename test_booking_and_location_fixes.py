#!/usr/bin/env python3
"""
Comprehensive test script for booking and location sharing fixes.
Tests the resolved foreign key issues and new customer location features.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://maintenance-platform-backend.onrender.com/api"
TEST_CUSTOMER_EMAIL = "customer@test.com"
TEST_CUSTOMER_PASSWORD = "password123"

class BookingLocationTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.customer_id = None
        
    def login_customer(self):
        """Login as test customer"""
        print("🔐 Logging in as customer...")
        
        response = self.session.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_CUSTOMER_EMAIL,
            "password": TEST_CUSTOMER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.customer_id = data['user']['id']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            print(f"✅ Customer login successful! Customer ID: {self.customer_id}")
            return True
        else:
            print(f"❌ Customer login failed: {response.status_code} - {response.text}")
            return False
    
    def test_customer_location_sharing(self):
        """Test customer location sharing functionality"""
        print("\n📍 Testing customer location sharing...")
        
        # Test location data (Cairo coordinates)
        location_data = {
            "latitude": 30.0444,
            "longitude": 31.2357,
            "accuracy": 10.0,
            "formatted_address": "القاهرة، مصر",
            "address_components": {
                "city": "القاهرة",
                "governorate": "القاهرة",
                "country": "مصر"
            }
        }
        
        # Update customer location
        response = self.session.post(f"{BASE_URL}/customers/location", json=location_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Customer location updated successfully!")
            print(f"   Location ID: {data['location']['id']}")
            print(f"   Coordinates: {data['location']['latitude']}, {data['location']['longitude']}")
            
            # Get customer location
            get_response = self.session.get(f"{BASE_URL}/customers/location")
            if get_response.status_code == 200:
                location = get_response.json()['location']
                print(f"✅ Customer location retrieved successfully!")
                print(f"   Active: {location['is_active']}")
                print(f"   Last updated: {location['last_updated']}")
                return True
            else:
                print(f"❌ Failed to retrieve customer location: {get_response.status_code}")
                return False
        else:
            print(f"❌ Failed to update customer location: {response.status_code} - {response.text}")
            return False
    
    def test_nearby_providers_search(self):
        """Test nearby providers search with customer location"""
        print("\n🔍 Testing nearby providers search...")
        
        # First, get available services
        services_response = self.session.get(f"{BASE_URL}/services")
        if services_response.status_code != 200:
            print(f"❌ Failed to get services: {services_response.status_code}")
            return False
        
        services = services_response.json().get('services', [])
        if not services:
            print("❌ No services available for testing")
            return False
        
        test_service = services[0]
        print(f"   Testing with service: {test_service['name']} (ID: {test_service['id']})")
        
        # Search for nearby providers
        search_data = {
            "service_id": test_service['id'],
            "latitude": 30.0444,
            "longitude": 31.2357,
            "max_distance_km": 25
        }
        
        response = self.session.post(f"{BASE_URL}/customers/nearby-providers", json=search_data)
        
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ Nearby providers search successful!")
            print(f"   Found {len(providers)} providers within {data['max_distance_km']}km")
            
            for i, provider in enumerate(providers[:3], 1):  # Show first 3
                print(f"   {i}. {provider.get('full_name', 'Unknown')} - {provider.get('distance_km', 0)}km away")
                if provider.get('current_location'):
                    print(f"      📍 Online with live location")
                    
            return True
        else:
            print(f"❌ Nearby providers search failed: {response.status_code} - {response.text}")
            return False
    
    def test_provider_search_fixed(self):
        """Test that the original provider search now works correctly"""
        print("\n🔧 Testing fixed provider search...")
        
        # Get available services
        services_response = self.session.get(f"{BASE_URL}/services")
        if services_response.status_code != 200:
            print(f"❌ Failed to get services: {services_response.status_code}")
            return False
        
        services = services_response.json().get('services', [])
        if not services:
            print("❌ No services available for testing")
            return False
        
        test_service = services[0]
        
        # Test original search endpoint
        search_data = {
            "service_id": test_service['id'],
            "latitude": 30.0444,
            "longitude": 31.2357,
            "max_distance_km": 25
        }
        
        response = self.session.post(f"{BASE_URL}/services/search", json=search_data)
        
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"✅ Original provider search fixed!")
            print(f"   Found {len(providers)} providers")
            print(f"   Service: {data.get('service', {}).get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Original provider search still failing: {response.status_code} - {response.text}")
            return False
    
    def test_booking_creation(self):
        """Test booking creation with fixed data format"""
        print("\n📅 Testing booking creation...")
        
        # Get available services and providers
        services_response = self.session.get(f"{BASE_URL}/services")
        if services_response.status_code != 200:
            print(f"❌ Failed to get services: {services_response.status_code}")
            return False
        
        services = services_response.json().get('services', [])
        if not services:
            print("❌ No services available for testing")
            return False
        
        test_service = services[0]
        
        # Search for providers
        search_data = {
            "service_id": test_service['id'],
            "latitude": 30.0444,
            "longitude": 31.2357,
            "max_distance_km": 25
        }
        
        search_response = self.session.post(f"{BASE_URL}/services/search", json=search_data)
        if search_response.status_code != 200:
            print(f"❌ Failed to search providers: {search_response.status_code}")
            return False
        
        providers = search_response.json().get('providers', [])
        if not providers:
            print("❌ No providers available for testing")
            return False
        
        test_provider = providers[0]
        
        # Create booking with correct format
        scheduled_date = datetime.now() + timedelta(days=1)
        booking_data = {
            "service_id": test_service['id'],
            "provider_id": test_provider['id'],
            "scheduled_date": scheduled_date.strftime("%Y-%m-%dT10:00:00"),
            "special_instructions": "Test booking from automated test",
            "service_address": {
                "street": "شارع التحرير",
                "city": "القاهرة",
                "governorate": "القاهرة",
                "latitude": 30.0444,
                "longitude": 31.2357,
                "formatted_address": "شارع التحرير، القاهرة، مصر",
                "phone": "01234567890"
            },
            "is_emergency": False
        }
        
        response = self.session.post(f"{BASE_URL}/services/bookings", json=booking_data)
        
        if response.status_code == 201:
            booking = response.json().get('booking', {})
            print(f"✅ Booking created successfully!")
            print(f"   Booking ID: {booking.get('id')}")
            print(f"   Status: {booking.get('booking_status')}")
            print(f"   Provider: {test_provider.get('full_name')}")
            print(f"   Service: {test_service.get('name')}")
            print(f"   Total Amount: {booking.get('total_amount')} EGP")
            return True
        else:
            print(f"❌ Booking creation failed: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive booking and location tests...\n")
        
        results = {}
        
        # Login
        results['login'] = self.login_customer()
        if not results['login']:
            print("❌ Cannot continue tests without login")
            return results
        
        # Test customer location sharing
        results['location_sharing'] = self.test_customer_location_sharing()
        
        # Test nearby providers search
        results['nearby_providers'] = self.test_nearby_providers_search()
        
        # Test fixed provider search
        results['provider_search_fixed'] = self.test_provider_search_fixed()
        
        # Test booking creation
        results['booking_creation'] = self.test_booking_creation()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The booking and location features are working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the error messages above.")
        
        return results

def main():
    """Main function"""
    tester = BookingLocationTester()
    results = tester.run_all_tests()
    return results

if __name__ == "__main__":
    main()