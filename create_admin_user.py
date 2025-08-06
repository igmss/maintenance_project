#!/usr/bin/env python3
"""
Create an admin user for testing admin frontend
"""

import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def create_admin_user():
    """Create an admin user for admin frontend testing"""
    print("🔧 Creating Admin User")
    print("-" * 30)
    
    admin_user = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '+201234567895',
        'password': 'Admin123!@#',
        'user_type': 'admin',  # This should be supported
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
    """Test admin login"""
    print("\n🧪 Testing Admin Login")
    print("-" * 30)
    
    admin_login = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'Admin123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            login_data = response.json()
            user = login_data.get('user', {})
            if user.get('user_type') == 'admin':
                print("   ✅ Admin login successful!")
                print(f"   📝 User type: {user.get('user_type')}")
                print(f"   📝 Token: {login_data.get('access_token', 'None')[:20]}...")
                return True
            else:
                print(f"   ⚠️ Login successful but user is not admin: {user.get('user_type')}")
                return False
        else:
            print(f"   ❌ Admin login failed: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
        return False

if __name__ == "__main__":
    print("🏢 Admin User Setup")
    print("=" * 40)
    
    # Note: Need to run fix_login_issues.sql in database first
    print("⚠️  IMPORTANT: Run fix_login_issues.sql in Supabase first!")
    print("   SQL: ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';")
    print()
    
    admin_created = create_admin_user()
    if admin_created:
        admin_login_works = test_admin_login()
        
        print("\n" + "=" * 40)
        print("📊 ADMIN SETUP SUMMARY")
        print("=" * 40)
        print(f"Admin user: {'✅ Ready' if admin_created else '❌ Failed'}")
        print(f"Admin login: {'✅ Working' if admin_login_works else '❌ Failed'}")
        
        if admin_created and admin_login_works:
            print("\n🎉 Admin frontend is ready!")
            print("📝 Admin credentials:")
            print("   Email: admin@maintenanceplatform.com")
            print("   Password: Admin123!@#")
        else:
            print("\n⚠️ Issues found with admin setup")