#!/bin/bash

echo "Starting AI Learning Helper Backend..."
echo "======================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your Azure credentials:"
    echo "  AZURE_API_KEY=your_api_key"
    echo "  AZURE_MODEL_ENDPOINT=your_endpoint"
    exit 1
fi

# Start the Flask server
echo ""
echo "Starting Flask server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
cd backend
python app.py
