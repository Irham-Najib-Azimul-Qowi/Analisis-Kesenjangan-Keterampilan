# ==============================================================================
# NAMA FILE: app.py
# FUNGSI FILE: Dashboard Streamlit untuk menampilkan hasil analisis kesenjangan
#              keterampilan (Skill Gap). Membaca data dari skill_gap_analysis.csv
#              yang dihasilkan oleh analysis.ipynb.
# ==============================================================================

# Mengimpor library 'streamlit' untuk membuat dashboard web interaktif
import streamlit as st

# Mengimpor library 'pandas' untuk membaca dan memanipulasi data CSV
import pandas as pd

# Mengimpor modul 'os' untuk memanipulasi path file
import os


# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="Skill Gap Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Dashboard Analisis Kesenjangan Skill (Skill Gap)")
st.markdown("""
Dashboard ini membandingkan proporsi kemunculan suatu keahlian antara **Kebutuhan Industri**
(berdasarkan lowongan kerja Adzuna) dan **Kurikulum Akademik** (berdasarkan standar O*NET).
* **Skor Gap Positif (+)** menunjukkan skill yang sangat dicari industri tetapi jarang diajarkan.
""")
st.divider()


# ==============================================================================
# 2. BACA DATA
# ==============================================================================
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_gap_analysis.csv")


@st.cache_data
def baca_data(file_path, mtime):
    """
    Membaca file hasil analisis skill gap dari CSV.

    Parameter:
        file_path (str) -- path lengkap ke file skill_gap_analysis.csv
        mtime (float) -- waktu modifikasi file, digunakan untuk invalidasi cache

    Return:
        DataFrame -- data hasil analisis skill gap
    """
    if not os.path.exists(file_path):
        # Jika file belum ada, tampilkan pesan error dan hentikan dashboard
        st.error("File skill_gap_analysis.csv belum ada — jalankan analysis.ipynb terlebih dahulu.")
        st.stop()

    return pd.read_csv(file_path)


# Baca data dengan cache berdasarkan waktu modifikasi file
mtime = os.path.getmtime(DATA_PATH) if os.path.exists(DATA_PATH) else 0
df = baca_data(DATA_PATH, mtime)


# ==============================================================================
# 3. SIDEBAR FILTER
# ==============================================================================
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Pilih kategori skill yang ingin ditampilkan di grafik.")

kategori_pilihan = st.sidebar.multiselect(
    "Pilih Kategori:",
    options=df["kategori"].unique(),
    default=df["kategori"].unique(),
)

# Filter DataFrame berdasarkan pilihan pengguna
if kategori_pilihan:
    df_filtered = df[df["kategori"].isin(kategori_pilihan)]
else:
    df_filtered = df


# ==============================================================================
# 4. TOP 3 SKILL GAP TERTINGGI
# ==============================================================================
st.subheader("🏆 Top 3 Kesenjangan Skill Gap Tertinggi")
st.markdown("Skill yang paling mendesak untuk ditambahkan ke materi pembelajaran:")

# Ambil 3 skill dengan skor gap tertinggi
top_3 = df_filtered.sort_values(by="skill_gap_score", ascending=False).head(3)

if not top_3.empty:
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            # st.metric() menampilkan angka besar yang jelas dan rapi
            st.metric(
                label=f"Peringkat {i + 1}",
                value=str(row["nama_skill"]).title(),
                delta=f"Gap: +{row['skill_gap_score']:.4f}",
            )
else:
    st.info("Pilih kategori di sidebar untuk menampilkan data.")

st.write("")


# ==============================================================================
# 5. GRAFIK PERBANDINGAN INDUSTRI vs AKADEMIK
# ==============================================================================
st.subheader("📈 Grafik Perbandingan: Industri vs Akademik")

n_skills = st.slider("Jumlah skill yang ditampilkan:", min_value=5, max_value=50, value=15)

df_chart = df_filtered.sort_values(by="skill_gap_score", ascending=False).head(n_skills)

if not df_chart.empty:
    # Siapkan data untuk grafik batang Streamlit
    df_chart_display = df_chart.set_index("nama_skill")[["industry_norm", "academic_norm"]].copy()
    df_chart_display.columns = ["Proporsi Industri", "Proporsi Akademik"]
    st.bar_chart(df_chart_display)

    # ==============================================================================
    # 6. TABEL DATA LENGKAP
    # ==============================================================================
    with st.expander("📄 Lihat Tabel Data Lengkap"):
        df_table = df_filtered.sort_values(by="skill_gap_score", ascending=False).reset_index(drop=True)
        kolom_tampil = ["nama_skill", "kategori", "industry_norm", "academic_norm", "skill_gap_score"]
        kolom_tersedia = [k for k in kolom_tampil if k in df_table.columns]
        st.dataframe(df_table[kolom_tersedia], use_container_width=True)
else:
    st.warning("Pilih minimal satu kategori di sidebar.")
