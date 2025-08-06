#!/usr/bin/env python3
"""
Simple admin setup after database is fixed
"""

import requests

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def quick_admin_test():
    """Quick test to see if we can create admin user"""
    print("🔧 Quick Admin Setup Test")
    print("=" * 40)
    
    # Test 1: Try to login existing admin user
    print("1️⃣ Testing existing admin login...")
    admin_login = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'Admin123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            user_data = response.json()
            user_type = user_data['user']['user_type']
            print(f"   ✅ Login works! User type: {user_type}")
            
            if user_type == 'admin':
                print("   🎉 Admin user is ready!")
                return True
            else:
                user_id = user_data['user']['id']
                print(f"   ⚠️ User exists but is '{user_type}', not admin")
                print(f"   💡 Run this SQL: UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
                return False
        else:
            error = response.json().get('error', 'Unknown')
            if 'status' in error:
                print("   ❌ Database status column still missing")
                print("   💡 Run fix_login_issues.sql first")
                return False
            else:
                print(f"   ℹ️ No existing admin user found ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Login test error: {e}")
        return False
    
    # Test 2: Create new admin user (as customer first)
    print("\n2️⃣ Creating new admin user...")
    new_admin = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '+201234567895', 
        'password': 'Admin123!@#',
        'user_type': 'customer',  # Create as customer first
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=new_admin)
        if response.status_code == 201:
            user_data = response.json()
            user_id = user_data['user']['id']
            print(f"   ✅ User created! ID: {user_id}")
            print(f"   💡 Run this SQL: UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
            return user_id
        elif response.status_code == 409:
            print("   ℹ️ User already exists")
            return False
        else:
            print(f"   ❌ Creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Creation error: {e}")
        return False

if __name__ == "__main__":
    result = quick_admin_test()
    
    print("\n" + "=" * 40)
    if result:
        print("✅ Check output above for next SQL command to run")
    else:
        print("⚠️ Fix database status column first, then run again")