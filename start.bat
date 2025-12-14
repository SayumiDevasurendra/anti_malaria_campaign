@echo off
echo ========================================
echo AMC Stain Time Optimization System
echo ========================================
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop both servers...
echo ========================================
pause > nul
