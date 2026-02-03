from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from constellation_app import ConstellationApp


class Extension:
    """Base class for all extensions"""
    
    def is_enabled(self) -> bool:
        """Check if the extension is enabled"""
        return True
    
    def init_app(self, app: "ConstellationApp") -> None:
        """Initialize the extension with the app"""
        raise NotImplementedError
