#!/usr/bin/env python3
"""
Test the provider services table fix
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_provider_profile_after_fix():
    print("👤 Testing Provider Profile After Provider Services Fix")
    print("=" * 58)
    
    # First, register a new service provider
    timestamp = int(time.time())
    test_email = f"testprovider{timestamp}@example.com"
    test_phone = f"010{timestamp % 100000000:08d}"
    test_password = "ProviderPass123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    print("1️⃣ Registering new service provider...")
    
    registration_data = {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "user_type": "service_provider",
        "first_name": "Ahmad",
        "last_name": "Provider",
        "national_id": "29501011234567",
        "date_of_birth": "1995-01-01",
        "preferred_language": "ar",
        "business_name": "Ahmad Technical Services"
    }
    
    try:
        # Register provider
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if register_response.status_code == 201:
            print("   ✅ Registration successful!")
        elif register_response.status_code == 409:
            print("   ✅ User already exists (registration works)")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            try:
                error = register_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw: {register_response.text[:200]}")
            return False
        
        # Login to get token
        print("\n2️⃣ Logging in to get access token...")
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
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
            
        login_result = login_response.json()
        access_token = login_result.get('access_token')
        
        if not access_token:
            print("   ❌ No access token received")
            return False
            
        print("   ✅ Login successful, token received")
        
        # Test provider profile endpoint
        print("\n3️⃣ Testing provider profile endpoint...")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        profile_response = requests.get(
            f"{BASE_URL}/api/providers/profile",
            headers=headers,
            timeout=15
        )
        
        print(f"   Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("   ✅ SUCCESS! Provider profile endpoint working!")
            result = profile_response.json()
            
            # Check if services are included
            services = result.get('services', [])
            print(f"   Services: {len(services)} found")
            
            # Display profile info
            profile = result.get('profile', {})
            print(f"   Provider: {profile.get('business_name', 'N/A')}")
            print(f"   Available: {profile.get('is_available', 'N/A')}")
            
            return True
            
        elif profile_response.status_code == 500:
            try:
                error = profile_response.json()
                error_msg = str(error)
                
                if "is_available" in error_msg or "is_active" in error_msg:
                    print("   ❌ Still missing is_available column in provider_services")
                    print("   💡 Run: database/fix_provider_services_table.sql")
                elif "does not exist" in error_msg:
                    print(f"   ❌ Missing database column: {error}")
                    print("   💡 Run the SQL migration script")
                else:
                    print(f"   ❌ Different 500 error: {error}")
                    
            except:
                print(f"   ❌ 500 error: {profile_response.text[:300]}")
                
        else:
            print(f"   ❓ Unexpected status: {profile_response.status_code}")
            try:
                error = profile_response.json()
                print(f"   Response: {error}")
            except:
                print(f"   Raw: {profile_response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        
    return False

def test_with_existing_provider():
    print("\n🔄 Testing with potentially existing provider...")
    print("=" * 50)
    
    # Try common test credentials
    test_credentials = [
        {"email_or_phone": "provider@example.com", "password": "provider123"},
        {"email_or_phone": "testprovider@test.com", "password": "testpass123"},
        {"email_or_phone": "01012345678", "password": "password123"}
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        print(f"{i}️⃣ Trying login with {creds['email_or_phone']}...")
        
        try:
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=creds,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                result = login_response.json()
                user = result.get('user', {})
                
                if user.get('user_type') == 'service_provider':
                    print("   ✅ Found existing service provider!")
                    
                    # Test profile
                    token = result.get('access_token')
                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
                        profile_response = requests.get(
                            f"{BASE_URL}/api/providers/profile",
                            headers=headers,
                            timeout=10
                        )
                        
                        if profile_response.status_code == 200:
                            print("   ✅ Profile endpoint works with existing provider!")
                            return True
                        else:
                            print(f"   ❌ Profile failed: {profile_response.status_code}")
                else:
                    print(f"   ⏭️  User type: {user.get('user_type')} (not service_provider)")
            else:
                print(f"   ⏭️  Login failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"   ⏭️  Error: {e}")
    
    return False

if __name__ == "__main__":
    print(f"🧪 Testing Provider Services Table Fix")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    success = test_provider_profile_after_fix()
    
    if not success:
        success = test_with_existing_provider()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    if success:
        print("🎉 PROVIDER SERVICES FIXED!")
        print("✅ Provider profile endpoint working")
        print("✅ Database schema matches backend model")
    else:
        print("❌ Still needs provider_services table fix")
        print("💡 Run: database/fix_provider_services_table.sql")
        print("🔄 Then test again")
    
    print("\n🌐 Test on frontend: siyaana.netlify.app")
    print("👤 Try logging in as a service provider")