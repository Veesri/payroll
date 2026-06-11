@echo off
echo Starting HRMS Backend (Flask)...
start cmd /k "cd backend && venv\Scripts\activate.bat && python app.py"

echo Starting HRMS Frontend (Vite)...
start cmd /k "cd frontend && npm run dev"

echo Both servers are starting up!
pause
