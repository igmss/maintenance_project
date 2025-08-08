#!/usr/bin/env python3
"""
Test admin login and verify token is working
"""
import requests
import json

def test_admin_authentication():
    """Test the complete admin authentication flow"""
    
    base_url = "https://maintenance-platform-backend.onrender.com"
    
    print("🔐 Testing Admin Authentication Flow")
    print("=" * 50)
    
    # Test login
    print("\n1. Testing admin login...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email_or_phone": "admin@maintenanceplatform.com",
        "password": "Aa123e456y@"
    })
    
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print("   ✅ Login successful!")
        print(f"   User type: {login_data.get('user', {}).get('user_type')}")
        print(f"   User email: {login_data.get('user', {}).get('email')}")
        
        token = login_data.get('access_token')
        if token:
            print(f"   Token received: {token[:20]}...")
            
            # Test protected endpoint
            print("\n2. Testing protected admin endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            
            dashboard_response = requests.get(f"{base_url}/api/admin/dashboard/stats", headers=headers)
            print(f"   Dashboard stats status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Admin dashboard accessible!")
                stats = dashboard_response.json()
                print(f"   Stats keys: {list(stats.keys())}")
            elif dashboard_response.status_code == 401:
                print("   ❌ Token rejected by admin endpoint")
            else:
                print(f"   ⚠️  Unexpected response: {dashboard_response.text[:100]}")
                
            # Test providers endpoint
            print("\n3. Testing providers endpoint...")
            providers_response = requests.get(f"{base_url}/api/admin/providers", headers=headers)
            print(f"   Providers status: {providers_response.status_code}")
            
            if providers_response.status_code == 200:
                providers_data = providers_response.json()
                providers = providers_data.get('providers', [])
                print(f"   ✅ Found {len(providers)} providers")
            else:
                print(f"   ❌ Providers endpoint failed: {providers_response.text[:100]}")
                
        else:
            print("   ❌ No token in response")
    else:
        print(f"   ❌ Login failed: {login_response.text}")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_admin_authentication()