import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
VISUALIZATIONS_DIR = os.path.join(BASE_DIR, "visualizations")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def ensure_dirs():
    for d in [DATA_DIR, UPLOADS_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
        os.makedirs(d, exist_ok=True)

def init_json_files():
    for f, default in [(USERS_FILE, {}), (REPORTS_FILE, {}), (HISTORY_FILE, {}), (SETTINGS_FILE, {})]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as file:
                json.dump(default, file, indent=2)

def load_json(filepath: str) -> Any:
    if not os.path.exists(filepath):
        return {} if any(x in filepath for x in ['settings','users','reports','history']) else []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath: str, data: Any):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

# ==================== USER SYSTEM ====================
def register_user(username: str, password: str, email: str) -> tuple[bool, str]:
    users = load_json(USERS_FILE)
    if not username or not password:
        return False, "Username and password are required"
    if username in users:
        return False, "Username already exists"
    users[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "email": email,
        "registered_at": datetime.now().isoformat(),
        "datasets_uploaded": 0,
        "reports_generated": 0,
        "analyses_count": 0,
        "last_login": None
    }
    save_json(USERS_FILE, users)
    return True, "Registration successful"

def authenticate_user(username: str, password: str) -> bool:
    users = load_json(USERS_FILE)
    if username not in users:
        return False
    if check_password_hash(users[username]["password_hash"], password):
        users[username]["last_login"] = datetime.now().isoformat()
        save_json(USERS_FILE, users)
        return True
    return False

def get_all_users() -> Dict:
    return load_json(USERS_FILE)

def get_user(username: str) -> Optional[Dict]:
    users = load_json(USERS_FILE)
    return users.get(username)

def update_user_stat(username: str, field: str, increment: int = 1):
    users = load_json(USERS_FILE)
    if username in users and field in users[username]:
        users[username][field] = users[username].get(field, 0) + increment
        save_json(USERS_FILE, users)

# ==================== SETTINGS ====================
def get_settings() -> Dict:
    return load_json(SETTINGS_FILE)

def save_user_settings(username: str, settings: Dict):
    all_settings = load_json(SETTINGS_FILE)
    all_settings[username] = settings
    save_json(SETTINGS_FILE, all_settings)

def get_user_settings(username: str) -> Dict:
    all_settings = load_json(SETTINGS_FILE)
    return all_settings.get(username, {"theme": "dark", "notifications": True})

