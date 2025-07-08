"Helper function"

last_used_id = 1000004  # Initialize with the lowest 7-digit number

class Helpers:
 @staticmethod
 def generate_sequential_id() -> str:
    global last_used_id
    if last_used_id >= 9999999:
        raise ValueError("No more IDs available")
    last_used_id += 1
    return str(last_used_id)

