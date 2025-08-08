#!/usr/bin/env python3
"""
Test script to verify provider approval workflow
"""
import requests
import json

def test_provider_approval():
    """Test the provider approval workflow"""
    
    base_url = "https://maintenance-platform-backend.onrender.com"
    
    # Admin login
    print("🔐 Testing admin login...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email_or_phone": "admin@maintenanceplatform.com",
        "password": "Aa123e456y@"
    })
    
    if login_response.status_code == 200:
        admin_token = login_response.json().get('access_token')
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all providers
    print("\n📋 Getting all providers...")
    providers_response = requests.get(f"{base_url}/api/admin/providers", headers=headers)
    
    if providers_response.status_code == 200:
        providers = providers_response.json().get('providers', [])
        print(f"✅ Found {len(providers)} providers")
        
        # Find cirkelrealty@gmail.com
        target_provider = None
        for provider in providers:
            if provider.get('user', {}).get('email') == 'cirkelrealty@gmail.com':
                target_provider = provider
                break
        
        if target_provider:
            print(f"🎯 Found target provider: {target_provider['first_name']} {target_provider['last_name']}")
            print(f"   Current status: {target_provider['verification_status']}")
            
            # Get provider documents
            print(f"\n📄 Getting documents for provider {target_provider['id']}...")
            docs_response = requests.get(f"{base_url}/api/admin/providers/{target_provider['id']}/documents", headers=headers)
            
            if docs_response.status_code == 200:
                documents = docs_response.json().get('documents', [])
                print(f"✅ Found {len(documents)} documents")
                for doc in documents:
                    print(f"   - {doc['document_type']}: {doc['verification_status']}")
            else:
                print(f"❌ Failed to get documents: {docs_response.status_code}")
            
            # Test approval if currently pending
            if target_provider['verification_status'] == 'pending':
                print(f"\n✅ Testing provider approval...")
                approval_response = requests.put(
                    f"{base_url}/api/admin/providers/{target_provider['id']}/verification",
                    headers=headers,
                    json={
                        "verification_status": "approved",
                        "rejection_reason": None
                    }
                )
                
                if approval_response.status_code == 200:
                    print("✅ Provider approval successful!")
                    print(f"   Response: {approval_response.json().get('message')}")
                else:
                    print(f"❌ Provider approval failed: {approval_response.status_code}")
                    print(f"   Error: {approval_response.text}")
            else:
                print(f"ℹ️  Provider status is already: {target_provider['verification_status']}")
        else:
            print("❌ cirkelrealty@gmail.com provider not found")
    else:
        print(f"❌ Failed to get providers: {providers_response.status_code}")

if __name__ == "__main__":
    test_provider_approval()