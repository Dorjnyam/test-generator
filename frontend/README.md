# Next.js Frontend

This is the companion UI for the PDF MCQ Generator backend. It lets you upload a PDF chapter, run the RAG pipeline, and review bilingual MCQs.

## Getting Started

```bash
cd frontend
npm install  # or pnpm install / yarn
npm run dev
```

The app runs at `http://localhost:3000`. By default it expects the backend at `http://localhost:8000`. Override by setting `NEXT_PUBLIC_BACKEND_URL` in a `.env.local` file.

## Features

- PDF upload with optional page range selection
- Instant feedback on chunks/ingested pages
- MCQ generation controls (question count + difficulty)
- Bilingual MCQ display with source tracking
- Export generated MCQs as JSON
- Interactive CLI (`python cli.py interactive`) remains available for terminal-only workflows

