"""Main module"""

import logging

from fastapi import FastAPI
from src.api.exception_handlers import setup_exception_handlers
from src.api.middleware import setup_middleware
from src.api.routes import setup_routes
from src.core import config, tasks

app = FastAPI()
request_logger = logging.getLogger("request")


def setup_event_handlers(app: FastAPI) -> None:
    app.add_event_handler("startup", tasks.create_start_app_handler(app))
    app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

    setup_routes(app)
    setup_event_handlers(app)
    setup_middleware(app)
    setup_exception_handlers(app)

    return app


app = create_app()
