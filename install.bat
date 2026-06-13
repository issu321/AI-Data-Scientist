@echo off
echo 🧠 AI Data Scientist - Installer
echo =================================

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)

if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo ⬆️ Upgrading pip...
venv\Scripts\pip install --upgrade pip

echo 📥 Installing dependencies...
venv\Scripts\pip install -r requirements.txt

echo 📁 Creating directories...
if not exist data mkdir data
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist visualizations mkdir visualizations
if not exist assets mkdir assets

echo ✅ Installation complete!
echo.
echo   Launching...(Please-Wait)
streamlit run streamlit_app.py
pause
