import bcrypt
import requests
import json

# Test the login endpoint with different PINs
base_url = "http://127.0.0.1:8000/api/v1/user"

# Test different PINs
test_pins = ["123456", "1234", "0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999", "admin", "password", "test", "user"]

print("Testing login with different PINs:")
print("=" * 50)

for user_id in ["1000001", "1000002", "1000003", "1000004", "1000005", "1000007"]:
    print(f"\nTesting user {user_id}:")
    for pin in test_pins:
        try:
            response = requests.post(
                f"{base_url}/login",
                json={"user_id": user_id, "pin": pin},
                timeout=5
            )
            if response.status_code == 200:
                print(f"  ✅ User {user_id} - PIN '{pin}' works!")
                break
            elif response.status_code == 401:
                continue  # Wrong credentials, try next PIN
            else:
                print(f"  ❌ User {user_id} - PIN '{pin}' - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ User {user_id} - PIN '{pin}' - Error: {e}")
            break
    else:
        print(f"  ❌ User {user_id} - No PIN found from test set") 