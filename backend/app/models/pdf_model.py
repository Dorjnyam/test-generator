"""Schemas for PDF ingestion and page-range customization."""

from typing import Optional
from pydantic import BaseModel, Field


class PageRange(BaseModel):
    """Represents a range of pages the user wants to ingest or query."""

    start_page: int = Field(ge=1, description="Inclusive starting page.")
    end_page: int = Field(ge=1, description="Inclusive ending page.")

    def normalized(self) -> "PageRange":
        """Return a copy that guarantees start <= end."""
        if self.start_page > self.end_page:
            return PageRange(start_page=self.end_page, end_page=self.start_page)
        return self


class PDFIngestResponse(BaseModel):
    """Metadata returned once a PDF has been processed into the RAG store."""

    pdf_id: str
    filename: str
    total_pages: int
    chunks_created: int
    ingested_range: Optional[PageRange] = None
    status: str = "processed"

