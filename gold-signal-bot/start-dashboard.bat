@echo off
echo ========================================
echo Starting Gold Signal Bot Dashboard
echo ========================================
echo.

echo Starting Backend API on port 5000...
start "Backend API" cmd /k "cd backend && python api.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend on port 4200...
start "Frontend Dashboard" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo Dashboard is starting...
echo ========================================
echo.
echo Backend API: http://127.0.0.1:5000
echo Frontend:    http://localhost:4200
echo.
echo Press any key to stop all servers...
pause > nul

taskkill /FI "WindowTitle eq Backend API*" /T /F
taskkill /FI "WindowTitle eq Frontend Dashboard*" /T /F

echo.
echo All servers stopped.
pause
