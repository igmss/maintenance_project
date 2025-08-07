#!/usr/bin/env python3
"""
Create proper admin user with correct phone and password format
"""
import requests
import json

BACKEND_URL = "https://maintenance-platform-backend.onrender.com"

def create_admin_user():
    print("🔧 Creating Admin User with Proper Credentials")
    print("=" * 60)
    
    # Use working phone format and password that meets requirements
    admin_data = {
        'email': 'admin@maintenanceplatform.com',
        'phone': '01012345678',  # Working Egyptian format
        'password': 'Admin123!',  # Meets all requirements: 8+ chars, upper, lower, digit
        'user_type': 'customer',  # Create as customer first (only allowed type)
        'first_name': 'Admin',
        'last_name': 'User'
    }
    
    print("1️⃣ Creating admin user...")
    print(f"   Email: {admin_data['email']}")
    print(f"   Phone: {admin_data['phone']}")
    print(f"   Password: {admin_data['password']}")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=admin_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Admin user created successfully!")
            user_data = response.json()
            user_id = user_data['user']['id']
            
            print(f"   📝 User ID: {user_id}")
            print(f"   📝 Access Token: {user_data.get('access_token', 'N/A')[:20]}...")
            
            print("\n💾 STEP 1: Run this SQL in Supabase to make user admin:")
            print("   " + "="*70)
            print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
            print("   " + "="*70)
            
            return user_id, admin_data['password']
            
        elif response.status_code == 409:
            print("   ✅ Admin user already exists")
            
            # Test login with the proper password
            print("\n2️⃣ Testing login with proper password...")
            login_data = {
                'email_or_phone': 'admin@maintenanceplatform.com',
                'password': 'Admin123!'
            }
            
            login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
            print(f"   Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                user_data = login_response.json()
                user_id = user_data['user']['id']
                user_type = user_data['user']['user_type']
                
                print("   ✅ Login successful with proper password!")
                print(f"   📝 User ID: {user_id}")
                print(f"   📝 Current Type: {user_type}")
                
                if user_type != 'admin':
                    print("\n💾 Run this SQL in Supabase to make user admin:")
                    print("   " + "="*70)
                    print(f"   UPDATE users SET user_type = 'admin' WHERE id = '{user_id}';")
                    print("   " + "="*70)
                else:
                    print("   ✅ User is already admin!")
                
                return user_id, 'Admin123!'
                
            else:
                # Try with original password
                print("   ❌ Login failed with new password, trying original...")
                login_data['password'] = 'admin123'
                
                login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
                print(f"   Original Password Status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    user_data = login_response.json()
                    user_id = user_data['user']['id']
                    print("   ✅ Original password works!")
                    print(f"   📝 User ID: {user_id}")
                    return user_id, 'admin123'
                    
                elif login_response.status_code == 500:
                    error_data = login_response.json()
                    if 'Invalid salt' in error_data.get('error', ''):
                        print("   ⚠️  Password hash corrupted, need to fix in database")
                        
                        # Get user ID another way if possible
                        print("\n💾 Run this SQL in Supabase to fix password and make admin:")
                        print("   " + "="*70)
                        print("   UPDATE users SET ")
                        print("     password_hash = '$2b$12$LQv3c1yqBwlFXK8QqLnF7.HX4/wKt8x5LdLFKJKzX8fW4KJj4xkMW',")
                        print("     user_type = 'admin'")
                        print("   WHERE email = 'admin@maintenanceplatform.com';")
                        print("   -- This sets password to 'Admin123!'")
                        print("   " + "="*70)
                        
                        return None, 'Admin123!'
                        
            return None, None
            
        else:
            error_data = response.json()
            print(f"   ❌ Failed: {error_data.get('error')}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None

def test_admin_login(password):
    print(f"\n🧪 Testing Admin Login with password: {password}")
    print("=" * 60)
    
    login_data = {
        'email_or_phone': 'admin@maintenanceplatform.com',
        'password': password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print("   ✅ Login successful!")
            print(f"   User Type: {user.get('user_type')}")
            
            if user.get('user_type') == 'admin':
                print("   ✅ Admin privileges confirmed!")
                return True
            else:
                print(f"   ⚠️  User type is '{user.get('user_type')}', need to update to 'admin'")
                return False
        else:
            error_data = response.json()
            print(f"   ❌ Login failed: {error_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛠️  Admin User Setup - Proper Credentials")
    print("=" * 70)
    
    user_id, password = create_admin_user()
    
    if password:
        print(f"\n📝 SUMMARY:")
        print(f"   Admin Email: admin@maintenanceplatform.com")
        print(f"   Admin Password: {password}")
        if user_id:
            print(f"   User ID: {user_id}")
        
        # Test the login
        success = test_admin_login(password)
        
        print("\n🎯 FINAL STEPS:")
        if not success:
            print("   1. Run the SQL command shown above in Supabase")
            print("   2. Update frontend LoginPage.jsx demo credentials if needed")
            print("   3. Test admin login in frontend")
        else:
            print("   ✅ Admin login is working!")
            print("   2. Update frontend demo credentials to match")
    else:
        print("\n❌ Admin user creation failed")
        print("💡 Check backend logs for more details")