#!/usr/bin/env python3
"""
Test the booking search fix
"""

import requests
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_services_search_fix():
    print("🔧 Testing Services Search Fix")
    print("=" * 40)
    
    # First, let's get some service categories and their services
    print("1️⃣ Getting service categories...")
    try:
        categories_response = requests.get(f"{BASE_URL}/api/services/categories", timeout=10)
        
        if categories_response.status_code == 200:
            categories_data = categories_response.json()
            categories = categories_data.get('categories', [])
            
            if categories:
                first_category = categories[0]
                print(f"✅ Found category: {first_category.get('name')} (ID: {first_category.get('id')})")
                
                # Get services in this category
                print(f"\n2️⃣ Getting services in category...")
                category_id = first_category.get('id')
                
                services_response = requests.get(
                    f"{BASE_URL}/api/services/categories/{category_id}/services",
                    timeout=10
                )
                
                if services_response.status_code == 200:
                    services_data = services_response.json()
                    services = services_data.get('services', [])
                    
                    if services:
                        first_service = services[0]
                        print(f"✅ Found service: {first_service.get('name')} (ID: {first_service.get('id')})")
                        
                        # Now test the search with correct service_id
                        print(f"\n3️⃣ Testing provider search with service ID...")
                        
                        search_data = {
                            "service_id": first_service.get('id'),  # Correct parameter
                            "latitude": 30.0444,  # Cairo coordinates
                            "longitude": 31.2357,
                            "max_distance_km": 25
                        }
                        
                        search_response = requests.post(
                            f"{BASE_URL}/api/services/search",
                            json=search_data,
                            headers={"Content-Type": "application/json"},
                            timeout=15
                        )
                        
                        print(f"Search response status: {search_response.status_code}")
                        
                        if search_response.status_code == 200:
                            print("✅ SUCCESS! Provider search now working!")
                            search_result = search_response.json()
                            providers = search_result.get('providers', [])
                            print(f"Found {len(providers)} providers")
                        elif search_response.status_code == 400:
                            try:
                                error = search_response.json()
                                if "service_id is required" in str(error):
                                    print("❌ Still has service_id issue - frontend fix needed")
                                else:
                                    print(f"❌ Different validation error: {error}")
                            except:
                                print(f"❌ 400 error: {search_response.text[:200]}")
                        else:
                            print(f"❓ Unexpected status: {search_response.status_code}")
                            try:
                                error = search_response.json()
                                print(f"Response: {error}")
                            except:
                                print(f"Raw: {search_response.text[:200]}")
                    else:
                        print("❌ No services found in category")
                else:
                    print(f"❌ Failed to get services: {services_response.status_code}")
            else:
                print("❌ No categories found")
        else:
            print(f"❌ Failed to get categories: {categories_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_parameter_validation():
    print("\n🧪 Testing Parameter Validation")
    print("=" * 35)
    
    # Test with missing parameters to confirm validation
    test_cases = [
        {
            "name": "Missing service_id",
            "data": {
                "latitude": 30.0444,
                "longitude": 31.2357
            },
            "expected_error": "service_id is required"
        },
        {
            "name": "Missing latitude", 
            "data": {
                "service_id": "test-id",
                "longitude": 31.2357
            },
            "expected_error": "latitude is required"
        },
        {
            "name": "Missing longitude",
            "data": {
                "service_id": "test-id", 
                "latitude": 30.0444
            },
            "expected_error": "longitude is required"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/services/search",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                try:
                    error = response.json()
                    error_msg = error.get('error', '')
                    if test_case['expected_error'] in error_msg:
                        print(f"   ✅ Correctly rejected: {error_msg}")
                    else:
                        print(f"   ❓ Different error: {error_msg}")
                except:
                    print(f"   ❌ Could not parse error: {response.text}")
            else:
                print(f"   ❓ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    print(f"🧪 Testing Booking Search Fix")
    print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_services_search_fix()
    test_parameter_validation()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("✅ If search works: Frontend fix is successful")
    print("❌ If still 'service_id required': Redeploy frontend") 
    print("🌐 Test on your frontend: siyaana.netlify.app")