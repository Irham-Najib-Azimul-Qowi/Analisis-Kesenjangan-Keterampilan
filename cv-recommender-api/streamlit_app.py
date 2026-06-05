# -*- coding: utf-8 -*-
"""
Dashboard Evaluasi CV & Rekomendasi Lowongan Kerja - Custom Design System
Project: CV Recommender & Skill Assessment API Interface
Semester 4 Politeknik Negeri Madiun
"""

import os
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 🎨 1. CUSTOM DESIGN SYSTEM STYLING
# ==============================================================================
st.set_page_config(
    page_title="CV Intelligence & Job Matcher",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected CSS implementing a premium, high-contrast dashboard UI/UX:
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Global Background and Typography */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        background-color: #f8fafc !important; /* Elegant off-white background */
        color: #0f172a !important; /* Deep slate text color */
    }
    
    /* Clean Top Header Bar */
    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    
    /* Dark Premium Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] h5, 
    [data-testid="stSidebar"] h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    [data-testid="stSidebar"] label p {
        color: #94a3b8 !important; /* Soft blue-gray for labels */
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #cbd5e1 !important; /* Legible white-gray text */
    }
    
    /* Sidebar Input Styling (Dark theme inputs) */
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] select, 
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within {
        border-color: #10b981 !important; /* Emerald green accent focus */
    }
    
    /* Main body headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Custom Card Style for Forms/Information Blocks */
    .custom-card {
        background-color: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 20px !important;
        padding: 28px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02), 0 8px 10px -6px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 25px !important;
    }
    
    /* Main Content Input Elements Styling */
    div.stTextInput input, 
    div.stSelectbox div[data-baseweb="select"], 
    div.stNumberInput input, 
    div.stTextArea textarea,
    div.stMultiSelect div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    
    div.stTextInput input:focus, 
    div.stSelectbox div[data-baseweb="select"]:focus-within, 
    div.stNumberInput input:focus, 
    div.stTextArea textarea:focus {
        border-color: #10b981 !important; /* Emerald Focus */
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
    }
    
    /* Button pill styling */
    div.stButton > button {
        border-radius: 9999px !important; /* Premium Pill style */
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important; /* Emerald to forest green gradient */
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #f1f5f9 !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    div.stButton > button[kind="secondary"]:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }
    
    /* Executive Metric KPI Card Layout */
    .kpi-card {
        background-color: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.01) !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 15px !important;
        border-left: 6px solid #e2e8f0 !important; /* Slate accent default */
    }
    
    .kpi-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.04) !important;
    }
    
    .kpi-title {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 8px !important;
    }
    
    .kpi-value {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.1 !important;
        margin-bottom: 4px !important;
    }
    
    .kpi-desc {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    
    /* Accents base on color scheme */
    .kpi-primary { border-left: 6px solid #10b981 !important; } /* Emerald Green */
    .kpi-secondary { border-left: 6px solid #6366f1 !important; } /* Indigo */
    .kpi-tertiary { border-left: 6px solid #f43f5e !important; } /* Rose/Red */
    .kpi-neutral { border-left: 6px solid #0f172a !important; } /* Dark Charcoal */
    
    /* Recommendation boxes */
    .recommendation-box {
        background-color: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.01) !important;
        margin-top: 20px !important;
    }
    
    /* Premium List Item styling inside Recommendations */
    .rec-item {
        background-color: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 18px !important;
        padding: 22px !important;
        margin-bottom: 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.01) !important;
    }
    
    .rec-item:hover {
        border-color: #10b981 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.05) !important;
    }

    /* Badges */
    .badge-met {
        display: inline-block !important;
        background-color: #ecfdf5 !important; /* Soft green */
        color: #047857 !important; /* Dark green */
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 9999px !important;
        margin-right: 8px !important;
        margin-bottom: 8px !important;
        border: 1px solid #a7f3d0 !important;
    }
    
    .badge-gap {
        display: inline-block !important;
        background-color: #fff1f2 !important; /* Soft red */
        color: #be123c !important; /* Dark red */
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 9999px !important;
        margin-right: 8px !important;
        margin-bottom: 8px !important;
        border: 1px solid #fecdd3 !important;
    }
    
    .badge-neutral {
        display: inline-block !important;
        background-color: #f8fafc !important;
        color: #475569 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 9999px !important;
        margin-right: 8px !important;
        margin-bottom: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Fallback taxonomy lists in case files aren't accessible (safety first)
DEFAULT_ROLES = ["data_engineer", "data_scientist", "data_analyst", "frontend_developer", "backend_developer", "ml_engineer"]
DEFAULT_SKILLS = [
    "python", "sql", "java", "javascript", "typescript", "c++", "php", "r", "scala", 
    "apache spark", "kafka", "airflow", "dbt", "etl", "data pipeline", "snowflake", "bigquery", "databricks",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "aws", "gcp", "azure",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "llm",
    "pandas", "numpy", "tableau", "power bi", "excel", "statistics", "data visualization",
    "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "linux", "git",
    "react", "next.js", "vue", "node.js", "fastapi", "rest api",
    "communication", "leadership", "teamwork", "problem solving", "project management"
]

# ==============================================================================
# 📥 2. API REQUEST UTILITIES
# ==============================================================================
def test_api_health(api_url):
    """Memeriksa kesehatan endpoint API."""
    try:
        response = requests.get(f"{api_url}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return True, f"API Aktif (Model Terpasang: {data.get('model_loaded', False)})"
        return False, f"API Error (HTTP {response.status_code})"
    except Exception as e:
        return False, "API Offline / Tidak Terhubung"

def fetch_api_roles(api_url):
    """Mendapatkan daftar role yang didukung dari backend API."""
    try:
        response = requests.get(f"{api_url}/roles", timeout=3)
        if response.status_code == 200:
            return response.json().get("roles", DEFAULT_ROLES)
    except:
        pass
    return DEFAULT_ROLES

def send_analyze_pdf(api_url, file_bytes, filename, target_role, top_k, api_key):
    """Kirim file PDF CV ke endpoint API."""
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    files = {"file": (filename, file_bytes, "application/pdf")}
    data = {"target_role": target_role, "top_k": int(top_k)}
    
    response = requests.post(f"{api_url}/analyze/pdf", files=files, data=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            err_detail = response.json().get("detail", response.text)
        except:
            err_detail = response.text
        raise Exception(f"Error {response.status_code}: {err_detail}")

def send_analyze_text(api_url, cv_text, target_role, top_k, api_key):
    """Kirim teks CV ke endpoint API."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
        
    payload = {
        "cv_text": cv_text,
        "target_role": target_role,
        "top_k": int(top_k)
    }
    
    response = requests.post(f"{api_url}/analyze/text", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            err_detail = response.json().get("detail", response.text)
        except:
            err_detail = response.text
        raise Exception(f"Error {response.status_code}: {err_detail}")

def send_analyze_structured(api_url, skills, experience_years, education, target_role, summary, api_key):
    """Kirim profil terstruktur ke endpoint API."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
        
    payload = {
        "skills": skills,
        "experience_years": int(experience_years),
        "education": education,
        "target_role": target_role,
        "summary": summary
    }
    
    response = requests.post(f"{api_url}/analyze/structured", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        try:
            err_detail = response.json().get("detail", response.text)
        except:
            err_detail = response.text
        raise Exception(f"Error {response.status_code}: {err_detail}")


# ==============================================================================
# 🖥️ 3. STREAMLIT USER INTERFACE
# ==============================================================================

# Title Header Section
col_header_title, col_header_logo = st.columns([5, 1])
with col_header_title:
    st.markdown("<h1 style='margin-bottom: 2px; color: #0f172a; font-family: \"Plus Jakarta Sans\", sans-serif; font-weight: 800;'>CV Intelligence & Job Matcher</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 15px; margin-top: 0px; font-weight: 500; font-family: Inter;'>Analisis Kesiapan Skill Terhadap Standar Jabatan & Rekomendasi Lowongan Kerja Semantik Terdekat (FAISS + BERT)</p>", unsafe_allow_html=True)
with col_header_logo:
    st.markdown("""
    <div style='background-color: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 10px; text-align: center;'>
        <span style='color: #059669; font-weight: 800; font-size: 14px; display: block; font-family: "Plus Jakarta Sans";'>FAISS</span>
        <span style='color: #0f172a; font-weight: 600; font-size: 10px; display: block; font-family: "Plus Jakarta Sans";'>SEMATCH</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SIDEBAR: CONFIGURATIONS
# --------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='margin-top:0px; font-size:22px;'>Konfigurasi API</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin:10px 0; border-color:#334155;'>", unsafe_allow_html=True)

default_backend = os.getenv("BACKEND_URL", "http://localhost:8080")
api_host = st.sidebar.text_input("Host API Backend:", value=default_backend, help="Tentukan alamat host server FastAPI Anda.")
api_key = st.sidebar.text_input("X-API-Key (Jika Diperlukan):", type="password", help="Masukkan API Key jika backend Anda diamankan.")

# Connection check
is_connected, conn_msg = test_api_health(api_host)
if is_connected:
    st.sidebar.success(f"{conn_msg}")
else:
    st.sidebar.error(f"{conn_msg}")

st.sidebar.markdown("<br><hr style='border-color:#334155;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='background-color:#1e293b; border: 1px solid #334155; border-radius:14px; padding:15px; font-size:12px; color:#cbd5e1; line-height: 1.5;'>
    <h5 style='margin:0 0 6px 0; color:#f8fafc; font-weight:700; font-family: Inter;'>Panduan Menjalankan API:</h5>
    <code style='color:#10b981; font-size:11px;'>uvicorn app.main:app --port 8080 --reload</code>
    <p style='margin:8px 0 0 0; color:#cbd5e1;'>Pastikan model binary seperti <code>faiss_job_index.bin</code> telah diunduh dan disimpan di dalam folder <code>models/</code> agar sistem inference berjalan sempurna.</p>
</div>
""", unsafe_allow_html=True)

# Fetch roles dynamically
roles_options = fetch_api_roles(api_host)
role_mapping = {r: r.replace("_", " ").title() for r in roles_options}

# Session state initialization for holding results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --------------------------------------------------------------------------
# MAIN CONTENT: UNIFIED FORM LAYOUT (NO TABS)
# --------------------------------------------------------------------------

# Container for the unified form
st.markdown("""
<div class="custom-card">
    <h3 style="font-size: 20px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; font-family: 'Plus Jakarta Sans', sans-serif;">
        Formulir Evaluasi CV & Kecocokan Kerja
    </h3>
    <p style="color: #64748b; font-size: 14px; margin: 0 0 24px 0; font-family: Inter;">
        Tentukan target profesi Anda, lalu unggah CV atau isi profil kompetensi Anda di bawah ini.
    </p>
</div>
""", unsafe_allow_html=True)

# Outer wrapper for form controls to style cleanly
form_container = st.container()

with form_container:
    # Row 1: Target Role & Top K
    col_job, col_k = st.columns([3, 2])
    with col_job:
        selected_role_key = st.selectbox(
            "Target Jabatan Industri:",
            options=roles_options,
            format_func=lambda x: role_mapping.get(x, x),
            key="main_target_role",
            help="Pilih profesi target untuk membandingkan kecocokan skill Anda."
        )
    with col_k:
        top_k_val = st.slider(
            "Jumlah Rekomendasi Lowongan (Top K):",
            min_value=1,
            max_value=10,
            value=5,
            key="main_top_k",
            help="Tentukan jumlah lowongan kerja terdekat yang ingin ditampilkan."
        )
        
    st.markdown("<hr style='margin: 20px 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)
    
    # Row 2: Method selection (Radio button group styled nicely)
    input_method = st.radio(
        "Pilih Metode Analisis:",
        options=[
            "Unggah Berkas PDF CV", 
            "Tempel Teks CV", 
            "Isi Profil Kompetensi Terstruktur"
        ],
        horizontal=True,
        key="main_input_method",
        help="Pilih metode input data CV/Profil pelamar yang paling praktis untuk Anda."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Conditional Form Fields base on Input Method
    if input_method == "Unggah Berkas PDF CV":
        st.markdown("<p style='font-size:14px; font-weight:600; color:#334155; margin-bottom:6px;'>Dokumen PDF CV:</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Pilih file PDF CV Anda:", 
            type=["pdf"], 
            key="pdf_uploader_main",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Mulai Analisis File PDF", type="primary", use_container_width=True, key="btn_pdf_main"):
            if uploaded_file is not None:
                with st.spinner("Mengunggah file PDF dan menjalankan analisis..."):
                    try:
                        file_bytes = uploaded_file.read()
                        res = send_analyze_pdf(
                            api_host, 
                            file_bytes, 
                            uploaded_file.name, 
                            selected_role_key, 
                            top_k_val, 
                            api_key
                        )
                        st.session_state.analysis_result = res
                        st.success("Analisis berhasil diselesaikan!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis PDF: {e}")
            else:
                st.warning("Mohon unggah file PDF CV Anda terlebih dahulu.")
                
    elif input_method == "Tempel Teks CV":
        st.markdown("<p style='font-size:14px; font-weight:600; color:#334155; margin-bottom:6px;'>Tulis atau Tempel Isi CV:</p>", unsafe_allow_html=True)
        cv_text_input = st.text_area(
            "Isi Teks CV:",
            height=280,
            placeholder="Tempel isi teks CV Anda di sini...\n\nContoh:\nJohn Doe\nData Scientist dengan 3 tahun pengalaman...\nSkills: Python, SQL, TensorFlow, Machine Learning...",
            key="text_area_main",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Mulai Analisis Teks CV", type="primary", use_container_width=True, key="btn_text_main"):
            if len(cv_text_input.strip()) >= 20:
                with st.spinner("Memproses teks CV dan menghitung keselarasan..."):
                    try:
                        res = send_analyze_text(
                            api_host, 
                            cv_text_input, 
                            selected_role_key, 
                            top_k_val, 
                            api_key
                        )
                        st.session_state.analysis_result = res
                        st.success("Analisis teks berhasil diselesaikan!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis teks CV: {e}")
            else:
                st.warning("Teks CV terlalu pendek. Pastikan teks minimal 20 karakter.")
                
    else: # Structured Form Input
        st.markdown("<p style='font-size:14px; font-weight:600; color:#334155; margin-bottom:12px;'>Isi Rincian Kompetensi Pelamar:</p>", unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            exp_years = st.number_input(
                "Pengalaman Kerja (Tahun):", 
                min_value=0, 
                max_value=40, 
                value=2, 
                step=1, 
                key="num_exp_main"
            )
            education_val = st.selectbox(
                "Tingkat Pendidikan Terakhir:",
                ["D3 - Ahli Madya", "D4 / S1 - Sarjana", "S2 - Magister", "S3 - Doktor", "SMA / SMK / Sederajat", "Lainnya"],
                key="sel_edu_main"
            )
        with col_f2:
            selected_skills = st.multiselect(
                "Pilih Keahlian Utama Anda (Teknologi & Tools):",
                options=sorted(DEFAULT_SKILLS),
                default=["python", "sql", "git"],
                key="multi_skills_main"
            )
            
        summary_text = st.text_area(
            "Ringkasan Profil Singkat (Opsional):",
            height=100,
            placeholder="Tulis ringkasan singkat profil karir atau minat profesional Anda...",
            key="text_summary_main"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Analisis Profil Terstruktur", type="primary", use_container_width=True, key="btn_struct_main"):
            if not selected_skills:
                st.warning("Mohon pilih minimal satu keahlian utama Anda.")
            else:
                with st.spinner("Menghitung skor indeks kecocokan..."):
                    try:
                        res = send_analyze_structured(
                            api_host,
                            selected_skills,
                            exp_years,
                            education_val,
                            selected_role_key,
                            summary_text,
                            api_key
                        )
                        st.session_state.analysis_result = res
                        st.success("Analisis terstruktur berhasil diselesaikan!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis profil terstruktur: {e}")


# ==================================
# 4. RENDER RESULTS SECTION
# ==============================================================================
if st.session_state.analysis_result is not None:
    res = st.session_state.analysis_result
    st.markdown("<br><hr style='border-color: #e2e8f0;'><br>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family: \"Plus Jakarta Sans\", sans-serif; color: #0f172a; margin-bottom: 5px; font-weight: 800;'>Hasil Analisis CV: {role_mapping.get(res.get('target_role'), res.get('target_role'))}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 15px; margin-bottom: 20px; font-family: Inter;'>Berikut adalah hasil evaluasi komparatif kecocokan profil Anda terhadap standar pasar industri:</p>", unsafe_allow_html=True)

    # KPI High Level Metrics base on design colors:
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    score = res.get("overall_readiness_score", 0)
    level = res.get("skill_assessment", {}).get("readiness_level", "BELUM DIKETAHUI")
    
    # Class mapping for top color accents
    if score >= 80:
        theme_class = "kpi-secondary" # Indigo
        level_color = "#6366f1"
    elif score >= 60:
        theme_class = "kpi-primary" # Emerald
        level_color = "#10b981"
    elif score >= 40:
        theme_class = "kpi-tertiary" # Rose
        level_color = "#f43f5e"
    else:
        theme_class = "kpi-neutral" # Charcoal
        level_color = "#0f172a"
        
    with col_m1:
        st.markdown(f"""
        <div class="kpi-card {theme_class}">
            <div class="kpi-title">Skor Kesiapan Kerja</div>
            <div class="kpi-value">{score}%</div>
            <div class="kpi-desc">Kesesuaian Total Kompetensi</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.markdown(f"""
        <div class="kpi-card {theme_class}">
            <div class="kpi-title">Kategori Kesiapan</div>
            <div class="kpi-value" style="font-size: 20px !important; color: {level_color} !important;">{level}</div>
            <div class="kpi-desc">Status Daya Saing Profil</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        total_matched = len(res.get("skill_assessment", {}).get("met", []))
        st.markdown(f"""
        <div class="kpi-card kpi-primary">
            <div class="kpi-title">Skill Terpenuhi</div>
            <div class="kpi-value" style="color: #059669 !important;">{total_matched} Skill</div>
            <div class="kpi-desc">Telah Terdeteksi di CV</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m4:
        total_gap = len(res.get("skill_assessment", {}).get("gap", []))
        st.markdown(f"""
        <div class="kpi-card kpi-tertiary">
            <div class="kpi-title">Kesenjangan Skill (Gap)</div>
            <div class="kpi-value" style="color: #be123c !important;">{total_gap} Skill</div>
            <div class="kpi-desc">Kelemahan Profil untuk Diperbaiki</div>
        </div>
        """, unsafe_allow_html=True)

    # Core details layouts
    col_details_left, col_details_right = st.columns([1, 1])

    with col_details_left:
        # Category Breakdown Chart
        st.markdown("<h3 style='font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 18px; margin-top: 15px; color: #0f172a; font-weight: 700;'>Rincian Kategori Kompetensi</h3>", unsafe_allow_html=True)
        
        breakdown = res.get("skill_assessment", {}).get("breakdown", {})
        if breakdown:
            categories_display = {
                "core_skills": "Core Skills (Utama)",
                "expected_skills": "Expected Skills (Diharapkan)",
                "nice_to_have": "Nice to Have (Opsional)",
                "soft_skills": "Soft Skills (Sosial)"
            }
            
            categories_data = []
            for k, name in categories_display.items():
                if k in breakdown:
                    categories_data.append({
                        "Kategori": name,
                        "Skor (%)": breakdown[k]["score"],
                        "Bobot Indeks": breakdown[k]["weight"]
                    })
            df_bd = pd.DataFrame(categories_data)
            
            # Using colors matching the color guide
            fig_bd = px.bar(
                df_bd,
                y="Kategori",
                x="Skor (%)",
                text="Skor (%)",
                color="Skor (%)",
                orientation="h",
                color_continuous_scale=["#f43f5e", "#10b981", "#059669"],
                hover_data=["Bobot Indeks"]
            )
            fig_bd.update_traces(texttemplate='%{text}%', textposition='inside')
            fig_bd.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                xaxis=dict(range=[0, 105], showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(title=None),
                margin=dict(l=10, r=10, t=10, b=10),
                height=240
            )
            st.plotly_chart(fig_bd, use_container_width=True)
            
        # Met & Gap skills lists
        st.markdown("<h3 style='font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 18px; color: #0f172a; font-weight: 700;'>Pemetaan Keahlian CV vs Kebutuhan Peran</h3>", unsafe_allow_html=True)
        
        # Display Met skills
        met_skills = res.get("skill_assessment", {}).get("met", [])
        if met_skills:
            st.markdown("<p style='font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 5px;'>Keahlian yang Anda miliki (Met):</p>", unsafe_allow_html=True)
            badges_html = "".join([f"<span class='badge-met'>{s}</span>" for s in met_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#64748B; font-size: 13px;'>Tidak ada keahlian terdaftar yang sesuai.</p>", unsafe_allow_html=True)
            
        # Display Gap skills
        gap_skills = res.get("skill_assessment", {}).get("gap", [])
        if gap_skills:
            st.markdown("<br><p style='font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 5px;'>Keahlian yang perlu dipelajari (Gap):</p>", unsafe_allow_html=True)
            badges_html = "".join([f"<span class='badge-gap'>{s}</span>" for s in gap_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<br><p style='color:#64748B; font-size: 13px;'>Hebat! Anda tidak memiliki kesenjangan skill dengan peran ini.</p>", unsafe_allow_html=True)
 
        # Learning Priority Recommendations
        priority_list = res.get("skill_assessment", {}).get("priority_learning", [])
        if priority_list:
            st.markdown("<br><h3 style='font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 18px; color: #0f172a; font-weight: 700;'>Rekomendasi Prioritas Belajar</h3>", unsafe_allow_html=True)
            
            p_data = []
            for item in priority_list:
                p_data.append({
                    "Skill / Teknologi": item["skill"].title(),
                    "Prioritas Up-skilling": "Tinggi (Core Skill)" if item["priority"] == "TINGGI" else "Sedang (Expected)"
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
 
    with col_details_right:
        # Job Recommendations list
        st.markdown("<h3 style='font-family: \"Plus Jakarta Sans\", sans-serif; font-size: 18px; margin-top: 15px; color: #0f172a; font-weight: 700;'>Rekomendasi Lowongan Kerja Relevan</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 15px; font-family: Inter;'>Inference semantik FAISS menampilkan lowongan terdekat yang cocok dengan isi profil/CV Anda:</p>", unsafe_allow_html=True)
        
        recs = res.get("recommended_jobs", [])
        if recs:
            for job in recs:
                conf = job.get("confidence_score", 0) * 100
                st.markdown(f"""
                <div class="rec-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin: 0; font-size: 16px; color: #0f172a; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700;">Rank #{job.get('rank', 0)} - {job.get('job_title', 'N/A')}</h4>
                        <span style="font-weight:700; color:#059669; font-size:14px;">Match: {conf:.1f}%</span>
                    </div>
                    <div style="color:#64748b; font-size:13px; font-weight:600; margin-bottom:4px;">Perusahaan: {job.get('company_name', 'N/A')} | Lokasi: {job.get('location', 'N/A')}</div>
                    <div style="font-size:12px; color:#475569; font-style:italic; margin-bottom:12px;">"{job.get('reasoning', '')}"</div>
                """, unsafe_allow_html=True)
                
                # Match & Missing skills inside the job card
                job_met = job.get("matched_skills", [])
                job_gap = job.get("missing_skills", [])
                
                if job_met:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#059669; display:block; margin-bottom:3px;'>Skill Cocok:</span>", unsafe_allow_html=True)
                    met_badges = "".join([f"<span class='badge-met' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_met])
                    st.markdown(f"<div style='margin-bottom:8px;'>{met_badges}</div>", unsafe_allow_html=True)
                    
                if job_gap:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#f43f5e; display:block; margin-bottom:3px;'>Skill Perlu Ditingkatkan:</span>", unsafe_allow_html=True)
                    gap_badges = "".join([f"<span class='badge-gap' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_gap])
                    st.markdown(f"<div>{gap_badges}</div>", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada lowongan kerja rekomendasi yang ditemukan untuk profil ini.")
 
    # Show raw JSON metadata inside expander
    with st.expander("Lihat Metadata Respons API (Raw JSON)"):
        st.json(res)
