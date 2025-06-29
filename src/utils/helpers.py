"Helper function"
import uuid


class Helpers:
    @staticmethod
    async def generate_uuid() -> str:
        """Generate a UUID as a string."""
        return str(uuid.uuid4())
