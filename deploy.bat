@echo off
echo === EGX 30 Stock Advisor Deployment ===
echo.

REM Check Python
python --version 2>NUL
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
pip install -r requirements_prod.txt

REM Run deployment script
echo.
echo Choose deployment target:
echo 1. Vercel (Frontend)
echo 2. Google Cloud Run (Backend)
echo 3. Both
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Deploying to Vercel...
    python setup_vercel_account.py
    cd vercel-deploy
    vercel
) else if "%choice%"=="2" (
    echo.
    echo Deploying to Google Cloud Run...
    python deploy_cloud.py
) else if "%choice%"=="3" (
    echo.
    echo Deploying to both platforms...
    echo.
    echo 1. Deploying to Vercel...
    python setup_vercel_account.py
    cd vercel-deploy
    vercel
    cd ..
    echo.
    echo 2. Deploying to Google Cloud Run...
    python deploy_cloud.py
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice
    exit /b 1
)

echo.
echo Deployment completed!
pause