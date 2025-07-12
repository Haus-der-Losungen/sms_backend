import bcrypt
import sqlite3

# Generate a hash for a known PIN
known_pin = "123456"
salt = bcrypt.gensalt()
pin_hash = bcrypt.hashpw(known_pin.encode('utf-8'), salt).decode('utf-8')

print(f"PIN: {known_pin}")
print(f"Generated hash: {pin_hash}")

# Update the database with the correct hash
conn = sqlite3.connect('arcadia.db')
cursor = conn.cursor()

# Update all users to use the same known PIN
update_query = """
UPDATE users 
SET pin_hash = ? 
WHERE is_deleted = FALSE
"""

cursor.execute(update_query, (pin_hash,))
conn.commit()

# Verify the update
cursor.execute("SELECT user_id, pin_hash FROM users WHERE is_deleted = FALSE")
results = cursor.fetchall()

print("\nUpdated users:")
for user_id, hash_value in results:
    print(f"User {user_id}: {hash_value}")

conn.close()
print(f"\n✅ All users now have PIN: {known_pin}") 