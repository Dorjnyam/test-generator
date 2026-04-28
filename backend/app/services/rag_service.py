"""ChromaDB helper utilities for storing and querying textbook content."""

from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class RAGService:
    """Thin wrapper around ChromaDB persistent collections."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    def reset_collection(self, pdf_id: str, metadata: Optional[Dict] = None):
        """Create a fresh collection for a PDF, replacing an existing one if needed."""
        from datetime import datetime
        
        try:
            self.client.delete_collection(name=pdf_id)
        except Exception:
            pass
        
        # Add creation time to metadata for cleanup tracking
        collection_metadata = metadata or {}
        collection_metadata["created_at"] = datetime.now().isoformat()
        
        return self.client.create_collection(name=pdf_id, metadata=collection_metadata)

    def add_chunks(
        self,
        pdf_id: str,
        chunks: List[Dict],
        embeddings: List[List[float]],
    ) -> int:
        """Store chunks plus embeddings with metadata."""
        collection = self.client.get_collection(name=pdf_id)
        ids = [f"{pdf_id}_chunk_{idx}" for idx in range(len(chunks))]

        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "chunk_id": idx,
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "word_count": chunk["word_count"],
                "section": chunk.get("section", "unknown"),
            }
            for idx, chunk in enumerate(chunks)
        ]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def fetch_pages(self, pdf_id: str, page_start: int, page_end: int) -> Dict[str, List]:
        """Retrieve chunks spanning a page range."""
        collection = self.client.get_collection(name=pdf_id)
        return collection.get(
            where={
                "$and": [
                    {"page_start": {"$gte": page_start}},
                    {"page_end": {"$lte": page_end}},
                ]
            },
            include=["documents", "metadatas"],
        )

    def query_related(
        self,
        pdf_id: str,
        query_embedding: List[float],
        exclusion_range: Tuple[int, int],
        n_results: int = 5,
    ) -> Dict:
        """Semantic search excluding the main page range to build distractors."""
        collection = self.client.get_collection(name=pdf_id)
        start, end = exclusion_range
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={
                "$or": [
                    {"page_end": {"$lt": start}},
                    {"page_start": {"$gt": end}},
                ]
            },
            include=["documents", "metadatas"],
        )

