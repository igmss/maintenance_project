#!/usr/bin/env python3
"""
Test Frontend-Backend Connections
Verify that all frontend applications can properly connect to the backend
"""

import requests
import json
import time

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_admin_frontend_connection():
    """Test admin frontend connection and authentication"""
    print("🔍 Testing Admin Frontend Connection")
    print("-" * 40)
    
    # Admin frontend uses mock authentication, so we test the API endpoints it uses
    endpoints = [
        "/api/admin/dashboard",
        "/api/admin/users", 
        "/api/admin/providers",
        "/api/admin/bookings",
        "/api/services/categories"
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            if response.status_code in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                results.append((endpoint, True, response.status_code))
                print(f"   ✅ {endpoint}: {response.status_code}")
            else:
                results.append((endpoint, False, response.status_code))
                print(f"   ❌ {endpoint}: {response.status_code}")
        except Exception as e:
            results.append((endpoint, False, str(e)))
            print(f"   ❌ {endpoint}: Error - {e}")
    
    return results

def test_web_frontend_auth():
    """Test web frontend authentication endpoints"""
    print("\n🔍 Testing Web Frontend Authentication")
    print("-" * 40)
    
    # Test registration
    print("1️⃣ Testing Registration...")
    test_user = {
        'email': f'webtest-{int(time.time())}@example.com',
        'phone': '+201234567893',
        'password': 'Test123!@#',
        'user_type': 'customer',
        'first_name': 'Web',
        'last_name': 'Test'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
        if response.status_code in [201, 409]:  # 201 = created, 409 = already exists
            print(f"   ✅ Registration: {response.status_code} - Working")
            reg_success = True
            if response.status_code == 201:
                reg_data = response.json()
        else:
            print(f"   ❌ Registration: {response.status_code} - {response.json().get('error', 'Unknown')}")
            reg_success = False
    except Exception as e:
        print(f"   ❌ Registration: Error - {e}")
        reg_success = False
    
    # Test login
    print("\n2️⃣ Testing Login...")
    try:
        login_data = {
            'email': test_user['email'],
            'password': test_user['password']
        }
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_response = response.json()
            if 'access_token' in login_response:
                print(f"   ✅ Login: Success - Token received")
                login_success = True
                token = login_response['access_token']
            else:
                print(f"   ⚠️ Login: Success but no token in response")
                login_success = False
        else:
            print(f"   ❌ Login: {response.status_code} - {response.json().get('error', 'Unknown')}")
            login_success = False
    except Exception as e:
        print(f"   ❌ Login: Error - {e}")
        login_success = False
    
    # Test protected endpoint with token
    if reg_success and login_success and 'token' in locals():
        print("\n3️⃣ Testing Protected Endpoint...")
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{BACKEND_URL}/api/users", headers=headers)
            if response.status_code == 200:
                print(f"   ✅ Protected endpoint: Success")
                protected_success = True
            else:
                print(f"   ❌ Protected endpoint: {response.status_code}")
                protected_success = False
        except Exception as e:
            print(f"   ❌ Protected endpoint: Error - {e}")
            protected_success = False
    else:
        protected_success = False
    
    return {
        'registration': reg_success,
        'login': login_success,
        'protected': protected_success
    }

def test_mobile_app_config():
    """Test mobile app API configuration"""
    print("\n🔍 Testing Mobile App Configuration")
    print("-" * 40)
    
    # Check if mobile app endpoints work
    mobile_endpoints = [
        "/api/health",
        "/api/info", 
        "/api/services/categories",
        "/api/auth/register",
        "/api/auth/login"
    ]
    
    results = []
    for endpoint in mobile_endpoints:
        try:
            if endpoint in ["/api/auth/register", "/api/auth/login"]:
                # Test POST endpoints
                response = requests.post(f"{BACKEND_URL}{endpoint}", json={})
                if response.status_code in [400, 422]:  # Bad request = endpoint works
                    results.append((endpoint, True, response.status_code))
                    print(f"   ✅ {endpoint}: {response.status_code} (endpoint exists)")
                else:
                    results.append((endpoint, False, response.status_code))
                    print(f"   ❌ {endpoint}: {response.status_code}")
            else:
                # Test GET endpoints
                response = requests.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    results.append((endpoint, True, response.status_code))
                    print(f"   ✅ {endpoint}: {response.status_code}")
                else:
                    results.append((endpoint, False, response.status_code))
                    print(f"   ❌ {endpoint}: {response.status_code}")
        except Exception as e:
            results.append((endpoint, False, str(e)))
            print(f"   ❌ {endpoint}: Error - {e}")
    
    return results

def check_cors_configuration():
    """Check CORS configuration for frontend access"""
    print("\n🔍 Testing CORS Configuration")
    print("-" * 40)
    
    try:
        # Test with OPTIONS request (preflight)
        response = requests.options(f"{BACKEND_URL}/api/health")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin', 'Not set'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods', 'Not set'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers', 'Not set')
        }
        
        print(f"   CORS Origin: {cors_headers['Access-Control-Allow-Origin']}")
        print(f"   CORS Methods: {cors_headers['Access-Control-Allow-Methods']}")
        print(f"   CORS Headers: {cors_headers['Access-Control-Allow-Headers']}")
        
        if cors_headers['Access-Control-Allow-Origin'] != 'Not set':
            print("   ✅ CORS appears to be configured")
            return True
        else:
            print("   ⚠️ CORS headers not found")
            return False
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return False

def main():
    print("🧪 Frontend-Backend Connection Testing")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test admin frontend
    admin_results = test_admin_frontend_connection()
    
    # Test web frontend authentication
    web_auth_results = test_web_frontend_auth()
    
    # Test mobile app configuration  
    mobile_results = test_mobile_app_config()
    
    # Test CORS
    cors_working = check_cors_configuration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST SUMMARY")
    print("=" * 50)
    
    # Admin Frontend
    admin_working = sum(1 for _, success, _ in admin_results if success)
    admin_total = len(admin_results)
    print(f"\n🏢 Admin Frontend:")
    print(f"   Endpoints working: {admin_working}/{admin_total}")
    if admin_working >= admin_total * 0.6:  # 60% threshold
        print("   ✅ Admin frontend can connect to backend")
    else:
        print("   ❌ Admin frontend has connection issues")
    
    # Web Frontend
    web_score = sum(web_auth_results.values())
    print(f"\n🌐 Web Frontend:")
    print(f"   Registration: {'✅' if web_auth_results['registration'] else '❌'}")
    print(f"   Login: {'✅' if web_auth_results['login'] else '❌'}")
    print(f"   Protected Routes: {'✅' if web_auth_results['protected'] else '❌'}")
    if web_score >= 2:
        print("   ✅ Web frontend authentication working")
    else:
        print("   ❌ Web frontend authentication has issues")
    
    # Mobile App
    mobile_working = sum(1 for _, success, _ in mobile_results if success)
    mobile_total = len(mobile_results)
    print(f"\n📱 Mobile App:")
    print(f"   Endpoints accessible: {mobile_working}/{mobile_total}")
    if mobile_working >= mobile_total * 0.8:  # 80% threshold
        print("   ✅ Mobile app can connect to backend")
    else:
        print("   ❌ Mobile app has connection issues")
    
    # CORS
    print(f"\n🔗 CORS Configuration:")
    print(f"   {'✅ Configured properly' if cors_working else '❌ Needs configuration'}")
    
    # Overall Status
    overall_score = (
        (admin_working / admin_total) + 
        (web_score / 3) + 
        (mobile_working / mobile_total) + 
        (1 if cors_working else 0)
    ) / 4
    
    print(f"\n🎯 Overall Connection Health: {overall_score * 100:.0f}%")
    
    if overall_score >= 0.8:
        print("🎉 Excellent! All frontends properly connected to backend")
    elif overall_score >= 0.6:
        print("✅ Good! Most frontends working, minor issues to fix")
    else:
        print("⚠️ Issues found that need attention")
    
    return overall_score

if __name__ == "__main__":
    main()