"""Automatic cleanup service for uploads and chroma_db directories."""

import logging
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)


class CleanupService:
    """Service to automatically clean old uploads and ChromaDB collections."""

    def __init__(self, max_age_hours: int = 24):
        """
        Initialize cleanup service.
        
        Args:
            max_age_hours: Maximum age in hours before files/collections are deleted (default: 24)
        """
        self.max_age_hours = max_age_hours
        self.uploads_dir = Path("uploads")
        self.chroma_db_path = Path(settings.CHROMA_DB_PATH)
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_db_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    def clean_uploads(self) -> int:
        """Remove old PDF files from uploads directory."""
        if not self.uploads_dir.exists():
            return 0

        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)

        try:
            for file_path in self.uploads_dir.glob("*.pdf"):
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old upload: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning uploads: {e}")
            return deleted_count

    def clean_chroma_db(self) -> int:
        """Remove old ChromaDB collections."""
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)

        try:
            collections = self.chroma_client.list_collections()
            for collection in collections:
                try:
                    # Get collection metadata to check creation time
                    metadata = collection.metadata or {}
                    
                    # Try to get creation time from metadata
                    created_str = metadata.get("created_at")
                    if created_str:
                        try:
                            created_time = datetime.fromisoformat(created_str)
                            if created_time < cutoff_time:
                                self.chroma_client.delete_collection(name=collection.name)
                                deleted_count += 1
                                logger.info(f"Deleted old ChromaDB collection: {collection.name}")
                        except (ValueError, TypeError):
                            # Invalid date format, check if empty instead
                            try:
                                count = collection.count()
                                if count == 0:
                                    self.chroma_client.delete_collection(name=collection.name)
                                    deleted_count += 1
                                    logger.info(f"Deleted empty ChromaDB collection: {collection.name}")
                            except Exception:
                                pass
                    else:
                        # If no creation time, check if collection is empty
                        try:
                            count = collection.count()
                            if count == 0:
                                self.chroma_client.delete_collection(name=collection.name)
                                deleted_count += 1
                                logger.info(f"Deleted empty ChromaDB collection: {collection.name}")
                        except Exception:
                            # Collection might be corrupted, try to delete it
                            try:
                                self.chroma_client.delete_collection(name=collection.name)
                                deleted_count += 1
                                logger.info(f"Deleted corrupted ChromaDB collection: {collection.name}")
                            except Exception:
                                pass
                except Exception as e:
                    logger.warning(f"Failed to process collection {collection.name}: {e}")

            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning ChromaDB: {e}")
            return deleted_count

    def clean_all(self) -> dict:
        """Clean both uploads and ChromaDB, return summary."""
        logger.info(f"Starting cleanup (max age: {self.max_age_hours} hours)")
        
        uploads_deleted = self.clean_uploads()
        collections_deleted = self.clean_chroma_db()
        
        result = {
            "uploads_deleted": uploads_deleted,
            "collections_deleted": collections_deleted,
            "timestamp": datetime.now().isoformat(),
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result

