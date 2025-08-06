#!/usr/bin/env python3
"""
Test with specific phone number: +201062831897
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_specific_phone():
    """Test registration with the specific phone number"""
    print("🔍 Testing with Specific Phone Number")
    print("=" * 50)
    
    # Use the specific phone number provided
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    test_phone = "+201062831897"  # User's specific phone number
    test_password = "TestPassword123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    # Test Registration
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
            print(f"   Phone (normalized): {register_result.get('user', {}).get('phone')}")
            
            # Test Login
            print("\n2️⃣ Testing Login...")
            login_data = {
                "email_or_phone": test_phone,
                "password": test_password
            }
            
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
            else:
                print(f"   ❌ Login failed!")
                try:
                    error_data = login_response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw Error: {login_response.text}")
                    
        else:
            print(f"   ❌ Registration failed!")
            try:
                error_data = register_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw Error: {register_response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_phone_variations():
    """Test different formats of the same phone number"""
    print("\n📞 Testing Phone Number Variations")
    print("=" * 50)
    
    phone_variations = [
        "+201062831897",    # International format
        "01062831897",      # Local format  
        "201062831897",     # Without + prefix
        "0020062831897"     # Alternative international
    ]
    
    for phone in phone_variations:
        print(f"\n🧪 Testing phone: {phone}")
        
        # Quick validation test (no actual registration)
        test_data = {
            "email": "test@example.com",
            "phone": phone,
            "password": "TestPassword123!",
            "user_type": "customer",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"   ✅ Format accepted!")
                # Clean up - this was just a test
                result = response.json()
                print(f"   Normalized to: {result.get('user', {}).get('phone')}")
            elif response.status_code == 409:
                print(f"   ✅ Format valid (user already exists)")
            else:
                print(f"   ❌ Format rejected: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', error_data)}")
                except:
                    print(f"   Raw: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    print(f"🚀 Testing Specific Phone Number at {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    test_specific_phone()
    test_phone_variations()