@echo off
echo Starting Mini Blog Portal...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt --only-binary=all
    if errorlevel 1 (
        echo.
        echo Warning: Some dependencies failed to install.
        echo Trying alternative installation method...
        pip install Flask Werkzeug Jinja2 psycopg2-binary --only-binary=all
        if errorlevel 1 (
            echo Error: Failed to install dependencies
            echo Please install manually: pip install -r requirements.txt
            pause
            exit /b 1
        )
    )
    echo.
)

REM Check if PostgreSQL is running
echo Checking database connection...
python -c "import psycopg2; print('Database connection test passed!')" 2>nul
if errorlevel 1 (
    echo.
    echo Warning: Database connection test failed.
    echo Please make sure PostgreSQL is running and accessible.
    echo You can still try to start the application.
    echo.
)

echo.
echo Starting Flask application...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
