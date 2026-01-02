@echo off
echo ========================================
echo Gold Signal Bot - Dashboard Setup
echo ========================================
echo.

echo [1/4] Installing Backend Dependencies...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] Installing Frontend Dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] Setup Complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Start Backend API:
echo    cd backend
echo    python api.py
echo.
echo 2. Start Frontend (in new terminal):
echo    cd frontend
echo    npm start
echo.
echo 3. Open browser to:
echo    http://localhost:4200
echo.
echo ========================================
pause
