@echo off
echo ============================================
echo   Starting Activity Tracker AI - Full Stack
echo ============================================
echo.

echo [1/3] Starting Python Backend...
start cmd /k "cd backend && python main.py"

timeout /t 5 /nobreak > nul

echo [2/3] Starting React Frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo   Application Starting...
echo ============================================
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:3000
echo   Electron app will auto-launch
echo ============================================
echo.
echo   Press any key to exit this window...
echo   (Keep backend and frontend windows open)
pause > nul
