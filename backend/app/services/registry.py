"""Shared service singletons to avoid repeated heavy initializations."""

from app.services.mcq_generator import MCQGenerator
from app.services.pdf_processor import PDFProcessor

mcq_generator = MCQGenerator()
pdf_processor = PDFProcessor()

