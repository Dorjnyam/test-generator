"""Core MCQ generator orchestrating the RAG pipeline."""

import random
from typing import Dict, List, Optional, Tuple
import json

from app.config import settings
from app.services.chunker import SmartChunker
from app.services.embedder import EmbedderService
from app.services.rag_service import RAGService
from app.services.concept_extractor import ConceptExtractor
from app.services.translator import TranslatorService
from app.services.llm_client import genai_client, GEMINI_MODEL


class MCQGenerator:
    """Coordinates chunking, concept extraction, and bilingual MCQ creation."""

    def __init__(self):
        self.chunker = SmartChunker(settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        self.embedder = EmbedderService()
        self.rag = RAGService()
        self.concept_extractor = ConceptExtractor()
        self.translator = TranslatorService()

    def process_pdf_to_rag(self, pdf_text: str, pdf_id: str, metadata: Dict) -> int:
        """Chunk, embed, and store PDF text in ChromaDB."""
        chunks = self.chunker.chunk_text(pdf_text)
        if not chunks:
            raise ValueError("No readable text detected in PDF.")

        self.rag.reset_collection(pdf_id, metadata=metadata)
        embeddings = self.embedder.encode([chunk["text"] for chunk in chunks])
        stored = self.rag.add_chunks(pdf_id, chunks, embeddings)
        return stored

    def extract_concepts(self, pdf_id: str, page_start: int, page_end: int) -> List[str]:
        """Use Gemini to pull 10-15 key concepts for the requested pages."""
        results = self.rag.fetch_pages(pdf_id, page_start, page_end)
        combined_text = "\n\n".join(results.get("documents", []))
        if not combined_text:
            return []
        return self.concept_extractor.extract(combined_text)

    def generate_mcqs(
        self,
        pdf_id: str,
        page_start: int,
        page_end: int,
        num_questions: int,
        difficulty: str,
    ) -> List[Dict]:
        """Primary entry point to build bilingual MCQs."""
        concepts = self.extract_concepts(pdf_id, page_start, page_end)
        concepts_to_test = concepts[:num_questions]
        mcqs: List[Dict] = []

        for idx, concept in enumerate(concepts_to_test):
            primary_text, page_reference = self._primary_context(pdf_id, page_start, page_end)
            distractor_text = self._distractor_context(pdf_id, concept, (page_start, page_end))
            mcq_payload = self._generate_single_mcq(
                concept=concept,
                primary_text=primary_text,
                distractor_text=distractor_text,
                difficulty=difficulty,
            )
            if mcq_payload:
                self._shuffle_choices(mcq_payload)
                self._enforce_translations(mcq_payload)
                if self._validate_mcq(mcq_payload):
                    mcq_payload["question_number"] = idx + 1
                    mcq_payload["page_reference"] = page_reference
                    mcqs.append(mcq_payload)

        return mcqs

    def _primary_context(self, pdf_id: str, start: int, end: int) -> Tuple[str, str]:
        """Fetch context text and format page reference."""
        results = self.rag.fetch_pages(pdf_id, start, end)
        documents = results.get("documents", [])
        primary_text = "\n".join(documents)
        return primary_text, f"{start}-{end}"

    def _distractor_context(self, pdf_id: str, concept: str, page_range: Tuple[int, int]) -> str:
        """Semantic search outside requested range to craft plausible distractors."""
        embedding = self.embedder.encode([concept])[0]
        related = self.rag.query_related(pdf_id, embedding, page_range)
        documents = related.get("documents", [[]])
        if documents and isinstance(documents[0], list):
            documents = documents[0]
        return "\n".join(documents)
    
    def _shuffle_choices(self, mcq: Dict):
        """Randomize choice order but preserve which is correct."""

        choices = mcq.get("choices", [])
        random.shuffle(choices)

        letters = ["A", "B", "C", "D"]
        for i, choice in enumerate(choices):
            choice["id"] = letters[i]

        mcq["choices"] = choices

    def _generate_single_mcq(
        self, concept: str, primary_text: str, distractor_text: str, difficulty: str
    ) -> Optional[Dict]:
        """Send structured prompt to Gemini to create a bilingual MCQ."""
        difficulty_guidelines = self._get_difficulty_guidelines(difficulty)
        prompt = f"""
You are an expert educator creating a single high-quality multiple choice question.

PRIMARY CONTEXT (use for correct answer):
{primary_text[:3000]}

RELATED CONTEXT (use for distractors):
{distractor_text[:2000]}

TASK:
- Concept: "{concept}"
- Difficulty Level: {difficulty.upper()}

{difficulty_guidelines}

REQUIREMENTS:
- Correct answer MUST originate from the primary context.
- Three distractors must be plausible, referencing related but incorrect ideas.
- Provide both English and Mongolian for question, answers, and explanations.
- DO NOT start the question with phrases such as:
  "According to the text", "According to the provided text", 
  "Өгөгдсөн текстийн дагуу", or similar expressions.
- Phrase the question naturally as a standard MCQ without referencing the source text directly.

OUTPUT JSON ONLY:
{{
  "question_en": "...",
  "question_mn": "...",
  "choices": [
    {{
      "id": "A",
      "text_en": "...",
      "text_mn": "...",
      "is_correct": true,
      "source": "Page ??",
      "explanation": "..."
    }}
  ],
  "concept": "{concept}",
  "difficulty": "{difficulty}",
  "explanation_en": "...",
  "explanation_mn": "..."
}}
"""
        try:
            response = genai_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            mcq = json.loads(response.text)
            return mcq
        except Exception:
            return None

    def _get_difficulty_guidelines(self, difficulty: str) -> str:
        """Return detailed guidelines for each difficulty level."""
        guidelines = {
            "easy": """DIFFICULTY GUIDELINES FOR EASY:
- Question Type: Test fundamental facts, definitions, or direct recall
- Question Structure: 
  * Use simple, direct questions: "What is...?", "Which of the following is...?"
  * Keep question length: 5-10 words
  * Focus on single concepts or definitions
- Answer Choices:
  * Keep each choice: 3-8 words, simple and direct
  * Correct answer should be a straightforward fact from the text
  * Distractors should be clearly wrong but related
- Cognitive Level: Remembering/Understanding (Bloom's Taxonomy Level 1-2)
- Example Question Style: "What is the overriding principle for successful software documentation?"
- Explanation: Brief, direct reference to the text (1-2 sentences)""",

            "medium": """DIFFICULTY GUIDELINES FOR MEDIUM:
- Question Type: Test understanding, application, or comparison
- Question Structure:
  * Use analytical questions: "What is the primary goal of...?", "Which characteristic best exemplifies...?"
  * Question length: 8-15 words
  * May require connecting 2-3 related concepts
- Answer Choices:
  * Each choice: 8-15 words, with some context
  * Correct answer requires understanding relationships or applications
  * Distractors should be plausible but miss key nuances
- Cognitive Level: Applying/Analyzing (Bloom's Taxonomy Level 3-4)
- Example Question Style: "What is the primary goal of task-oriented software documentation?"
- Explanation: Moderate depth, explains why the answer is correct (2-4 sentences)""",

            "hard": """DIFFICULTY GUIDELINES FOR HARD:
- Question Type: Test analysis, synthesis, multi-step reasoning, or evaluation
- Question Structure:
  * Use complex analytical questions: "What is the fundamental principle that defines...?", 
    "When designing... what are the core...?", "Which approach best integrates...?"
  * Question length: 12-20 words
  * Requires synthesizing multiple concepts or evaluating scenarios
- Answer Choices:
  * Each choice: 15-25 words, with detailed context and multiple concepts
  * Correct answer requires deep analysis, synthesis, or evaluation
  * Distractors should be sophisticated and require careful reasoning to eliminate
- Cognitive Level: Analyzing/Synthesizing/Evaluating (Bloom's Taxonomy Level 4-6)
- Example Question Style: "When designing effective technical software documentation that helps adapt software to a user's job, what are the core user motivators that the documentation should emphasize?"
- Explanation: Comprehensive, explains relationships, implications, and reasoning (4-6 sentences)"""
        }
        return guidelines.get(difficulty.lower(), guidelines["medium"])

    def _enforce_translations(self, mcq: Dict):
        """Fill any missing Mongolian text using the translator service."""
        question_en = mcq.get("question_en", "")
        question_mn = mcq.get("question_mn")
        if question_en and not question_mn:
            _, mn = self.translator.bilingual_pair(question_en)
            mcq["question_mn"] = mn

        explanation_en = mcq.get("explanation_en", "")
        explanation_mn = mcq.get("explanation_mn")
        if explanation_en and not explanation_mn:
            _, mn = self.translator.bilingual_pair(explanation_en)
            mcq["explanation_mn"] = mn

        for choice in mcq.get("choices", []):
            if choice.get("text_en") and not choice.get("text_mn"):
                _, mn = self.translator.bilingual_pair(choice["text_en"])
                choice["text_mn"] = mn

    def _validate_mcq(self, mcq: Dict) -> bool:
        """Basic structural validation and optional difficulty check."""
        if not mcq.get("question_en") or not mcq.get("question_mn"):
            return False
        choices = mcq.get("choices", [])
        if len(choices) != 4:
            return False
        correct = [choice for choice in choices if choice.get("is_correct")]
        if len(correct) != 1:
            return False
        return True

    def _validate_difficulty_level(self, mcq: Dict, expected_difficulty: str) -> bool:
        """Optional: Validate that generated question matches difficulty level."""
        question = mcq.get("question_en", "")
        if not question:
            return True  # Skip validation if question is missing
        
        question_word_count = len(question.split())
        avg_choice_length = sum(len(choice.get("text_en", "").split()) 
                                for choice in mcq.get("choices", [])) / max(len(mcq.get("choices", [])), 1)
        
        difficulty_ranges = {
            "easy": {"question_words": (5, 12), "choice_words": (3, 10)},
            "medium": {"question_words": (8, 18), "choice_words": (8, 18)},
            "hard": {"question_words": (12, 25), "choice_words": (15, 30)},
        }
        
        ranges = difficulty_ranges.get(expected_difficulty.lower(), difficulty_ranges["medium"])
        q_min, q_max = ranges["question_words"]
        c_min, c_max = ranges["choice_words"]
        
        # Allow some flexibility (80% of range)
        q_range = q_max - q_min
        c_range = c_max - c_min
        q_min_adj = q_min + (q_range * 0.1)
        q_max_adj = q_max - (q_range * 0.1)
        c_min_adj = c_min + (c_range * 0.1)
        c_max_adj = c_max - (c_range * 0.1)
        
        question_ok = q_min_adj <= question_word_count <= q_max_adj
        choice_ok = c_min_adj <= avg_choice_length <= c_max_adj
        
        # Return True if within range, or if it's close (don't be too strict)
        return question_ok or (question_word_count >= q_min * 0.8 and question_word_count <= q_max * 1.2)

