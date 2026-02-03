from .account import (
    Account,
    AccountStatus,
)

# Create a proxy object that always returns the current db_session from models.engine
class DBSessionProxy:
    """Proxy that always returns the current db_session from models.engine"""
    
    def __getattr__(self, name):
        from . import engine
        if engine.db_session is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return getattr(engine.db_session, name)
    
    def __setattr__(self, name, value):
        from . import engine
        if engine.db_session is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return setattr(engine.db_session, name, value)

db_session = DBSessionProxy()

__all__ = [
    "Account",
    "AccountStatus",
    "db_session"
]

