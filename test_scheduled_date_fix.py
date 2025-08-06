#!/usr/bin/env python3
"""
Test the scheduled_date column fix specifically
"""

import requests
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_specific_booking_error():
    print("🔧 Testing Specific Booking Schema Fix")
    print("=" * 45)
    
    # The exact endpoint that was failing
    failing_endpoint = "/api/services/bookings?per_page=10"
    
    print(f"Testing failing endpoint: {failing_endpoint}")
    
    # First try to login to get a token
    login_data = {
        "email_or_phone": "testuser1754490357@example.com",  # From our earlier successful registration
        "password": "TestPassword123!"
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            
            print(f"✅ Login successful, testing bookings endpoint...")
            
            # Test the failing bookings endpoint
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            bookings_response = requests.get(
                f"{BASE_URL}{failing_endpoint}",
                headers=headers,
                timeout=15
            )
            
            print(f"Bookings endpoint status: {bookings_response.status_code}")
            
            if bookings_response.status_code == 200:
                print("✅ SUCCESS! Bookings endpoint now working!")
                data = bookings_response.json()
                print(f"Response: {data}")
            elif bookings_response.status_code == 500:
                try:
                    error = bookings_response.json()
                    error_msg = str(error)
                    if "scheduled_date does not exist" in error_msg:
                        print("❌ Still has scheduled_date issue - run the SQL fix")
                    elif "booking_status does not exist" in error_msg:
                        print("❌ Still has booking_status issue") 
                    else:
                        print(f"❌ Different 500 error: {error}")
                except:
                    print(f"❌ 500 error (raw): {bookings_response.text[:200]}")
            else:
                print(f"❓ Unexpected status: {bookings_response.status_code}")
                try:
                    error = bookings_response.json()
                    print(f"Response: {error}")
                except:
                    print(f"Raw response: {bookings_response.text[:200]}")
                    
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            # Try with a different user that might exist
            print("Trying with the user from our successful registration...")
            
            # Try creating a new user and then testing
            timestamp = int(time.time())
            reg_data = {
                "email": f"schematest{timestamp}@example.com",
                "phone": f"01012{timestamp % 100000:05d}",
                "password": "TestPassword123!",
                "user_type": "customer",
                "first_name": "Schema",
                "last_name": "Test"
            }
            
            reg_response = requests.post(
                f"{BASE_URL}/api/auth/register",
                json=reg_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if reg_response.status_code == 201:
                print("✅ New user registered, trying login...")
                
                login_response2 = requests.post(
                    f"{BASE_URL}/api/auth/login",
                    json={"email_or_phone": reg_data["email"], "password": reg_data["password"]},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if login_response2.status_code == 200:
                    login_result2 = login_response2.json()
                    token2 = login_result2.get('access_token')
                    
                    headers2 = {
                        "Authorization": f"Bearer {token2}",
                        "Content-Type": "application/json"
                    }
                    
                    bookings_response2 = requests.get(
                        f"{BASE_URL}{failing_endpoint}",
                        headers=headers2,
                        timeout=15
                    )
                    
                    print(f"Bookings test with new user: {bookings_response2.status_code}")
                    
                    if bookings_response2.status_code == 200:
                        print("✅ SUCCESS! Schema fix worked!")
                    else:
                        try:
                            error = bookings_response2.json()
                            print(f"❌ Still failing: {error}")
                        except:
                            print(f"❌ Raw error: {bookings_response2.text[:200]}")
                else:
                    print(f"❌ Login with new user failed: {login_response2.status_code}")
            else:
                print(f"❌ User registration failed: {reg_response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print(f"🧪 Testing Scheduled Date Fix")
    print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_specific_booking_error()
    
    print("\n" + "=" * 50)
    print("💡 TO FIX:")
    print("1. Run: database/fix_bookings_schema_precise.sql")
    print("2. This adds the missing 'scheduled_date' column")
    print("3. Maps existing 'preferred_date' + 'preferred_time' to 'scheduled_date'")
    print("4. Fills in other missing required columns")
    print("\n✅ After running SQL, the dashboard should work!")