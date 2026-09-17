#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.11-3.13 is required. Install Python, then run this script again."
  exit 1
fi
"$PYTHON" -c 'import sys; assert (3,11) <= sys.version_info[:2] <= (3,13), "Use Python 3.11, 3.12 or 3.13."'
if [ ! -d .venv ]; then "$PYTHON" -m venv .venv; fi
if ! .venv/bin/python -c 'import streamlit, mysql.connector, pandas, dotenv' >/dev/null 2>&1; then
  .venv/bin/python -m pip install -r requirements.txt
fi
if [ ! -f .env ]; then .venv/bin/python scripts/setup.py; fi
.venv/bin/python scripts/doctor.py
exec .venv/bin/python -m streamlit run app.py
