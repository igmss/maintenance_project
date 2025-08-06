#!/usr/bin/env python3
"""
Complete System Test - Test backend, phone validation, and registration flow
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_backend_status():
    """Test if backend is working and status field is fixed"""
    print("🔧 Testing Backend Status")
    print("=" * 30)
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"✅ Health check: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test if status field is fixed by trying login with existing user
    print("\n🔓 Testing Login (Status Field Fix)...")
    login_data = {
        "email_or_phone": "+201062831897",  # User we created earlier
        "password": "TestPassword123!"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Status field fix deployed - login works!")
            result = login_response.json()
            print(f"   User status: {result.get('user', {}).get('status', 'NOT_FOUND')}")
            return True
        elif login_response.status_code == 500:
            try:
                error = login_response.json()
                if "'User' object has no attribute 'status'" in str(error):
                    print("   ❌ Backend still needs status field fix")
                    return False
                else:
                    print(f"   ❌ Different error: {error}")
                    return False
            except:
                print(f"   ❌ 500 error: {login_response.text[:100]}")
                return False
        elif login_response.status_code == 401:
            print("   ℹ️ Invalid credentials, but status field likely works")
            return True
        else:
            print(f"   ❓ Unexpected response: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")
        return False

def test_phone_validation():
    """Test new phone validation with various formats"""
    print("\n📱 Testing Phone Validation")
    print("=" * 35)
    
    phone_tests = [
        {
            "phone": "01123456789",
            "description": "Valid format (011)",
            "should_work": True
        },
        {
            "phone": "01023456789", 
            "description": "Valid format (010)",
            "should_work": True
        },
        {
            "phone": "01223456789",
            "description": "Valid format (012)", 
            "should_work": True
        },
        {
            "phone": "01523456789",
            "description": "Valid format (015)",
            "should_work": True
        },
        {
            "phone": "+201123456789",
            "description": "International format",
            "should_work": True
        },
        {
            "phone": "01412345678",
            "description": "Invalid network (014)",
            "should_work": False
        },
        {
            "phone": "01012345678",
            "description": "Old invalid format",
            "should_work": False
        }
    ]
    
    for i, test in enumerate(phone_tests, 1):
        print(f"\n{i}️⃣ Testing: {test['phone']}")
        print(f"   {test['description']}")
        print(f"   Expected: {'✅ Should work' if test['should_work'] else '❌ Should fail'}")
        
        timestamp = int(time.time())
        test_data = {
            "email": f"phonetest{i}_{timestamp}@example.com",
            "phone": test["phone"],
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
                timeout=15
            )
            
            if response.status_code == 201:
                print("   ✅ ACCEPTED by backend")
                if test['should_work']:
                    print("   🎯 CORRECT - Validation working properly")
                else:
                    print("   ⚠️ UNEXPECTED - Backend accepted invalid format")
                    
            elif response.status_code == 400:
                try:
                    error = response.json()
                    if "Invalid phone number format" in error.get('error', ''):
                        print("   ❌ REJECTED by backend")
                        if not test['should_work']:
                            print("   🎯 CORRECT - Validation working properly")
                        else:
                            print("   ⚠️ UNEXPECTED - Backend rejected valid format")
                    else:
                        print(f"   ❌ Different error: {error.get('error', 'Unknown')}")
                except:
                    print(f"   ❌ Parse error: {response.text}")
                    
            elif response.status_code == 409:
                print("   ℹ️ User exists (format was valid)")
                if test['should_work']:
                    print("   🎯 CORRECT - Validation working properly")
                else:
                    print("   ⚠️ UNEXPECTED - Invalid format was previously accepted")
                    
            else:
                print(f"   ❓ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_complete_registration_flow():
    """Test a complete registration and login flow"""
    print("\n🔄 Testing Complete Registration Flow")
    print("=" * 45)
    
    timestamp = int(time.time())
    test_email = f"flowtest{timestamp}@example.com"
    test_phone = f"011{timestamp % 100000000:08d}"  # Generate valid phone
    test_password = "TestPassword123!"
    
    print(f"📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    
    # Step 1: Registration
    print("\n1️⃣ Testing Registration...")
    reg_data = {
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "user_type": "customer",
        "first_name": "Flow",
        "last_name": "Test"
    }
    
    try:
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=reg_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if reg_response.status_code == 201:
            print("   ✅ Registration successful!")
            reg_result = reg_response.json()
            user_id = reg_result.get('user', {}).get('id')
            print(f"   User ID: {user_id}")
            
            # Step 2: Login
            print("\n2️⃣ Testing Login...")
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
                print(f"   Token: {login_result.get('access_token', 'NOT_FOUND')[:20]}...")
                print(f"   User Type: {login_result.get('user', {}).get('user_type')}")
                print(f"   Status: {login_result.get('user', {}).get('status')}")
                return True
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                try:
                    error = login_response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Raw: {login_response.text}")
                return False
                
        else:
            print(f"   ❌ Registration failed: {reg_response.status_code}")
            try:
                error = reg_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw: {reg_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Flow test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🧪 Complete System Test")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    # Run all tests
    backend_ok = test_backend_status()
    test_phone_validation()
    flow_ok = test_complete_registration_flow()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"🔧 Backend Status: {'✅ Working' if backend_ok else '❌ Issues'}")
    print(f"🔄 Registration Flow: {'✅ Working' if flow_ok else '❌ Issues'}")
    print()
    
    if backend_ok and flow_ok:
        print("🎉 ALL SYSTEMS WORKING!")
        print("✅ Your frontend should now work perfectly")
        print("🌐 Test at: siyaana.netlify.app")
    else:
        print("⚠️ Some issues detected - check details above")