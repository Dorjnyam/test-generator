"""Routes for PDF upload and ingestion into the RAG store."""

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
import logging

from app.config import settings
from app.models.pdf_model import PDFIngestResponse, PageRange
from app.services.registry import mcq_generator, pdf_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pdf", tags=["pdf"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


@router.post("/upload", response_model=PDFIngestResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    start_page: Optional[int] = Query(None, ge=1, description="Inclusive start page to ingest."),
    end_page: Optional[int] = Query(None, ge=1, description="Inclusive end page to ingest."),
):
    """Handle PDF ingestion with optional page-range customization."""
    if not file.filename.lower().endswith(tuple(settings.allowed_extensions)):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_id = str(uuid.uuid4())
    saved_path = UPLOAD_DIR / f"{pdf_id}.pdf"

    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text, total_pages, normalized_range = pdf_processor.extract_text(
            saved_path, page_start=start_page, page_end=end_page
        )
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Unable to extract text from PDF.")

        range_model = PageRange(start_page=normalized_range[0], end_page=normalized_range[1])

        metadata = {
            "title": file.filename,
            "total_pages": total_pages,
            "ingested_range": f"{range_model.start_page}-{range_model.end_page}",
        }

        chunks_created = mcq_generator.process_pdf_to_rag(
            pdf_text=extracted_text,
            pdf_id=pdf_id,
            metadata=metadata,
        )

        return PDFIngestResponse(
            pdf_id=pdf_id,
            filename=file.filename,
            total_pages=total_pages,
            chunks_created=chunks_created,
            ingested_range=range_model,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("PDF upload failed")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {exc}") from exc

