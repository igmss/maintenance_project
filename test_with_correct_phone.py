#!/usr/bin/env python3
"""
Test with correct Egyptian phone format
"""
import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def test_phone_formats():
    print("📱 Testing Egyptian Phone Formats")
    print("=" * 50)
    
    # Egyptian phone formats that should work based on the regex
    # Pattern: ^(\+20|0020|20)?01[0125][0-9]{8}$
    phone_formats = [
        '+201012345678',  # +20 prefix
        '0201012345678',  # 020 prefix  
        '201012345678',   # 20 prefix
        '01012345678',    # 01 prefix
    ]
    
    for i, phone in enumerate(phone_formats, 1):
        print(f"\n{i}️⃣ Testing phone: {phone}")
        
        customer_data = {
            'email': f'test{i}@example.com',
            'phone': phone,
            'password': 'Test123!',
            'user_type': 'customer',
            'first_name': 'Test',
            'last_name': 'Customer'
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/api/auth/register", json=customer_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                print("   ✅ Registration successful!")
                
                # Test login
                login_data = {
                    'email_or_phone': customer_data['email'],
                    'password': customer_data['password']
                }
                
                login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
                if login_response.status_code == 200:
                    print("   ✅ Login successful too!")
                    return phone  # Return working format
                else:
                    print(f"   ❌ Login failed: {login_response.status_code}")
                    
            elif response.status_code == 409:
                print("   ✅ User already exists - format is valid")
                return phone  # Format is valid
            else:
                error_data = response.json()
                print(f"   ❌ Registration failed: {error_data.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def create_admin_with_working_phone(working_phone_format):
    print(f"\n🔧 Creating admin user with working phone format: {working_phone_format}")
    print("=" * 70)
    
    # Create admin with working phone format
    admin_data = {
        'email': 'admin@maintenanceplatform.com',
        'phone': working_phone_format,
        'password': 'admin123',
        'user_type': 'customer',  # Create as customer first
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=admin_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Admin user created successfully!")
            user_data = response.json()
            user_id = user_data['user']['id']
            
            print(f"   📝 User ID: {user_id}")
            print("\n💾 IMPORTANT: Run this SQL in Supabase to make user admin:")
            print("   " + "="*60)
            print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
            print("   " + "="*60)
            
            return True
            
        elif response.status_code == 409:
            print("   ✅ Admin user already exists")
            
            # Try to login and get user ID
            login_data = {
                'email_or_phone': 'admin@maintenanceplatform.com',
                'password': 'admin123'
            }
            
            login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
            if login_response.status_code == 200:
                user_data = login_response.json()
                user_id = user_data['user']['id']
                user_type = user_data['user']['user_type']
                
                print(f"   📝 Existing User ID: {user_id}")
                print(f"   📝 Current Type: {user_type}")
                
                if user_type != 'admin':
                    print("\n💾 IMPORTANT: Run this SQL in Supabase to make user admin:")
                    print("   " + "="*60)
                    print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
                    print("   " + "="*60)
                else:
                    print("   ✅ User is already admin!")
                    
            elif login_response.status_code == 500:
                error_data = login_response.json()
                if 'Invalid salt' in error_data.get('error', ''):
                    print("   ⚠️  Password hash issue detected")
                    print("\n💾 IMPORTANT: Run this SQL in Supabase to fix password:")
                    print("   " + "="*60)
                    print("   UPDATE users SET password_hash = '$2b$12$LQv3c1yqBwlFXK8QqLnF7.SWMX.jMa7dWRvyS5J5HZzJQK7.YtWNW'")
                    print("   WHERE email = 'admin@maintenanceplatform.com';")
                    print("   -- This sets password to 'admin123'")
                    print("   " + "="*60)
            
            return True
        else:
            error_data = response.json()
            print(f"   ❌ Failed: {error_data.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Admin User Creation with Correct Phone Format")
    print("=" * 60)
    
    # Find working phone format
    working_format = test_phone_formats()
    
    if working_format:
        print(f"\n✅ Found working phone format: {working_format}")
        success = create_admin_with_working_phone(working_format)
        
        if success:
            print("\n🎉 NEXT STEPS:")
            print("   1. Run the SQL command shown above in Supabase")
            print("   2. Test admin login again")
            print("   3. If still getting 'Invalid salt', run the password fix SQL too")
    else:
        print("\n❌ No working phone format found")
        print("💡 Check backend phone validation regex")