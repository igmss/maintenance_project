#!/usr/bin/env python3
"""
Simple script to test API endpoints after the routing fix
"""

import requests
import json

# Backend API URL
API_BASE_URL = "https://maintenance-platform-backend.onrender.com"

def test_api_endpoints():
    """Test the API endpoints to ensure they return JSON"""
    test_endpoints = [
        {"url": "/", "description": "Root endpoint"},
        {"url": "/api/health", "description": "Health check"},
        {"url": "/api/info", "description": "API info"},
        {"url": "/api/users", "description": "Users endpoint"},
        {"url": "/test", "description": "Test interface"},
    ]
    
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    for endpoint in test_endpoints:
        try:
            url = f"{API_BASE_URL}{endpoint['url']}"
            print(f"\n📍 Testing: {endpoint['description']}")
            print(f"   URL: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            content_type = response.headers.get('content-type', 'Not specified')
            print(f"   Content-Type: {content_type}")
            
            # Check if response is JSON
            if 'application/json' in content_type:
                try:
                    json_data = response.json()
                    print(f"   ✅ Valid JSON response")
                    
                    # Show a preview of the response
                    if isinstance(json_data, dict):
                        if 'message' in json_data:
                            print(f"   Message: {json_data['message']}")
                        if 'endpoints' in json_data:
                            print(f"   Available endpoints: {len(json_data['endpoints'])}")
                        if 'error' in json_data:
                            print(f"   Error: {json_data['error']}")
                    elif isinstance(json_data, list):
                        print(f"   Items count: {len(json_data)}")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Content-Type says JSON but failed to parse")
                    print(f"   Preview: {response.text[:200]}...")
            else:
                print(f"   ⚠️  Non-JSON response")
                if response.status_code == 200:
                    # Check if it's HTML (which was the original problem)
                    if 'text/html' in content_type:
                        print(f"   ❌ HTML response detected (this was the bug)")
                        if '<title>' in response.text:
                            # Extract title
                            title_start = response.text.find('<title>') + 7
                            title_end = response.text.find('</title>')
                            title = response.text[title_start:title_end]
                            print(f"   HTML Title: {title}")
                    print(f"   Preview: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

def check_specific_users_endpoint():
    """Test the /api/users endpoint specifically"""
    print("\n" + "=" * 50)
    print("🔍 Detailed Users Endpoint Test")
    print("=" * 50)
    
    url = f"{API_BASE_URL}/api/users"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print(f"✅ Successfully parsed JSON")
                    print(f"Data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"Number of users: {len(data)}")
                        if data:
                            print(f"Sample user keys: {list(data[0].keys()) if data else 'No users'}")
                    else:
                        print(f"Response: {data}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response: {response.text[:500]}...")
            else:
                print(f"❌ Non-JSON content type: {response.headers.get('content-type')}")
                print(f"Raw response: {response.text[:500]}...")
        else:
            print(f"❌ Non-200 status code")
            print(f"Response: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Error testing users endpoint: {e}")

def main():
    """Main function"""
    print("🚀 API Endpoint Testing Script")
    
    # Test all endpoints
    test_api_endpoints()
    
    # Focus on users endpoint
    check_specific_users_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nKey findings:")
    print("- If /api/users returns JSON: ✅ Routing fix worked")
    print("- If /api/users returns HTML: ❌ Still serving static files")
    print("- Check /test endpoint for the test interface")

if __name__ == "__main__":
    main()