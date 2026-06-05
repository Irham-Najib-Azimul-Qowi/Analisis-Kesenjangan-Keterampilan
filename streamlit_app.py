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
# 🎨 1. CUSTOM DESIGN SYSTEM STYLING (MATCHING THE STYLE GUIDE IMAGE)
# ==============================================================================
st.set_page_config(
    page_title="CV Intelligence & Job Matcher",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected CSS implementing the design system from the uploaded image:
# - Primary Color: Emerald Green (#22C55E)
# - Secondary Color: Medium Green (#16A34A)
# - Tertiary Color: Coral/Salmon Pink (#FF8B7C)
# - Neutral Dark: Charcoal (#1F2937)
# - Page Background: Ice-blue/soft blue-gray (#EBF2FC)
# - Font: Inter (Headline, Body, Label)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Global Background and Typography */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #EBF2FC !important; /* Soft ice-blue background from image */
        color: #1F2937 !important; /* Neutral dark text */
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #D1E2F4 !important;
    }
    
    /* Clean Top Header Bar */
    [data-testid="stHeader"] {
        background-color: rgba(235, 242, 252, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #D1E2F4 !important;
    }
    
    /* Headings styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #1F2937 !important;
        letter-spacing: -0.5px !important;
    }

    /* Style Streamlit Tabs as Pill-shaped Segmented Controls */
    div[data-testid="stTabBar"] {
        background-color: #E2E8F0 !important;
        padding: 6px !important;
        border-radius: 30px !important;
        margin-bottom: 25px !important;
        display: inline-flex !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    div[data-testid="stTabBar"] button {
        background-color: transparent !important;
        border: none !important;
        border-radius: 24px !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        background-color: #16A34A !important; /* Secondary green for active pill tab */
        color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(22, 163, 74, 0.25) !important;
    }
    
    div[data-testid="stTabBar"] button:hover {
        color: #16A34A !important;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"]:hover {
        color: #FFFFFF !important;
    }
    
    /* Custom Card Style for Forms/Information Blocks */
    .custom-card {
        background-color: #FFFFFF !important;
        border: 1px solid #D1E2F4 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 4px 15px rgba(31, 41, 55, 0.03) !important;
        margin-bottom: 20px !important;
    }
    
    /* Executive Metric KPI Card Layout */
    .kpi-card {
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        background-color: #ffffff !important;
        border: 1px solid #D1E2F4 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 4px 15px rgba(31, 41, 55, 0.03) !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 15px !important;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px) !important;
        border-color: #16A34A !important;
        box-shadow: 0 10px 25px -4px rgba(22, 163, 74, 0.08) !important;
    }
    
    .kpi-title {
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 6px !important;
    }
    
    .kpi-value {
        font-size: 36px !important;
        font-weight: 800 !important;
        color: #1F2937 !important; /* Neutral dark */
        margin-bottom: 4px !important;
        letter-spacing: -1px !important;
        line-height: 1.1 !important;
    }
    
    .kpi-desc {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    
    /* Accents base on color scheme image */
    .kpi-primary { border-top: 5px solid #22C55E !important; } /* Emerald Green */
    .kpi-secondary { border-top: 5px solid #16A34A !important; } /* Medium Green */
    .kpi-tertiary { border-top: 5px solid #FF8B7C !important; } /* Coral/Salmon Pink */
    .kpi-neutral { border-top: 5px solid #1F2937 !important; } /* Dark Charcoal */

    /* Custom inputs rounded design */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] select, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea {
        border-radius: 16px !important; /* Rounded inputs */
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        padding: 10px 14px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Button pill styling */
    div.stButton > button {
        border-radius: 24px !important; /* Pill style */
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #16A34A !important; /* Medium green */
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2) !important;
        padding: 0.5rem 2.5rem !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #22C55E !important; /* Bright Emerald green on hover */
        box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #E2E8F0 !important; /* Light blue-gray button */
        color: #1F2937 !important;
        border: 1px solid #CBD5E1 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #CBD5E1 !important;
        border-color: #94A3B8 !important;
    }
    
    /* Recommendation boxes */
    .recommendation-box {
        background-color: #ffffff !important;
        border: 1px solid #D1E2F4 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 15px rgba(31, 41, 55, 0.03) !important;
        margin-top: 20px !important;
    }
    
    /* Premium List Item styling inside Recommendations */
    .rec-item {
        background-color: #FFFFFF !important;
        border: 1px solid #D1E2F4 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 8px rgba(31, 41, 55, 0.01) !important;
    }
    
    .rec-item:hover {
        border-color: #16A34A !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(22, 163, 74, 0.05) !important;
    }

    /* Badges */
    .badge-met {
        display: inline-block !important;
        background-color: #DCFCE7 !important; /* Soft green */
        color: #15803D !important; /* Dark green */
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 4px 10px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        border: 1px solid #86EFAC !important;
    }
    
    .badge-gap {
        display: inline-block !important;
        background-color: #FFE4E6 !important; /* Soft coral/salmon red */
        color: #B91C1C !important; /* Dark red */
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 4px 10px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        border: 1px solid #FECDD3 !important;
    }
    
    .badge-neutral {
        display: inline-block !important;
        background-color: #F1F5F9 !important;
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 4px 10px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        border: 1px solid #E2E8F0 !important;
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
    st.markdown("<h1 style='margin-bottom:0px; color:#1F2937; font-family: Inter;'>💼 CV Intelligence & Job Matcher</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:16px; margin-top:2px; font-weight: 500; font-family: Inter;'>Analisis Kesiapan Skill Terhadap Standar Jabatan & Rekomendasi Lowongan Kerja Semantik Terdekat (FAISS + BERT)</p>", unsafe_allow_html=True)
with col_header_logo:
    st.markdown("""
    <div style='background-color:rgba(22, 163, 74, 0.08); border:1px solid rgba(22, 163, 74, 0.2); border-radius:16px; padding:10px; text-align:center;'>
        <span style='color:#16A34A; font-weight:800; font-size:14px; display:block; font-family: "Inter";'>FAISS</span>
        <span style='color:#1F2937; font-weight:600; font-size:10px; display:block; font-family: "Inter";'>SEMATCH</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top:10px; margin-bottom:25px; border-color:#D1E2F4;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SIDEBAR: CONFIGURATIONS
# --------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='color:#16A34A; margin-top:0px; font-size:22px; font-family: Inter;'>⚙️ Konfigurasi API</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin:10px 0; border-color:#D1E2F4;'>", unsafe_allow_html=True)

default_backend = os.getenv("BACKEND_URL", "http://localhost:8080")
api_host = st.sidebar.text_input("Host API Backend:", value=default_backend, help="Tentukan alamat host server FastAPI Anda.")
api_key = st.sidebar.text_input("X-API-Key (Jika Diperlukan):", type="password", help="Masukkan API Key jika backend Anda diamankan.")

# Connection check
is_connected, conn_msg = test_api_health(api_host)
if is_connected:
    st.sidebar.success(f"🟢 {conn_msg}")
else:
    st.sidebar.error(f"🔴 {conn_msg}")

st.sidebar.markdown("<br><h4 style='color:#1F2937; font-size:14px; font-weight:700; margin:0; font-family: Inter;'>🎯 PENGATURAN TARGET</h4></div>", unsafe_allow_html=True)

# Dynamic roles fetching
roles_options = fetch_api_roles(api_host)
role_mapping = {r: r.replace("_", " ").title() for r in roles_options}

selected_role_key = st.sidebar.selectbox(
    "Target Jabatan Industri:",
    options=roles_options,
    format_func=lambda x: role_mapping.get(x, x)
)

top_k_val = st.sidebar.slider(
    "Rekomendasi Pekerjaan (Top K):",
    min_value=1,
    max_value=10,
    value=5
)

st.sidebar.markdown("<br><hr style='border-color:#D1E2F4;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='background-color:#FFFFFF; border: 1px solid #D1E2F4; border-radius:14px; padding:15px; font-size:12px; color:#475569; line-height: 1.5;'>
    <h5 style='margin:0 0 6px 0; color:#1F2937; font-weight:700; font-family: Inter;'>Panduan Menjalankan API:</h5>
    <code style='color:#16A34A; font-size:11px;'>uvicorn app.main:app --port 8080 --reload</code>
    <p style='margin:8px 0 0 0;'>Pastikan model binary seperti <code>faiss_job_index.bin</code> telah diunduh dan disimpan di dalam folder <code>models/</code> agar sistem inference berjalan sempurna.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# MAIN CONTENT: USER SUBMISSIONS (TABS AS DISTINCT DIRECT CHOICES)
# --------------------------------------------------------------------------

# Separate user options explicitly as requested: "input gitu atau upload cv"
tab_pdf, tab_text, tab_structured = st.tabs([
    "📂 Unggah Dokumen CV (PDF)", 
    "✍️ Tempel / Ketik Teks CV", 
    "📋 Profil Kompetensi Terstruktur"
])

# Session state initialization for holding results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

with tab_pdf:
    st.markdown("""
    <div class="custom-card">
        <h3 style="font-size:18px; font-weight:700; color:#1F2937; margin-bottom:5px; font-family: Inter;">📂 Unggah Berkas PDF CV</h3>
        <p style="color:#64748B; font-size:14px; margin-bottom:15px;">Sistem akan mengekstraksi teks dari berkas PDF Anda dan melakukan analisis keselarasan otomatis menggunakan modul NLP.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Pilih file PDF CV Anda:", type=["pdf"], key="pdf_uploader_main")
    
    if st.button("Mulai Analisis File PDF", type="primary", use_container_width=True, key="btn_pdf_main"):
        if uploaded_file is not None:
            with st.spinner("⏳ Mengunggah file PDF dan menjalankan model AI..."):
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

with tab_text:
    st.markdown("""
    <div class="custom-card">
        <h3 style="font-size:18px; font-weight:700; color:#1F2937; margin-bottom:5px; font-family: Inter;">✍️ Tempel / Ketik Teks CV</h3>
        <p style="color:#64748B; font-size:14px; margin-bottom:15px;">Tuliskan atau tempel konten teks CV Anda (pengalaman kerja, skill, pendidikan) secara langsung ke dalam bidang teks di bawah ini.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cv_text_input = st.text_area(
        "Isi Teks CV:",
        height=300,
        placeholder="Tempel isi CV Anda di sini...\n\nContoh:\nJohn Doe\nData Scientist dengan 3 tahun pengalaman...\nSkills: Python, SQL, TensorFlow, Machine Learning...",
        key="text_area_main"
    )
    
    if st.button("Mulai Analisis Teks CV", type="primary", use_container_width=True, key="btn_text_main"):
        if len(cv_text_input.strip()) >= 20:
            with st.spinner("⏳ Memproses teks CV dan menghitung keselarasan skill..."):
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

with tab_structured:
    st.markdown("""
    <div class="custom-card">
        <h3 style="font-size:18px; font-weight:700; color:#1F2937; margin-bottom:5px; font-family: Inter;">📋 Penilaian Profil Kompetensi Terstruktur</h3>
        <p style="color:#64748B; font-size:14px; margin-bottom:15px;">Input informasi keahlian, pengalaman, dan latar belakang Anda secara terstruktur tanpa perlu mengunggah dokumen.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        exp_years = st.number_input("Pengalaman Kerja (Tahun):", min_value=0, max_value=40, value=2, step=1, key="num_exp_main")
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
    
    if st.button("Analisis Profil Terstruktur", type="primary", use_container_width=True, key="btn_struct_main"):
        if not selected_skills:
            st.warning("Mohon pilih minimal satu keahlian utama Anda.")
        else:
            with st.spinner("⏳ Menghitung skor indeks kecocokan profil..."):
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


# ==============================================================================
# 📊 4. RENDER RESULTS SECTION
# ==============================================================================
if st.session_state.analysis_result is not None:
    res = st.session_state.analysis_result
    st.markdown("<br><hr style='border-color:#D1E2F4;'><br>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family: Inter; color:#1F2937; margin-bottom:5px;'>📊 Hasil Analisis CV: {role_mapping.get(res.get('target_role'), res.get('target_role'))}</h2>", unsafe_allow_html=True)
    st.markdown("Berikut adalah hasil evaluasi komparatif kecocokan profil Anda terhadap standar pasar industri:")

    # KPI High Level Metrics base on design colors:
    # - Green (#22C55E / #16A34A) for high scores/matched skills
    # - Coral/Salmon Pink (#FF8B7C) for gaps/learning priorities
    # - Charcoal (#1F2937) for general targets
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    score = res.get("overall_readiness_score", 0)
    level = res.get("skill_assessment", {}).get("readiness_level", "BELUM DIKETAHUI")
    emoji = res.get("skill_assessment", {}).get("readiness_emoji", "⚪")
    
    # Class mapping for top color accents
    if score >= 80:
        theme_class = "kpi-secondary" # Medium Green
        level_color = "#16A34A"
    elif score >= 60:
        theme_class = "kpi-primary" # Emerald Green
        level_color = "#22C55E"
    elif score >= 40:
        theme_class = "kpi-tertiary" # Coral
        level_color = "#FF8B7C"
    else:
        theme_class = "kpi-neutral" # Charcoal
        level_color = "#1F2937"
        
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
            <div class="kpi-value" style="font-size: 20px !important; color: {level_color} !important;">{emoji} {level}</div>
            <div class="kpi-desc">Status Daya Saing Profil</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        total_matched = len(res.get("skill_assessment", {}).get("met", []))
        st.markdown(f"""
        <div class="kpi-card kpi-primary">
            <div class="kpi-title">Skill Terpenuhi</div>
            <div class="kpi-value" style="color: #16A34A !important;">{total_matched} Skill</div>
            <div class="kpi-desc">Telah Terdeteksi di CV</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m4:
        total_gap = len(res.get("skill_assessment", {}).get("gap", []))
        st.markdown(f"""
        <div class="kpi-card kpi-tertiary">
            <div class="kpi-title">Kesenjangan Skill (Gap)</div>
            <div class="kpi-value" style="color: #FF8B7C !important;">{total_gap} Skill</div>
            <div class="kpi-desc">Kelemahan Profil untuk Diperbaiki</div>
        </div>
        """, unsafe_allow_html=True)

    # Core details layouts
    col_details_left, col_details_right = st.columns([1, 1])

    with col_details_left:
        # Category Breakdown Chart
        st.markdown("<h3 style='font-family: Inter; font-size: 18px; margin-top:15px; color:#1F2937;'>📊 Rincian Kategori Kompetensi</h3>", unsafe_allow_html=True)
        
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
            
            # Using colors matching the color guide: Greens and Coral
            fig_bd = px.bar(
                df_bd,
                y="Kategori",
                x="Skor (%)",
                text="Skor (%)",
                color="Skor (%)",
                orientation="h",
                color_continuous_scale=["#FF8B7C", "#16A34A", "#22C55E"], # From Coral to Emerald Green
                hover_data=["Bobot Indeks"]
            )
            fig_bd.update_traces(texttemplate='%{text}%', textposition='inside')
            fig_bd.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                xaxis=dict(range=[0, 105], showgrid=True, gridcolor="#D1E2F4"),
                yaxis=dict(title=None),
                margin=dict(l=10, r=10, t=10, b=10),
                height=240
            )
            st.plotly_chart(fig_bd, use_container_width=True)
            
        # Met & Gap skills lists
        st.markdown("<h3 style='font-family: Inter; font-size: 18px; color:#1F2937;'>🔍 Pemetaan Keahlian CV vs Kebutuhan Peran</h3>", unsafe_allow_html=True)
        
        # Display Met skills
        met_skills = res.get("skill_assessment", {}).get("met", [])
        if met_skills:
            st.markdown("**Keahlian yang Anda miliki (Met):**")
            badges_html = "".join([f"<span class='badge-met'>{s}</span>" for s in met_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#64748B; font-size: 13px;'>Tidak ada keahlian terdaftar yang sesuai.</p>", unsafe_allow_html=True)
            
        # Display Gap skills
        gap_skills = res.get("skill_assessment", {}).get("gap", [])
        if gap_skills:
            st.markdown("<br>**Keahlian yang perlu dipelajari (Gap):**", unsafe_allow_html=True)
            badges_html = "".join([f"<span class='badge-gap'>{s}</span>" for s in gap_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<br><p style='color:#64748B; font-size: 13px;'>Hebat! Anda tidak memiliki kesenjangan skill dengan peran ini.</p>", unsafe_allow_html=True)

        # Learning Priority Recommendations
        priority_list = res.get("skill_assessment", {}).get("priority_learning", [])
        if priority_list:
            st.markdown("<br><h3 style='font-family: Inter; font-size: 18px; color:#1F2937;'>🚀 Rekomendasi Prioritas Belajar</h3>", unsafe_allow_html=True)
            
            p_data = []
            for item in priority_list:
                p_data.append({
                    "Skill / Teknologi": item["skill"].title(),
                    "Prioritas Up-skilling": "🔴 TINGGI (Core Skill)" if item["priority"] == "TINGGI" else "🟡 SEDANG (Expected)"
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

    with col_details_right:
        # Job Recommendations list
        st.markdown("<h3 style='font-family: Inter; font-size: 18px; margin-top:15px; color:#1F2937;'>💼 Rekomendasi Lowongan Kerja Relevan</h3>", unsafe_allow_html=True)
        st.markdown("Inference semantik FAISS menampilkan lowongan terdekat yang cocok dengan isi profil/CV Anda:")
        
        recs = res.get("recommended_jobs", [])
        if recs:
            for job in recs:
                conf = job.get("confidence_score", 0) * 100
                st.markdown(f"""
                <div class="rec-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; font-size:16px; color:#1F2937; font-family:Inter;">Rank #{job.get('rank', 0)} - {job.get('job_title', 'N/A')}</h4>
                        <span style="font-weight:700; color:#16A34A; font-size:14px;">Match: {conf:.1f}%</span>
                    </div>
                    <div style="color:#64748b; font-size:13px; font-weight:600; margin-bottom:4px;">🏭 {job.get('company_name', 'N/A')} | 📍 {job.get('location', 'N/A')}</div>
                    <div style="font-size:12px; color:#475569; font-style:italic; margin-bottom:12px;">"{job.get('reasoning', '')}"</div>
                """, unsafe_allow_html=True)
                
                # Match & Missing skills inside the job card
                job_met = job.get("matched_skills", [])
                job_gap = job.get("missing_skills", [])
                
                if job_met:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#16A34A; display:block; margin-bottom:3px;'>Skill Cocok:</span>", unsafe_allow_html=True)
                    met_badges = "".join([f"<span class='badge-met' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_met])
                    st.markdown(f"<div style='margin-bottom:8px;'>{met_badges}</div>", unsafe_allow_html=True)
                    
                if job_gap:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#FF8B7C; display:block; margin-bottom:3px;'>Skill Perlu Ditingkatkan:</span>", unsafe_allow_html=True)
                    gap_badges = "".join([f"<span class='badge-gap' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_gap])
                    st.markdown(f"<div>{gap_badges}</div>", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada lowongan kerja rekomendasi yang ditemukan untuk profil ini.")

    # Show raw JSON metadata inside expander
    with st.expander("🛠️ Lihat Metadata Respons API (Raw JSON)"):
        st.json(res)
