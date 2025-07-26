"""Route config"""

from fastapi import FastAPI

from src.core import config


def setup_routes(app: FastAPI) -> None:
    """Configure all application routes."""
    from src.api.routes.user import user_router
    from src.api.routes.profile import profile_router
    from src.api.routes.admin import admin_router
  



    api_prefix = config.API_PREFIX

    app.include_router(user_router, prefix=f"{api_prefix}/user", tags=["users"])
    app.include_router(profile_router, prefix=f"{api_prefix}/profile", tags=["profile"])
    app.include_router(admin_router, prefix=f"{api_prefix}/admin", tags=["admin"])
  
   
    