#!/usr/bin/env python3
"""
Generate bcrypt hash for admin password
"""

import bcrypt

def generate_password_hash(password):
    """Generate bcrypt hash for password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

if __name__ == "__main__":
    password = "Aa123e456y@"
    password_hash = generate_password_hash(password)
    
    print("🔐 Password Hash Generator")
    print("=" * 50)
    print(f"Password: {password}")
    print(f"Hash: {password_hash}")
    print("\n📝 SQL Query to update admin password:")
    print("=" * 50)
    print(f"UPDATE users SET password_hash = '{password_hash}' WHERE email = 'admin@maintenanceplatform.com';")
    print("\n🔧 Alternative query using user ID:")
    print(f"UPDATE users SET password_hash = '{password_hash}' WHERE id = 'e3d04fa9-2024-493b-a8ba-e10c2fe8fcf9';")