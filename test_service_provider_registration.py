#!/usr/bin/env python3
"""
Test service provider registration fix
"""

import requests
import time
from datetime import datetime, date

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_service_provider_registration():
    print("👷 Testing Service Provider Registration")
    print("=" * 45)
    
    # Generate unique test data
    timestamp = int(time.time())
    test_email = f"provider{timestamp}@example.com"
    test_phone = f"010{timestamp % 100000000:08d}"
    test_password = "ProviderPass123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    # Test service provider registration
    print("1️⃣ Testing Service Provider Registration...")
    
    registration_data = {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "user_type": "service_provider",
        "first_name": "Ahmed",
        "last_name": "Provider",
        "national_id": "12345678901234",  # 14 digit Egyptian national ID
        "date_of_birth": "1990-05-15",   # YYYY-MM-DD format
        "preferred_language": "ar",
        "business_name": "Ahmed's Maintenance Services"  # Optional
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Service provider registration successful!")
            result = response.json()
            user = result.get('user', {})
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            print(f"   Access Token: {result.get('access_token', 'NOT_FOUND')[:20]}...")
            
            # Test login with the new service provider
            print("\n2️⃣ Testing Service Provider Login...")
            login_data = {
                "email_or_phone": test_email,
                "password": test_password
            }
            
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if login_response.status_code == 200:
                print("   ✅ Service provider login successful!")
                login_result = login_response.json()
                print(f"   Login User Type: {login_result.get('user', {}).get('user_type')}")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                try:
                    error = login_response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Raw: {login_response.text}")
            
        elif response.status_code == 400:
            try:
                error = response.json()
                error_msg = error.get('error', '')
                if "'national_id' is an invalid keyword argument" in error_msg:
                    print("   ❌ Still has national_id model issue - database/backend not updated")
                elif "national_id is required" in error_msg:
                    print("   ❌ Missing national_id in request")
                elif "date_of_birth is required" in error_msg:
                    print("   ❌ Missing date_of_birth in request")
                else:
                    print(f"   ❌ Validation error: {error_msg}")
            except:
                print(f"   ❌ 400 error: {response.text}")
                
        elif response.status_code == 409:
            print("   ℹ️ User already exists (test successful)")
            
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Response: {error}")
            except:
                print(f"   Raw: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_customer_registration_still_works():
    print("\n👤 Testing Customer Registration (Should Still Work)")
    print("=" * 55)
    
    timestamp = int(time.time())
    test_email = f"customer{timestamp}@example.com"
    test_phone = f"012{timestamp % 100000000:08d}"
    
    customer_data = {
        "email": test_email,
        "phone": test_phone,
        "password": "CustomerPass123!",
        "user_type": "customer",
        "first_name": "Sara",
        "last_name": "Customer"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=customer_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 201:
            print("   ✅ Customer registration still works!")
        elif response.status_code == 409:
            print("   ✅ Customer registration works (user exists)")
        else:
            print(f"   ❌ Customer registration broken: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Customer test failed: {e}")

if __name__ == "__main__":
    print(f"🧪 Testing Service Provider Registration Fix")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    test_service_provider_registration()
    test_customer_registration_still_works()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("✅ If registration works: Backend + database fix successful")
    print("❌ If 'invalid keyword argument': Run database migration")
    print("💡 Need to run: database/fix_service_provider_profiles.sql")
    print("🚀 Then redeploy backend to pick up model changes")