#!/usr/bin/env python3
"""
Test different phone number formats to help user understand what works
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_phone_formats():
    """Test various phone number formats"""
    print("📱 Testing Egyptian Phone Number Formats")
    print("=" * 50)
    
    # Test different phone formats
    phone_formats = [
        {
            "phone": "01123456789",
            "description": "Standard Egyptian format (01 + 1 + 9 digits)",
            "expected": "✅ Should work"
        },
        {
            "phone": "+201123456789", 
            "description": "International format (+20 + 1 + 9 digits)",
            "expected": "✅ Should work"
        },
        {
            "phone": "201123456789",
            "description": "Without + prefix (20 + 1 + 9 digits)", 
            "expected": "✅ Should work"
        },
        {
            "phone": "01012345678",
            "description": "Different network (01 + 0 + 9 digits)",
            "expected": "❌ Won't work (needs 1 after 01)"
        },
        {
            "phone": "1123456789",
            "description": "Missing country/area code",
            "expected": "❌ Won't work"
        },
        {
            "phone": "01234567890",
            "description": "Too many digits",
            "expected": "❌ Won't work"
        }
    ]
    
    for i, test_case in enumerate(phone_formats, 1):
        print(f"\n{i}️⃣ Testing: {test_case['phone']}")
        print(f"   Format: {test_case['description']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Test with registration endpoint
        timestamp = int(datetime.now().timestamp())
        test_data = {
            "email": f"test{i}_{timestamp}@example.com",
            "phone": test_case["phone"],
            "password": "TestPassword123!",
            "user_type": "customer",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 201:
                print("   ✅ ACCEPTED - Registration successful!")
            elif response.status_code == 400:
                try:
                    error = response.json()
                    if "Invalid phone number format" in error.get('error', ''):
                        print("   ❌ REJECTED - Invalid phone format")
                    else:
                        print(f"   ❌ REJECTED - {error.get('error', 'Unknown error')}")
                except:
                    print(f"   ❌ REJECTED - {response.text}")
            elif response.status_code == 409:
                print("   ✅ ACCEPTED - Phone format valid (user exists)")
            else:
                print(f"   ❓ UNEXPECTED - Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR - {e}")

def show_valid_formats():
    """Show examples of valid phone formats"""
    print(f"\n📋 VALID EGYPTIAN PHONE FORMATS:")
    print("=" * 40)
    print("✅ 01123456789  (Vodafone - starts with 010, 011, 012)")
    print("✅ 01023456789  (Vodafone)")
    print("✅ 01223456789  (Vodafone)")
    print("✅ 01523456789  (Etisalat - starts with 015)")
    print("✅ 01003456789  (Orange - starts with 010)")
    print("✅ 01273456789  (WE - starts with 012)")
    print("\n🌍 INTERNATIONAL FORMATS:")
    print("✅ +201123456789")
    print("✅ 201123456789")
    print("\n❌ INVALID FORMATS:")
    print("❌ 01012345678  (missing digit)")
    print("❌ 012345678901 (too many digits)")
    print("❌ 05123456789  (doesn't start with 1 after area code)")

if __name__ == "__main__":
    print(f"🧪 Phone Format Testing")
    print(f"🕒 {datetime.now()}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    show_valid_formats()
    test_phone_formats()
    
    print("\n" + "=" * 50)
    print("💡 TIP FOR FRONTEND:")
    print("Try registering with: 01123456789")
    print("This is a standard Egyptian mobile format")