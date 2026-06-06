# 🧠 AI Data Scientist

**Developed by [issu321](https://github.com/issu321)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

A complete, production-ready AI-powered data science platform built with Streamlit. Automatically analyze, visualize, and build machine learning models from any CSV dataset.

## 🚀 Features

- **📂 Smart Upload**: Upload any CSV with automatic session management (no cache conflicts)
- **📋 Dataset Explorer**: Full profiling with data types, missing values, duplicates, memory usage
- **📈 Auto Visualizations**: Interactive Plotly charts (histograms, box plots, heatmaps, PCA, clustering)
- **🧠 AI Insights**: Real calculated insights (correlations, skewness, imbalances, anomalies)
- **🤖 AutoML Engine**: Automatic classification & regression with model leaderboard
- **📑 Report Generation**: Export HTML, JSON, and TXT reports
- **📤 Export Center**: Download datasets, charts, insights, and model results
- **👤 User System**: Registration, login, password hashing, session tracking
- **🎨 Premium UI**: Glassmorphism design with dark/light mode toggle
- **📚 History Tracking**: Complete audit trail of all dataset operations

## 🛠️ Installation

### Local Development

```bash
git clone https://github.com/issu321/AI-Data-Scientist.git
cd AI-Data-Scientist
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### One-Line Install (Linux/Mac)

```bash
curl -sSL https://raw.githubusercontent.com/issu321/AI-Data-Scientist/main/install.sh | bash
```

### Windows

```powershell
.\install.bat
```

## 📁 Architecture

```
AI-Data-Scientist/
├── streamlit_app.py      # Main application (all pages)
├── data_analyzer.py      # Data profiling, visualizations, insights
├── automl_engine.py      # ML model training & evaluation
├── utils.py              # Auth, storage, themes, session management
├── requirements.txt      # Dependencies
├── README.md             # Documentation
├── install.sh            # Linux/Mac installer
├── install.bat           # Windows installer
├── data/                 # JSON storage
│   ├── users.json
│   ├── reports.json
│   ├── history.json
│   └── settings.json
├── uploads/              # Uploaded datasets
├── reports/              # Generated reports
├── visualizations/       # Exported charts
└── assets/               # Static assets
```

## 🌐 Deployment

### Streamlit Community Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select the `AI-Data-Scientist` repository
5. Set main file path to `streamlit_app.py`
6. Click Deploy

**No additional configuration required.**

## 📊 Usage Guide

1. **Register/Login** - Create an account or sign in
2. **Upload Dataset** - Drag & drop any CSV file
3. **Explore** - View automatic data profiling
4. **Visualize** - Browse interactive charts
5. **Insights** - Read AI-generated data insights
6. **AutoML** - Select target column and train models
7. **Reports** - Export professional reports
8. **Export** - Download cleaned data and charts

## 🔒 Security

- Passwords hashed with Werkzeug (bcrypt)
- No plain text storage
- JSON-based persistence (no SQL injection risk)
- Session isolation per user

## 🐛 Critical Bug Fix

**Previous versions had a dataset caching bug where Dataset B would incorrectly use Dataset A's cached results.**

This version implements a robust `clear_all_dataset_state()` function that:
- Removes previous dataframe references
- Clears analysis cache
- Clears visualization cache
- Clears AutoML results
- Clears feature importance
- Clears insight cache

Every upload is completely independent.

## 📝 Developer

- **GitHub**: [@issu321](https://github.com/issu321)
- **Repository**: [AI-Data-Scientist](https://github.com/issu321/AI-Data-Scientist)

## 📄 License

MIT License
