#!/usr/bin/env python3
"""
Test script for admin-provider workflow including document management
Tests:
1. Provider document upload
2. Admin viewing documents
3. Admin approving/rejecting providers
4. Document review functionality
"""

import requests
import json
import os
import sys
import time
from io import BytesIO

# Configuration
BASE_URL = "https://maintenance-platform-backend.onrender.com/api"
TEST_PROVIDER_EMAIL = "test_provider_workflow@example.com"
TEST_ADMIN_EMAIL = "admin@maintenanceplatform.com"
TEST_ADMIN_PASSWORD = "Aa123456789@"

class WorkflowTester:
    def __init__(self):
        self.provider_token = None
        self.admin_token = None
        self.provider_id = None
        self.test_document_id = None
        
    def log(self, message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def make_request(self, method, endpoint, token=None, data=None, files=None):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        headers = {}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if files:
                # For file uploads, don't set Content-Type header
                response = requests.request(method, url, headers=headers, data=data, files=files)
            elif data:
                headers['Content-Type'] = 'application/json'
                response = requests.request(method, url, headers=headers, data=json.dumps(data))
            else:
                response = requests.request(method, url, headers=headers)
            
            self.log(f"{method} {endpoint} -> Status: {response.status_code}")
            
            if response.status_code >= 400:
                self.log(f"Error response: {response.text}")
                
            return response
        except Exception as e:
            self.log(f"Request failed: {str(e)}")
            return None
    
    def test_admin_login(self):
        """Test admin login"""
        self.log("Testing admin login...")
        
        response = self.make_request('POST', '/auth/login', data={
            'email': TEST_ADMIN_EMAIL,
            'password': TEST_ADMIN_PASSWORD
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get('access_token')
            self.log("✅ Admin login successful")
            return True
        else:
            self.log("❌ Admin login failed")
            return False
    
    def test_create_test_provider(self):
        """Create a test provider for workflow testing"""
        self.log("Creating test provider...")
        
        # First register as user
        user_data = {
            'email': TEST_PROVIDER_EMAIL,
            'password': 'TestPassword123!',
            'phone': '+201234567890',
            'user_type': 'service_provider'
        }
        
        response = self.make_request('POST', '/auth/register', data=user_data)
        
        if not response or response.status_code != 201:
            self.log("❌ Failed to register test provider")
            return False
        
        # Login as provider
        response = self.make_request('POST', '/auth/login', data={
            'email': TEST_PROVIDER_EMAIL,
            'password': 'TestPassword123!'
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.provider_token = data.get('access_token')
            self.log("✅ Provider login successful")
            
            # Create provider profile
            profile_data = {
                'first_name': 'Test',
                'last_name': 'Provider',
                'business_name': 'Test Business',
                'experience_years': 5,
                'bio': 'Test provider for workflow testing'
            }
            
            response = self.make_request('POST', '/auth/complete-provider-profile', 
                                       token=self.provider_token, data=profile_data)
            
            if response and response.status_code == 201:
                profile = response.json().get('profile', {})
                self.provider_id = profile.get('id')
                self.log(f"✅ Provider profile created with ID: {self.provider_id}")
                return True
            else:
                self.log("❌ Failed to create provider profile")
                return False
        else:
            self.log("❌ Provider login failed")
            return False
    
    def test_document_upload(self):
        """Test provider document upload"""
        self.log("Testing document upload...")
        
        if not self.provider_token:
            self.log("❌ No provider token available")
            return False
        
        # Create a dummy PDF file
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000104 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n164\n%%EOF"
        
        files = {
            'document': ('test_certificate.pdf', dummy_pdf_content, 'application/pdf')
        }
        
        data = {
            'document_type': 'certificate'
        }
        
        response = self.make_request('POST', '/providers/documents/upload', 
                                   token=self.provider_token, data=data, files=files)
        
        if response and response.status_code == 201:
            document_data = response.json().get('document', {})
            self.test_document_id = document_data.get('id')
            self.log(f"✅ Document uploaded successfully with ID: {self.test_document_id}")
            return True
        else:
            self.log("❌ Document upload failed")
            return False
    
    def test_admin_view_providers(self):
        """Test admin viewing providers"""
        self.log("Testing admin view providers...")
        
        if not self.admin_token:
            self.log("❌ No admin token available")
            return False
        
        response = self.make_request('GET', '/admin/providers', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            self.log(f"✅ Admin can view {len(providers)} providers")
            
            # Check if our test provider is in the list
            test_provider = next((p for p in providers if p.get('id') == self.provider_id), None)
            if test_provider:
                self.log(f"✅ Test provider found in admin list: {test_provider.get('first_name')} {test_provider.get('last_name')}")
                return True
            else:
                self.log("❌ Test provider not found in admin list")
                return False
        else:
            self.log("❌ Failed to get providers list")
            return False
    
    def test_admin_view_documents(self):
        """Test admin viewing provider documents"""
        self.log("Testing admin view provider documents...")
        
        if not self.admin_token or not self.provider_id:
            self.log("❌ Missing admin token or provider ID")
            return False
        
        response = self.make_request('GET', f'/admin/providers/{self.provider_id}/documents', 
                                   token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            self.log(f"✅ Admin can view {len(documents)} documents for provider")
            
            if documents:
                doc = documents[0]
                self.log(f"✅ Document details: Type={doc.get('document_type')}, Status={doc.get('verification_status')}")
                return True
            else:
                self.log("❌ No documents found for provider")
                return False
        else:
            self.log("❌ Failed to get provider documents")
            return False
    
    def test_document_review(self):
        """Test admin reviewing documents"""
        self.log("Testing document review...")
        
        if not self.admin_token or not self.test_document_id:
            self.log("❌ Missing admin token or document ID")
            return False
        
        # First approve the document
        response = self.make_request('PUT', f'/admin/documents/{self.test_document_id}/review',
                                   token=self.admin_token, data={
                                       'action': 'approve'
                                   })
        
        if response and response.status_code == 200:
            self.log("✅ Document approved successfully")
            
            # Then reject it to test both flows
            response = self.make_request('PUT', f'/admin/documents/{self.test_document_id}/review',
                                       token=self.admin_token, data={
                                           'action': 'reject',
                                           'reason': 'Test rejection for workflow verification'
                                       })
            
            if response and response.status_code == 200:
                self.log("✅ Document rejection successful")
                return True
            else:
                self.log("❌ Document rejection failed")
                return False
        else:
            self.log("❌ Document approval failed")
            return False
    
    def test_provider_verification(self):
        """Test provider verification workflow"""
        self.log("Testing provider verification...")
        
        if not self.admin_token or not self.provider_id:
            self.log("❌ Missing admin token or provider ID")
            return False
        
        # First approve the provider
        response = self.make_request('POST', f'/admin/providers/{self.provider_id}/verify',
                                   token=self.admin_token, data={
                                       'action': 'approve'
                                   })
        
        if response and response.status_code == 200:
            self.log("✅ Provider approved successfully")
            
            # Then reject to test both flows
            response = self.make_request('POST', f'/admin/providers/{self.provider_id}/verify',
                                       token=self.admin_token, data={
                                           'action': 'reject',
                                           'reason': 'Test rejection for workflow verification'
                                       })
            
            if response and response.status_code == 200:
                self.log("✅ Provider rejection successful")
                return True
            else:
                self.log("❌ Provider rejection failed")
                return False
        else:
            self.log("❌ Provider approval failed")
            return False
    
    def cleanup(self):
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        # In a real scenario, you might want to delete the test provider
        # For now, we'll just log the cleanup
        self.log("✅ Cleanup completed")
    
    def run_all_tests(self):
        """Run all workflow tests"""
        self.log("Starting admin-provider workflow tests...")
        
        tests = [
            ("Admin Login", self.test_admin_login),
            ("Create Test Provider", self.test_create_test_provider),
            ("Document Upload", self.test_document_upload),
            ("Admin View Providers", self.test_admin_view_providers),
            ("Admin View Documents", self.test_admin_view_documents),
            ("Document Review", self.test_document_review),
            ("Provider Verification", self.test_provider_verification),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running Test: {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} PASSED")
                else:
                    failed += 1
                    self.log(f"❌ {test_name} FAILED")
            except Exception as e:
                failed += 1
                self.log(f"❌ {test_name} FAILED with exception: {str(e)}")
            
            time.sleep(1)  # Brief pause between tests
        
        # Cleanup
        self.cleanup()
        
        # Summary
        self.log(f"\n--- Test Results Summary ---")
        self.log(f"Total Tests: {passed + failed}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 All tests passed! The admin-provider workflow is working correctly.")
        else:
            self.log("⚠️ Some tests failed. Please review the issues above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = WorkflowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)