#!/usr/bin/env python3
"""
Quick API test after database migration
"""

import requests
import json
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_key_endpoints():
    print("🧪 Testing key endpoints after migration...")
    print("=" * 40)
    
    # Test health
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Health: {response.status_code} - {response.json()}")
    
    # Test service categories
    response = requests.get(f"{BASE_URL}/api/services/categories")
    print(f"Categories: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Found {len(data.get('categories', []))} categories")
    else:
        print(f"  Error: {response.json().get('error', 'Unknown')[:50]}...")
    
    # Test registration
    test_user = {
        'email': f'test-{int(time.time())}@example.com',
        'phone': '+201234567890',
        'password': 'Test123!@#',
        'user_type': 'customer',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
    print(f"Registration: {response.status_code}")
    if response.status_code in [201, 409]:  # 201 = success, 409 = user exists
        print("  ✅ Registration endpoint working!")
    else:
        print(f"  Error: {response.json().get('error', 'Unknown')[:50]}...")

if __name__ == "__main__":
    test_key_endpoints()