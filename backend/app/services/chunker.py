"""Intelligent chunking strategy implementation."""

from typing import Dict, List
import re


class SmartChunker:
    """Creates overlapping logical chunks preserving context."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[Dict]:
        """Return chunk dictionaries with metadata (page_start/end, word_count)."""
        paragraphs = re.split(r"\n\s*\n", text)
        chunks: List[Dict] = []

        current_chunk = []
        current_word_count = 0
        chunk_start_page = 1
        current_page = 1

        for paragraph in paragraphs:
            clean_para = paragraph.strip()
            if not clean_para:
                continue

            page_marker = re.search(r"\[PAGE (\d+)\]", clean_para)
            if page_marker:
                current_page = int(page_marker.group(1))
                clean_para = re.sub(r"\[PAGE \d+\]", "", clean_para).strip()

            para_words = clean_para.split()
            if current_word_count + len(para_words) > self.chunk_size and current_word_count > 0:
                chunks.append(
                    {
                        "text": " ".join(current_chunk).strip(),
                        "page_start": chunk_start_page,
                        "page_end": current_page,
                        "word_count": current_word_count,
                    }
                )
                overlap_words = current_chunk[-self.overlap :] if self.overlap else []
                current_chunk = overlap_words + para_words
                current_word_count = len(current_chunk)
                chunk_start_page = current_page
            else:
                current_chunk.extend(para_words)
                current_word_count += len(para_words)

        if current_chunk:
            chunks.append(
                {
                    "text": " ".join(current_chunk).strip(),
                    "page_start": chunk_start_page,
                    "page_end": current_page,
                    "word_count": current_word_count,
                }
            )

        return chunks

