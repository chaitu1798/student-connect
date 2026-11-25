@echo off
echo ========================================================
echo Starting Backend (FastAPI + Uvicorn)
echo ========================================================
call .\venv\Scripts\activate
uvicorn app.main:app --app-dir backend --reload --port 8000
