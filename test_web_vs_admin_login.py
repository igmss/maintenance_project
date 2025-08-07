#!/usr/bin/env python3
"""
Test Web vs Admin Login - Understand the difference
"""
import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_web_login():
    print("🌐 Testing Web Frontend Login")
    print("=" * 50)
    
    # Test with a customer account (like what works in web frontend)
    # First try to create a test customer
    customer_data = {
        'email': 'testcustomer@example.com',
        'phone': '+201234567891',
        'password': 'Test123!',
        'user_type': 'customer',
        'first_name': 'Test',
        'last_name': 'Customer'
    }
    
    print("1️⃣ Creating test customer...")
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=customer_data)
        if response.status_code == 201:
            print("   ✅ Customer created successfully")
        elif response.status_code == 409:
            print("   ✅ Customer already exists")
        else:
            print(f"   ❌ Customer creation failed: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2️⃣ Testing customer login...")
    login_data = {
        'email_or_phone': 'testcustomer@example.com',
        'password': 'Test123!'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print("   ✅ Customer login successful!")
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Status: {user.get('status')}")
            return True
        else:
            error_data = response.json()
            print(f"   ❌ Login failed: {error_data.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_admin_user_exists():
    print("\n🔍 Checking if admin user exists in database")
    print("=" * 50)
    
    # Try to register admin user to see what happens
    admin_data = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '+201234567890',
        'password': 'admin123',
        'user_type': 'customer',  # Try as customer first
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    print("1️⃣ Attempting to register admin email as customer...")
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=admin_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 409:
            print("   ✅ Admin user already exists in database")
            return True
        elif response.status_code == 201:
            print("   ✅ Admin user was created as customer (needs upgrade)")
            return True
        else:
            error_data = response.json()
            print(f"   ❌ Registration failed: {error_data.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_admin_login_detailed():
    print("\n🔐 Testing Admin Login (Detailed)")
    print("=" * 50)
    
    admin_credentials = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'admin123'
    }
    
    print("1️⃣ Testing admin login...")
    print(f"   Email: {admin_credentials['email_or_phone']}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=admin_credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print("   ✅ Login successful!")
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Status: {user.get('status')}")
            
            if user.get('user_type') == 'admin':
                print("   ✅ User has admin privileges!")
                return True
            else:
                print("   ⚠️  User exists but is not admin type")
                print(f"   Current type: {user.get('user_type')}")
                print("   → Need to update user_type to 'admin' in database")
                return False
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
                print(f"   ❌ Login failed: {error_msg}")
                
                if 'Invalid salt' in error_msg:
                    print("   → Password hash issue - need to reset password")
                elif 'Invalid credentials' in error_msg:
                    print("   → Either user doesn't exist or password is wrong")
                elif 'suspended' in error_msg.lower():
                    print("   → Account is suspended")
                
            except:
                print(f"   ❌ Login failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Web vs Admin Login Comparison Test")
    print("=" * 60)
    
    # Test backend health
    try:
        health_response = requests.get(f"{BACKEND_URL}/health")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
    except:
        print("❌ Cannot reach backend")
    
    # Run tests
    web_success = test_web_login()
    admin_exists = check_admin_user_exists()
    admin_success = test_admin_login_detailed()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Web Frontend Login:     {'✅ WORKING' if web_success else '❌ FAILED'}")
    print(f"Admin User Exists:      {'✅ YES' if admin_exists else '❌ NO'}")
    print(f"Admin Login:           {'✅ WORKING' if admin_success else '❌ FAILED'}")
    
    if web_success and not admin_success:
        print("\n💡 DIAGNOSIS:")
        print("   - Backend auth system is working (web login works)")
        print("   - Issue is specifically with admin user setup")
        print("\n🔧 RECOMMENDED FIXES:")
        if admin_exists:
            print("   1. Run comprehensive_db_fix.sql in Supabase")
            print("   2. This will fix user_type and password hash")
        else:
            print("   1. Create admin user with proper credentials")
            print("   2. Set user_type to 'admin' in database")