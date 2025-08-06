#!/usr/bin/env python3
"""
Test everything after backend restart
"""

import requests

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_after_restart():
    """Test login after backend restart"""
    print("🔄 Testing After Backend Restart")
    print("=" * 40)
    
    # Test login with existing user
    login_data = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'Admin123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ LOGIN WORKS! Status column fixed!")
            user_data = response.json()
            user = user_data['user']
            user_type = user.get('user_type')
            user_id = user.get('id')
            
            print(f"📝 User type: {user_type}")
            print(f"📝 User ID: {user_id}")
            
            if user_type == 'admin':
                print("🎉 ADMIN USER IS READY!")
                return True
            else:
                print(f"⚠️  User is '{user_type}', needs to be admin")
                print(f"💡 Run: UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
                return 'partial'
        else:
            error = response.json().get('error', 'Unknown')
            if 'status' in error:
                print("❌ Still getting status error - backend may not be restarted yet")
                print("⏳ Wait a bit longer and try again")
                return False
            else:
                print(f"ℹ️  Different error: {response.status_code} - {error}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = test_after_restart()
    
    print("\n" + "=" * 40)
    if result is True:
        print("🎉 EVERYTHING IS WORKING!")
    elif result == 'partial':
        print("✅ Login fixed! Just need to make user admin")
    else:
        print("⏳ Backend may still be restarting - try again in 1-2 minutes")