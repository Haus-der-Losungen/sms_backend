import requests
import json

# Test user creation
base_url = "http://127.0.0.1:8000/api/v1/user"

test_data = {
    "user": {
        "role": "student",
        "pin": "123456"
    },
    "profile": {
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "email": "test@example.com",
        "gender": "other"
    }
}

print("Testing user creation:")
print(f"URL: {base_url}/create-user")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/create-user",
        json=test_data,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}") 