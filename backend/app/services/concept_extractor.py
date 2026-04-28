"""LLM-powered concept extraction for selected page ranges."""

from typing import List
import json

from app.services.llm_client import genai_client, GEMINI_MODEL


class ConceptExtractor:
    """Uses Gemini to identify main concepts, facts, and relationships."""

    def extract(self, text: str, max_concepts: int = 15) -> List[str]:
        """Return a list of prioritized concepts from the provided chapter text."""
        prompt = f"""
Analyze this textbook section and extract the key concepts that should be tested.

TEXT:
{text[:8000]}

INSTRUCTIONS:
- Return ONLY JSON.
- Include 10-{max_concepts} concept strings covering definitions, processes, and relationships.

FORMAT:
{{"concepts": ["concept1", "concept2"]}}
"""
        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        data = json.loads(response.text)
        return data.get("concepts", [])

