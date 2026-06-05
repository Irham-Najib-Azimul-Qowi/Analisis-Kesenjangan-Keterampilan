# -*- coding: utf-8 -*-
"""
Dashboard Evaluasi CV & Rekomendasi Lowongan Kerja - Clean Modern Light Theme
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
# 🎨 1. HIGH-CONTRAST MODERN LIGHT THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="CV Intelligence & Job Matcher",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injected CSS for ultra-clean light mode with high-end presentation aesthetics
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Global Typography Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Clean Top Header Bar */
    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    
    /* Executive Metric KPI Card Layout */
    .kpi-card {
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.06) !important;
        transition: all 0.2s ease-in-out !important;
        margin-bottom: 15px !important;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px) !important;
        border-color: #4f46e5 !important;
        box-shadow: 0 10px 25px -4px rgba(79, 70, 229, 0.08) !important;
    }
    
    .kpi-title {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 5px !important;
    }
    
    .kpi-value {
        font-size: 34px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin-bottom: 4px !important;
        letter-spacing: -0.8px !important;
        line-height: 1.1 !important;
    }
    
    .kpi-desc {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    
    /* Color accent indicators */
    .kpi-indigo { border-top: 4px solid #4f46e5 !important; }
    .kpi-teal { border-top: 4px solid #0d9488 !important; }
    .kpi-amber { border-top: 4px solid #d97706 !important; }
    .kpi-rose { border-top: 4px solid #e11d48 !important; }
    .kpi-orange { border-top: 4px solid #ea580c !important; }
    
    /* Custom Styled recommendation boxes */
    .recommendation-box {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01) !important;
        margin-top: 20px !important;
    }
    
    /* Premium List Item styling inside Recommendations */
    .rec-item {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 15px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .rec-item:hover {
        border-color: #cbd5e1 !important;
        background-color: #f1f5f9 !important;
    }

    /* Badges */
    .badge-met {
        display: inline-block !important;
        background-color: #d1fae5 !important;
        color: #065f46 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        border: 1px solid #a7f3d0 !important;
    }
    
    .badge-gap {
        display: inline-block !important;
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
        border: 1px solid #fca5a5 !important;
    }
    
    .badge-neutral {
        display: inline-block !important;
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 12px !important;
        margin-right: 6px !important;
        margin-bottom: 6px !important;
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
    st.markdown("<h1 style='margin-bottom:0px; color:#0f172a; font-family: Outfit;'>CV Intelligent Evaluator & Job Matcher</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:16px; margin-top:2px; font-weight: 500;'>Analisis Kesiapan Skill Terhadap Standar Jabatan & Rekomendasi Lowongan Kerja Semantik Terdekat (FAISS + BERT)</p>", unsafe_allow_html=True)
with col_header_logo:
    st.markdown("""
    <div style='background-color:rgba(79, 70, 229, 0.08); border:1px solid rgba(79, 70, 229, 0.15); border-radius:12px; padding:10px; text-align:center;'>
        <span style='color:#4f46e5; font-weight:800; font-size:14px; display:block; font-family: "Outfit";'>FAISS</span>
        <span style='color:#334155; font-weight:600; font-size:10px; display:block; font-family: "Outfit";'>SEMATCH</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top:10px; margin-bottom:25px; border-color:#e2e8f0;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# SIDEBAR: CONFIGURATIONS
# --------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='color:#4f46e5; margin-top:0px; font-size:22px; font-family: Outfit;'>⚙️ Konfigurasi API</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin:10px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)

default_backend = os.getenv("BACKEND_URL", "http://localhost:8080")
api_host = st.sidebar.text_input("Host API Backend:", value=default_backend, help="Tentukan alamat host server FastAPI Anda.")
api_key = st.sidebar.text_input("X-API-Key (Jika Diperlukan):", type="password", help="Masukkan API Key jika backend Anda diamankan.")

# Connection check
is_connected, conn_msg = test_api_health(api_host)
if is_connected:
    st.sidebar.success(f"🟢 {conn_msg}")
else:
    st.sidebar.error(f"🔴 {conn_msg}")

st.sidebar.markdown("<br><h4 style='color:#334155; font-size:14px; font-weight:700; margin:0; font-family: Outfit;'>🎯 PENGATURAN TARGET</h4></div>", unsafe_allow_html=True)

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

