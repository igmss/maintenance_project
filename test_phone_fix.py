#!/usr/bin/env python3
"""
Quick test of phone validation fix
"""

import requests
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_phone_fix():
    print("📱 Testing Phone Validation Fix")
    print("=" * 35)
    
    # Test the formats that should now work
    test_phones = ["01123456789", "01023456789", "+201123456789"]
    
    for phone in test_phones:
        print(f"\n🧪 Testing: {phone}")
        
        timestamp = int(time.time())
        data = {
            "email": f"test{timestamp}@example.com",
            "phone": phone,
            "password": "TestPassword123!",
            "user_type": "customer", 
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=10)
            
            if response.status_code == 201:
                print("   ✅ ACCEPTED - Phone validation fixed!")
            elif response.status_code == 409:
                print("   ✅ ACCEPTED (user exists) - Phone validation working!")
            elif response.status_code == 400:
                error = response.json()
                if "Invalid phone number format" in error.get('error', ''):
                    print("   ❌ Still rejected - backend not deployed yet")
                else:
                    print(f"   ℹ️ Different error: {error.get('error')}")
            else:
                print(f"   ❓ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_phone_fix()
    print("\n💡 If still rejected, redeploy backend with the phone validation fix")