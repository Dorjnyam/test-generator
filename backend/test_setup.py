"""Quick smoke test for local setup."""

print("Testing core dependencies...")
modules = {
    "fastapi": "FastAPI",
    "pdfplumber": "pdfplumber",
    "google.genai": "google-genai",
    "chromadb": "ChromaDB",
    "sentence_transformers": "sentence-transformers",
}

for module, human_name in modules.items():
    try:
        __import__(module)
        print(f" ✓ {human_name}")
    except ImportError:
        print(f" ✗ {human_name} NOT installed")

print("\nAttempting to load embedding model...")
try:
    from sentence_transformers import SentenceTransformer

    SentenceTransformer("all-MiniLM-L6-v2")
    print(" ✓ Embedding model downloaded")
except Exception as exc:
    print(f" ✗ Error loading model: {exc}")

