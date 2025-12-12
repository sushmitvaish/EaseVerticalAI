#!/bin/bash
# Setup script for DealerFlow Lead Generator

set -e

echo "===================================="
echo "DealerFlow Lead Generator Setup"
echo "===================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo ""
    echo ".env file already exists."
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/axlewave_context
mkdir -p data/results_cache
mkdir -p data/prompt_logs

# Initialize company context
echo ""
echo "Initializing company context..."
python -c "from utils.document_processor import doc_processor; doc_processor.save_context()"

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Install Ollama: brew install ollama (macOS) or visit https://ollama.com"
echo "3. Pull a model: ollama pull llama3.1:8b"
echo "4. Run the app: streamlit run app.py"
echo ""
echo "To activate the virtual environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
