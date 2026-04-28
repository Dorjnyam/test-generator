FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (exclude dev dependencies)
COPY requirements.prod.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import uvicorn; print(f'✓ uvicorn {uvicorn.__version__} installed')" \
    && pip cache purge \
    && find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete 2>/dev/null || true

# Copy application code
COPY . .

# Create directories
RUN mkdir -p uploads chroma_db

# Remove build tools and clean up to reduce image size
# Verify uvicorn still available before cleanup
RUN python -c "import uvicorn; print(f'✓ uvicorn {uvicorn.__version__} verified before cleanup')" \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip \
    && python -c "import uvicorn; print(f'✓ uvicorn {uvicorn.__version__} verified after cleanup')" \
    && find /usr/local/lib/python3.11 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

EXPOSE 8080

# Use PORT env var from Fly.io, default to 8080
# Verify uvicorn is available and then start
CMD ["/bin/sh", "-c", "python -c 'import uvicorn; print(f\"Starting with uvicorn {uvicorn.__version__}\")' && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
