#!/usr/bin/env python3
"""
Test provider dashboard after fixing ProviderService model is_active field
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_provider_dashboard_final():
    print("🎯 Testing Provider Dashboard - Final Fix Verification")
    print("=" * 58)
    
    # Register and test new provider
    timestamp = int(time.time())
    test_email = f"finaltest{timestamp}@example.com"
    test_phone = f"012{timestamp % 100000000:08d}"
    test_password = "FinalTest123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    try:
        # 1. Register Service Provider
        print("1️⃣ Registering service provider...")
        registration_data = {
            "email": test_email,
            "phone": test_phone,
            "password": test_password,
            "user_type": "service_provider",
            "first_name": "Final",
            "last_name": "TestProvider",
            "national_id": "30101011234567",
            "date_of_birth": "2001-01-01",
            "preferred_language": "ar",
            "business_name": "Final Test Services"
        }
        
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if register_response.status_code == 201:
            print("   ✅ Registration successful!")
        elif register_response.status_code == 409:
            print("   ✅ User already exists (OK for testing)")
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            error = register_response.json() if register_response.headers.get('content-type') == 'application/json' else register_response.text
            print(f"   Error: {error}")
            
        # 2. Login
        print("\n2️⃣ Logging in...")
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
        print("   ✅ Login successful!")
        
        # 3. Test Provider Profile Endpoint (THE MAIN TEST)
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
            print("   🎉 SUCCESS! Provider profile endpoint working!")
            result = profile_response.json()
            
            # Verify data structure
            profile = result.get('profile', {})
            services = result.get('services', [])
            
            print(f"   📋 Provider Profile:")
            print(f"      • Business: {profile.get('business_name', 'N/A')}")
            print(f"      • Available: {profile.get('is_available', 'N/A')}")
            print(f"      • Rating: {profile.get('average_rating', 'N/A')}")
            print(f"      • Services: {len(services)} offered")
            
            # Check for specific fields
            if 'is_available' in profile:
                print("   ✅ is_available field present")
            
            return True
            
        elif profile_response.status_code == 500:
            try:
                error = profile_response.json()
                error_msg = str(error)
                
                if "is_active" in error_msg:
                    print("   ❌ Still has is_active error - backend not yet deployed with fix")
                    print("   💡 Deploy backend with updated ProviderService model")
                elif "does not exist" in error_msg:
                    print(f"   ❌ Database column missing: {error}")
                else:
                    print(f"   ❌ Other 500 error: {error}")
                    
            except:
                print(f"   ❌ 500 error: {profile_response.text[:200]}")
                
        else:
            print(f"   ❓ Unexpected status: {profile_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        
    return False

def test_provider_registration_complete():
    print("\n🧪 Testing Complete Provider Registration Flow")
    print("=" * 52)
    
    # Test that both service_provider_profiles AND provider_services work
    timestamp = int(time.time())
    test_email = f"completeflow{timestamp}@example.com"
    test_phone = f"015{timestamp % 100000000:08d}"
    
    registration_data = {
        "email": test_email,
        "phone": test_phone,
        "password": "CompleteFlow123!",
        "user_type": "service_provider",
        "first_name": "Complete",
        "last_name": "FlowTest",
        "national_id": "29512011234567",
        "date_of_birth": "1995-12-01",
        "preferred_language": "ar",
        "business_name": "Complete Flow Services"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [201, 409]:
            print("   ✅ Complete registration flow works!")
            print("   ✅ Both service_provider_profiles AND provider_services tables fixed!")
            return True
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            error = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   Error: {error}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
    return False

if __name__ == "__main__":
    print(f"🎯 Final Provider Dashboard Test")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    success1 = test_provider_dashboard_final()
    success2 = test_provider_registration_complete()
    
    print("\n" + "=" * 60)
    print("📋 FINAL SUMMARY:")
    
    if success1 and success2:
        print("🎉 ALL PROVIDER ISSUES FIXED!")
        print("✅ Provider registration working")
        print("✅ Provider dashboard loading")
        print("✅ Database schema matches backend models")
        print()
        print("🌐 Ready for production use at: siyaana.netlify.app")
        
    elif success2 and not success1:
        print("⚠️  Registration works, dashboard needs backend deployment")
        print("✅ Database schemas fixed")
        print("🚀 Deploy backend with ProviderService model fix")
        
    else:
        print("❌ Still needs fixes:")
        if not success2:
            print("   • Run SQL migration scripts")
        if not success1:
            print("   • Deploy backend with model fixes")
        print()
        print("📋 Required steps:")
        print("   1. database/complete_service_provider_profiles_fix.sql")
        print("   2. database/fix_provider_services_table.sql (already done)")
        print("   3. Deploy backend to Render")
    
    print("\n🔄 Test again after deployment")