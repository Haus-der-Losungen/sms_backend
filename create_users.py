#!/usr/bin/env python3
"""
Script to create 20 users via the API endpoint.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any
import random

# Sample data for generating realistic users
FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", 
    "Ivy", "Jack", "Kate", "Liam", "Maya", "Noah", "Olivia", "Paul", 
    "Quinn", "Ruby", "Sam", "Tara"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
]

GENDERS = ["male", "female"]

# API configuration
BASE_URL = "http://127.0.0.1:8000"
CREATE_USER_ENDPOINT = f"{BASE_URL}/api/v1/user/create-user"

def generate_user_data(index: int) -> Dict[str, Any]:
    """Generate realistic user data for the given index."""
    first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
    last_name = LAST_NAMES[index % len(LAST_NAMES)]
    gender = GENDERS[index % len(GENDERS)]
    
    # Generate a unique phone number
    phone = f"1{random.randint(100000000, 999999999)}"
    
    # Generate a unique email
    email = f"{first_name.lower()}.{last_name.lower()}{index}@example.com"
    
    # Generate a PIN (4-6 digits)
    pin = str(random.randint(1000, 999999))
    
    return {
        "user": {
            "role": "student",
            "pin": pin
        },
        "profile": {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "gender": gender
        }
    }

async def create_user(session: aiohttp.ClientSession, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a single user via the API."""
    try:
        async with session.post(
            CREATE_USER_ENDPOINT,
            json=user_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 201:
                result = await response.json()
                print(f"✅ Created user: {user_data['profile']['first_name']} {user_data['profile']['last_name']}")
                print(f"   User ID: {result['user_id']}, PIN: {result['pin']}, Profile ID: {result['profile_id']}")
                return result
            else:
                error_text = await response.text()
                print(f"❌ Failed to create user: {user_data['profile']['first_name']} {user_data['profile']['last_name']}")
                print(f"   Status: {response.status}, Error: {error_text}")
                return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

async def create_multiple_users(num_users: int = 20):
    """Create multiple users sequentially to avoid SQLite locking."""
    print(f"🚀 Creating {num_users} users...")
    print("=" * 50)
    
    # Generate user data
    users_data = [generate_user_data(i) for i in range(num_users)]
    
    # Create users sequentially
    results = []
    async with aiohttp.ClientSession() as session:
        for user_data in users_data:
            result = await create_user(session, user_data)
            results.append(result)
    
    # Count successful creations
    successful = sum(1 for result in results if result is not None)
    failed = len(results) - successful
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   ✅ Successfully created: {successful} users")
    print(f"   ❌ Failed: {failed} users")
    print(f"   📈 Success rate: {(successful/len(results)*100):.1f}%")

if __name__ == "__main__":
    print("🎯 User Creation Script")
    print("=" * 50)
    asyncio.run(create_multiple_users(20)) 