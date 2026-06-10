# -*- coding: utf-8 -*-
# ==============================================================================
# 🖥️ DASHBOARD INTERAKTIF: Dashboard Evaluasi CV & Rekomendasi Lowongan Kerja
# Berkas ini mendefinisikan antarmuka pengguna (user interface) menggunakan Streamlit,
# membaca input berkas PDF CV, dan memanggil AI pipeline untuk menampilkan metrik.
# Politeknik Negeri Madiun - S4 Data Engineering
# ==============================================================================

# --- MOCK TORCHVISION (Mencegah Crash di Streamlit Cloud Python 3.14) ---
# Di Python 3.14 (Streamlit Cloud), file watcher memindai module path 'transformers' 
# dan memicu import 'torchvision' (opsional). Kita membuat mock agar tidak crash.
import sys
from types import ModuleType
try:
    import torchvision
except ImportError:
    class MockModule(ModuleType):
        def __getattr__(self, name):
            return MockModule(name)
        def __call__(self, *args, **kwargs):
            return MockModule("mock")
    mock_tv = MockModule("torchvision")
    sys.modules["torchvision"] = mock_tv
    sys.modules["torchvision.transforms"] = mock_tv
    sys.modules["torchvision.transforms.v2"] = mock_tv
    sys.modules["torchvision.ops"] = mock_tv
    sys.modules["torchvision.ops.boxes"] = mock_tv

# Mengimpor modul bawaan Python 'os' untuk manipulasi path berkas fisik model
import os

# Mengimpor modul bawaan Python 'io' untuk mengelola aliran data input-output berkas di memori
import io

# Mengimpor pustaka 'pdfplumber' untuk mengekstrak teks dari berkas PDF CV yang diunggah
import pdfplumber

# Mengimpor library 'pandas' (sebagai pd) untuk manipulasi data tabular/DataFrame
import pandas as pd

# Mengimpor library 'numpy' (sebagai np) untuk penanganan array data numerik
import numpy as np

# Mengimpor library 'streamlit' (sebagai st) untuk membuat dashboard web interaktif secara instan
import streamlit as st

# Mengimpor objek konfigurasi global settings dari berkas konfigurasi lokal app.config
from app.config import settings

# Mengimpor kelas pipeline model ML dari berkas integrasi lokal app.pipeline
from app.pipeline import CVAnalysisPipeline


# ==============================================================================
# 🎨 1. SETTING HALAMAN & CSS MODERN (BADGES)
# ==============================================================================
# st.set_page_config(): Mengatur parameter dasar tampilan halaman web Streamlit
# page_title: Judul tab browser
# page_icon: Emoji ikon tab browser
# layout: 'wide' untuk memanfaatkan seluruh lebar layar browser secara horizontal
st.set_page_config(
    page_title="CV Recommender System",
    page_icon="💼",
    layout="wide"
)

