#!/usr/bin/env python3
"""
Test the correct login parameters for web frontend
"""

import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_correct_login():
    """Test login with correct parameters"""
    print("🔧 Testing Login with Correct Parameters")
    print("-" * 40)
    
    # Create a test user first
    test_user = {
        'email': 'logintest@example.com',
        'phone': '+201234567894',
        'password': 'Test123!@#',
        'user_type': 'customer',
        'first_name': 'Login',
        'last_name': 'Test'
    }
    
    print("1️⃣ Creating test user...")
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
        if response.status_code in [201, 409]:
            print(f"   ✅ User created/exists: {response.status_code}")
        else:
            print(f"   ❌ User creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    print("\n2️⃣ Testing login with WRONG parameters (email + password)...")
    wrong_login = {
        'email': test_user['email'],  # WRONG - should be email_or_phone
        'password': test_user['password']
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=wrong_login)
        print(f"   ❌ Wrong params: {response.status_code} - {response.json().get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Wrong params error: {e}")
    
    print("\n3️⃣ Testing login with CORRECT parameters (email_or_phone + password)...")
    correct_login = {
        'email_or_phone': test_user['email'],  # CORRECT
        'password': test_user['password']
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=correct_login)
        if response.status_code == 200:
            login_data = response.json()
            print(f"   ✅ Correct params: {response.status_code} - Login successful!")
            print(f"   📝 Token received: {login_data.get('access_token', 'None')[:20]}...")
            return True
        else:
            print(f"   ❌ Correct params failed: {response.status_code} - {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Correct params error: {e}")
        return False

def test_phone_login():
    """Test login with phone number"""
    print("\n4️⃣ Testing login with phone number...")
    
    phone_login = {
        'email_or_phone': '+201234567894',  # Use phone instead of email
        'password': 'Test123!@#'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=phone_login)
        if response.status_code == 200:
            print(f"   ✅ Phone login: {response.status_code} - Success!")
            return True
        else:
            print(f"   ❌ Phone login failed: {response.status_code} - {response.json().get('error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"   ❌ Phone login error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Login Parameter Testing")
    print("=" * 50)
    
    email_success = test_correct_login()
    phone_success = test_phone_login()
    
    print("\n" + "=" * 50)
    print("📊 LOGIN TEST SUMMARY")
    print("=" * 50)
    print(f"Email login: {'✅ Working' if email_success else '❌ Failed'}")
    print(f"Phone login: {'✅ Working' if phone_success else '❌ Failed'}")
    
    if email_success and phone_success:
        print("\n🎉 Backend login is working correctly!")
        print("🔧 Frontend needs to send 'email_or_phone' instead of 'email'")
    else:
        print("\n⚠️ Login issues found")