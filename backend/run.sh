#!/usr/bin/env bash
set -e

if [ -z "$VIRTUAL_ENV" ]; then
  if [ -d "venv" ]; then
    source venv/bin/activate
  else
    echo "Virtual environment not found. Create one first."
    exit 1
  fi
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