st.sidebar.markdown("<br><hr style='border-color:#e2e8f0;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='background-color:#f8fafc; border: 1px solid #e2e8f0; border-radius:10px; padding:15px; font-size:12px; color:#475569; line-height: 1.5;'>
    <h5 style='margin:0 0 6px 0; color:#0f172a; font-weight:700; font-family: Outfit;'>Panduan Menjalankan API:</h5>
    <code style='color:#ec4899; font-size:11px;'>uvicorn app.main:app --port 8080 --reload</code>
    <p style='margin:8px 0 0 0;'>Pastikan model binary seperti <code>faiss_job_index.bin</code> telah diunduh dan disimpan di dalam folder <code>models/</code> agar sistem inference berjalan sempurna.</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# MAIN CONTENT: USER SUBMISSIONS (TABS)
# --------------------------------------------------------------------------
tab_upload, tab_structured = st.tabs(["📂 Unggah CV (PDF / Teks)", "📝 Formulir Profil Terstruktur"])

# Session state initialization for holding results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

with tab_upload:
    st.markdown("<h3 style='font-size:18px; font-weight:700; color:#0f172a; margin-bottom:5px; font-family: Outfit;'>Kirim File CV atau Teks</h3>", unsafe_allow_html=True)
    st.markdown("Pilih salah satu metode di bawah ini untuk menyerahkan CV Anda:")
    
    cv_method = st.radio("Metode Input:", ["Unggah File PDF", "Tempel Teks CV (Plain Text)"], horizontal=True)
    
    if cv_method == "Unggah File PDF":
        uploaded_file = st.file_uploader("Pilih file PDF CV Anda:", type=["pdf"])
        
        if st.button("Mulai Analisis File PDF", type="primary", use_container_width=True):
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
                
    else:
        cv_text_input = st.text_area(
            "Tempel isi teks CV Anda di sini (Pastikan mengandung deskripsi profil, pengalaman, dan keahlian):",
            height=300,
            placeholder="Contoh:\n\nJohn Doe\nData Engineer dengan 3 tahun pengalaman...\nKeahlian: Python, SQL, Apache Spark, Cloud AWS..."
        )
        
        if st.button("Mulai Analisis Teks CV", type="primary", use_container_width=True):
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
    st.markdown("<h3 style='font-size:18px; font-weight:700; color:#0f172a; margin-bottom:5px; font-family: Outfit;'>Penilaian Skill Cepat (Tanpa Unggah Dokumen)</h3>", unsafe_allow_html=True)
    st.markdown("Masukkan informasi profil Anda secara manual untuk diuji keselarasan kompetensinya:")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        exp_years = st.number_input("Pengalaman Kerja (Tahun):", min_value=0, max_value=40, value=2, step=1)
        education_val = st.selectbox(
            "Tingkat Pendidikan Terakhir:",
            ["D3 - Ahli Madya", "D4 / S1 - Sarjana", "S2 - Magister", "S3 - Doktor", "SMA / SMK / Sederajat", "Lainnya"]
        )
    with col_f2:
        selected_skills = st.multiselect(
            "Pilih Keahlian Utama Anda (Teknologi & Tools):",
            options=sorted(DEFAULT_SKILLS),
            default=["python", "sql", "git"]
        )
        
    summary_text = st.text_area(
        "Ringkasan Profil Singkat (Opsional):",
        height=100,
        placeholder="Tulis ringkasan singkat profil karir atau minat profesional Anda..."
    )
    
    if st.button("Analisis Profil Terstruktur", type="primary", use_container_width=True):
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
    st.markdown("<br><hr style='border-color:#e2e8f0;'><br>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family: Outfit; color:#0f172a; margin-bottom:5px;'>📊 Hasil Analisis CV: {role_mapping.get(res.get('target_role'), res.get('target_role'))}</h2>", unsafe_allow_html=True)
    st.markdown("Berikut adalah hasil evaluasi komparatif kecocokan profil Anda terhadap standar pasar industri:")

    # KPI High Level Metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    score = res.get("overall_readiness_score", 0)
    level = res.get("skill_assessment", {}).get("readiness_level", "BELUM DIKETAHUI")
    emoji = res.get("skill_assessment", {}).get("readiness_emoji", "⚪")
    
    # Theme color base on level
    if score >= 80:
        theme_class = "kpi-teal"
        level_color = "#0d9488"
    elif score >= 60:
        theme_class = "kpi-indigo"
        level_color = "#4f46e5"
    elif score >= 40:
        theme_class = "kpi-orange"
        level_color = "#ea580c"
    else:
        theme_class = "kpi-rose"
        level_color = "#e11d48"
        
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
            <div class="kpi-value" style="font-size: 22px !important; color: {level_color} !important;">{emoji} {level}</div>
            <div class="kpi-desc">Status Daya Saing Profil</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        total_matched = len(res.get("skill_assessment", {}).get("met", []))
        st.markdown(f"""
        <div class="kpi-card kpi-teal">
            <div class="kpi-title">Skill Terpenuhi</div>
            <div class="kpi-value">{total_matched} Skill</div>
            <div class="kpi-desc">Telah Terdeteksi di CV</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m4:
        total_gap = len(res.get("skill_assessment", {}).get("gap", []))
        st.markdown(f"""
        <div class="kpi-card kpi-amber">
            <div class="kpi-title">Kesenjangan Skill (Gap)</div>
            <div class="kpi-value">{total_gap} Skill</div>
            <div class="kpi-desc">Kelemahan Profil untuk Diperbaiki</div>
        </div>
        """, unsafe_allow_html=True)

    # Core details layouts
    col_details_left, col_details_right = st.columns([1, 1])

    with col_details_left:
        # Category Breakdown Chart
        st.markdown("<h3 style='font-family: Outfit; font-size: 18px; margin-top:15px; color:#0f172a;'>📊 Rincian Kategori Kompetensi</h3>", unsafe_allow_html=True)
        
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
            
            fig_bd = px.bar(
                df_bd,
                y="Kategori",
                x="Skor (%)",
                text="Skor (%)",
                color="Kategori",
                orientation="h",
                color_discrete_sequence=px.colors.qualitative.Safe,
                hover_data=["Bobot Indeks"]
            )
            fig_bd.update_traces(texttemplate='%{text}%', textposition='inside')
            fig_bd.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(range=[0, 105], showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(title=None),
                margin=dict(l=10, r=10, t=10, b=10),
                height=240
            )
            st.plotly_chart(fig_bd, use_container_width=True)
            
        # Met & Gap skills lists
        st.markdown("<h3 style='font-family: Outfit; font-size: 18px; color:#0f172a;'>🔍 Pemetaan Keahlian CV vs Kebutuhan Peran</h3>", unsafe_allow_html=True)
        
        # Display Met skills
        met_skills = res.get("skill_assessment", {}).get("met", [])
        if met_skills:
            st.markdown("**Keahlian yang Anda miliki (Met):**")
            badges_html = "".join([f"<span class='badge-met'>{s}</span>" for s in met_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#94a3b8; font-size: 13px;'>Tidak ada keahlian terdaftar yang sesuai.</p>", unsafe_allow_html=True)
            
        # Display Gap skills
        gap_skills = res.get("skill_assessment", {}).get("gap", [])
        if gap_skills:
            st.markdown("<br>**Keahlian yang perlu dipelajari (Gap):**", unsafe_allow_html=True)
            badges_html = "".join([f"<span class='badge-gap'>{s}</span>" for s in gap_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<br><p style='color:#94a3b8; font-size: 13px;'>Hebat! Anda tidak memiliki kesenjangan skill dengan peran ini.</p>", unsafe_allow_html=True)

        # Learning Priority Recommendations
        priority_list = res.get("skill_assessment", {}).get("priority_learning", [])
        if priority_list:
            st.markdown("<br><h3 style='font-family: Outfit; font-size: 18px; color:#0f172a;'>🚀 Rekomendasi Prioritas Belajar</h3>", unsafe_allow_html=True)
            
            p_data = []
            for item in priority_list:
                p_data.append({
                    "Skill / Teknologi": item["skill"].title(),
                    "Prioritas Up-skilling": "🔴 TINGGI (Core Skill)" if item["priority"] == "TINGGI" else "🟡 SEDANG (Expected)"
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)

    with col_details_right:
        # Job Recommendations list
        st.markdown("<h3 style='font-family: Outfit; font-size: 18px; margin-top:15px; color:#0f172a;'>💼 Rekomendasi Lowongan Kerja Relevan</h3>", unsafe_allow_html=True)
        st.markdown("Inference semantik FAISS menampilkan lowongan terdekat yang cocok dengan isi profil/CV Anda:")
        
        recs = res.get("recommended_jobs", [])
        if recs:
            for job in recs:
                conf = job.get("confidence_score", 0) * 100
                st.markdown(f"""
                <div class="rec-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; font-size:16px; color:#0f172a; font-family:Outfit;">Rank #{job.get('rank', 0)} - {job.get('job_title', 'N/A')}</h4>
                        <span style="font-weight:700; color:#4f46e5; font-size:14px;">Match: {conf:.1f}%</span>
                    </div>
                    <div style="color:#64748b; font-size:13px; font-weight:600; margin-bottom:4px;">🏭 {job.get('company_name', 'N/A')} | 📍 {job.get('location', 'N/A')}</div>
                    <div style="font-size:12px; color:#475569; font-style:italic; margin-bottom:12px;">"{job.get('reasoning', '')}"</div>
                """, unsafe_allow_html=True)
                
                # Match & Missing skills inside the job card
                job_met = job.get("matched_skills", [])
                job_gap = job.get("missing_skills", [])
                
                if job_met:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#0d9488; display:block; margin-bottom:3px;'>Skill Cocok:</span>", unsafe_allow_html=True)
                    met_badges = "".join([f"<span class='badge-met' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_met])
                    st.markdown(f"<div style='margin-bottom:8px;'>{met_badges}</div>", unsafe_allow_html=True)
                    
                if job_gap:
                    st.markdown("<span style='font-size:11px; font-weight:700; color:#ea580c; display:block; margin-bottom:3px;'>Skill Perlu Ditingkatkan:</span>", unsafe_allow_html=True)
                    gap_badges = "".join([f"<span class='badge-gap' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_gap])
                    st.markdown(f"<div>{gap_badges}</div>", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada lowongan kerja rekomendasi yang ditemukan untuk profil ini.")

    # Show raw JSON metadata inside expander
    with st.expander("🛠️ Lihat Metadata Respons API (Raw JSON)"):
        st.json(res)
