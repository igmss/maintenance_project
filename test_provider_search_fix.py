#!/usr/bin/env python3
"""
Test provider search functionality after fixing location issues
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"
# BASE_URL = "http://localhost:8000"  # Uncomment for local testing

def test_provider_search():
    print("🔍 Testing Provider Search After Location Fix")
    print("=" * 50)
    
    # Test coordinates (Cairo center)
    test_coordinates = {
        "latitude": 30.0444,
        "longitude": 31.2357,
        "max_distance_km": 50
    }
    
    print(f"📍 Test location: {test_coordinates['latitude']}, {test_coordinates['longitude']}")
    print(f"🎯 Search radius: {test_coordinates['max_distance_km']}km")
    print()
    
    try:
        # 1. Test online providers endpoint
        print("1️⃣ Testing online providers endpoint...")
        params = {
            'latitude': test_coordinates['latitude'],
            'longitude': test_coordinates['longitude'],
            'radius': test_coordinates['max_distance_km']
        }
        
        response = requests.get(
            f"{BASE_URL}/api/providers/online",
            params=params,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print(f"   ✅ Found {len(providers)} online providers")
            
            if providers:
                print("   📋 Sample providers:")
                for i, provider in enumerate(providers[:3]):
                    distance = provider.get('distance_km', 'N/A')
                    print(f"      {i+1}. {provider.get('business_name', 'N/A')} - {distance}km away")
            else:
                print("   ⚠️  No providers found!")
        else:
            print(f"   ❌ Error: {response.text}")
        
        print()
        
        # 2. Test service search endpoint (need a service ID)
        print("2️⃣ Testing service search endpoint...")
        
        # First get available services
        services_response = requests.get(f"{BASE_URL}/api/services/categories", timeout=30)
        
        if services_response.status_code == 200:
            categories = services_response.json().get('categories', [])
            if categories and categories[0].get('services'):
                test_service_id = categories[0]['services'][0]['id']
                
                search_data = {
                    "latitude": test_coordinates['latitude'],
                    "longitude": test_coordinates['longitude'],
                    "service_id": test_service_id,
                    "max_distance_km": test_coordinates['max_distance_km']
                }
                
                search_response = requests.post(
                    f"{BASE_URL}/api/services/search",
                    json=search_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                print(f"   Status: {search_response.status_code}")
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    providers = search_data.get('providers', [])
                    print(f"   ✅ Found {len(providers)} providers for service")
                    
                    if providers:
                        print("   📋 Service providers:")
                        for i, provider in enumerate(providers[:3]):
                            distance = provider.get('distance_km', 'N/A')
                            price = provider.get('price', 'N/A')
                            print(f"      {i+1}. {provider.get('business_name', 'N/A')} - {distance}km - {price} EGP")
                else:
                    print(f"   ❌ Search error: {search_response.text}")
            else:
                print("   ⚠️  No services found to test with")
        else:
            print(f"   ❌ Could not get services: {services_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_provider_location_api():
    """Test the provider location update endpoint"""
    print("\n🌍 Testing Provider Location Update API")
    print("=" * 40)
    
    # This would require a valid provider token
    # For now, just show the expected format
    location_data = {
        "latitude": 30.0444,
        "longitude": 31.2357,
        "accuracy": 10.0,
        "is_online": True,
        "battery_level": 85
    }
    
    print("📱 Expected location update format:")
    print(f"   POST {BASE_URL}/api/providers/location")
    print(f"   Headers: Authorization: Bearer <provider_token>")
    print(f"   Body: {json.dumps(location_data, indent=2)}")
    
    print("\n💡 Note: Providers need to call this endpoint to update their location!")

def check_database_state():
    """Make API calls to check the current database state"""
    print("\n📊 Checking Database State")
    print("=" * 30)
    
    try:
        # Check if we can get any providers at all
        response = requests.get(f"{BASE_URL}/api/providers/online?radius=100", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_found = len(data.get('providers', []))
            print(f"✅ API is working - found {total_found} online providers within 100km")
            
            if total_found == 0:
                print("⚠️  This suggests:")
                print("   - Provider locations table is still empty, OR")
                print("   - Providers are not marked as online, OR") 
                print("   - There's an issue with the search query")
                print("\n🔧 Run the fix script: python3 fix_existing_providers_locations.py")
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_provider_search()
    test_provider_location_api()
    check_database_state()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("If no providers are found:")
    print("1. Run: python3 fix_existing_providers_locations.py")
    print("2. Ask providers to update their location via the mobile app")
    print("3. Check that providers are calling POST /api/providers/location")
    print("4. Verify providers are marked as online and available")
    print("\n🚀 After running the fix, providers should appear in search results!")