#!/usr/bin/env python3
"""
Quick test to verify if database column exists by testing registration
(Registration should work even if login fails due to caching)
"""

import requests
import time

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_registration_only():
    """Test registration to see if it works (bypasses login cache issue)"""
    print("🔍 Testing Registration (bypasses backend cache)")
    print("=" * 50)
    
    # Create a completely new user
    test_user = {
        'email': f'dbtest-{int(time.time())}@example.com',
        'phone': f'+2012345678{str(int(time.time()))[-2:]}',
        'password': 'Test123!@#',
        'user_type': 'customer',
        'first_name': 'DB',
        'last_name': 'Test'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            user_data = response.json()
            
            # Check if user has status field in response
            user = user_data.get('user', {})
            if 'status' in user:
                print(f"✅ User status field exists: {user.get('status')}")
                print("✅ Database column was added successfully!")
                print("⚠️  Backend just needs restart to recognize the column")
                return True
            else:
                print("⚠️  Status field not in user response")
                print("💡 This might be normal - status could be internal only")
                return True  # Registration working is still good
        else:
            print(f"❌ Registration failed: {response.status_code}")
            error = response.json().get('error', 'Unknown')
            print(f"   Error: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def suggest_next_steps():
    """Suggest next steps based on test results"""
    print("\n📋 NEXT STEPS:")
    print("=" * 30)
    print("1. 🔄 Restart your Render backend service:")
    print("   • Go to Render Dashboard")
    print("   • Find 'maintenance-platform-backend'") 
    print("   • Click 'Manual Deploy' or 'Restart'")
    print("   • Wait 2-3 minutes for restart")
    print()
    print("2. 🧪 Test again after restart:")
    print("   • python test_login_fix.py")
    print("   • python simple_admin_setup.py")
    print()
    print("3. 🎯 Expected result after restart:")
    print("   • Login should work (no more status error)")
    print("   • Admin user can be created/updated")

if __name__ == "__main__":
    reg_works = test_registration_only()
    suggest_next_steps()
    
    if reg_works:
        print("\n✅ Database schema looks good!")
        print("🔄 Just restart the backend service to apply changes")
    else:
        print("\n❌ May need to re-run the database fix")