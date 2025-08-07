#!/usr/bin/env python3
"""
Create a customer user that can be manually changed to admin in database
"""

import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def create_user_for_admin():
    """Create a customer user that will be changed to admin manually"""
    print("🔧 Creating User for Admin Conversion")
    print("-" * 50)
    
    user_data = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '01012345678',
        'password': 'admin123',
        'user_type': 'customer',  # Will be changed to 'admin' manually
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=user_data)
        if response.status_code == 201:
            print("   ✅ User created successfully!")
            data = response.json()
            user_id = data.get('user', {}).get('id')
            print(f"   📝 User ID: {user_id}")
            print("   📝 Now manually change user_type to 'admin' in database")
            return True, user_id
        elif response.status_code == 409:
            print("   ⚠️ User already exists!")
            # Try to get user info via login
            login_data = {
                'email_or_phone': 'admin@maintenanceplatform.com',
                'password': 'admin123'
            }
            login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
            if login_response.status_code == 200:
                user_data = login_response.json().get('user', {})
                user_id = user_data.get('id')
                current_type = user_data.get('user_type')
                print(f"   📝 Existing User ID: {user_id}")
                print(f"   📝 Current Type: {current_type}")
                if current_type != 'admin':
                    print("   📝 Change user_type to 'admin' in database")
                else:
                    print("   ✅ User is already admin!")
                return True, user_id
            return True, None
        else:
            print(f"   ❌ User creation failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'Unknown')}")
            return False, None
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        return False, None

def test_login():
    """Test login after user creation"""
    print("\n🧪 Testing Login")
    print("-" * 50)
    
    login_data = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            user = login_result.get('user', {})
            print("   ✅ Login successful!")
            print(f"   📝 User type: {user.get('user_type')}")
            print(f"   📝 Email: {user.get('email')}")
            return True, user.get('user_type')
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'Unknown')}")
            return False, None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False, None

if __name__ == "__main__":
    print("🏢 Creating User for Admin Conversion")
    print("=" * 60)
    print("Email: admin@maintenanceplatform.com")
    print("Password: admin123")
    print("=" * 60)
    
    user_created, user_id = create_user_for_admin()
    if user_created:
        login_works, user_type = test_login()
        
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        print(f"User created: {'✅ Yes' if user_created else '❌ No'}")
        print(f"Login works: {'✅ Yes' if login_works else '❌ No'}")
        print(f"Current type: {user_type}")
        
        if user_created and login_works:
            if user_type == 'admin':
                print("\n🎉 Admin user is ready!")
            else:
                print("\n📝 MANUAL DATABASE UPDATE NEEDED:")
                print("=" * 60)
                print("Run this SQL in your database:")
                print(f"UPDATE users SET user_type = 'admin' WHERE email = 'admin@maintenanceplatform.com';")
                if user_id:
                    print(f"-- Or by ID: UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
                print("\nAfter running the SQL, the admin login will work!")
        else:
            print("\n⚠️ Issues found with user setup")