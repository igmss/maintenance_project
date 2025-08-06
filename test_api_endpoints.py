#!/usr/bin/env python3
"""
API Endpoint Testing Script for Maintenance Platform Backend
Run this script to test all available endpoints after fixing the database schema.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_endpoint(method, endpoint, data=None, headers=None, expected_status=200):
    """Test a single endpoint and return the result"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        success = response.status_code == expected_status
        return {
            'success': success,
            'status_code': response.status_code,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url
        }

def main():
    print("🧪 Testing Maintenance Platform API Endpoints")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test cases
    tests = [
        # Basic endpoints
        ('GET', '/api/health', None, None, 200),
        ('GET', '/api/info', None, None, 200),
        
        # Service endpoints
        ('GET', '/api/services/categories', None, None, 200),
        ('GET', '/api/services/categories?lang=ar', None, None, 200),
        ('GET', '/api/services/categories?lang=en', None, None, 200),
        
        # User endpoints (basic test)
        ('GET', '/api/users', None, None, 200),
        
        # Auth endpoints
        ('POST', '/api/auth/register', {
            'email': 'test@example.com',
            'phone': '+201234567890',
            'password': 'Test123!@#',
            'user_type': 'customer',
            'first_name': 'Test',
            'last_name': 'User'
        }, None, 201),
        
        ('POST', '/api/auth/login', {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }, None, 401),
    ]
    
    results = []
    
    for method, endpoint, data, headers, expected_status in tests:
        print(f"🔍 Testing {method} {endpoint}")
        result = test_endpoint(method, endpoint, data, headers, expected_status)
        results.append((endpoint, result))
        
        if result['success']:
            print(f"   ✅ Success ({result['status_code']})")
        else:
            print(f"   ❌ Failed ({result.get('status_code', 'ERROR')})")
            if 'error' in result:
                print(f"      Error: {result['error']}")
            elif 'response' in result:
                error_msg = result['response'].get('error', str(result['response']))[:100]
                print(f"      Response: {error_msg}...")
        print()
    
    # Summary
    successful = sum(1 for _, result in results if result['success'])
    total = len(results)
    
    print("📊 Test Summary")
    print("=" * 20)
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - successful} tests failed. Check the database schema and configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())