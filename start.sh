#!/bin/bash

echo "Starting Mini Blog Portal..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt --only-binary=all
    if [ $? -ne 0 ]; then
        echo
        echo "Warning: Some dependencies failed to install."
        echo "Trying alternative installation method..."
        pip3 install Flask Werkzeug Jinja2 psycopg2-binary --only-binary=all
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install dependencies"
            echo "Please install manually: pip3 install -r requirements.txt"
            exit 1
        fi
    fi
    echo
fi

# Check if PostgreSQL is running
echo "Checking database connection..."
python3 -c "import psycopg2; print('Database connection test passed!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo
    echo "Warning: Database connection test failed."
    echo "Please make sure PostgreSQL is running and accessible."
    echo "You can still try to start the application."
    echo
fi

echo
echo "Starting Flask application..."
echo "Open your browser and go to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo

python3 app.py
