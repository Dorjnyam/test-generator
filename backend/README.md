# PDF MCQ Generator Backend

FastAPI backend implementing a RAG-powered MCQ generator with Gemini and ChromaDB.

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
copy env.template .env  # or cp env.template .env on mac/linux
```

Fill in `GEMINI_API_KEY` inside `.env`. Then run:

```bash
python test_setup.py
python test_gemini.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`

## Command-line Usage

Process a PDF (optionally pick a page range):

```bash
cd backend
python cli.py process --pdf path/to/book.pdf --start-page 40 --end-page 80
```

Generate MCQs for an ingested PDF:

```bash
python cli.py generate --pdf-id YOUR_PDF_ID --page-start 40 --page-end 80 --num-questions 12
python cli.py generate --pdf-id book_69b51eb3 --page-start 31 --page-end 58 --num-questions 10 --difficulty hard
```
Or run the guided flow (prompts for PDF path, pages, question count, etc.):

```bash
python cli.py interactive
```

Clean up old uploads and ChromaDB collections:

```bash
# Use default max age (24 hours)
python cli.py cleanup

# Custom max age (e.g., 12 hours)
python cli.py cleanup --max-age-hours 12
```

All CLI commands work directly in Windows CMD/Powershell or macOS/Linux shells.

## Key Endpoints

- `POST /api/pdf/upload`: upload a PDF with optional `start_page` and `end_page` query params to ingest a specific chapter/range.
- `POST /api/mcq/generate`: generate bilingual MCQs for a processed PDF and page range.

The MCQ pipeline extracts concepts, gathers cross-chapter context for distractors, validates outputs, and returns bilingual JSON with page references.

C:\Users\dell\Downloads\4_1\tusliin_barimt_bichig\book.pdf
C:\Users\dell\Downloads\BABOK_Guide_v3_Member 1.pdf
C:\Users\dell\Downloads\Modern_Software_Engineering.pdf