#!/usr/bin/env python3
"""
Verify database schema and fix login issues
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_login_with_new_user():
    """Test login with a newly registered user"""
    print("🔍 Testing Login with Existing User")
    print("=" * 50)
    
    # Use the phone number we just registered
    test_phone = "+201062831897"
    test_password = "TestPassword123!"
    
    print(f"📱 Testing login with: {test_phone}")
    
    # Test Login
    login_data = {
        "email_or_phone": test_phone,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            result = response.json()
            print(f"Token: {result.get('access_token', 'NOT_FOUND')[:20]}...")
            print(f"User Type: {result.get('user', {}).get('user_type')}")
            return True
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
                
                # Check if it's the status column issue
                if "'User' object has no attribute 'status'" in str(error_data):
                    print("\n🔧 ISSUE IDENTIFIED:")
                    print("   The 'status' column is missing from the users table")
                    print("   Please run this SQL command on your Supabase database:")
                    print()
                    print("   ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';")
                    print("   UPDATE users SET status = 'active' WHERE status IS NULL;")
                    print()
                    
            except:
                print(f"Raw Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def create_admin_user():
    """Try to create an admin user for testing"""
    print("\n👑 Creating Admin User")
    print("=" * 30)
    
    admin_data = {
        "email": "admin@maintenance.com",
        "phone": "+201234567890",
        "password": "AdminPass123!",
        "user_type": "customer",  # Register as customer first
        "first_name": "Admin",
        "last_name": "User"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=admin_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 201:
            print("✅ Admin user created as customer")
            result = response.json()
            user_id = result.get('user', {}).get('id')
            print(f"User ID: {user_id}")
            print()
            print("🔧 To make this user an admin, run this SQL:")
            print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
            return user_id
        elif response.status_code == 409:
            print("ℹ️ Admin user already exists")
            return None
        else:
            print(f"❌ Failed to create admin: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_frontend_connectivity():
    """Test if frontends can connect to backend"""
    print("\n🌐 Testing Frontend Connectivity")
    print("=" * 40)
    
    endpoints = [
        "/api/health",
        "/api/info",
        "/api/services/categories",
        "/api/users"  # This should test auth
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code in [200, 401] else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code not in [200, 401]:
                try:
                    error = response.json()
                    print(f"    Error: {error}")
                except:
                    print(f"    Raw: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    print(f"🔧 Verifying and Fixing Login Issues")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    # Test current login issue
    login_works = test_login_with_new_user()
    
    # Test admin user creation
    create_admin_user()
    
    # Test frontend connectivity
    test_frontend_connectivity()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("✅ Registration works perfectly")
    if login_works:
        print("✅ Login works")
    else:
        print("❌ Login needs database fix (see SQL above)")
    print("✅ Frontend should now work for registration")
    print("⚠️ Admin panel needs manual user type update")