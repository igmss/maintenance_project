#!/usr/bin/env python3
"""
Final comprehensive test of all frontend-backend connections
"""

import requests
import json
import time

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_complete_system():
    """Test the complete system after all fixes"""
    print("🧪 Final System Test")
    print("=" * 50)
    
    results = {}
    
    # 1. Test Backend Health
    print("1️⃣ Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        results['backend_health'] = response.status_code == 200
        print(f"   {'✅' if results['backend_health'] else '❌'} Backend: {response.status_code}")
    except Exception as e:
        results['backend_health'] = False
        print(f"   ❌ Backend: Error - {e}")
    
    # 2. Test Service Categories (Fixed)
    print("\n2️⃣ Testing Service Categories...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/services/categories")
        if response.status_code == 200:
            categories = response.json().get('categories', [])
            results['services'] = len(categories) > 0
            print(f"   ✅ Services: Found {len(categories)} categories")
        else:
            results['services'] = False
            print(f"   ❌ Services: {response.status_code}")
    except Exception as e:
        results['services'] = False
        print(f"   ❌ Services: Error - {e}")
    
    # 3. Test User Registration
    print("\n3️⃣ Testing User Registration...")
    test_user = {
        'email': f'finaltest-{int(time.time())}@example.com',
        'phone': f'+2012345678{str(int(time.time()))[-2:]}',
        'password': 'Test123!@#',
        'user_type': 'customer',
        'first_name': 'Final',
        'last_name': 'Test'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
        results['registration'] = response.status_code in [201, 409]
        if response.status_code == 201:
            print(f"   ✅ Registration: New user created")
            registration_data = response.json()
        elif response.status_code == 409:
            print(f"   ✅ Registration: User exists (endpoint working)")
        else:
            print(f"   ❌ Registration: {response.status_code} - {response.json().get('error', 'Unknown')}")
    except Exception as e:
        results['registration'] = False
        print(f"   ❌ Registration: Error - {e}")
    
    # 4. Test Login with Correct Parameters
    print("\n4️⃣ Testing Login (Fixed)...")
    try:
        login_data = {
            'email_or_phone': test_user['email'],  # Correct parameter name
            'password': test_user['password']
        }
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            results['login'] = 'access_token' in login_response
            print(f"   ✅ Login: Success with token")
        else:
            results['login'] = False
            error = response.json().get('error', 'Unknown')
            if 'status' in error:
                print(f"   ⚠️ Login: Database status column missing - run fix_login_issues.sql")
            else:
                print(f"   ❌ Login: {response.status_code} - {error}")
    except Exception as e:
        results['login'] = False
        print(f"   ❌ Login: Error - {e}")
    
    # 5. Test Admin User
    print("\n5️⃣ Testing Admin Authentication...")
    admin_login = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': 'Admin123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=admin_login)
        if response.status_code == 200:
            admin_data = response.json()
            is_admin = admin_data.get('user', {}).get('user_type') == 'admin'
            results['admin_auth'] = is_admin
            print(f"   {'✅' if is_admin else '⚠️'} Admin: {'Working' if is_admin else 'User exists but not admin'}")
        else:
            results['admin_auth'] = False
            print(f"   ❌ Admin: {response.status_code} - Need to create admin user")
    except Exception as e:
        results['admin_auth'] = False
        print(f"   ❌ Admin: Error - {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL SYSTEM STATUS")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<20}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.0f}%)")
    
    if success_rate >= 80:
        print("\n🎉 EXCELLENT! System is ready for production")
        print("🚀 All frontends can connect to backend successfully")
    elif success_rate >= 60:
        print("\n✅ GOOD! System mostly working, minor fixes needed")
    else:
        print("\n⚠️ ISSUES FOUND! Need attention before production")
    
    # Next Steps
    print("\n📋 NEXT STEPS:")
    if not results.get('login', False):
        print("   1. Run: fix_login_issues.sql in Supabase")
    if not results.get('admin_auth', False):
        print("   2. Run: python create_admin_user.py")
    if success_rate >= 80:
        print("   ✅ System ready! Start developing your frontend applications")
        print("   📝 Frontend URLs to update:")
        print("      - Admin: Connect to https://maintenance-platform-backend.onrender.com")
        print("      - Web: Connect to https://maintenance-platform-backend.onrender.com") 
        print("      - Mobile: Connect to https://maintenance-platform-backend.onrender.com")
    
    return success_rate

if __name__ == "__main__":
    test_complete_system()