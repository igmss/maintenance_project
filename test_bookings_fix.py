#!/usr/bin/env python3
"""
Test bookings functionality after database schema fix
"""

import requests
import time

BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_bookings_functionality():
    print("📅 Testing Bookings Functionality")
    print("=" * 40)
    
    # First, test if we can access a user dashboard (this was failing before)
    print("1️⃣ Testing Dashboard Access (what was failing)...")
    
    # Try to login first to get a token
    login_data = {
        "email_or_phone": "+201062831897",
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
            user = login_result.get('user')
            
            print(f"   ✅ Login successful")
            print(f"   User ID: {user.get('id')}")
            print(f"   User Type: {user.get('user_type')}")
            
            # Now test dashboard/bookings access
            print("\n2️⃣ Testing Bookings Query...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Test bookings endpoint (this should have been failing)
            dashboard_response = requests.get(
                f"{BASE_URL}/api/bookings",  # or whatever endpoint was failing
                headers=headers,
                timeout=15
            )
            
            print(f"   Bookings endpoint status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Bookings query successful!")
                bookings_data = dashboard_response.json()
                print(f"   Bookings found: {len(bookings_data) if isinstance(bookings_data, list) else 'N/A'}")
            elif dashboard_response.status_code == 404:
                print("   ℹ️ Bookings endpoint not found (might be different URL)")
            else:
                print(f"   ❌ Bookings query failed: {dashboard_response.status_code}")
                try:
                    error = dashboard_response.json()
                    if "booking_status does not exist" in str(error):
                        print("   ❌ Still has booking_status column issue - database not updated yet")
                    else:
                        print(f"   Error: {error}")
                except:
                    print(f"   Raw error: {dashboard_response.text[:200]}")
            
            # Test other potential dashboard endpoints
            print("\n3️⃣ Testing Other Dashboard Endpoints...")
            test_endpoints = [
                "/api/dashboard",
                "/api/customer/dashboard", 
                "/api/user/bookings",
                "/api/customer/bookings"
            ]
            
            for endpoint in test_endpoints:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
                    status = "✅" if response.status_code in [200, 404] else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    
                    if response.status_code == 500:
                        try:
                            error = response.json()
                            if "booking_status does not exist" in str(error):
                                print(f"      ❌ This endpoint also has the booking_status issue")
                        except:
                            pass
                            
                except Exception as e:
                    print(f"   ❌ {endpoint}: {e}")
            
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            try:
                error = login_response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def test_database_schema():
    print("\n🗄️ Testing Database Schema Fix")
    print("=" * 35)
    
    # Test if any endpoint that uses bookings works
    print("Checking if backend can handle bookings queries...")
    
    # Just test the health endpoint to make sure backend is up
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend might be down")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")

if __name__ == "__main__":
    print(f"🔧 Testing Bookings Fix")
    print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Backend: {BASE_URL}")
    print()
    
    test_database_schema()
    test_bookings_functionality()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print("If you see 'booking_status does not exist' errors:")
    print("1. Run the SQL script: database/fix_bookings_table.sql")
    print("2. Restart your backend service")
    print("3. Test your frontend again")
    print()
    print("✅ Once fixed, your dashboard should load properly!")