# st.markdown(): Menyisipkan kode CSS kustom ke dalam halaman HTML
# Kelas CSS .badge-met: Badge hijau muda untuk keahlian pelamar yang terpenuhi
# Kelas CSS .badge-gap: Badge merah muda untuk keahlian pelamar yang kurang (gap)
# unsafe_allow_html=True: Mengizinkan kompilasi HTML/CSS langsung di Streamlit
st.markdown("""
<style>
    .badge-met {
        display: inline-block;
        background-color: #d1e7dd;
        color: #0f5132;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 5px;
        margin: 2px;
    }
    .badge-gap {
        display: inline-block;
        background-color: #f8d7da;
        color: #842029;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 5px;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Daftar keahlian standar (fallback list) yang muncul di multiselect jika taksonomi gagal dimuat
DEFAULT_SKILLS = [
    "python", "sql", "java", "javascript", "typescript", "c++", "c#", "php", "r", "html", "css",
    "apache spark", "kafka", "airflow", "etl", "snowflake", "bigquery", "databricks",
    "postgresql", "mysql", "mongodb", "redis", "aws", "gcp", "azure",
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp",
    "pandas", "numpy", "tableau", "power bi", "excel", "data visualization",
    "docker", "kubernetes", "git", "linux", "ci/cd",
    "react", "node.js", "django", "fastapi", "rest api",
    "communication", "teamwork", "problem solving", "leadership"
]


# ==============================================================================
# 🧠 2. INISIALISASI PIPELINE MODEL AI (Sentence-BERT & FAISS)
# ==============================================================================
# Decorator @st.cache_resource: Memastikan model AI yang berat (300MB+)
# hanya di-load sekali ke dalam memori RAM saat server pertama kali dinyalakan.
# show_spinner: Menampilkan animasi memuat berkas di layar web secara dramatis.
@st.cache_resource(show_spinner="Memuat Model AI (Sentence-BERT & FAISS)...")
def get_pipeline():
    # Mengambil lokasi absolut path folder di mana berkas script ini berada
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Menggabungkan direktori berkas dengan nama subfolder 'models' untuk path artefak ML
    model_dir = os.path.join(base_dir, "models")
    # Instansiasi objek pipeline dengan memberikan model_dir dan nama model embedding
    return CVAnalysisPipeline(
        model_dir=model_dir,
        embedding_model_name=settings.EMBEDDING_MODEL
    )

# Memuat objek pipeline ke variabel global. Jika gagal (misal file model terhapus), stop web.
try:
    pipeline = get_pipeline()
    # Mengambil seluruh daftar key target peran pekerjaan yang didukung oleh model
    roles_options = list(pipeline.job_profiles.keys())
except Exception as e:
    st.error(f"Gagal memuat model machine learning: {e}")
    st.stop()

# Merapikan tampilan nama target peran (contoh: 'data_engineer' -> 'Data Engineer') menggunakan title()
role_labels = {r: r.replace("_", " ").title() for r in roles_options}


# ==============================================================================
# 🖥️ 3. TAMPILAN USER INTERFACE (SIDEBAR & PANEL UTAMA)
# ==============================================================================
# st.title(): Merender judul utama berukuran H1
st.title("💼 CV Intelligence & Job Matcher")
# st.markdown(): Menulis paragraf deskripsi
st.markdown("Analisis kecocokan CV Anda terhadap standar kompetensi industri dan temukan lowongan kerja relevan secara instan.")
# st.divider(): Merender garis pemisah horizontal
st.divider()

# --- SIDEBAR: Konfigurasi Analisis ---
st.sidebar.header("⚙️ Konfigurasi")
# st.sidebar.selectbox(): Membuat pilihan dropdown di panel samping
# format_func: Fungsi pemeta nama agar opsi yang tampil di layar lebih rapi
selected_role = st.sidebar.selectbox(
    "Pilih Target Jabatan:",
    options=roles_options,
    format_func=lambda x: role_labels.get(x, x)
)
# st.sidebar.slider(): Membuat slider pengatur jumlah rekomendasi lowongan kerja (K)
top_k_val = st.sidebar.slider(
    "Jumlah Rekomendasi Lowongan:",
    min_value=1,
    max_value=10,
    value=5
)

# --- PANEL UTAMA: Form Input Profil/CV ---
# st.container(border=True): Wadah dengan garis batas tipis yang rapi dan premium
with st.container(border=True):
    st.subheader("📋 Input Profil Kompetensi Anda")
    
    # st.radio(): Tombol pilihan eksklusif horizontal
    input_method = st.radio(
        "Pilih Cara Input:",
        options=["Unggah Berkas PDF CV", "Isi Profil Kompetensi Terstruktur"],
        horizontal=True
    )
    
    st.write("")
    
    # Inisialisasi variabel kosong untuk menampung teks isi CV
    cv_text = ""
    
    # Opsi A: Mengunggah berkas file PDF CV pelamar langsung
    if input_method == "Unggah Berkas PDF CV":
        # st.file_uploader(): Membuat kolom upload berkas khusus PDF
        uploaded_file = st.file_uploader("Unggah file PDF CV Anda:", type=["pdf"])
        if uploaded_file is not None:
            try:
                # Menggunakan pdfplumber.open() dengan data byte berkas dari memory buffer (BytesIO)
                with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                    # Mengekstrak seluruh teks per halaman menggunakan list comprehension
                    # page.extract_text(): Fungsi mengekstrak karakter teks dari lembaran PDF
                    pages_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
                # Menggabungkan baris teks halaman dengan pemisah baris baru (\n)
                cv_text = "\n".join(pages_text)
                st.success("Teks CV berhasil diekstrak dari berkas PDF!")
            except Exception as e:
                st.error(f"Gagal membaca berkas PDF: {e}")
                
    # Opsi B: Mengisi formulir profil manual terstruktur
    else:
        # st.columns(2): Membagi form menjadi 2 kolom vertikal yang seimbang
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            # st.number_input(): Kolom pengisian angka tahun pengalaman kerja
            exp_years = st.number_input("Pengalaman Kerja (Tahun):", min_value=0, max_value=45, value=2)
            # st.selectbox(): Kolom pilihan pendidikan terakhir
            education_val = st.selectbox("Pendidikan Terakhir:", ["D3 - Ahli Madya", "D4 / S1 - Sarjana", "S2 - Magister", "SMA / SMK"])
        with col_f2:
            # st.multiselect(): Kolom pilihan banyak skill dari daftar default
            selected_skills = st.multiselect("Pilih Keahlian Utama Anda:", options=sorted(DEFAULT_SKILLS), default=["python", "sql", "git"])
            # st.text_input(): Kolom teks deskripsi karir
            summary_text = st.text_input("Ringkasan Minat Karir (Opsional):", placeholder="Misal: Tertarik membangun data pipeline...")
            
        # Merangkai isian variabel form terstruktur menjadi teks deskriptif (pseudo-CV)
        cv_text = f"""
        Professional with {exp_years} years of experience.
        Education: {education_val}. Target Role: {selected_role}.
        Skills: {", ".join(selected_skills)}. {summary_text}
        """

    # st.button(): Membuat tombol utama eksekusi analisis kompetensi CV
    submit_button = st.button("Mulai Analisis CV", type="primary", use_container_width=True)


# ==============================================================================
# 📊 4. TAMPILAN OUTPUT HASIL ANALISIS (SIMPEL & ELEGAN)
# ==============================================================================
if submit_button:
    # Validasi: Memeriksa apakah teks CV kosong atau terlalu pendek (< 20 karakter)
    if not cv_text or len(cv_text.strip()) < 20:
        st.warning("Mohon masukkan informasi profil atau unggah berkas PDF CV terlebih dahulu.")
    else:
        # st.spinner(): Menampilkan efek animasi berputar saat model sedang memproses inferensi
        with st.spinner("Model AI sedang menganalisis kecocokan semantik & kecocokan skill..."):
            try:
                # Memanggil objek pipeline ML terintegrasi untuk menganalisis CV
                # Parameter cv_text: Teks CV yang akan dievaluasi
                # Parameter selected_role: Peran pekerjaan target pilihan
                # Parameter top_k_val: Jumlah lowongan rekomendasi yang dicari
                result = pipeline.analyze(cv_text, selected_role, top_k_val)
                
                st.success("Analisis selesai!")
                st.divider()
                
                # Menampilkan subheader hasil evaluasi untuk jabatan target
                st.subheader(f"📊 Hasil Evaluasi Kompetensi: {role_labels.get(selected_role)}")
                
                # --- A. RINGKASAN METRIK UTAMA (KPI) ---
                # Membagi panel atas hasil menjadi 3 kolom metrik ringkas
                col_m1, col_m2, col_m3 = st.columns(3)
                
                # Mengambil nilai skor kesiapan, level, emoji, dan rasio skill
                score = result.get("overall_readiness_score", 0)
                level = result.get("skill_assessment", {}).get("readiness_level")
                emoji = result.get("skill_assessment", {}).get("readiness_emoji", "⚪")
                total_met = len(result.get("skill_assessment", {}).get("met", []))
                total_gap = len(result.get("skill_assessment", {}).get("gap", []))
                
                # st.metric(): Merender visualisasi metrik angka/nilai secara bersih dan premium
                col_m1.metric(label="Skor Kesiapan Kerja", value=f"{score}%")
                col_m2.metric(label="Status Kesiapan", value=f"{emoji} {level}")
                col_m3.metric(label="Rasio Skill Terpenuhi", value=f"{total_met} / {total_met + total_gap}")
                
                st.write("")
                
                # --- B. GRAFIK KATEGORI & BADGE SKILL ---
                # Membagi kolom visualisasi kiri (grafik & badge) dan kanan (lowongan) dengan rasio seimbang
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.subheader("💡 Kesiapan Per Kategori Skill")
                    bd = result.get("skill_assessment", {}).get("breakdown", {})
                    categories_map = {
                        "core_skills": "Core Skills (Utama)",
                        "expected_skills": "Expected Skills (Penting)",
                        "nice_to_have": "Nice to Have (Tambahan)",
                        "soft_skills": "Soft Skills (Sosial)"
                    }
                    
                    # Merender progress bar bawaan Streamlit (st.progress) yang sangat ringan dan bersih
                    for key, label in categories_map.items():
                        if key in bd:
                            score_cat = bd[key]["score"]
                            # Tampilkan label dan skor
                            st.write(f"**{label}** : {score_cat}%")
                            # st.progress(): Menampilkan bilah kemajuan (skala 0.0 - 1.0)
                            st.progress(score_cat / 100.0)
                            
                    st.write("")
                    st.subheader("🛠️ Pemetaan Keahlian")
                    met_skills = result.get("skill_assessment", {}).get("met", [])
                    gap_skills = result.get("skill_assessment", {}).get("gap", [])
                    
                    # Merender badge skill hijau menggunakan CSS .badge-met kustom
                    st.write("**Keahlian yang Anda Miliki (Terdeteksi):**")
                    if met_skills:
                        st.markdown("".join([f'<span class="badge-met">{s}</span>' for s in met_skills]), unsafe_allow_html=True)
                    else:
                        st.caption("Tidak ada skill relevan terdeteksi.")
                        
                    st.write("")
                    # Merender badge skill merah menggunakan CSS .badge-gap kustom
                    st.write("**Keahlian yang Perlu Dipelajari (Gap):**")
                    if gap_skills:
                        st.markdown("".join([f'<span class="badge-gap">{s}</span>' for s in gap_skills]), unsafe_allow_html=True)
                    else:
                        st.caption("Hebat! Anda memenuhi semua standar skill industri.")
                
                # --- C. REKOMENDASI LOWONGAN PEKERJAAN ---
                with col_right:
                    st.subheader("💼 Rekomendasi Lowongan Kerja Relevan")
                    st.markdown("Berikut daftar lowongan kerja terdekat berdasarkan analisis semantik BERT & kemiripan skill:")
                    
                    jobs = result.get("recommended_jobs", [])
                    if jobs:
                        # Melakukan iterasi untuk setiap pekerjaan di dalam list jobs
                        for job in jobs:
                            match_pct = job.get("confidence_score", 0) * 100
                            
                            # st.container(border=True): Kartu pembatas informasi lowongan secara premium
                            with st.container(border=True):
                                col_title, col_match = st.columns([3, 1])
                                col_title.markdown(f"**Rank #{job.get('rank')} - {job.get('job_title')}**")
                                col_match.markdown(f"<span style='color:#198754; font-weight:bold;'>Match: {match_pct:.1f}%</span>", unsafe_allow_html=True)
                                
                                st.caption(f"🏢 {job.get('company_name')}  |  📍 {job.get('location')}")
                                st.markdown(f"_{job.get('reasoning')}_")
                    else:
                        st.info("Tidak ditemukan lowongan pekerjaan yang cocok.")
                        
                # --- D. RAW DATA JSON RESPONS ---
                # st.expander(): Wadah drop-down expander lipat untuk melihat detail data mentah JSON
                with st.expander("Lihat Data Mentah Model (JSON Response)"):
                    # st.json(): Merender struktur JSON secara cantik dan interaktif
                    st.json(result)
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {e}")


