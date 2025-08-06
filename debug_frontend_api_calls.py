#!/usr/bin/env python3
"""
Debug frontend API call issues - check what the frontend is actually hitting
"""

import requests
from datetime import datetime

# Test the exact endpoints the frontend is trying to call
BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_frontend_endpoints():
    """Test the exact API calls the frontend is making"""
    print("🔍 Debugging Frontend API Call Issues")
    print("=" * 50)
    
    # Test the endpoints mentioned in the error
    test_endpoints = [
        {
            "url": f"{BASE_URL}/api/services/categories",
            "method": "GET",
            "description": "Service categories (causing JSON parse error)"
        },
        {
            "url": f"{BASE_URL}/auth/login", 
            "method": "POST",
            "description": "Login endpoint (405 error)",
            "data": {"email_or_phone": "test", "password": "test"}
        },
        {
            "url": f"{BASE_URL}/api/auth/login",
            "method": "POST", 
            "description": "Correct login endpoint",
            "data": {"email_or_phone": "test", "password": "test"}
        },
        {
            "url": f"{BASE_URL}/api/health",
            "method": "GET",
            "description": "Health check"
        },
        {
            "url": f"{BASE_URL}/api/info",
            "method": "GET", 
            "description": "API info"
        }
    ]
    
    for test in test_endpoints:
        print(f"\n🧪 Testing: {test['description']}")
        print(f"   URL: {test['url']}")
        print(f"   Method: {test['method']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:
                response = requests.post(
                    test['url'], 
                    json=test.get('data', {}),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            
            # Check if response is HTML (error page) or JSON
            content = response.text[:200]
            if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                print("   ❌ Response is HTML (error page):")
                print(f"   Preview: {content[:100]}...")
            else:
                print("   ✅ Response appears to be JSON/text")
                if response.status_code == 200:
                    try:
                        json_data = response.json()
                        print(f"   Data preview: {str(json_data)[:100]}...")
                    except:
                        print(f"   Text preview: {content[:100]}...")
                elif response.status_code in [400, 401, 404, 405]:
                    print(f"   Error response: {content[:100]}...")
                        
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_cors_and_options():
    """Test CORS preflight requests"""
    print(f"\n🌐 Testing CORS Configuration")
    print("=" * 35)
    
    test_url = f"{BASE_URL}/api/auth/login"
    
    try:
        # Test OPTIONS request (CORS preflight)
        options_response = requests.options(test_url, timeout=10)
        print(f"OPTIONS request: {options_response.status_code}")
        print(f"CORS headers:")
        cors_headers = {k: v for k, v in options_response.headers.items() 
                       if 'access-control' in k.lower() or 'origin' in k.lower()}
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def check_netlify_redirects():
    """Check what happens when frontend makes calls through Netlify redirects"""
    print(f"\n📡 Testing Netlify Redirect Behavior")
    print("=" * 40)
    
    # These would be the URLs if the frontend is deployed on Netlify
    netlify_admin_url = "https://adminsiyaana.netlify.app/"  # Replace with actual URL
    netlify_web_url = "https://siyaana.netlify.app/"      # Replace with actual URL
    
    print("ℹ️  Note: Replace with your actual Netlify URLs to test redirects")
    print(f"   Admin frontend: {netlify_admin_url}/api/health")
    print(f"   Web frontend: {netlify_web_url}/api/health")
    print("   These should redirect to your backend if configured correctly")

if __name__ == "__main__":
    print(f"🚀 Debugging Frontend API Issues")
    print(f"🕒 {datetime.now()}")
    print()
    
    test_frontend_endpoints()
    test_cors_and_options()
    check_netlify_redirects()
    
    print("\n" + "=" * 50)
    print("🔧 LIKELY ISSUES:")
    print("1. Frontend calling wrong endpoint paths")
    print("2. CORS configuration problems") 
    print("3. Netlify redirect configuration")
    print("4. Backend routing issues")
    print("\n💡 CHECK:")
    print("- Frontend API base URL configuration")
    print("- Netlify _redirects or netlify.toml rules")
    print("- Backend CORS settings")