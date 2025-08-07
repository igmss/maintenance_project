#!/usr/bin/env python3
"""
Test Admin Login
"""
import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_admin_login():
    print("🧪 Testing Admin Login")
    print("=" * 50)
    
    # Test with user provided credentials
    admin_credentials = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'admin123'
    }
    
    print("1️⃣ Testing with provided credentials...")
    print(f"   Email: {admin_credentials['email_or_phone']}")
    print(f"   Password: {admin_credentials['password']}")
    
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
                print("   ❌ User does not have admin privileges")
                print("   Need to update user_type to 'admin' in database")
                return False
        else:
            error_data = response.json()
            print(f"   ❌ Login failed: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_demo_credentials():
    print("\n2️⃣ Testing with demo credentials from frontend...")
    
    # Test with demo credentials shown in frontend
    demo_credentials = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'admin123'  # Same as provided, just confirming
    }
    
    print(f"   Email: {demo_credentials['email_or_phone']}")
    print(f"   Password: {demo_credentials['password']}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json=demo_credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print("   ✅ Demo login successful!")
            print(f"   User Type: {user.get('user_type')}")
            return True
        else:
            error_data = response.json()
            print(f"   ❌ Demo login failed: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Admin Login Test")
    print("=" * 50)
    
    # Test backend health first
    try:
        health_response = requests.get(f"{BACKEND_URL}/health")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print("❌ Backend health check failed")
    except:
        print("❌ Cannot reach backend")
    
    success1 = test_admin_login()
    success2 = test_demo_credentials()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    if success1 or success2:
        print("✅ Admin login is working!")
    else:
        print("❌ Admin login needs to be fixed")
        print("\n💡 Next steps:")
        print("   1. Check if admin user exists in database")
        print("   2. Verify user_type is set to 'admin'")
        print("   3. Ensure user status is 'active'")