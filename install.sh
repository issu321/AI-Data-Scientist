#!/bin/bash
set -e

echo "🧠 AI Data Scientist - Installer"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create directories
mkdir -p data uploads reports visualizations assets

# Initialize JSON files
for f in users.json reports.json history.json settings.json; do
    if [ ! -f "data/$f" ]; then
        echo "{}" > "data/$f"
    fi
done

echo "✅ Installation complete!"
echo ""
echo "To start the app:"
echo "  source venv/bin/activate"
echo "  streamlit run streamlit_app.py"
