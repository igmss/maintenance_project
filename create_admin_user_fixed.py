#!/usr/bin/env python3
"""
Create admin user by registering as customer then updating to admin
"""

import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def create_admin_user_workaround():
    """Create admin user using workaround method"""
    print("🔧 Creating Admin User (Workaround Method)")
    print("-" * 50)
    
    # Step 1: Create user as 'customer' (allowed by backend)
    print("1️⃣ Creating user as customer...")
    admin_user = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '+201234567895',
        'password': 'Admin123!@#',
        'user_type': 'customer',  # Create as customer first
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=admin_user)
        if response.status_code == 201:
            print("   ✅ User created successfully as customer")
            user_data = response.json()
            user_id = user_data['user']['id']
            print(f"   📝 User ID: {user_id}")
        elif response.status_code == 409:
            print("   ✅ User already exists")
            # Try to get user ID by logging in
            login_data = {
                'email_or_phone': admin_user['email'],
                'password': admin_user['password']
            }
            login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
            if login_response.status_code == 200:
                user_id = login_response.json()['user']['id']
                print(f"   📝 Existing User ID: {user_id}")
            else:
                print("   ❌ Could not get user ID from existing user")
                return False
        else:
            print(f"   ❌ User creation failed: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        return False
    
    # Step 2: Show SQL command to update user_type to admin
    print(f"\n2️⃣ Database Update Required:")
    print("   Run this SQL in Supabase to make user an admin:")
    print("   " + "="*50)
    print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
    print("   " + "="*50)
    
    return True

def test_admin_login_after_update():
    """Test admin login after manual database update"""
    print("\n🧪 Testing Admin Login (After Database Update)")
    print("-" * 50)
    
    admin_login = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'Admin123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            login_data = response.json()
            user = login_data.get('user', {})
            user_type = user.get('user_type')
            
            print(f"   ✅ Login successful!")
            print(f"   📝 User type: {user_type}")
            print(f"   📝 Email: {user.get('email')}")
            
            if user_type == 'admin':
                print("   🎉 ADMIN USER IS READY!")
                return True
            else:
                print(f"   ⚠️ User type is '{user_type}', not 'admin'")
                print("   💡 Run the UPDATE SQL command shown above")
                return False
        else:
            error = response.json().get('error', 'Unknown')
            if 'status' in error:
                print("   ⚠️ Login failed - need to run fix_login_issues.sql first")
            else:
                print(f"   ❌ Login failed: {response.status_code} - {error}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False

if __name__ == "__main__":
    print("🏢 Admin User Setup (Fixed Method)")
    print("=" * 60)
    
    print("⚠️  PREREQUISITES:")
    print("   1. Run fix_login_issues.sql in Supabase first!")
    print("   2. Add status column to users table")
    print()
    
    # Create admin user
    user_created = create_admin_user_workaround()
    
    if user_created:
        # Test login (will show if manual update is needed)
        login_works = test_admin_login_after_update()
        
        print("\n" + "=" * 60)
        print("📊 ADMIN SETUP SUMMARY")
        print("=" * 60)
        print(f"User creation: {'✅ Complete' if user_created else '❌ Failed'}")
        print(f"Admin login: {'✅ Ready' if login_works else '⏳ Pending database update'}")
        
        if user_created and not login_works:
            print("\n📋 NEXT STEPS:")
            print("   1. Copy the UPDATE SQL command shown above")
            print("   2. Run it in Supabase SQL Editor")
            print("   3. Test login again")
        elif user_created and login_works:
            print("\n🎉 ADMIN USER IS FULLY READY!")
            print("📝 Admin credentials:")
            print("   Email: admin@maintenanceplatform.com")
            print("   Password: Admin123!@#")
    else:
        print("\n❌ Admin user creation failed")