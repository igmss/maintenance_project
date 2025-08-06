#!/usr/bin/env python3
"""
Test the corrected Egyptian phone format: 010/011/012/015 + 8 digits
"""

import requests
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_correct_phone_formats():
    print("📱 Testing Correct Egyptian Phone Format")
    print("=" * 45)
    print("Format: 010/011/012/015 + 8 digits")
    print()
    
    test_cases = [
        {
            "phone": "01012345678",
            "description": "010 + 8 digits (Vodafone/Orange)",
            "should_work": True
        },
        {
            "phone": "01112345678", 
            "description": "011 + 8 digits (Vodafone)",
            "should_work": True
        },
        {
            "phone": "01212345678",
            "description": "012 + 8 digits (Vodafone/WE)",
            "should_work": True
        },
        {
            "phone": "01512345678",
            "description": "015 + 8 digits (Etisalat)",
            "should_work": True
        },
        {
            "phone": "+201012345678",
            "description": "International format",
            "should_work": True
        },
        {
            "phone": "01312345678",
            "description": "013 + 8 digits (invalid network)",
            "should_work": False
        },
        {
            "phone": "01123456789",
            "description": "Old format (01 + 1 + 9 digits)",
            "should_work": False
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}️⃣ Testing: {test['phone']}")
        print(f"   {test['description']}")
        print(f"   Expected: {'✅ Should work' if test['should_work'] else '❌ Should fail'}")
        
        timestamp = int(time.time())
        data = {
            "email": f"formattest{i}_{timestamp}@example.com",
            "phone": test["phone"],
            "password": "TestPassword123!",
            "user_type": "customer",
            "first_name": "Format",
            "last_name": "Test"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 201:
                print("   ✅ ACCEPTED by backend")
                if test['should_work']:
                    print("   🎯 CORRECT!")
                else:
                    print("   ⚠️ UNEXPECTED - Should have been rejected")
                    
            elif response.status_code == 400:
                try:
                    error = response.json()
                    if "Invalid phone number format" in error.get('error', ''):
                        print("   ❌ REJECTED by backend")
                        if not test['should_work']:
                            print("   🎯 CORRECT!")
                        else:
                            print("   ⚠️ UNEXPECTED - Should have been accepted")
                    else:
                        print(f"   ❌ Different error: {error.get('error', 'Unknown')}")
                except:
                    print(f"   ❌ Error response: {response.text}")
                    
            elif response.status_code == 409:
                print("   ℹ️ User exists (format was valid)")
                if test['should_work']:
                    print("   🎯 CORRECT!")
                else:
                    print("   ⚠️ UNEXPECTED - Invalid format was accepted before")
                    
            else:
                print(f"   ❓ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
        
        print()

if __name__ == "__main__":
    print("🧪 Testing Correct Phone Format After Fix")
    print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    test_correct_phone_formats()
    
    print("=" * 50)
    print("✅ VALID FORMATS:")
    print("  📱 01012345678 (010 + 8 digits)")
    print("  📱 01112345678 (011 + 8 digits)")  
    print("  📱 01212345678 (012 + 8 digits)")
    print("  📱 01512345678 (015 + 8 digits)")
    print("  📱 +201012345678 (international)")
    print()
    print("❌ INVALID FORMATS:")
    print("  📱 01312345678 (013 not valid)")
    print("  📱 01123456789 (old format)")
    print("  📱 010123456789 (too many digits)")