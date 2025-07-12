import requests
import json

# Test a simple login request
base_url = "http://127.0.0.1:8000/api/v1/user"

# Test with the expected format
test_data = {
    "user_id": "1000001",
    "pin": "123456"
}

print("Testing login request:")
print(f"URL: {base_url}/login")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/login",
        json=test_data,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}") 