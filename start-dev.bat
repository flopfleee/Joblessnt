@echo off

start "Backend" powershell -NoExit -Command "cd '%~dp0backend'; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload"

start "Frontend" powershell -NoExit -Command "cd '%~dp0frontend'; npm run dev"