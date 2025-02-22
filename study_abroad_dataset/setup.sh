#!/bin/bash

# Setup script for Study Abroad Q&A Dataset Generator

echo "Setting up Study Abroad Q&A Dataset Generator..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data output logs

# Create .env file template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    echo "Please update .env with your actual Gemini API key"
fi

# Make the script executable
chmod +x src/main.py

echo "Setup complete!"
echo "
Next steps:
1. Update .env with your Gemini API key
2. Run the generator:
   python src/main.py --total-conversations 1000
"
