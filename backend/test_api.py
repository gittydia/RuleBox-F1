import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_api_endpoints():
    print("Testing RuleBox F1 API Endpoints...")
    print("=" * 50)
    
    # Test 1: Data Status
    print("\n1. Testing /api/data-status")
    try:
        response = requests.get(f"{BASE_URL}/api/data-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: Found {data.get('total_documents', 0)} documents")
            print(f"  Collections: {data.get('collections', {})}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Search
    print("\n2. Testing /api/search")
    try:
        search_data = {"query": "engine power unit"}
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✓ Success: Found {len(results)} search results")
            if results:
                print(f"  First result: {results[0].get('title', 'No title')[:50]}...")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: AI Query
    print("\n3. Testing /api/ai-query")
    try:
        ai_data = {"query": "What are the main engine regulations?"}
        response = requests.post(
            f"{BASE_URL}/api/ai-query",
            json=ai_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"✓ Success: AI response received ({len(response_text)} characters)")
            print(f"  Response preview: {response_text[:100]}...")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: User Registration
    print("\n4. Testing /auth/register")
    try:
        register_data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: {data.get('message', 'User registered')}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: User Login
    print("\n5. Testing /auth/login")
    try:
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('token', '')
            print(f"✓ Success: Login token received ({len(token)} characters)")
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
