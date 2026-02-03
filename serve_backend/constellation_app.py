from fastapi import FastAPI
from typing import Optional


class ConstellationApp(FastAPI):
    """Custom FastAPI application class for constellation backend."""
    
    _app_instance: Optional['ConstellationApp'] = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ConstellationApp._app_instance = self
    
    @classmethod
    def get_app(cls) -> Optional['ConstellationApp']:
        """
        Get the current application instance
        
        Returns:
            Current ConstellationApp instance or None
        """
        return cls._app_instance


def get_app() -> Optional[ConstellationApp]:
    """
    Get the current application instance
    
    Returns:
        Current ConstellationApp instance or None
    """
    return ConstellationApp.get_app()
