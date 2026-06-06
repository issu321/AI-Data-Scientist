import base64
import json
import os
from datetime import datetime
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from automl_engine import AutoMLEngine
from data_analyzer import DataAnalyzer
from utils import (add_history, authenticate_user, clear_all_dataset_state,
                   ensure_dirs, get_all_users, get_theme_css, get_user,
                   get_user_history, get_user_reports, get_user_settings,
                   init_json_files, register_user, save_report,
                   save_user_settings, set_dataset_session, update_user_stat,
                   validate_password)

# ==================== INITIALIZATION ====================
st.set_page_config(page_title="AI Data Scientist", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
ensure_dirs()
init_json_files()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

# Theme
theme = st.session_state.theme
if st.session_state.user:
    user_settings = get_user_settings(st.session_state.user)
    theme = user_settings.get("theme", "dark")
    st.session_state.theme = theme

st.markdown(get_theme_css(theme), unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================
with st.sidebar:
    st.markdown('<div style="text-align:center; margin-bottom:20px;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#667eea; margin:0;">🧠 AI Data Scientist</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#a0a0c0; font-size:0.75rem;">Developed by issu321</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.user:
        st.markdown(f'<p style="text-align:center; color:#e0e0ff; font-size:0.9rem;">👤 {st.session_state.user}</p>', unsafe_allow_html=True)
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        pages = [
            ("🏠", "Home"), ("📊", "Dashboard"), ("📂", "Upload Dataset"),
            ("📋", "Dataset Explorer"), ("📈", "Visualizations"), ("🧠", "AI Insights"),
            ("🤖", "AutoML"), ("📑", "Reports"), ("📚", "Dataset History"),
            ("👤", "User Profile"), ("👥", "Users Directory"), ("📤", "Export Center"),
            ("⚙", "Settings"), ("📞", "Contact"), ("🚪", "Logout")
        ]

        for icon, p in pages:
            active = "active" if st.session_state.page == p else ""
            st.markdown(f'<div class="nav-item {active}">{icon} {p}</div>', unsafe_allow_html=True)
            if st.button(f"{p}", key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p
                st.rerun()
    else:
        st.session_state.page = "Login"

# ==================== HELPER FUNCTIONS ====================
def require_auth():
    if not st.session_state.user:
        st.session_state.page = "Login"
        st.rerun()

def require_dataset():
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("📂 Please upload a dataset first.")
        return False
    return True

def get_analyzer():
    return DataAnalyzer(st.session_state.df, st.session_state.get('df_name', 'Dataset'))

def nav_to(page):
    st.session_state.page = page
    st.rerun()

# ==================== LOGIN PAGE ====================
if st.session_state.page == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="hero-title">🧠 AI Data Scientist</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Your intelligent data analysis companion</p>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                if submitted:
                    if authenticate_user(username, password):
                        st.session_state.user = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Username")
                new_email = st.text_input("Email")
                new_pass = st.text_input("Password", type="password")
                new_pass2 = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register", use_container_width=True)
                if submitted:
                    valid, msg = validate_password(new_pass)
                    if not valid:
                        st.error(msg)
                    elif new_pass != new_pass2:
                        st.error("Passwords do not match")
                    else:
                        success, msg = register_user(new_user, new_pass, new_email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

# ==================== HOME PAGE ====================
elif st.session_state.page == "Home":
    require_auth()
    st.markdown('<h1 class="hero-title">Welcome to AI Data Scientist</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Upload any CSV dataset and let AI automatically analyze, visualize, and build machine learning models for you.</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    features = [
        ("📊", "Auto Analysis", "Automatic data profiling, quality scoring, and statistical summaries"),
        ("📈", "Smart Visualizations", "Interactive Plotly charts generated based on your data types"),
        ("🤖", "AutoML Engine", "Automatic classification & regression with model leaderboard"),
        ("🧠", "AI Insights", "Real data-driven insights from actual calculations"),
        ("📑", "Reports", "Export professional HTML, JSON, and TXT reports"),
        ("⚙", "Full Control", "Dark/light themes, user management, and session tracking")
    ]
    for i, (icon, title, desc) in enumerate(features):
        with [c1, c2, c3][i % 3]:
            st.markdown(f'<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown(f'<div class="feature-icon">{icon}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="feature-title">{title}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="feature-desc">{desc}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center;">Quick Start</h3>', unsafe_allow_html=True)
    steps = ["1. Upload your CSV", "2. Explore automatically generated analytics", "3. Run AutoML", "4. Export reports"]
    for step in steps:
        st.markdown(f'<div class="glass-card" style="padding:12px; margin:6px 0;">{step}</div>', unsafe_allow_html=True)

# ==================== DASHBOARD ====================
elif st.session_state.page == "Dashboard":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📊 Dashboard</h1>', unsafe_allow_html=True)

    user = get_user(st.session_state.user)
    all_users = get_all_users()
    total_datasets = sum(u.get("datasets_uploaded", 0) for u in all_users.values())
    total_reports = sum(u.get("reports_generated", 0) for u in all_users.values())
    total_analyses = sum(u.get("analyses_count", 0) for u in all_users.values())

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (user.get("datasets_uploaded", 0), "Datasets Uploaded"),
        (user.get("reports_generated", 0), "Reports Generated"),
        (user.get("analyses_count", 0), "Analyses Completed"),
        (len(all_users), "Total Users")
    ]
    for col, (val, label) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    if require_dataset():
        analyzer = get_analyzer()
        quality = analyzer.data_quality_score()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.df.shape[0]:,}</div><div class="metric-label">Rows</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.df.shape[1]}</div><div class="metric-label">Columns</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{quality["overall"]}%</div><div class="metric-label">Quality Score</div></div>', unsafe_allow_html=True)
        with c4:
            missing = quality["missing_cells"]
            st.markdown(f'<div class="metric-card"><div class="metric-value">{missing:,}</div><div class="metric-label">Missing Cells</div></div>', unsafe_allow_html=True)

        # Recent activity chart
        history = get_user_history(st.session_state.user)
        if history:
            hist_df = pd.DataFrame(history[-10:])
            hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'])
            fig = px.scatter(hist_df, x='timestamp', y='action', color='dataset_name',
                           title="Recent Activity", height=300)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff' if theme=='dark' else '#302b63')
            st.plotly_chart(fig, use_container_width=True)

# ==================== UPLOAD DATASET ====================
elif st.session_state.page == "Upload Dataset":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📂 Upload Dataset</h1>', unsafe_allow_html=True)

    def on_upload_change():
        clear_all_dataset_state()

    uploaded_file = st.file_uploader("Upload CSV File", type=['csv'], on_change=on_upload_change, key="csv_uploader")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.error("Uploaded file is empty")
            else:
                set_dataset_session(df, uploaded_file.name)
                update_user_stat(st.session_state.user, "datasets_uploaded")
                add_history(st.session_state.user, uploaded_file.name, "Upload", f"{df.shape[0]} rows, {df.shape[1]} columns")
                st.success(f"✅ Loaded '{uploaded_file.name}': {df.shape[0]:,} rows × {df.shape[1]} columns")

                # Auto-run analysis
                with st.spinner("Running automated analysis..."):
                    analyzer = get_analyzer()
                    st.session_state.analysis_results = analyzer.get_profile()
                    st.session_state.viz_results = analyzer.generate_visualizations(theme)
                    st.session_state.insights = analyzer.generate_insights()
                    update_user_stat(st.session_state.user, "analyses_count")

                st.info("Analysis complete! Navigate to Dataset Explorer, Visualizations, or AI Insights.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        if 'df' in st.session_state and st.session_state.df is not None:
            st.info(f"Current dataset: **{st.session_state.df_name}** ({st.session_state.df.shape[0]:,} rows)")
            if st.button("🗑️ Clear Current Dataset", use_container_width=True):
                clear_all_dataset_state()
                st.rerun()

# ==================== DATASET EXPLORER ====================
elif st.session_state.page == "Dataset Explorer":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📋 Dataset Explorer</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    analyzer = get_analyzer()
    profile = analyzer.get_profile()
    quality = analyzer.data_quality_score()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{profile["shape"][0]:,}</div><div class="metric-label">Rows</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{profile["shape"][1]}</div><div class="metric-label">Columns</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{quality["overall"]}%</div><div class="metric-label">Quality Score</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{profile["memory_usage_mb"]} MB</div><div class="metric-label">Memory Usage</div></div>', unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "🔍 Columns", "❌ Missing & Duplicates", "👁️ Preview"])

    with tab1:
        st.subheader("Data Types")
        dtype_df = pd.DataFrame({
            'Column': list(profile['dtypes'].keys()),
            'Type': list(profile['dtypes'].values()),
            'Unique': [profile['unique_values'][c] for c in profile['dtypes'].keys()],
            'Missing': [profile['missing'][c] for c in profile['dtypes'].keys()],
            'Missing %': [profile['missing_pct'][c] for c in profile['dtypes'].keys()]
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with tab2:
        search = st.text_input("Search columns")
        cols = [c for c in st.session_state.df.columns if search.lower() in c.lower()] if search else list(st.session_state.df.columns)
        for col in cols:
            with st.expander(f"{col} ({profile['dtypes'][col]})"):
                if col in analyzer.numeric_cols:
                    st.write(st.session_state.df[col].describe())
                else:
                    st.write(st.session_state.df[col].value_counts().head(10))

    with tab3:
        st.subheader("Missing Values")
        missing_df = pd.DataFrame({
            'Column': list(profile['missing'].keys()),
            'Missing Count': list(profile['missing'].values()),
            'Missing %': list(profile['missing_pct'].values())
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing %', ascending=False)
        if not missing_df.empty:
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        else:
            st.success("No missing values found!")

        st.subheader("Duplicates")
        st.write(f"Duplicate rows: **{quality['duplicate_rows']:,}** ({quality['duplicate_rows']/len(st.session_state.df)*100:.2f}%)")

    with tab4:
        st.dataframe(st.session_state.df.head(100), use_container_width=True)

# ==================== VISUALIZATIONS ====================
elif st.session_state.page == "Visualizations":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📈 Visualizations</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    if 'viz_results' not in st.session_state or not st.session_state.viz_results:
        with st.spinner("Generating visualizations..."):
            analyzer = get_analyzer()
            st.session_state.viz_results = analyzer.generate_visualizations(theme)

    viz = st.session_state.viz_results
    tabs = st.tabs(["📊 Overview", "🔢 Numeric", "📁 Categorical", "🔗 Advanced"])

    with tabs[0]:
        if "correlation" in viz:
            st.plotly_chart(viz["correlation"], use_container_width=True, key="corr_viz")
        if "missing_heatmap" in viz:
            st.plotly_chart(viz["missing_heatmap"], use_container_width=True, key="miss_viz")

    with tabs[1]:
        numeric_viz = [k for k in viz.keys() if k.startswith("dist_")]
        if numeric_viz:
            for k in numeric_viz:
                st.plotly_chart(viz[k], use_container_width=True, key=f"num_{k}")
        else:
            st.info("No numeric columns found")

    with tabs[2]:
        cat_viz = [k for k in viz.keys() if k.startswith("cat_")]
        if cat_viz:
            for k in cat_viz:
                st.plotly_chart(viz[k], use_container_width=True, key=f"cat_{k}")
        else:
            st.info("No categorical columns found")

    with tabs[3]:
        if "pca" in viz:
            st.plotly_chart(viz["pca"], use_container_width=True, key="pca_viz")
        if "clusters" in viz:
            st.plotly_chart(viz["clusters"], use_container_width=True, key="clust_viz")
        if "pairplot" in viz:
            st.plotly_chart(viz["pairplot"], use_container_width=True, key="pair_viz")

# ==================== AI INSIGHTS ====================
elif st.session_state.page == "AI Insights":
    require_auth()
    st.markdown('<h1 style="text-align:center;">🧠 AI Insights</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    if 'insights' not in st.session_state or not st.session_state.insights:
        with st.spinner("Generating insights..."):
            analyzer = get_analyzer()
            st.session_state.insights = analyzer.generate_insights()

    insights = st.session_state.insights
    for ins in insights:
        badge_class = f"badge-{ins['type']}"
        st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<span class="badge {badge_class}">{ins["type"].upper()}</span> <strong style="font-size:1.1rem;">{ins["title"]}</strong>', unsafe_allow_html=True)
        st.markdown(f'<p style="margin-top:8px;">{ins["content"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== AUTOML ====================
elif st.session_state.page == "AutoML":
    require_auth()
    st.markdown('<h1 style="text-align:center;">🤖 AutoML Engine</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    df = st.session_state.df
    engine = AutoMLEngine(df)
    suggestions = engine.suggest_targets()

    col1, col2 = st.columns([2, 1])
    with col1:
        # Safe index selection
        default_index = 0
        if suggestions and len(suggestions) > 0:
            try:
                default_index = list(df.columns).index(suggestions[0])
            except ValueError:
                default_index = 0
        target = st.selectbox("Select Target Column", df.columns, index=default_index)
    with col2:
        problem_type = engine.detect_problem_type(target)
        st.markdown(f'<div class="metric-card" style="margin-top:24px;"><div class="metric-value" style="font-size:1.2rem;">{problem_type.replace("_", " ").title()}</div><div class="metric-label">Detected Problem</div></div>', unsafe_allow_html=True)

    if st.button("🚀 Train Models", use_container_width=True):
        with st.spinner("Training models... This may take a moment"):
            try:
                results = engine.run(target)
                st.session_state.automl_results = results
                st.session_state.target_column = target
                add_history(st.session_state.user, st.session_state.df_name, "AutoML", f"Target: {target}, Type: {problem_type}")
            except Exception as e:
                st.error(f"AutoML training failed: {str(e)}")
                st.session_state.automl_results = {"error": str(e)}

    if 'automl_results' in st.session_state and st.session_state.automl_results:
        results = st.session_state.automl_results
        if "error" in results:
            st.error(f"⚠️ {results['error']}")
            st.info("Tips: Try a different target column, ensure the dataset has at least 5 rows with valid numeric features, or check that your target column has enough variety.")
        else:
            st.subheader("🏆 Model Leaderboard")
            leaderboard = results.get("leaderboard", [])
            if leaderboard:
                lb_df = pd.DataFrame([r for r in leaderboard if r.get("status") == "success"])
                if not lb_df.empty:
                    st.dataframe(lb_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("All models failed to train. The dataset may be too small or have incompatible features for the selected target.")

            st.subheader("⭐ Best Model")
            best = results.get('best_model', None)
            if best:
                st.success(f"**{best}** selected as best performer")
            else:
                st.warning("No best model could be determined.")

            if results.get("feature_importance"):
                st.subheader("🔥 Feature Importance")
                fi = results["feature_importance"]
                fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance"]).head(15)
                fig = px.bar(fi_df, x="Importance", y="Feature", orientation='h',
                           title="Top Features", color_discrete_sequence=["#667eea"], height=400)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff' if theme=='dark' else '#302b63')
                st.plotly_chart(fig, use_container_width=True, key="fi_viz")

# ==================== REPORTS ====================
elif st.session_state.page == "Reports":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📑 Reports</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    analyzer = get_analyzer()
    insights = st.session_state.get('insights', analyzer.generate_insights())
    automl = st.session_state.get('automl_results', None)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📄 Generate HTML Report", use_container_width=True):
            html = analyzer.generate_html_report(insights, automl)
            report_id = save_report(st.session_state.user, "html", html, {"dataset": st.session_state.df_name})
            st.success(f"HTML Report saved! ID: {report_id[:8]}")
            st.download_button("Download HTML", html, file_name=f"report_{st.session_state.df_name}.html", mime="text/html", use_container_width=True)
    with c2:
        if st.button("📄 Generate JSON Report", use_container_width=True):
            report_data = {
                "dataset": st.session_state.df_name,
                "profile": analyzer.get_profile(),
                "quality": analyzer.data_quality_score(),
                "insights": insights,
                "automl": automl
            }
            json_str = json.dumps(report_data, indent=2, default=str)
            report_id = save_report(st.session_state.user, "json", json_str, {"dataset": st.session_state.df_name})
            st.success(f"JSON Report saved! ID: {report_id[:8]}")
            st.download_button("Download JSON", json_str, file_name=f"report_{st.session_state.df_name}.json", mime="application/json", use_container_width=True)
    with c3:
        if st.button("📄 Generate TXT Report", use_container_width=True):
            txt = analyzer.generate_txt_report(insights)
            report_id = save_report(st.session_state.user, "txt", txt, {"dataset": st.session_state.df_name})
            st.success(f"TXT Report saved! ID: {report_id[:8]}")
            st.download_button("Download TXT", txt, file_name=f"report_{st.session_state.df_name}.txt", mime="text/plain", use_container_width=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.subheader("📚 Your Reports")
    reports = get_user_reports(st.session_state.user)
    if reports:
        for rid, r in list(reports.items())[-10:]:
            with st.expander(f"{r['type'].upper()} Report - {r['created_at'][:10]} ({r['metadata'].get('dataset', 'N/A')})"):
                st.write(f"Type: {r['type']}")
                st.write(f"Created: {r['created_at']}")
                if r['type'] == 'html':
                    st.markdown(r['content'][:500] + "...", unsafe_allow_html=True)
                elif r['type'] == 'txt':
                    st.text(r['content'][:500] + "...")
                else:
                    st.code(r['content'][:500] + "...")
    else:
        st.info("No reports generated yet")

# ==================== DATASET HISTORY ====================
elif st.session_state.page == "Dataset History":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📚 Dataset History</h1>', unsafe_allow_html=True)

    history = get_user_history(st.session_state.user)
    if history:
        hist_df = pd.DataFrame(history[::-1])
        st.dataframe(hist_df[['timestamp', 'dataset_name', 'action', 'details']], use_container_width=True, hide_index=True)
    else:
        st.info("No history yet. Upload a dataset to get started!")

# ==================== USER PROFILE ====================
elif st.session_state.page == "User Profile":
    require_auth()
    st.markdown('<h1 style="text-align:center;">👤 User Profile</h1>', unsafe_allow_html=True)

    user = get_user(st.session_state.user)
    if user:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:4rem;">👤</div>', unsafe_allow_html=True)
            st.markdown(f'<h3>{user["username"]}</h3>', unsafe_allow_html=True)
            st.markdown(f'<p>{user["email"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write(f"**Registered:** {user['registered_at'][:10]}")
            st.write(f"**Last Login:** {user['last_login'][:10] if user['last_login'] else 'Never'}")
            st.write(f"**Datasets Uploaded:** {user.get('datasets_uploaded', 0)}")
            st.write(f"**Reports Generated:** {user.get('reports_generated', 0)}")
            st.write(f"**Analyses Completed:** {user.get('analyses_count', 0)}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== USERS DIRECTORY ====================
elif st.session_state.page == "Users Directory":
    require_auth()
    st.markdown('<h1 style="text-align:center;">👥 Users Directory</h1>', unsafe_allow_html=True)

    users = get_all_users()
    if users:
        user_data = []
        for u, data in users.items():
            user_data.append({
                "Username": u,
                "Email": data.get("email", ""),
                "Registered": data.get("registered_at", "")[:10],
                "Datasets": data.get("datasets_uploaded", 0),
                "Reports": data.get("reports_generated", 0),
                "Analyses": data.get("analyses_count", 0)
            })
        st.dataframe(pd.DataFrame(user_data), use_container_width=True, hide_index=True)
    else:
        st.info("No users registered yet")

# ==================== EXPORT CENTER ====================
elif st.session_state.page == "Export Center":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📤 Export Center</h1>', unsafe_allow_html=True)

    if not require_dataset():
        st.stop()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Dataset")
        csv = st.session_state.df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Original CSV", csv, file_name=f"original_{st.session_state.df_name}", mime="text/csv", use_container_width=True)

        analyzer = get_analyzer()
        cleaned = analyzer.export_cleaned_data()
        csv_clean = cleaned.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned CSV", csv_clean, file_name=f"cleaned_{st.session_state.df_name}", mime="text/csv", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Visualizations")
        if 'viz_results' in st.session_state and st.session_state.viz_results:
            for name, fig in st.session_state.viz_results.items():
                img_bytes = fig.to_image(format="png", scale=2)
                st.download_button(f"Download {name}", img_bytes, file_name=f"{name}.png", mime="image/png", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧠 Insights & Models")
        if 'insights' in st.session_state and st.session_state.insights:
            insights_json = json.dumps(st.session_state.insights, indent=2)
            st.download_button("Download Insights JSON", insights_json, file_name="insights.json", mime="application/json", use_container_width=True)
        if 'automl_results' in st.session_state and st.session_state.automl_results:
            automl_json = json.dumps(st.session_state.automl_results, indent=2, default=str)
            st.download_button("Download AutoML Results", automl_json, file_name="automl_results.json", mime="application/json", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== SETTINGS ====================
elif st.session_state.page == "Settings":
    require_auth()
    st.markdown('<h1 style="text-align:center;">⚙ Settings</h1>', unsafe_allow_html=True)

    settings = get_user_settings(st.session_state.user)

    with st.form("settings_form"):
        st.subheader("Appearance")
        new_theme = st.radio("Theme", ["dark", "light"], index=0 if settings.get("theme", "dark") == "dark" else 1, horizontal=True)
        st.subheader("Notifications")
        notifications = st.toggle("Enable notifications", value=settings.get("notifications", True))

        submitted = st.form_submit_button("Save Settings", use_container_width=True)
        if submitted:
            save_user_settings(st.session_state.user, {"theme": new_theme, "notifications": notifications})
            st.session_state.theme = new_theme
            st.success("Settings saved!")
            st.rerun()

# ==================== CONTACT ====================
elif st.session_state.page == "Contact":
    require_auth()
    st.markdown('<h1 style="text-align:center;">📞 Contact</h1>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("""
    <h3>Developer Information</h3>
    <p><strong>Developer:</strong> issu321</p>
    <p><strong>GitHub:</strong> <a href="https://github.com/issu321" target="_blank">https://github.com/issu321</a></p>
    <p><strong>Repository:</strong> <a href="https://github.com/issu321/AI-Data-Scientist" target="_blank">https://github.com/issu321/AI-Data-Scientist</a></p>
    <p><strong>Project:</strong> AI Data Scientist</p>
    <p><strong>Deployment:</strong> Streamlit Community Cloud</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("contact_form"):
        st.text_input("Subject")
        st.text_area("Message")
        if st.form_submit_button("Send Message", use_container_width=True):
            st.success("Message sent! (Demo mode - messages not stored)")

# ==================== LOGOUT ====================
elif st.session_state.page == "Logout":
    st.session_state.user = None
    st.session_state.page = "Login"
    clear_all_dataset_state()
    st.success("Logged out successfully")
    st.rerun()
