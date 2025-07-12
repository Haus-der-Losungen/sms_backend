"""Dependency for db."""

import logging
from typing import Callable
from databases import Database
from fastapi import Depends, Request
from src.db.repos.base import BaseRepository

app_logger = logging.getLogger("app")


def get_database(request: Request) -> Database:
    db = getattr(request.app.state, "_db", None)
    if db is None:
        raise RuntimeError("Db connection not initialized.")
    return db


def get_repository(repo_type: type[BaseRepository]) -> Callable:
    def get_repo(db: Database = Depends(get_database)) -> BaseRepository:
        return repo_type(db)
    return get_repo