from typing import TYPE_CHECKING
from controllers import account_router

from .base import Extension

if TYPE_CHECKING:
    from constellation_app import ConstellationApp


class RoutersExtension(Extension):
    """Router extension for registering all API routes"""
    
    def init_app(self, app: "ConstellationApp") -> None:
        """Register all routers with the app"""
        app.include_router(account_router)


ext_routers = RoutersExtension()
