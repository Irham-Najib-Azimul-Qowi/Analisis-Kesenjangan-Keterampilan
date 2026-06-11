# ==============================================================================
# NAMA FILE: streamlit_app.py
# FUNGSI FILE: Antarmuka pengguna (dashboard) Streamlit untuk mengevaluasi CV
#              pelamar kerja dan menampilkan rekomendasi lowongan kerja serta
#              skor kesiapan kompetensi. Memanggil model_utils.py untuk logika AI.
# ==============================================================================

# Mengimpor library 'streamlit' untuk membuat dashboard web interaktif
import streamlit as st

# Mengimpor modul 'os' untuk memanipulasi path file
import os

# Mengimpor modul 'io' untuk mengelola data file di memori (BytesIO)
import io

# Mengimpor library 'pdfplumber' untuk mengekstrak teks dari file PDF CV
import pdfplumber

# Mengimpor fungsi-fungsi logika inti dari file model_utils.py
from model_utils import muat_model_dan_data, analisis_cv


# ==============================================================================
# 1. MUAT MODEL AI (hanya sekali saat server pertama kali dijalankan)
# ==============================================================================
# @st.cache_resource memastikan model berat (~300MB) hanya dimuat sekali ke RAM
@st.cache_resource(show_spinner="Memuat Model AI (Sentence-BERT & FAISS)...")
def load_model():
    """
    Memuat seluruh artefak model dari folder 'models/'.

    Return:
        dict -- hasil dari muat_model_dan_data() berisi model, index, metadata
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "models")
    return muat_model_dan_data(model_dir)


# Memuat model — jika gagal (misal file model terhapus), hentikan aplikasi
try:
    data_model = load_model()
    # Ambil daftar peran jabatan yang tersedia dari profil
    daftar_role = list(data_model["profil_jabatan"].keys())
except Exception as e:
    st.error(f"Gagal memuat model: {e}")
    st.stop()


# ==============================================================================
# 2. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(page_title="CV Recommender System", page_icon="💼", layout="wide")
st.title("💼 CV Intelligence & Job Matcher")
st.markdown("Analisis kecocokan CV Anda terhadap standar kompetensi industri dan temukan lowongan kerja relevan.")
st.divider()


# ==============================================================================
# 3. SIDEBAR — Pilih target jabatan dan jumlah rekomendasi
# ==============================================================================
st.sidebar.header("⚙️ Konfigurasi")

# Merapikan nama role: 'data_engineer' → 'Data Engineer'
label_role = {r: r.replace("_", " ").title() for r in daftar_role}

target_role = st.sidebar.selectbox(
    "Pilih Target Jabatan:",
    options=daftar_role,
    format_func=lambda x: label_role.get(x, x),
)

top_k = st.sidebar.slider("Jumlah Rekomendasi Lowongan:", min_value=1, max_value=10, value=5)


# ==============================================================================
# 4. INPUT CV — Upload PDF atau tempel teks manual
# ==============================================================================
with st.container(border=True):
    st.subheader("📋 Input CV Anda")

    uploaded_file = st.file_uploader("Unggah file PDF CV Anda:", type=["pdf"])

    cv_text = ""
    if uploaded_file is not None:
        try:
            # Membaca byte file PDF dari memori menggunakan BytesIO
            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                # Ekstrak teks dari setiap halaman PDF
                halaman = [page.extract_text() for page in pdf.pages if page.extract_text()]
            cv_text = "\n".join(halaman)
            st.success("Teks CV berhasil diekstrak dari PDF!")
        except Exception as e:
            st.error(f"Gagal membaca PDF: {e}")

    # Alternatif: tempel teks CV secara manual
    cv_text = st.text_area(
        "Atau tempel teks CV Anda di sini:",
        value=cv_text,
        height=150,
        placeholder="Salin dan tempel isi CV Anda ke sini jika tidak punya file PDF...",
    )

    tombol_analisis = st.button("🔍 Mulai Analisis CV", type="primary", use_container_width=True)


# ==============================================================================
# 5. TAMPILKAN HASIL ANALISIS
# ==============================================================================
if tombol_analisis:
    # Validasi input tidak kosong
    if not cv_text or len(cv_text.strip()) < 20:
        st.warning("Mohon masukkan CV yang lebih lengkap (minimal 20 karakter).")
    else:
        with st.spinner("Model AI sedang menganalisis CV Anda..."):
            try:
                hasil = analisis_cv(cv_text, target_role, data_model, top_k)

                st.success("Analisis selesai!")
                st.divider()

                kesiapan = hasil["skor_kesiapan"]

                # --- A. METRIK UTAMA (3 kolom) ---
                st.subheader(f"📊 Hasil Evaluasi: {label_role.get(target_role)}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Skor Kesiapan Kerja", f"{kesiapan['overall_readiness_score']}%")
                col2.metric("Status Kesiapan", f"{kesiapan['readiness_emoji']} {kesiapan['readiness_level']}")
                col3.metric("Rasio Skill Terpenuhi", f"{len(kesiapan['met'])} / {len(kesiapan['met']) + len(kesiapan['gap'])}")

                st.write("")

                # --- B. KESIAPAN PER KATEGORI + PEMETAAN SKILL ---
                col_kiri, col_kanan = st.columns([1, 1])

                with col_kiri:
                    st.subheader("💡 Kesiapan Per Kategori Skill")
                    nama_kategori = {
                        "core_skills": "Core Skills (Utama)",
                        "expected_skills": "Expected Skills (Penting)",
                        "nice_to_have": "Nice to Have (Tambahan)",
                        "soft_skills": "Soft Skills (Sosial)",
                    }
                    for key, label in nama_kategori.items():
                        if key in kesiapan["breakdown"]:
                            skor = kesiapan["breakdown"][key]["score"]
                            st.write(f"**{label}** : {skor}%")
                            # st.progress() menampilkan bilah kemajuan (skala 0.0 - 1.0)
                            st.progress(skor / 100.0)

                    st.write("")
                    st.subheader("🛠️ Pemetaan Keahlian")

                    # Tampilkan skill yang dimiliki dengan emoji ✅
                    st.write("**Keahlian yang Anda Miliki:**")
                    if kesiapan["met"]:
                        st.write("  ".join([f"✅ {s}" for s in kesiapan["met"]]))
                    else:
                        st.caption("Tidak ada skill relevan terdeteksi.")

                    st.write("")
                    # Tampilkan skill yang kurang dengan emoji ❌
                    st.write("**Keahlian yang Perlu Dipelajari:**")
                    if kesiapan["gap"]:
                        st.write("  ".join([f"❌ {s}" for s in kesiapan["gap"]]))
                    else:
                        st.caption("Hebat! Anda memenuhi semua standar skill industri.")

                # --- C. REKOMENDASI LOWONGAN KERJA ---
                with col_kanan:
                    st.subheader("💼 Rekomendasi Lowongan Kerja")
                    lowongan = hasil["lowongan_rekomendasi"]

                    if lowongan:
                        for job in lowongan:
                            # Setiap lowongan ditampilkan dalam expander yang bisa dibuka/tutup
                            skor_persen = job["confidence_score"] * 100
                            judul = f"#{job['rank']} — {job['job_title']} ({skor_persen:.1f}%)"

                            with st.expander(judul):
                                st.write(f"🏢 **Perusahaan:** {job['company_name']}")
                                st.write(f"📍 **Lokasi:** {job['location']}")
                                st.write(f"📝 {job['reasoning']}")

                                if job["matched_skills"]:
                                    st.write("✅ **Skill cocok:** " + ", ".join(job["matched_skills"]))
                                if job["missing_skills"]:
                                    st.write("❌ **Skill kurang:** " + ", ".join(job["missing_skills"]))
                    else:
                        st.info("Tidak ditemukan lowongan yang cocok.")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses: {e}")
