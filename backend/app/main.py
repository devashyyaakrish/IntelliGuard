"""
MD-ADSS FastAPI Application Entry Point
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings
from app.core.security import configure_cors
from app.nova.nova_forge import get_forge
from app.routes import analytics, incidents, threats, websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle management."""
    settings = get_settings()
    forge = get_forge()

    # Activate demo scenario on startup for immediate hackathon demo value
    forge.set_attack_scenario("all")
    logger.info("MD-ADSS starting — demo scenario: ALL (mixed attacks)")

    # Start the Nova Forge pipeline as a background task
    pipeline_task = asyncio.create_task(
        forge.start(
            log_interval=settings.LOG_GENERATION_INTERVAL,
            detect_interval=settings.THREAT_DETECTION_INTERVAL,
        )
    )
    logger.info("Nova Forge pipeline started")

    yield  # Application runs

    # Shutdown
    await forge.stop()
    pipeline_task.cancel()
    try:
        await pipeline_task
    except asyncio.CancelledError:
        pass
    logger.info("MD-ADSS shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Multi-Domain Adversarial Decision Support System — AI-Powered Cybersecurity Platform",
        lifespan=lifespan,
    )

    configure_cors(app)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Register routes
    app.include_router(threats.router)
    app.include_router(incidents.router)
    app.include_router(analytics.router)
    app.include_router(websocket.router)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "system": settings.APP_NAME, "version": settings.APP_VERSION}

    @app.get("/")
    async def root():
        return {
            "system": "MD-ADSS",
            "description": "Multi-Domain Adversarial Decision Support System",
            "powered_by": ["Amazon Nova Lite", "Amazon Nova Act", "Amazon Nova Forge"],
            "docs": "/docs",
        }

    return app


app = create_app()
