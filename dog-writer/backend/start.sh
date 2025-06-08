#!/bin/bash
cd /app/dog-writer/backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} 