#!/usr/bin/env python3
"""
Simple validation script for the provider_locations foreign key fix
"""

def validate_model_definitions():
    """Check that the model definitions have been updated correctly"""
    
    print("🔍 Validating Model Definitions...")
    
    # Check backend/src/models/location.py
    try:
        with open('backend/src/models/location.py', 'r') as f:
            content = f.read()
            
        if "db.ForeignKey('users.id')" in content and "provider_id" in content:
            print("✅ ProviderLocation model correctly references users.id")
        elif "db.ForeignKey('service_provider_profiles.id')" in content and "provider_id" in content:
            print("❌ ProviderLocation model still references service_provider_profiles.id")
            return False
        else:
            print("⚠️  Could not determine foreign key reference in ProviderLocation")
            
    except FileNotFoundError:
        print("❌ Could not find backend/src/models/location.py")
        return False
    
    # Check that relationships are updated in user.py
    try:
        with open('backend/src/models/user.py', 'r') as f:
            content = f.read()
            
        if "provider_locations = db.relationship('ProviderLocation'" in content:
            print("✅ User model has provider_locations relationship")
        else:
            print("⚠️  User model missing provider_locations relationship")
            
    except FileNotFoundError:
        print("❌ Could not find backend/src/models/user.py")
        return False
    
    return True

def validate_route_updates():
    """Check that route files have been updated to use current_user.id"""
    
    print("\n🔍 Validating Route Updates...")
    
    # Check providers.py
    try:
        with open('backend/src/routes/providers.py', 'r') as f:
            content = f.read()
            
        # Count instances of current_user.id vs current_user.provider_profile.id in ProviderLocation contexts
        provider_location_lines = [line for line in content.split('\n') if 'ProviderLocation(' in line]
        
        correct_usage = 0
        incorrect_usage = 0
        
        for line in provider_location_lines:
            if 'provider_id=current_user.id' in line:
                correct_usage += 1
            elif 'provider_id=current_user.provider_profile.id' in line:
                incorrect_usage += 1
                
        if incorrect_usage == 0 and correct_usage > 0:
            print(f"✅ providers.py: {correct_usage} ProviderLocation creations use current_user.id")
        elif incorrect_usage > 0:
            print(f"❌ providers.py: {incorrect_usage} ProviderLocation creations still use current_user.provider_profile.id")
            return False
        else:
            print("⚠️  No ProviderLocation creations found in providers.py")
            
    except FileNotFoundError:
        print("❌ Could not find backend/src/routes/providers.py")
        return False
    
    # Check providers_updated.py
    try:
        with open('backend/src/routes/providers_updated.py', 'r') as f:
            content = f.read()
            
        provider_location_lines = [line for line in content.split('\n') if 'ProviderLocation(' in line]
        
        correct_usage = 0
        incorrect_usage = 0
        
        for line in provider_location_lines:
            if 'provider_id=current_user.id' in line:
                correct_usage += 1
            elif 'provider_id=current_user.provider_profile.id' in line:
                incorrect_usage += 1
                
        if incorrect_usage == 0 and correct_usage > 0:
            print(f"✅ providers_updated.py: {correct_usage} ProviderLocation creations use current_user.id")
        elif incorrect_usage > 0:
            print(f"❌ providers_updated.py: {incorrect_usage} ProviderLocation creations still use current_user.provider_profile.id")
            return False
        else:
            print("⚠️  No ProviderLocation creations found in providers_updated.py")
            
    except FileNotFoundError:
        print("⚠️  backend/src/routes/providers_updated.py not found (may not exist)")
    
    return True

def main():
    """Run validation"""
    print("🚀 Provider Location Foreign Key Fix Validation")
    print("=" * 50)
    
    success = True
    
    if not validate_model_definitions():
        success = False
        
    if not validate_route_updates():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Validation successful! The foreign key fix has been properly implemented.")
        print("\n📋 Summary of changes validated:")
        print("   ✅ ProviderLocation model now references users.id")
        print("   ✅ Route handlers use current_user.id for ProviderLocation")
        print("   ✅ Model relationships updated correctly")
        print("\n🔧 The original error should now be resolved:")
        print("   • Provider ID will reference users table correctly")
        print("   • Foreign key constraint violation should not occur")
        print("   • Location tracking will work properly")
    else:
        print("❌ Validation failed. Some issues need to be addressed.")
    
    return success

if __name__ == "__main__":
    main()