# ==================== HISTORY ====================
def add_history(username: str, dataset_name: str, action: str, details: str = ""):
    history = load_json(HISTORY_FILE)
    if username not in history:
        history[username] = []
    history[username].append({
        "id": str(uuid.uuid4()),
        "dataset_name": dataset_name,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    save_json(HISTORY_FILE, history)

def get_user_history(username: str) -> List[Dict]:
    history = load_json(HISTORY_FILE)
    return history.get(username, [])

# ==================== REPORTS ====================
def save_report(username: str, report_type: str, content: str, metadata: Dict = None) -> str:
    reports = load_json(REPORTS_FILE)
    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "username": username,
        "type": report_type,
        "content": content,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat()
    }
    save_json(REPORTS_FILE, reports)
    update_user_stat(username, "reports_generated")
    return report_id

def get_user_reports(username: str) -> Dict[str, Dict]:
    reports = load_json(REPORTS_FILE)
    return {k: v for k, v in reports.items() if v.get("username") == username}

# ==================== THEME CSS ====================
def get_theme_css(theme: str = "dark") -> str:
    if theme == "dark":
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            background-attachment: fixed;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 24px;
            margin: 12px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255,255,255,0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(101, 78, 163, 0.2) 0%, rgba(234, 76, 137, 0.2) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #e0e0ff;
            text-shadow: 0 0 20px rgba(101, 78, 163, 0.5);
        }
        .metric-label {
            font-size: 0.85rem;
            color: #a0a0c0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        .nav-item {
            padding: 10px 14px;
            border-radius: 12px;
            margin: 2px 0;
            color: #c0c0d0;
            transition: all 0.2s;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            box-shadow: 0 0 20px rgba(101, 78, 163, 0.3);
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: #e0e0ff;
        }
        .stSelectbox>div>div>div {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
        }
        h1, h2, h3 { color: #e0e0ff; }
        p, li, span { color: #c0c0d0; }
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1rem;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #a0a0c0;
            text-align: center;
            max-width: 600px;
            margin: 0 auto 2rem;
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .feature-title { font-size: 1.1rem; font-weight: 600; color: #e0e0ff; margin-bottom: 0.3rem; }
        .feature-desc { font-size: 0.85rem; color: #a0a0c0; }
        .stDataFrame { border-radius: 12px; overflow: hidden; }
        .report-card {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #667eea;
            padding: 16px;
            border-radius: 0 12px 12px 0;
            margin: 8px 0;
        }
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            margin: 24px 0;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 2px;
        }
        .badge-success { background: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid rgba(46, 204, 113, 0.3); }
        .badge-warning { background: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid rgba(241, 196, 15, 0.3); }
        .badge-info { background: rgba(52, 152, 219, 0.2); color: #3498db; border: 1px solid rgba(52, 152, 219, 0.3); }
        .badge-danger { background: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid rgba(231, 76, 60, 0.3); }
        </style>
        """
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            background-attachment: fixed;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 24px;
            margin: 12px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), inset 0 0 0 1px rgba(255,255,255,0.5);
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12), inset 0 0 0 1px rgba(255,255,255,0.6);
            border-color: rgba(200, 200, 220, 0.6);
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(101, 78, 163, 0.1) 0%, rgba(234, 76, 137, 0.1) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(200, 200, 220, 0.4);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #302b63;
            text-shadow: 0 0 20px rgba(101, 78, 163, 0.2);
        }
        .metric-label {
            font-size: 0.85rem;
            color: #555577;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        .nav-item {
            padding: 10px 14px;
            border-radius: 12px;
            margin: 2px 0;
            color: #555577;
            transition: all 0.2s;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
        }
        .nav-item:hover, .nav-item.active {
            background: rgba(101, 78, 163, 0.1);
            color: #302b63;
            box-shadow: 0 0 20px rgba(101, 78, 163, 0.1);
        }
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
            width: 100%;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(200, 200, 220, 0.5);
            border-radius: 12px;
            color: #302b63;
        }
        .stSelectbox>div>div>div {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(200, 200, 220, 0.5);
            border-radius: 12px;
        }
        h1, h2, h3 { color: #302b63; }
        p, li, span { color: #444466; }
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1rem;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #555577;
            text-align: center;
            max-width: 600px;
            margin: 0 auto 2rem;
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .feature-title { font-size: 1.1rem; font-weight: 600; color: #302b63; margin-bottom: 0.3rem; }
        .feature-desc { font-size: 0.85rem; color: #555577; }
        .stDataFrame { border-radius: 12px; overflow: hidden; }
        .report-card {
            background: rgba(255, 255, 255, 0.5);
            border-left: 4px solid #667eea;
            padding: 16px;
            border-radius: 0 12px 12px 0;
            margin: 8px 0;
        }
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
            margin: 24px 0;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 2px;
        }
        .badge-success { background: rgba(46, 204, 113, 0.15); color: #27ae60; border: 1px solid rgba(46, 204, 113, 0.2); }
        .badge-warning { background: rgba(241, 196, 15, 0.15); color: #d4ac0d; border: 1px solid rgba(241, 196, 15, 0.2); }
        .badge-info { background: rgba(52, 152, 219, 0.15); color: #2980b9; border: 1px solid rgba(52, 152, 219, 0.2); }
        .badge-danger { background: rgba(231, 76, 60, 0.15); color: #c0392b; border: 1px solid rgba(231, 76, 60, 0.2); }
        </style>
        """

# ==================== SESSION MANAGER (CRITICAL BUG FIX) ====================
def clear_all_dataset_state():
    """Completely clear all dataset-related session state when new file uploaded."""
    keys = [
        'df', 'df_name', 'df_shape', 'analysis_results', 'viz_results',
        'insights', 'automl_results', 'feature_importance', 'report_data',
        'current_dataset_id', 'explorer_state', 'cleaned_df', 'target_column',
        'uploaded_file_name', 'last_upload_hash'
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

def set_dataset_session(df, name):
    clear_all_dataset_state()
    st.session_state.df = df
    st.session_state.df_name = name
    st.session_state.current_dataset_id = f"{name}_{datetime.now().timestamp()}"
    st.session_state.df_shape = df.shape
    st.session_state.uploaded_file_name = name

# ==================== PASSWORD VALIDATION ====================
def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain a digit"
    return True, "Password valid"
