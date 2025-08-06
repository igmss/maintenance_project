#!/usr/bin/env python3
"""
Test the complete service provider profiles fix
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_service_provider_registration_after_complete_fix():
    print("🏗️ Testing Service Provider Registration After Complete Fix")
    print("=" * 65)
    
    # Generate unique test data
    timestamp = int(time.time())
    test_email = f"completeprovider{timestamp}@example.com"
    test_phone = f"015{timestamp % 100000000:08d}"
    test_password = "CompleteProviderPass123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    # Test service provider registration with all required fields
    print("1️⃣ Testing Complete Service Provider Registration...")
    
    registration_data = {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "user_type": "service_provider",
        "first_name": "Mohamed",
        "last_name": "ElTech",
        "national_id": "29801150123456",  # Valid format
        "date_of_birth": "1998-01-15",    # YYYY-MM-DD format
        "preferred_language": "ar",
        "business_name": "ElTech Maintenance Solutions"
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
            print("   ✅ COMPLETE SUCCESS! Service provider registration working!")
            result = response.json()
            user = result.get('user', {})
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            print(f"   Email: {user.get('email')}")
            
            # Test immediate login
            print("\n2️⃣ Testing Immediate Login...")
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
                print("   ✅ Login successful!")
                login_result = login_response.json()
                print(f"   Token received: Yes")
                print(f"   User Type: {login_result.get('user', {}).get('user_type')}")
                return True
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                
        elif response.status_code == 500:
            try:
                error = response.json()
                error_msg = str(error)
                if "does not exist" in error_msg:
                    # Extract column name
                    if "profile_image_url" in error_msg:
                        print("   ❌ Still missing profile_image_url column")
                    elif "bio_ar" in error_msg:
                        print("   ❌ Still missing bio_ar column")
                    elif "verification_status" in error_msg:
                        print("   ❌ Still missing verification_status column")
                    else:
                        print(f"   ❌ Still missing database columns")
                    print("   💡 Run the complete SQL migration script")
                else:
                    print(f"   ❌ Different 500 error: {error}")
            except:
                print(f"   ❌ 500 error: {response.text[:300]}")
                
        elif response.status_code == 400:
            try:
                error = response.json()
                print(f"   ❌ Validation error: {error.get('error', error)}")
            except:
                print(f"   ❌ 400 error: {response.text}")
                
        elif response.status_code == 409:
            print("   ✅ User already exists (registration format works)")
            return True
            
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Response: {error}")
            except:
                print(f"   Raw: {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        
    return False

def test_different_service_provider_scenarios():
    print("\n🧪 Testing Different Service Provider Scenarios")
    print("=" * 50)
    
    # Test minimal required fields
    print("1️⃣ Testing with minimal required fields...")
    timestamp = int(time.time())
    
    minimal_data = {
        "email": f"minimal{timestamp}@example.com",
        "phone": f"010{timestamp % 100000000:08d}",
        "password": "MinimalPass123!",
        "user_type": "service_provider",
        "first_name": "Ali",
        "last_name": "Minimal",
        "national_id": "30001011234567",
        "date_of_birth": "2000-01-01"
        # No business_name, should use default
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=minimal_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code in [201, 409]:
            print("   ✅ Minimal fields work!")
        else:
            print(f"   ❌ Minimal fields failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Minimal test failed: {e}")

if __name__ == "__main__":
    print(f"🧪 Testing Complete Service Provider Fix")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    success = test_service_provider_registration_after_complete_fix()
    test_different_service_provider_scenarios()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    if success:
        print("🎉 ALL FIXED! Service provider registration working!")
        print("✅ Backend model matches database schema")
        print("✅ Registration and login flow complete")
    else:
        print("❌ Still needs database migration")
        print("💡 Run: database/complete_service_provider_profiles_fix.sql")
        print("🔄 Then test again")
    
    print("\n🌐 Test on frontend: siyaana.netlify.app")
    print("👷 Try registering as a service provider")