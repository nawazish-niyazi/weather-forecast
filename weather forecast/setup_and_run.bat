@echo off
:: Move to the directory where the batch file is located
cd /d "%~dp0"

echo.
echo  ===========================================
echo  Starting Weather Forecast Pro...
echo  ===========================================
echo.

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python.
    pause
    exit /b
)

:: Install dependencies directly (simpler than venv for debugging)
echo [1/2] Checking dependencies (requests, pillow)...
python -m pip install requests Pillow --quiet

:: Run the app and wait
echo [2/2] Launching application...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed.
    echo Please see the error message above.
)

echo.
echo [DONE] The session has ended.
pause
