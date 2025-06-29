""" configs."""

from databases import DatabaseURL
from starlette.config import Config

config = Config(".env")

# Project configs
PROJECT_NAME = "Arcadia"
VERSION = "1.0"
API_PREFIX = "/api/v1"

# Environment configs
ENV = config("ENV", cast=str, default="DEV")

# Database config
# Sqlite3
if ENV == "DEV":
    DATABASE_URL = config(
        "DATABASE_URL",
        cast=DatabaseURL,
        default="sqlite:///arcadia.db",  
    )
else:
    DATABASE_URL = config(
        "PROD_DATABASE_URL",
        cast=DatabaseURL,
        default="sqlite:///arcadia.db",  
    )

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=60)
REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", cast=int, default=7)
SECRET_KEY = config("SECRET_KEY", cast=str, default="")
ALGORITHM = config("ALGORITHM", cast=str, default="HS256")

