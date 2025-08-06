#!/usr/bin/env python3
"""
Test login after backend deployment with status field fix
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_complete_flow():
    """Test the complete registration and login flow"""
    print("🎯 Testing Complete Flow After Backend Deploy")
    print("=" * 50)
    
    # Test existing user login
    print("1️⃣ Testing Login with Existing User...")
    login_data = {
        "email_or_phone": "+201062831897",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            result = response.json()
            print(f"   Token: {result.get('access_token', 'NOT_FOUND')[:20]}...")
            print(f"   User Type: {result.get('user', {}).get('user_type')}")
            print(f"   Status: {result.get('user', {}).get('status')}")
            
            # Test admin user login
            print("\n2️⃣ Testing Admin User Login...")
            admin_login = {
                "email_or_phone": "admin@maintenance.com",
                "password": "AdminPass123!"
            }
            
            admin_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json=admin_login,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Admin Status: {admin_response.status_code}")
            
            if admin_response.status_code == 200:
                print("   ✅ Admin login successful!")
                admin_result = admin_response.json()
                print(f"   Admin User Type: {admin_result.get('user', {}).get('user_type')}")
            else:
                print("   ℹ️ Admin login failed (password might be different)")
                
        else:
            print("   ❌ Login still failing!")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_frontend_compatibility():
    """Test all endpoints that frontend uses"""
    print("\n🌐 Testing Frontend API Compatibility")
    print("=" * 45)
    
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/info", "API info"),
        ("/api/services/categories", "Service categories"),
        ("/api/users", "Users list (should require auth)")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            status = "✅" if response.status_code in [200, 401] else "❌"
            print(f"{status} {endpoint}: {response.status_code} ({description})")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    print(f"🚀 Testing After Backend Deployment")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    test_complete_flow()
    test_frontend_compatibility()
    
    print("\n" + "=" * 50)
    print("🎉 If login works, your frontends should now be fully functional!")
    print("📱 Test registration and login from your deployed Netlify frontends")
    print("👑 Admin panel should work with the existing admin user")