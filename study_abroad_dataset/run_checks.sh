#!/bin/bash

# Run all quality checks and tests before data generation

echo "Running pre-generation checks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "❌ Error: Python 3.8 or higher is required (current: $python_version)"
    exit 1
fi

# Run setup verification
echo -e "\nRunning setup verification..."
python test_setup.py
if [ $? -ne 0 ]; then
    echo "❌ Setup verification failed"
    exit 1
fi

# Check if Gemini API key is properly set
echo -e "\nChecking API key configuration..."
if [ -f ".env" ]; then
    if grep -q "GEMINI_API_KEY=your_api_key_here" ".env"; then
        echo "❌ Error: GEMINI_API_KEY not configured in .env"
        exit 1
    else
        echo "✅ API key configuration check passed"
    fi
else
    echo "❌ Error: .env file not found"
    exit 1
fi

# Run the example script to verify generation works
echo -e "\nRunning basic generation test..."
python examples/basic_generation.py
if [ $? -ne 0 ]; then
    echo "❌ Basic generation test failed"
    exit 1
fi

echo -e "\n✅ All checks passed!"
echo """
You can now run the dataset generator:

To generate with default settings:
python src/main.py

To customize generation:
python src/main.py --total-conversations 10000 --batch-size 5
"""
