#!/usr/bin/env python3
"""
Quick API test after precise database migration
Tests the specific endpoints that were failing
"""

import requests
import json
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_critical_endpoints():
    print("🧪 Testing API after precise migration...")
    print("=" * 50)
    
    results = []
    
    # Test 1: Health check (should still work)
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("   ✅ Health: OK")
            results.append(("Health", True))
        else:
            print(f"   ❌ Health: {response.status_code}")
            results.append(("Health", False))
    except Exception as e:
        print(f"   ❌ Health: Error - {e}")
        results.append(("Health", False))
    
    # Test 2: Service categories (main fix)
    print("\n2️⃣ Testing service categories (MAIN FIX)...")
    try:
        response = requests.get(f"{BASE_URL}/api/services/categories")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            print(f"   ✅ Services: Found {len(categories)} categories")
            results.append(("Services", True))
        else:
            error = response.json().get('error', 'Unknown error')
            if 'price_unit' in error:
                print(f"   ❌ Services: Still missing price_unit column!")
            else:
                print(f"   ⚠️ Services: Different error - {error[:50]}...")
            results.append(("Services", False))
    except Exception as e:
        print(f"   ❌ Services: Error - {e}")
        results.append(("Services", False))
    
    # Test 3: User registration (second main fix)
    print("\n3️⃣ Testing user registration (SECOND FIX)...")
    try:
        test_user = {
            'email': f'test-{int(time.time())}@example.com',
            'phone': '+201234567890',
            'password': 'Test123!@#',
            'user_type': 'customer',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 201:
            print("   ✅ Registration: Successfully created user")
            results.append(("Registration", True))
        elif response.status_code == 409:
            print("   ✅ Registration: User already exists (endpoint working)")
            results.append(("Registration", True))
        else:
            error = response.json().get('error', 'Unknown error')
            if 'is_active' in error:
                print(f"   ❌ Registration: Still missing is_active column!")
            else:
                print(f"   ⚠️ Registration: Different error - {error[:50]}...")
            results.append(("Registration", False))
    except Exception as e:
        print(f"   ❌ Registration: Error - {e}")
        results.append(("Registration", False))
    
    # Test 4: Users endpoint
    print("\n4️⃣ Testing users endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Users: Found {len(data)} users")
            results.append(("Users", True))
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"   ⚠️ Users: {error[:50]}...")
            results.append(("Users", False))
    except Exception as e:
        print(f"   ❌ Users: Error - {e}")
        results.append(("Users", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION TEST RESULTS:")
    print("-" * 30)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<15}: {status}")
    
    print(f"\nSuccess Rate: {successful}/{total} ({(successful/total)*100:.0f}%)")
    
    if successful >= 3:  # Health + Services + Registration = core functionality
        print("\n🎉 MIGRATION SUCCESSFUL! Core functionality is working.")
        if successful == total:
            print("🚀 All endpoints are working perfectly!")
    else:
        print("\n⚠️ Migration may need additional fixes.")
        print("Check the specific error messages above.")

if __name__ == "__main__":
    test_critical_endpoints()