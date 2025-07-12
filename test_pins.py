import bcrypt

# Test the stored hashes with different PINs
stored_hashes = [
    "$2b$12$eKqE5yysrvmfEbdpWc2k..IA7aQUAWI5tCWKUSSOv3gOa5mnTwXZq",
    "$2b$12$SRazh3jdhP2zB83QLyFP2ua5WMyzLqrdLYFPY.yssE5RalbYNDxQe",
    "$2b$12$d4trZUIrOM4j6wKn8Chqo.NsKPMYfIFYYo5VzkVhvzT7Ov8LKdrkW"
]

# Test common PINs
test_pins = ["123456", "1234", "0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999"]

print("Testing PIN verification:")
print("=" * 50)

for i, hash_value in enumerate(stored_hashes):
    print(f"\nHash {i+1}: {hash_value}")
    for pin in test_pins:
        if bcrypt.checkpw(pin.encode('utf-8'), hash_value.encode('utf-8')):
            print(f"  ✅ PIN '{pin}' matches this hash")
            break
    else:
        print(f"  ❌ No common PIN matches this hash") 