"""Command-line utilities for the MCQ generator backend."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import uuid

from app.services.registry import mcq_generator, pdf_processor
from app.services.cleanup_service import CleanupService
from app.config import settings


def ingest_pdf(pdf_path: Path, pdf_id: str | None, start_page: int | None, end_page: int | None):
    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    resolved_pdf_id = pdf_id or pdf_path.stem.replace(" ", "_") + f"_{uuid.uuid4().hex[:8]}"
    text, total_pages, (range_start, range_end) = pdf_processor.extract_text(
        pdf_path, page_start=start_page, page_end=end_page
    )
    metadata = {
        "title": pdf_path.name,
        "total_pages": total_pages,
        "ingested_range": f"{range_start}-{range_end}",
    }
    chunks = mcq_generator.process_pdf_to_rag(text, pdf_id=resolved_pdf_id, metadata=metadata)
    result = {
        "pdf_id": resolved_pdf_id,
        "total_pages": total_pages,
        "ingested_pages": f"{range_start}-{range_end}",
        "chunks_created": chunks,
    }
    return result


def process_command(args: argparse.Namespace):
    """Ingest a PDF into the RAG store."""
    result = ingest_pdf(
        pdf_path=Path(args.pdf),
        pdf_id=args.pdf_id,
        start_page=args.start_page,
        end_page=args.end_page,
    )
    print(json.dumps(result, indent=2))


def generate_command(args: argparse.Namespace):
    """Generate MCQs for an already ingested PDF."""
    mcqs = mcq_generator.generate_mcqs(
        pdf_id=args.pdf_id,
        page_start=args.page_start,
        page_end=args.page_end,
        num_questions=args.num_questions,
        difficulty=args.difficulty,
    )
    print(json.dumps({"total_generated": len(mcqs), "mcqs": mcqs}, indent=2, ensure_ascii=False))


def cleanup_command(args: argparse.Namespace):
    """Clean up old uploads and ChromaDB collections."""
    max_age_hours = args.max_age_hours or settings.CLEANUP_MAX_AGE_HOURS
    
    print(f"Starting cleanup (max age: {max_age_hours} hours)...")
    cleanup = CleanupService(max_age_hours=max_age_hours)
    result = cleanup.clean_all()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n✓ Cleanup completed: {result['uploads_deleted']} uploads, {result['collections_deleted']} collections deleted")


def parse_json_filename(filename: str) -> dict | None:
    """
    Parse JSON filename like 'ch1_easy_11_29.json' or 'ch1_hard_11_29.json'.
    Returns dict with: chapter, difficulty, page_start, page_end, or None if invalid.
    """
    # Pattern: ch{number}_{difficulty}_{start}_{end}.json
    pattern = r'ch(\d+)_(easy|medium|hard)_(\d+)_(\d+)\.json'
    match = re.match(pattern, filename, re.IGNORECASE)
    if match:
        return {
            'chapter': int(match.group(1)),
            'difficulty': match.group(2).lower(),
            'page_start': int(match.group(3)),
            'page_end': int(match.group(4)),
        }
    return None


def batch_generate_command(args: argparse.Namespace):
    """
    Generate MCQs for multiple JSON files in a folder.
    Reads JSON filenames to extract chapter, difficulty, and page ranges.
    """
    # Try multiple path resolution strategies
    folder_path = Path(args.folder)
    
    # Strategy 1: If absolute path, use as-is
    if folder_path.is_absolute():
        folder_path = folder_path.expanduser().resolve()
    else:
        # Strategy 2: Try from current working directory
        if folder_path.exists():
            folder_path = folder_path.resolve()
        else:
            # Strategy 3: Try from parent directory (workspace root if running from backend/)
            parent_folder = Path("..") / folder_path
            if parent_folder.exists():
                folder_path = parent_folder.resolve()
            else:
                # Strategy 4: Try from workspace root (two levels up from backend/)
                workspace_folder = Path("../..") / folder_path
                if workspace_folder.exists():
                    folder_path = workspace_folder.resolve()
                else:
                    # Strategy 5: Expand user and resolve
                    folder_path = folder_path.expanduser().resolve()
    
    if not folder_path.exists() or not folder_path.is_dir():
        # Provide helpful error message
        current_dir = Path.cwd()
        suggestions = [
            f"Current directory: {current_dir}",
            f"Tried: {folder_path}",
            f"Try using absolute path or relative from workspace root",
        ]
        raise SystemExit(f"Folder not found: {args.folder}\n" + "\n".join(suggestions))
    
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")
    
    # Find all JSON files matching pattern
    json_files = sorted(folder_path.glob("ch*_*.json"))
    if not json_files:
        print(f"No matching JSON files found in {folder_path}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    print(f"PDF: {pdf_path}")
    print(f"Output folder: {folder_path}\n")
    
    # Ingest PDF once (use full range or first file's range)
    pdf_id = args.pdf_id or pdf_path.stem.replace(" ", "_") + f"_{uuid.uuid4().hex[:8]}"
    
    # Determine page range from all files
    all_ranges = []
    for json_file in json_files:
        parsed = parse_json_filename(json_file.name)
        if parsed:
            all_ranges.append((parsed['page_start'], parsed['page_end']))
    
    if not all_ranges:
        raise SystemExit("No valid JSON files found with expected naming pattern (ch{num}_{difficulty}_{start}_{end}.json)")
    
    min_page = min(r[0] for r in all_ranges)
    max_page = max(r[1] for r in all_ranges)
    
    print(f"Ingesting PDF pages {min_page}-{max_page}...")
    ingest_result = ingest_pdf(pdf_path, pdf_id=pdf_id, start_page=min_page, end_page=max_page)
    print(f"✓ PDF ingested: {ingest_result['pdf_id']}\n")
    
    # Process each JSON file
    success_count = 0
    error_count = 0
    
    for json_file in json_files:
        parsed = parse_json_filename(json_file.name)
        if not parsed:
            print(f"⚠ Skipping {json_file.name} (invalid filename pattern)")
            error_count += 1
            continue
        
        chapter = parsed['chapter']
        difficulty = parsed['difficulty']
        page_start = parsed['page_start']
        page_end = parsed['page_end']
        num_questions = args.num_questions
        
        print(f"Generating {json_file.name}...")
        print(f"  Chapter: {chapter}, Difficulty: {difficulty}, Pages: {page_start}-{page_end}, Questions: {num_questions}")
        
        try:
            mcqs = mcq_generator.generate_mcqs(
                pdf_id=pdf_id,
                page_start=page_start,
                page_end=page_end,
                num_questions=num_questions,
                difficulty=difficulty,
            )
            
            # Write to JSON file
            output_data = {
                "total_generated": len(mcqs),
                "mcqs": mcqs
            }
            
            with json_file.open('w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Generated {len(mcqs)} MCQs, saved to {json_file.name}\n")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Batch generation complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(json_files)}")


def interactive_command(_args: argparse.Namespace):
    """Guided flow: ask for PDF, optional pages, question count, and difficulty."""
    print("=== Interactive MCQ Generator ===")
    pdf_path = Path(input("PDF path: ").strip())
    start_page_raw = input("Start page (leave blank for first page): ").strip()
    end_page_raw = input("End page (leave blank for last page): ").strip()
    num_questions_raw = input("How many questions? [default 10]: ").strip()
    difficulty_raw = input("Difficulty [easy|medium|hard, default medium]: ").strip().lower()

    start_page = int(start_page_raw) if start_page_raw else None
    end_page = int(end_page_raw) if end_page_raw else None
    num_questions = int(num_questions_raw) if num_questions_raw else 10
    difficulty = difficulty_raw if difficulty_raw in {"easy", "hard"} else "medium"

    ingest_result = ingest_pdf(pdf_path, pdf_id=None, start_page=start_page, end_page=end_page)
    print(json.dumps(ingest_result, indent=2))
    generated_pdf_id = ingest_result["pdf_id"]

    gen_args = argparse.Namespace(
        pdf_id=generated_pdf_id,
        page_start=start_page or 1,
        page_end=end_page or ingest_result["total_pages"],
        num_questions=num_questions,
        difficulty=difficulty,
    )
    generate_command(gen_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG-powered MCQ generator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("process", help="Extract + chunk a PDF into the vector store")
    ingest.add_argument("--pdf", required=True, help="Path to the PDF file")
    ingest.add_argument("--pdf-id", help="Optional custom identifier for this PDF")
    ingest.add_argument("--start-page", type=int, help="Inclusive start page to ingest")
    ingest.add_argument("--end-page", type=int, help="Inclusive end page to ingest")
    ingest.set_defaults(func=process_command)

    generate = sub.add_parser("generate", help="Generate MCQs for an ingested PDF")
    generate.add_argument("--pdf-id", required=True, help="Identifier returned during processing")
    generate.add_argument("--page-start", type=int, required=True, help="Starting page number")
    generate.add_argument("--page-end", type=int, required=True, help="Ending page number")
    generate.add_argument("--num-questions", type=int, default=10, help="Number of MCQs to create")
    generate.add_argument(
        "--difficulty", choices=["easy", "medium", "hard"], default="medium", help="Question difficulty"
    )
    generate.set_defaults(func=generate_command)

    interactive = sub.add_parser("interactive", help="Prompt-driven flow (enter PDF path, pages, etc.)")
    interactive.set_defaults(func=interactive_command)

    cleanup = sub.add_parser("cleanup", help="Clean up old uploads and ChromaDB collections")
    cleanup.add_argument(
        "--max-age-hours",
        type=int,
        help=f"Maximum age in hours before deletion (default: {settings.CLEANUP_MAX_AGE_HOURS})"
    )
    cleanup.set_defaults(func=cleanup_command)

    batch = sub.add_parser("batch-generate", help="Generate MCQs for all JSON files in a folder based on filenames")
    batch.add_argument("--pdf", required=True, help="Path to the PDF file")
    batch.add_argument("--folder", required=True, help="Folder containing JSON files (e.g., modern_software_engineering/)")
    batch.add_argument("--pdf-id", help="Optional custom identifier for this PDF (auto-generated if not provided)")
    batch.add_argument("--num-questions", type=int, default=10, help="Number of MCQs per file (default: 10)")
    batch.set_defaults(func=batch_generate_command)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

