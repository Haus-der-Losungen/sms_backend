"""Helper utilities for the application."""

import os
import json
import random
from pathlib import Path


class Helpers:
    """Helper class for utility functions."""
    
    _id_file = Path("last_used_id.json")
    _default_start_id = 1000004
    _max_id = 9999999
    
    @classmethod
    def _load_last_id(cls) -> int:
        """Load the last used ID from persistent storage."""
        try:
            if cls._id_file.exists():
                with open(cls._id_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_used_id', cls._default_start_id)
            return cls._default_start_id
        except (json.JSONDecodeError, IOError):
            return cls._default_start_id
    
    @classmethod
    def _save_last_id(cls, last_id: int) -> None:
        """Save the last used ID to persistent storage."""
        try:
            with open(cls._id_file, 'w') as f:
                json.dump({'last_used_id': last_id}, f)
        except IOError as e:
            raise ValueError(f"Failed to save last used ID: {e}")
    
    @classmethod
    def generate_sequential_id(cls) -> str:
        """Generate a sequential ID and persist the last used ID."""
        last_used_id = cls._load_last_id()
        
        if last_used_id >= cls._max_id:
            raise ValueError("No more IDs available")
        
        new_id = last_used_id + 1
        cls._save_last_id(new_id)
        
        return str(new_id)
    
    @classmethod
    def generate_pin(cls) -> str:
        """Generate a random 6-digit PIN for user creation."""
        pin = str(random.randint(100000, 999999))
        print(f"Generated PIN: {pin}")  # Debug log
        return pin

