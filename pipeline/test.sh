#!/bin/bash
# Local comprehensive Python testing script
# Run this before pushing to ensure all checks pass

set -e  # Exit on error

echo "========================================="
echo "Running comprehensive Python tests"
echo "========================================="
echo ""

# Check if we're in the pipeline directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Must be run from the pipeline/ directory"
    exit 1
fi

# Check if virtual environment is active (optional but recommended)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected. Consider using 'python3 -m venv venv && source venv/bin/activate'"
    echo ""
fi

# Install test dependencies if not already installed
echo "📦 Installing test dependencies..."
pip install -q flake8 black pytest pytest-cov 2>/dev/null || true
echo ""

# Step 1: Flake8 linting
echo "🔍 Running flake8 linting..."
echo "---"
# Critical errors only (syntax errors, undefined names)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv,__pycache__,.pytest_cache

# All errors as warnings
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --exclude=venv,__pycache__,.pytest_cache
echo "✅ Flake8 passed"
echo ""

# Step 2: Black formatting check
echo "🎨 Checking code formatting with black..."
echo "---"
black --check --diff . --exclude='/(venv|__pycache__|\.pytest_cache)/'
echo "✅ Black formatting passed"
echo ""

# Step 3: Run pytest (unit tests only)
echo "🧪 Running pytest (unit tests)..."
echo "---"
pytest -v --cov=. --cov-report=term --cov-report=html --ignore=simple_test.py
echo "✅ Pytest passed"
echo ""
echo "ℹ️  Note: simple_test.py (integration tests) requires real API keys"
echo "   To run integration tests: python3 simple_test.py"
echo ""

# Step 4: Generate coverage summary
echo "📊 Test coverage summary:"
echo "   Full HTML report available at: htmlcov/index.html"
echo ""

echo "========================================="
echo "✅ All tests passed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  - Review coverage report: open pipeline/htmlcov/index.html"
echo "  - Run 'npm run test:frontend' to test frontend"
echo "  - Commit your changes with confidence!"
