"""Routes for manual cleanup operations."""

import logging
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.services.cleanup_service import CleanupService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cleanup", tags=["cleanup"])


@router.post("/run")
async def run_cleanup():
    """Manually trigger cleanup of uploads and ChromaDB."""
    if not settings.CLEANUP_ENABLED:
        raise HTTPException(status_code=403, detail="Cleanup is disabled")
    
    try:
        cleanup = CleanupService(max_age_hours=settings.CLEANUP_MAX_AGE_HOURS)
        result = cleanup.clean_all()
        return {
            "success": True,
            "message": "Cleanup completed",
            "result": result,
        }
    except Exception as e:
        logger.exception("Manual cleanup failed")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {e}") from e

