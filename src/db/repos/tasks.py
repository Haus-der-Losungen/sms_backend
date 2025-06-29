"""database tasks"""

import logging

from databases import Database
from fastapi import FastAPI

from src.core.config import DATABASE_URL

app_logger = logging.getLogger("app")


async def connect_database(app: FastAPI) -> None:
    try:
        database = Database(DATABASE_URL)
        await database.connect()
        app.state._db = database
        app_logger.info("Connected to db.")
    except Exception as e:
        app_logger.exception(
            "Failed to connect to db",
        )


async def disconnect_database(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
        app_logger.info("Disconnected from db")
    except Exception as e:
        app_logger.exception(
            "Error disconnecting from db",
        )