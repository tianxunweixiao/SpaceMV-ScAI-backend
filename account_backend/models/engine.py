from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
engine = None
SessionLocal = None
db_session = None


def init_db(database_uri: str, pool_size: int = 30, max_overflow: int = 10):
    """Initialize database connection"""
    global engine, SessionLocal, db_session
    
    engine = create_engine(
        database_uri,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        echo=False
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a db object that mimics flask_sqlalchemy's interface
    class DB:
        def __init__(self):
            self.session = None
            self.Model = declarative_base(metadata=metadata)
        
        def init_app(self, app):
            pass
        
        def create_session(self):
            self.session = SessionLocal()
            return self.session
        
        def close_session(self):
            if self.session:
                self.session.close()
                self.session = None
    
    db_session = DB()
    return db_session
