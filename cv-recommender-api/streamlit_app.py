# -*- coding: utf-8 -*-
"""
Dashboard Evaluasi CV & Rekomendasi Lowongan Kerja - Custom Design System
Project: CV Recommender & Skill Assessment API Interface
Semester 4 Politeknik Negeri Madiun
"""

import os
import io
import pdfplumber
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.config import settings
from app.pipeline import CVAnalysisPipeline

# ==============================================================================
# 🎨 1. CUSTOM DESIGN SYSTEM STYLING
# ==============================================================================
st.set_page_config(
    page_title="CV Intelligence & Job Matcher",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan modern (meniru Gap Analysis)
st.markdown("""
<style>
    /* Metric/KPI Card Layout */
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
    }
    
    .kpi-title {
        font-size: 1rem;
        color: #555;
        margin-bottom: 10px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .kpi-desc {
        font-size: 0.85rem;
        color: #666;
    }
    
    /* Recommendation boxes */
    .recommendation-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    
    /* Premium List Item styling inside Recommendations */
    .rec-item {
        background-color: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
 
    /* Badges */
    .badge-met {
        display: inline-block;
        background-color: #d4edda;
        color: #155724;
        font-size: 12px;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .badge-gap {
        display: inline-block;
        background-color: #f8d7da;
        color: #721c24;
        font-size: 12px;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    .badge-neutral {
        display: inline-block;
        background-color: #e2e3e5;
        color: #383d41;
        font-size: 12px;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
        margin-right: 5px;
        margin-bottom: 5px;
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
# 🧠 2. AI PIPELINE INITIALIZATION
# ==============================================================================
@st.cache_resource(show_spinner="Sedang memuat AI Models (BERT & FAISS)...")
def load_pipeline():
    return CVAnalysisPipeline(
        model_dir=settings.MODEL_DIR,
        embedding_model_name=settings.EMBEDDING_MODEL,
    )

try:
    pipeline = load_pipeline()
    roles_options = list(pipeline.job_profiles.keys())
except Exception as e:
    st.error(f"Gagal memuat model AI: {e}")
    st.stop()


role_mapping = {r: r.replace("_", " ").title() for r in roles_options}

# ==============================================================================
# 🖥️ 3. STREAMLIT USER INTERFACE
# ==============================================================================

# ================= HEADER =================
st.title("📄 CV Intelligence & Job Matcher")
st.markdown("""
Dashboard ini dirancang untuk melakukan **Analisis Kesiapan Skill** Terhadap Standar Jabatan & memberikan **Rekomendasi Lowongan Kerja** Semantik Terdekat berbasis model FAISS + BERT.
""")
st.divider()
# Session state initialization for holding results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --------------------------------------------------------------------------
# MAIN CONTENT: UNIFIED FORM LAYOUT (NO TABS)
# --------------------------------------------------------------------------

# Container for the unified form
# Container for the unified form
with st.container(border=True):
    st.subheader("📋 Formulir Evaluasi CV & Kecocokan Kerja")
    st.write("Tentukan target profesi Anda, lalu unggah CV atau isi profil kompetensi Anda di bawah ini.")

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
        
    st.markdown("<hr style='margin: 20px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    
    # Row 2: Method selection (Radio button group styled nicely)
    input_method = st.radio(
        "Pilih Metode Analisis:",
        options=[
            "Unggah Berkas PDF CV", 
            "Isi Profil Kompetensi Terstruktur"
        ],
        horizontal=True,
        key="main_input_method",
        help="Pilih metode input data CV/Profil pelamar yang paling praktis untuk Anda."
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Conditional Form Fields base on Input Method
    if input_method == "Unggah Berkas PDF CV":
        st.markdown("**Dokumen PDF CV:**")
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
                        text_pages = []
                        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                            for page in pdf.pages:
                                t = page.extract_text()
                                if t:
                                    text_pages.append(t)
                        cv_text = "\\n".join(text_pages)
                        if len(cv_text.strip()) < 20:
                            st.error("PDF tidak mengandung teks yang cukup")
                            st.stop()
                        
                        res = pipeline.analyze(cv_text, selected_role_key, top_k_val)
                        st.session_state.analysis_result = res
                        st.success("Analisis berhasil diselesaikan!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis PDF: {e}")
            else:
                st.warning("Mohon unggah file PDF CV Anda terlebih dahulu.")
                
    else: # Structured Form Input
        st.markdown("**Isi Rincian Kompetensi Pelamar:**")
        
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
        
        if st.button("Mulai Analisis Profil Terstruktur", type="primary", use_container_width=True, key="btn_struct_main"):
            if not selected_skills:
                st.warning("Mohon pilih minimal satu keahlian utama Anda.")
            else:
                with st.spinner("Menghitung skor indeks kecocokan..."):
                    try:
                        cv_text = f"""
                        Professional with {exp_years} years of experience.
                        Education: {education_val}. Target: {selected_role_key}.
                        Skills: {", ".join(selected_skills)}. {summary_text}
                        """
                        res = pipeline.analyze(cv_text.strip(), selected_role_key)
                        st.session_state.analysis_result = res
                        st.success("Analisis terstruktur berhasil diselesaikan!")
                    except Exception as e:
                        st.error(f"Gagal menganalisis profil terstruktur: {e}")


# ==================================
# 4. RENDER RESULTS SECTION
# ==============================================================================
if st.session_state.analysis_result is not None:
    res = st.session_state.analysis_result
    st.divider()
    st.header(f"Hasil Analisis CV: {role_mapping.get(res.get('target_role'), res.get('target_role'))}")
    st.write("Berikut adalah hasil evaluasi komparatif kecocokan profil Anda terhadap standar pasar industri:")

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
            <div class="kpi-value" style="font-size: 1.5rem; color: {level_color};">{level}</div>
            <div class="kpi-desc">Status Daya Saing Profil</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        total_matched = len(res.get("skill_assessment", {}).get("met", []))
        st.markdown(f"""
        <div class="kpi-card kpi-primary">
            <div class="kpi-title">Skill Terpenuhi</div>
            <div class="kpi-value" style="color: #10b981;">{total_matched} Skill</div>
            <div class="kpi-desc">Telah Terdeteksi di CV</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_m4:
        total_gap = len(res.get("skill_assessment", {}).get("gap", []))
        st.markdown(f"""
        <div class="kpi-card kpi-tertiary">
            <div class="kpi-title">Kesenjangan Skill (Gap)</div>
            <div class="kpi-value" style="color: #f43f5e;">{total_gap} Skill</div>
            <div class="kpi-desc">Kelemahan Profil untuk Diperbaiki</div>
        </div>
        """, unsafe_allow_html=True)

    # Core details layouts
    col_details_left, col_details_right = st.columns([1, 1])

    with col_details_left:
        # Category Breakdown Chart
        st.subheader("Rincian Kategori Kompetensi")
        
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
        st.subheader("Pemetaan Keahlian CV vs Kebutuhan Peran")
        
        # Display Met skills
        met_skills = res.get("skill_assessment", {}).get("met", [])
        if met_skills:
            st.markdown("**Keahlian yang Anda miliki (Met):**")
            badges_html = "".join([f"<span class='badge-met'>{s}</span>" for s in met_skills])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
        else:
            st.caption("Tidak ada keahlian terdaftar yang sesuai.")
            
        # Display Gap skills
        gap_skills = res.get("skill_assessment", {}).get("gap", [])
        if gap_skills:
            st.markdown("**Keahlian yang perlu dipelajari (Gap):**")
            badges_html = "".join([f"<span class='badge-gap'>{s}</span>" for s in gap_skills])
            st.markdown(f"<div>{badges_html}</div><br>", unsafe_allow_html=True)
        else:
            st.caption("Hebat! Anda tidak memiliki kesenjangan skill dengan peran ini.")
 
        # Learning Priority Recommendations
        priority_list = res.get("skill_assessment", {}).get("priority_learning", [])
        if priority_list:
            st.subheader("Rekomendasi Prioritas Belajar")
            
            p_data = []
            for item in priority_list:
                p_data.append({
                    "Skill / Teknologi": item["skill"].title(),
                    "Prioritas Up-skilling": "Tinggi (Core Skill)" if item["priority"] == "TINGGI" else "Sedang (Expected)"
                })
            st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
 
    with col_details_right:
        # Job Recommendations list
        st.subheader("Rekomendasi Lowongan Kerja Relevan")
        st.write("Inference semantik FAISS menampilkan lowongan terdekat yang cocok dengan isi profil/CV Anda:")
        
        recs = res.get("recommended_jobs", [])
        if recs:
            for job in recs:
                conf = job.get("confidence_score", 0) * 100
                st.markdown(f"""
                <div class="rec-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin: 0; font-size: 16px; color: #212529; font-weight: bold;">Rank #{job.get('rank', 0)} - {job.get('job_title', 'N/A')}</h4>
                        <span style="font-weight:bold; color:#198754; font-size:14px;">Match: {conf:.1f}%</span>
                    </div>
                    <div style="color:#495057; font-size:13px; font-weight:600; margin-bottom:4px;">Perusahaan: {job.get('company_name', 'N/A')} | Lokasi: {job.get('location', 'N/A')}</div>
                    <div style="font-size:12px; color:#6c757d; font-style:italic; margin-bottom:12px;">"{job.get('reasoning', '')}"</div>
                """, unsafe_allow_html=True)
                
                # Match & Missing skills inside the job card
                job_met = job.get("matched_skills", [])
                job_gap = job.get("missing_skills", [])
                
                if job_met:
                    st.markdown("<span style='font-size:11px; font-weight:bold; color:#198754; display:block; margin-bottom:3px;'>Skill Cocok:</span>", unsafe_allow_html=True)
                    met_badges = "".join([f"<span class='badge-met' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_met])
                    st.markdown(f"<div style='margin-bottom:8px;'>{met_badges}</div>", unsafe_allow_html=True)
                    
                if job_gap:
                    st.markdown("<span style='font-size:11px; font-weight:bold; color:#dc3545; display:block; margin-bottom:3px;'>Skill Perlu Ditingkatkan:</span>", unsafe_allow_html=True)
                    gap_badges = "".join([f"<span class='badge-gap' style='padding:2px 6px !important; font-size:10px !important;'>{s}</span>" for s in job_gap])
                    st.markdown(f"<div>{gap_badges}</div>", unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Tidak ada lowongan kerja rekomendasi yang ditemukan untuk profil ini.")
 
    # Show raw JSON metadata inside expander
    with st.expander("Lihat Metadata Respons API (Raw JSON)"):
        st.json(res)
