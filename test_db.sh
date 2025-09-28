#!/bin/bash
# Test script for database interface

echo "Testing Employee Database Interface..."
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Run the test script
echo "Running setup tests..."
python test_setup.py

echo ""
echo "To test the database interface interactively:"
echo "  python mcp/simple_db_interface.py"
