"""Routes for MCQ generation leveraging the RAG pipeline."""

from fastapi import APIRouter, HTTPException

from app.models.mcq_model import MCQRequest, MCQResponse
from app.services.registry import mcq_generator

router = APIRouter(prefix="/api/mcq", tags=["mcq"])


@router.post("/generate", response_model=MCQResponse)
async def generate_mcqs(request: MCQRequest):
    """Generate MCQs for a previously ingested PDF and specific page range."""
    try:
        mcqs = mcq_generator.generate_mcqs(
            pdf_id=request.pdf_id,
            page_start=request.page_start,
            page_end=request.page_end,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
        )
        return MCQResponse(pdf_id=request.pdf_id, mcqs=mcqs, total_generated=len(mcqs))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating MCQs: {exc}") from exc

