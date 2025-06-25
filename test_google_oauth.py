#!/usr/bin/env python3
"""
Test script to verify Google OAuth redirect URI configuration
"""

import requests
import urllib.parse

def test_google_login_redirect():
    """Test the Google login endpoint to see the redirect URI being used"""
    
    # Test the Google login endpoint
    login_url = "http://localhost:8000/api/v1/auth/google/login"
    
    try:
        print("🔍 Testing Google OAuth redirect URI...")
        print(f"📡 Making request to: {login_url}")
        
        # Make a GET request to the login endpoint
        response = requests.get(login_url, allow_redirects=False)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 307:  # Temporary redirect
            redirect_url = response.headers.get('Location')
            print(f"🔄 Redirect URL: {redirect_url}")
            
            # Parse the redirect URL to extract the redirect_uri parameter
            parsed_url = urllib.parse.urlparse(redirect_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            redirect_uri = query_params.get('redirect_uri', [None])[0]
            client_id = query_params.get('client_id', [None])[0]
            
            print(f"🎯 Extracted redirect_uri: {redirect_uri}")
            print(f"🔑 Client ID: {client_id}")
            
            # Check if redirect_uri matches expected value
            expected_redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
            
            if redirect_uri == expected_redirect_uri:
                print("✅ SUCCESS: Redirect URI matches expected value!")
                print(f"   Expected: {expected_redirect_uri}")
                print(f"   Actual:   {redirect_uri}")
            else:
                print("❌ ERROR: Redirect URI mismatch!")
                print(f"   Expected: {expected_redirect_uri}")
                print(f"   Actual:   {redirect_uri}")
                
        else:
            print(f"❌ Unexpected response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
        print("   Make sure your backend is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_callback_endpoint():
    """Test the callback endpoint directly (should show error without proper parameters)"""
    
    callback_url = "http://localhost:8000/api/v1/auth/google/callback"
    
    try:
        print("\n🔍 Testing callback endpoint...")
        print(f"📡 Making request to: {callback_url}")
        
        response = requests.get(callback_url, allow_redirects=False)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 307:  # Redirect to frontend with error
            redirect_url = response.headers.get('Location')
            print(f"🔄 Redirect URL: {redirect_url}")
            
            if "error=no_code" in redirect_url:
                print("✅ SUCCESS: Callback endpoint is working correctly!")
                print("   It properly handles missing authorization code")
            else:
                print("⚠️  WARNING: Unexpected redirect response")
                
        else:
            print(f"📄 Response content: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Google OAuth Redirect URI Test")
    print("=" * 50)
    
    test_google_login_redirect()
    test_callback_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("1. If redirect URI matches expected value, your backend is configured correctly")
    print("2. Make sure to add this redirect URI to your Google Console:")
    print("   http://localhost:8000/api/v1/auth/google/callback")
    print("3. The callback endpoint should redirect to frontend with error when accessed directly")

if __name__ == "__main__":
    main() 