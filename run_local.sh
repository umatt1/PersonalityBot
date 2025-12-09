#!/bin/bash

# Local development script for PersonalityBot

echo "==================================="
echo "PersonalityBot Local Development"
echo "==================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create memory data directory if it doesn't exist
mkdir -p memory_data

# Run the bot
echo "Starting PersonalityBot..."
echo "Press Ctrl+C to stop"
echo "==================================="
python main.py
