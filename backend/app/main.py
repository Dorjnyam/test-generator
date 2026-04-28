"""FastAPI application entry point."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging to stdout/stderr for Fly.io
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

try:
    from app.config import settings
    from app.api.pdf_router import router as pdf_router
    from app.api.mcq_router import router as mcq_router
    from app.api.cleanup_router import router as cleanup_router
    from app.services.cleanup_service import CleanupService
except Exception as e:
    logger.error(f"Failed to import modules: {e}", exc_info=True)
    raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    logger.info(f"GEMINI_API_KEY present: {bool(settings.GEMINI_API_KEY)}")
    logger.info(f"FRONTEND_URL: {settings.FRONTEND_URL}")
    logger.info(f"DEBUG: {settings.DEBUG}")
    
    if settings.CLEANUP_ENABLED:
        try:
            cleanup = CleanupService(max_age_hours=settings.CLEANUP_MAX_AGE_HOURS)
            result = cleanup.clean_all()
            logger.info(f"Startup cleanup completed: {result}")
        except Exception as e:
            logger.warning(f"Startup cleanup failed: {e}")
    
    logger.info("Application startup complete, listening on 0.0.0.0:8080")
    yield
    
    # Shutdown (if needed)
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """Initialize FastAPI app with routers and middleware."""
    try:
        logger.info("Creating FastAPI app...")
        app = FastAPI(
            title=settings.APP_NAME,
            version=settings.APP_VERSION,
            debug=settings.DEBUG,
            lifespan=lifespan,
        )

        # Support multiple frontend URLs (for production deployment)
        frontend_urls = [settings.FRONTEND_URL]
        if settings.FRONTEND_URLS:
            frontend_urls.extend([url.strip() for url in settings.FRONTEND_URLS.split(",") if url.strip()])
        
        logger.info(f"CORS allowed origins: {frontend_urls}")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=frontend_urls,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(pdf_router)
        app.include_router(mcq_router)
        app.include_router(cleanup_router)

        @app.get("/")
        async def root():
            return {
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "status": "running",
            }

        logger.info("FastAPI app created successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to create app: {e}", exc_info=True)
        raise


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

