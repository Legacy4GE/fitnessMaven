#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/FitnessMaven"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the FastAPI app with hot reload
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
