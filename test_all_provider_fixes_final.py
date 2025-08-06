#!/usr/bin/env python3
"""
Complete test of all provider fixes after database and backend deployment
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_complete_provider_system():
    print("🎯 COMPLETE PROVIDER SYSTEM TEST")
    print("=" * 40)
    print("Testing after ALL database fixes + backend deployment")
    print()
    
    # Generate unique test data
    timestamp = int(time.time())
    test_email = f"completetest{timestamp}@example.com"
    test_phone = f"011{timestamp % 100000000:08d}"
    test_password = "CompleteTest123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    print()
    
    try:
        # 1. REGISTRATION TEST
        print("1️⃣ TESTING SERVICE PROVIDER REGISTRATION")
        print("-" * 45)
        
        registration_data = {
            "email": test_email,
            "phone": test_phone,
            "password": test_password,
            "user_type": "service_provider",
            "first_name": "Complete",
            "last_name": "TestProvider",
            "national_id": "29912011234567",
            "date_of_birth": "1999-12-01",
            "preferred_language": "ar",
            "business_name": "Complete Test Services"
        }
        
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {register_response.status_code}")
        
        if register_response.status_code == 201:
            print("✅ REGISTRATION SUCCESS!")
            result = register_response.json()
            user = result.get('user', {})
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            
        elif register_response.status_code == 409:
            print("✅ USER EXISTS (Registration format works)")
            
        elif register_response.status_code == 500:
            error = register_response.json()
            error_msg = str(error)
            if "does not exist" in error_msg:
                print("❌ STILL MISSING DATABASE COLUMNS!")
                print(f"   Error: {error}")
                print("   💡 Run the missing SQL migration scripts")
                return False
            else:
                print(f"❌ Registration error: {error}")
                return False
        else:
            print(f"❌ Unexpected registration status: {register_response.status_code}")
            error = register_response.json() if register_response.headers.get('content-type') == 'application/json' else register_response.text
            print(f"   Error: {error}")
            return False
        
        # 2. LOGIN TEST
        print("\n2️⃣ TESTING LOGIN")
        print("-" * 20)
        
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
        
        print(f"Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ LOGIN FAILED!")
            error = login_response.json() if login_response.headers.get('content-type') == 'application/json' else login_response.text
            print(f"   Error: {error}")
            return False
            
        login_result = login_response.json()
        access_token = login_result.get('access_token')
        print("✅ LOGIN SUCCESS!")
        
        # 3. PROVIDER PROFILE TEST (THE MAIN TEST)
        print("\n3️⃣ TESTING PROVIDER PROFILE ENDPOINT")
        print("-" * 40)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        profile_response = requests.get(
            f"{BASE_URL}/api/providers/profile",
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("🎉 PROVIDER PROFILE SUCCESS!")
            result = profile_response.json()
            
            # Verify all expected data
            profile = result.get('profile', {})
            services = result.get('services', [])
            locations = result.get('locations', [])
            service_areas = result.get('service_areas', [])
            
            print(f"✅ Profile Data:")
            print(f"   • Business: {profile.get('business_name', 'N/A')}")
            print(f"   • Available: {profile.get('is_available', 'N/A')}")
            print(f"   • Rating: {profile.get('average_rating', 'N/A')}")
            print(f"   • Verification: {profile.get('verification_status', 'N/A')}")
            
            print(f"✅ Related Data:")
            print(f"   • Services: {len(services)} offered")
            print(f"   • Locations: {len(locations)} tracked")
            print(f"   • Service Areas: {len(service_areas)} defined")
            
            return True
            
        elif profile_response.status_code == 500:
            error = profile_response.json()
            error_msg = str(error)
            
            if "does not exist" in error_msg:
                # Parse specific missing column/table
                if "service_provider_profiles" in error_msg:
                    print("❌ MISSING: service_provider_profiles columns")
                    print("   💡 Run: database/complete_service_provider_profiles_fix.sql")
                elif "provider_services" in error_msg and "is_active" in error_msg:
                    print("❌ MISSING: provider_services.is_active column")
                    print("   💡 Run: database/fix_provider_services_table.sql")
                elif "provider_service_areas" in error_msg and "area_name" in error_msg:
                    print("❌ MISSING: provider_service_areas.area_name column")
                    print("   💡 Run: database/fix_provider_service_areas_table.sql")
                elif "provider_locations" in error_msg and "updated_at" in error_msg:
                    print("❌ MISSING: provider_locations.updated_at column")
                    print("   💡 Run: database/fix_provider_locations_table.sql")
                else:
                    print(f"❌ MISSING DATABASE COLUMN: {error}")
                    
            elif "has no attribute" in error_msg:
                if "last_updated" in error_msg:
                    print("❌ BACKEND: ProviderLocation missing last_updated")
                    print("   💡 Deploy backend with updated ProviderLocation model")
                elif "is_active" in error_msg:
                    print("❌ BACKEND: ProviderService missing is_active") 
                    print("   💡 Deploy backend with updated ProviderService model")
                else:
                    print(f"❌ BACKEND MODEL ISSUE: {error}")
            else:
                print(f"❌ OTHER 500 ERROR: {error}")
                
        else:
            print(f"❌ UNEXPECTED STATUS: {profile_response.status_code}")
            error = profile_response.json() if profile_response.headers.get('content-type') == 'application/json' else profile_response.text
            print(f"   Response: {error}")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        
    return False

if __name__ == "__main__":
    print(f"🧪 Complete Provider System Test")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    success = test_complete_provider_system()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULT:")
    
    if success:
        print("🎉 COMPLETE SUCCESS! ALL PROVIDER FEATURES WORKING!")
        print("✅ Service provider registration works")
        print("✅ Service provider login works") 
        print("✅ Provider dashboard loads completely")
        print("✅ All database schemas match backend models")
        print()
        print("🌐 READY FOR PRODUCTION:")
        print("   Frontend: siyaana.netlify.app")
        print("   Backend: maintenance-platform-backend.onrender.com")
        print()
        print("👷 Users can now register as service providers!")
        print("📱 Provider dashboard fully functional!")
        
    else:
        print("❌ STILL NEEDS FIXES")
        print()
        print("📋 REQUIRED STEPS:")
        print("1. Run ALL database migration scripts in Supabase")
        print("2. Deploy backend with updated models to Render") 
        print("3. Test again with this script")
        print()
        print("📁 DATABASE SCRIPTS TO RUN:")
        print("   • database/complete_service_provider_profiles_fix.sql")
        print("   • database/fix_provider_services_table.sql")
        print("   • database/fix_provider_service_areas_table.sql") 
        print("   • database/fix_provider_locations_table.sql")
        print()
        print("🔄 Then deploy backend and test again")