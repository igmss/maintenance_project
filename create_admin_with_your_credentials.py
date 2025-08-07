#!/usr/bin/env python3
"""
Create admin user with specific credentials provided by user
"""

import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def create_admin_user():
    """Create admin user with provided credentials"""
    print("🔧 Creating Admin User with Provided Credentials")
    print("-" * 50)
    
    admin_user = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '+201234567890',
        'password': 'admin123',
        'user_type': 'admin',
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=admin_user)
        if response.status_code == 201:
            print("   ✅ Admin user created successfully!")
            return True
        elif response.status_code == 409:
            print("   ✅ Admin user already exists!")
            return True
        else:
            print(f"   ❌ Admin user creation failed: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Error creating admin user: {e}")
        return False

def test_admin_login():
    """Test admin login with provided credentials"""
    print("\n🧪 Testing Admin Login")
    print("-" * 50)
    
    admin_login = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            login_data = response.json()
            user = login_data.get('user', {})
            print("   ✅ Login successful!")
            print(f"   📝 User type: {user.get('user_type')}")
            print(f"   📝 Email: {user.get('email')}")
            print(f"   📝 Token: {login_data.get('access_token', 'None')[:20]}...")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False

if __name__ == "__main__":
    print("🏢 Creating Admin User with Your Credentials")
    print("=" * 60)
    print("Email: admin@maintenanceplatform.com")
    print("Password: admin123")
    print("=" * 60)
    
    admin_created = create_admin_user()
    if admin_created:
        admin_login_works = test_admin_login()
        
        print("\n" + "=" * 60)
        print("📊 ADMIN SETUP SUMMARY")
        print("=" * 60)
        print(f"Admin user: {'✅ Ready' if admin_created else '❌ Failed'}")
        print(f"Admin login: {'✅ Working' if admin_login_works else '❌ Failed'}")
        
        if admin_created and admin_login_works:
            print("\n🎉 Admin user is ready!")
            print("📝 Use these credentials in the admin dashboard:")
            print("   Email: admin@maintenanceplatform.com")
            print("   Password: admin123")
        else:
            print("\n⚠️ Issues found with admin setup")