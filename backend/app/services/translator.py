"""Lightweight translator leveraging Gemini for Mongolian output."""

from typing import Tuple

from app.services.llm_client import genai_client, GEMINI_MODEL


class TranslatorService:
    """Wraps Gemini for bilingual question/answer rendering."""

    def bilingual_pair(self, english_text: str) -> Tuple[str, str]:
        """
        Return a tuple (en, mn) ensuring Mongolian translation reads naturally.

        The service keeps the English text untouched and relies on Gemini for MN.
        """
        prompt = (
            "Translate the following educational text to Mongolian (MN). "
            "Preserve scientific terminology and keep the tone academic. "
            "Only respond with the Mongolian translation.\n\n"
            f"TEXT:\n{english_text}"
        )
        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return english_text, response.text.strip()

