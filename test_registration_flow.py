#!/usr/bin/env python3
"""
Test Registration Flow - Debug registration issues from frontend perspective
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_registration_and_login():
    """Test the complete registration and login flow"""
    print("🔍 Testing Registration and Login Flow")
    print("=" * 50)
    
    # Generate unique test user
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    # Generate valid Egyptian phone: 01 + 1 + 9 digits
    test_phone = f"011{timestamp % 1000000000:09d}"  # Valid Egyptian phone format (011 + 9 digits)
    test_password = "TestPassword123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    # 1. Test Registration
    print("1️⃣ Testing Registration...")
    registration_data = {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "user_type": "customer",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {register_response.status_code}")
        
        if register_response.status_code == 201:
            print("   ✅ Registration successful!")
            register_result = register_response.json()
            print(f"   User ID: {register_result.get('user', {}).get('id')}")
            print(f"   User Type: {register_result.get('user', {}).get('user_type')}")
        else:
            print(f"   ❌ Registration failed!")
            try:
                error_data = register_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw Error: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Registration request failed: {e}")
        return False
    
    # 2. Test Login with email
    print("\n2️⃣ Testing Login with Email...")
    login_data = {
        "email_or_phone": test_email,
        "password": test_password
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Login successful!")
            login_result = login_response.json()
            print(f"   Token: {login_result.get('access_token', 'NOT_FOUND')[:20]}...")
            print(f"   User Type: {login_result.get('user', {}).get('user_type')}")
        else:
            print(f"   ❌ Login failed!")
            try:
                error_data = login_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw Error: {login_response.text}")
                
    except Exception as e:
        print(f"   ❌ Login request failed: {e}")
    
    # 3. Test Login with phone
    print("\n3️⃣ Testing Login with Phone...")
    login_data_phone = {
        "email_or_phone": test_phone,
        "password": test_password
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data_phone,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Phone login successful!")
        else:
            print(f"   ❌ Phone login failed!")
            try:
                error_data = login_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw Error: {login_response.text}")
                
    except Exception as e:
        print(f"   ❌ Phone login request failed: {e}")
    
    return True

def test_invalid_registrations():
    """Test various invalid registration scenarios"""
    print("\n🚫 Testing Invalid Registration Scenarios")
    print("=" * 50)
    
    invalid_scenarios = [
        {
            "name": "Missing Email",
            "data": {
                "phone": "01123456789",
                "password": "TestPass123!",
                "user_type": "customer",
                "first_name": "Test",
                "last_name": "User"
            }
        },
        {
            "name": "Invalid User Type",
            "data": {
                "email": "test@example.com",
                "phone": "01123456789", 
                "password": "TestPass123!",
                "user_type": "admin",  # Should be rejected
                "first_name": "Test",
                "last_name": "User"
            }
        },
        {
            "name": "Short Password",
            "data": {
                "email": "test2@example.com",
                "phone": "01223456789",
                "password": "123",
                "user_type": "customer",
                "first_name": "Test",
                "last_name": "User"
            }
        },
        {
            "name": "Missing Required Fields",
            "data": {
                "email": "test3@example.com"
                # Missing phone, password, user_type
            }
        }
    ]
    
    for scenario in invalid_scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=scenario['data'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code != 201:
                print(f"   ✅ Correctly rejected!")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', error_data)}")
                except:
                    print(f"   Raw Response: {response.text}")
            else:
                print(f"   ❌ Unexpectedly accepted!")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_backend_health():
    """Quick backend health check"""
    print("🏥 Backend Health Check")
    print("=" * 30)
    
    endpoints = [
        "/api/health",
        "/api/info", 
        "/api/services/categories"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    print()

if __name__ == "__main__":
    print(f"🚀 Testing Registration Flow at {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    # Run tests
    test_backend_health()
    test_registration_and_login()
    test_invalid_registrations()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("- Check registration errors above")
    print("- Check login flow after successful registration") 
    print("- Verify error handling for invalid data")