import logging
import time

from fastapi.middleware.cors import CORSMiddleware
from configs import constellation_config
from contexts.wrapper import RecyclableContextVar
from constellation_app import ConstellationApp

# Application Factory Function
def create_fastapi_app_with_configs() -> ConstellationApp:
    """
    create a raw fastapi app
    with configs loaded from .env file
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if constellation_config.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    constellation_app = ConstellationApp(
        title="Constellation API",
        debug=constellation_config.DEBUG
    )

    # add CORS middleware
    constellation_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add middleware for request context
    @constellation_app.middleware("http")
    async def add_request_context(request, call_next):
        # add an unique identifier to each request
        RecyclableContextVar.increment_thread_recycles()
        response = await call_next(request)
        return response

    return constellation_app


def create_app() -> ConstellationApp:
    start_time = time.perf_counter()
    app = create_fastapi_app_with_configs()
    initialize_extensions(app)
    end_time = time.perf_counter()
    if constellation_config.DEBUG:
        logging.info(f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)")
    return app


def initialize_extensions(app: ConstellationApp):
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
            if constellation_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue

        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if constellation_config.DEBUG:
            logging.info(f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)")