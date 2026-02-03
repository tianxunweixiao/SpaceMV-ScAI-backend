import logging
import os
import time

from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler
from configs import app_config
from constellation_app import ConstellationApp


# Application Factory Function
def create_fastapi_app_with_configs() -> ConstellationApp:
    """
    Create a raw FastAPI app with configs loaded from .env file
    """
    log_file = "backend.log"

    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if app_config.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  
                backupCount=1,          
                encoding="utf-8"
            )
        ]
    )
    
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    
    constellation_app = ConstellationApp(
        title="Constellation API",
        debug=app_config.DEBUG
    )

    # Add CORS middleware
    constellation_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return constellation_app


def create_app() -> ConstellationApp:
    """
    Create and configure the application with all extensions
    """
    start_time = time.perf_counter()
    app = create_fastapi_app_with_configs()
    initialize_extensions(app)
    end_time = time.perf_counter()
    if app_config.DEBUG:
        logging.info(f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)")
    return app


def initialize_extensions(app: ConstellationApp):
    """
    Initialize all application extensions
    
    Args:
        app: ConstellationApp instance
    """
    from extensions import (
        ext_database,
        ext_routers
    )

    extensions = [
        ext_database,
        ext_routers
    ]
    
    for ext in extensions:
        short_name = ext.__class__.__name__
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if app_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue

        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if app_config.DEBUG:
            logging.info(f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)")