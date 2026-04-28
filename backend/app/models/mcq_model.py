"""Pydantic schemas for MCQ generation pipeline."""

from typing import List, Optional
from pydantic import BaseModel, Field


class MCQChoice(BaseModel):
    """Choice data contract for bilingual MCQs."""

    id: str
    text_en: str
    text_mn: str
    is_correct: bool
    explanation: Optional[str] = None
    source: Optional[str] = None


class MCQ(BaseModel):
    """Full MCQ payload returned to clients."""

    question_number: int
    question_en: str
    question_mn: str
    choices: List[MCQChoice]
    explanation_en: str
    explanation_mn: str
    concept: str
    difficulty: str
    page_reference: Optional[str] = None


class MCQRequest(BaseModel):
    """Request body for generating MCQs from an existing PDF ingestion."""

    pdf_id: str
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    num_questions: int = Field(default=10, ge=1, le=20)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")


class MCQResponse(BaseModel):
    """Response wrapper for MCQ generation results."""

    pdf_id: str
    mcqs: List[MCQ]
    total_generated: int

