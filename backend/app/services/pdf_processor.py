"""PDF text extraction and cleaning utilities."""

from pathlib import Path
from typing import Optional, Tuple

import pdfplumber


class PDFProcessor:
    """Extracts raw text plus lightweight metadata from PDF files."""

    def extract_text(
        self,
        file_path: Path,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
    ) -> Tuple[str, int, Tuple[int, int]]:
        """
        Read text from a PDF file.

        Args:
            file_path: path to the uploaded PDF.
            page_start: optional inclusive start page requested by user.
            page_end: optional inclusive end page requested by user.

        Returns:
            tuple: (text, total_pages, (range_start, range_end))
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        with pdfplumber.open(str(file_path)) as pdf:
            total_pages = len(pdf.pages)
            start = page_start or 1
            end = page_end or total_pages
            start = max(1, min(start, total_pages))
            end = max(1, min(end, total_pages))
            if start > end:
                start, end = end, start

            text_parts = []
            for index in range(start - 1, end):
                page = pdf.pages[index]
                page_text = page.extract_text() or ""
                cleaned = page_text.strip()
                if cleaned:
                    text_parts.append(f"\n[PAGE {index + 1}]\n{cleaned}\n")

        return "".join(text_parts), total_pages, (start, end)

