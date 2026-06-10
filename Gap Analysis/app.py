# ==============================================================================
# 🖥️ DASHBOARD INTERAKTIF: Dashboard Analisis Kesenjangan Keahlian (Skill Gap Analysis)
# Berkas ini mendefinisikan antarmuka pengguna (user interface) menggunakan Streamlit,
# membaca data analisis gabungan, memfilter berdasarkan kategori, dan memvisualisasikan gap.
# ==============================================================================

# Mengimpor library 'streamlit' (sebagai st) untuk merancang dashboard web interaktif
import streamlit as st

# Mengimpor library 'pandas' (sebagai pd) untuk memanipulasi berkas CSV data tabel/DataFrame
import pandas as pd

# Mengimpor modul bawaan Python 'os' untuk berinteraksi dengan sistem berkas (path berkas)
import os


# ==============================================================================
# 🎨 1. KONFIGURASI HALAMAN & STYLE CSS
# ==============================================================================
# st.set_page_config(): Mengatur judul tab web browser, ikon emoji, dan memaksakan layout melebar (wide)
st.set_page_config(
    page_title="Skill Gap Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# st.markdown(): Menyisipkan gaya CSS kustom untuk memperindah metric card hasil gap tertinggi
# Kelas CSS .metric-card: Wadah kartu putih berbayang tipis dan border abu-abu terang
# Kelas CSS .metric-value: Menampilkan nama kompetensi/skill berukuran besar dan tebal berwarna biru
# Kelas CSS .metric-label: Menampilkan teks penunjuk peringkat keahlian
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0d6efd;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 📂 2. PEMUATAN DATASET (DATAFRAME)
# ==============================================================================
# Mendefinisikan jalur path fisik absolut file 'skill_gap_analysis.csv' secara otomatis
# os.path.dirname(): Mengambil direktori induk tempat berkas script ini berjalan (folder 'Gap Analysis')
# os.path.abspath(__file__): Mengambil alamat absolut berkas script aktif saat ini
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_gap_analysis.csv")

# Mengaktifkan decorator caching data Streamlit agar pembacaan CSV dari disk hanya dipicu
# jika file mengalami perubahan waktu modifikasi fisik di sistem operasi (mtime).
@st.cache_data
def load_data(file_path, mtime):
    # Memeriksa apakah file target CSV tersebut ada di penyimpanan disk
    if os.path.exists(file_path):
        # Membaca data CSV dan mengubahnya menjadi DataFrame Pandas
        df = pd.read_csv(file_path)
    else:
        # Menyusun DataFrame fallback/cadangan secara otomatis jika file data CSV belum terbentuk
        df = pd.DataFrame({
            'nama_skill': ['python', 'komunikasi', 'sql', 'kepemimpinan', 'machine learning'],
            'industry_norm': [0.4, 0.2, 0.35, 0.1, 0.5],
            'academic_norm': [0.1, 0.3, 0.2, 0.2, 0.05],
            'skill_gap_score': [0.3, -0.1, 0.15, -0.1, 0.45]
        })
    
    # Menambahkan kolom 'kategori' secara otomatis jika belum didefinisikan sebelumnya di dalam CSV
    if 'kategori' not in df.columns:
        # Kata kunci pencocokan untuk memilah Hard Skill dengan Soft Skill secara otomatis
        soft_skills_keywords = ['komunikasi', 'kepemimpinan', 'manajemen', 'kerja sama', 'analitis', 'problem solving', 'leadership', 'communication']
        
        # Fungsi pembantu internal untuk mengklasifikasi kategori nama skill
        def assign_category(skill):
            for ss in soft_skills_keywords:
                if isinstance(skill, str) and ss in skill.lower():
                    return 'Soft Skill'
            return 'Hard Skill'
        
        # Menerapkan klasifikasi menggunakan apply() pada kolom nama_skill
        df['kategori'] = df['nama_skill'].apply(assign_category)
        
    return df

# os.path.getmtime(): Mengambil waktu modifikasi fisik berkas dari OS untuk invalidasi cache otomatis
mtime = os.path.getmtime(DATA_PATH) if os.path.exists(DATA_PATH) else 0
# Memuat berkas data tabular ke variabel df
df = load_data(DATA_PATH, mtime)


# ==============================================================================
# 🔍 3. SIDEBAR FILTER DATA
# ==============================================================================
# st.sidebar: Menuliskan antarmuka masukan pada panel samping (sidebar)
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Pilih kategori skill yang ingin Anda evaluasi di grafik.")
# st.sidebar.multiselect(): Membuat kolom pilihan ganda dropdown dinamis
# options: Opsi pilihan unik dari kolom kategori di DataFrame
# default: Pilihan awal yang tercentang otomatis (seluruh kategori unik)
kategori_pilihan = st.sidebar.multiselect(
    "Pilih Kategori:",
    options=df['kategori'].unique(),
    default=df['kategori'].unique()
)

# Menyaring DataFrame berdasarkan pilihan kategori pengguna di sidebar
# isin(): Mencocokkan nilai baris kategori di DataFrame dengan list kategori_pilihan
if kategori_pilihan:
    df_filtered = df[df['kategori'].isin(kategori_pilihan)]
else:
    df_filtered = df


# ==============================================================================
# 🖥️ 4. HEADER UTAMA DASHBOARD
# ==============================================================================
# st.title(): Merender judul H1 besar di bagian atas panel utama
st.title("📊 Dashboard Analisis Kesenjangan Skill (Skill Gap)")
# st.markdown(): Paragraf pengantar alur kerja data untuk memandu penguji
st.markdown("""
Dashboard ini digunakan untuk membandingkan proporsi kemunculan suatu kompetensi keahlian antara **Kebutuhan Industri** (berdasarkan iklan lowongan kerja) dan **Kurikulum Akademik** (berdasarkan O*NET standard).
* **Skor Gap Positif (+)** menunjukkan keahlian tersebut sangat dicari di industri tetapi masih jarang diajarkan di institusi akademik (*under-represented*).
""")
st.divider()


# ==============================================================================
# 🏆 5. TOP 3 SKILL GAP (SCORECARD METRICS)
# ==============================================================================
st.subheader("🏆 Top 3 Kesenjangan Skill Gap Tertinggi")
st.markdown("Berikut adalah 3 skill utama yang mendesak untuk ditambahkan ke dalam materi pembelajaran/pelatihan:")

# Mengurutkan baris DataFrame berdasarkan kolom 'skill_gap_score' secara menurun (Descending)
# head(3): Mengambil 3 baris data teratas (peringkat 1-3 kesenjangan tertinggi)
top_3 = df_filtered.sort_values(by='skill_gap_score', ascending=False).head(3)

# Memeriksa apakah list data top_3 kosong
if not top_3.empty:
    # Membagi baris menjadi 3 kolom vertikal sejajar untuk meletakkan kartu nilai
    cols = st.columns(3)
    # Melakukan perulangan indeks numerik dan baris data top_3 menggunakan iterrows()
    for i, (idx, row) in enumerate(top_3.iterrows()):
        # Memformat nama skill menjadi huruf kapital di awal kata menggunakan title()
        skill_name = str(row['nama_skill']).title()
        score = row['skill_gap_score']
        
        # Menuliskan HTML kustom kartu nilai di kolom terkait (indeks i)
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Peringkat {i+1} (Kesenjangan Tertinggi)</div>
                <div class="metric-value">{skill_name}</div>
                <div style="color: {'#dc3545' if score > 0 else '#198754'}; font-weight: bold; margin-top: 5px;">
                    Skor Gap: +{score:.4f}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Pilih kategori di sidebar untuk menampilkan data.")

st.write("")
st.write("")


# ==============================================================================
# 📈 6. GRAFIK PERBANDINGAN (STREAMLIT NATIVE BAR CHART)
# ==============================================================================
st.subheader("📈 Grafik Perbandingan Proporsi: Industri vs Akademik")

# st.slider(): Slider pengatur jumlah skill (N) yang ditampilkan di grafik agar tidak terlalu rapat
n_skills = st.slider("Jumlah Kompetensi Keahlian untuk Ditampilkan:", min_value=5, max_value=50, value=15)

# Urutkan DataFrame dan ambil N baris teratas
df_chart = df_filtered.sort_values(by='skill_gap_score', ascending=False).head(n_skills)

# Memeriksa apakah data chart tidak kosong
if not df_chart.empty:
    # st.bar_chart() bawaan Streamlit membutuhkan index DataFrame sebagai sumbu X kategori,
    # dan kolom-kolom DataFrame sebagai sumbu Y nilai grup batang.
    # set_index(): Mengubah kolom 'nama_skill' menjadi indeks data
    df_chart_display = df_chart.set_index('nama_skill')[['industry_norm', 'academic_norm']].copy()
    # Mengubah nama kolom agar tampil cantik di label legenda grafik
    df_chart_display.columns = ['Proporsi Industri', 'Proporsi Akademik']
    
    # st.bar_chart(): Menggambar grafik batang berkelompok (grouped bar chart) interaktif,
    # responsif, dan menggunakan visualisasi berbasis pustaka Altair secara native.
    st.bar_chart(df_chart_display)
    
    # ==============================================================================
    # 📑 7. TABEL DATA MENTAH
    # ==============================================================================
    # st.expander(): Membuat wadah akordeon yang bisa dilipat/buka untuk menghemat tempat layar
    with st.expander("📄 Lihat Tabel Data Lengkap (Semua Baris)"):
        # Reset indeks data agar penomoran tabel dimulai dari angka 0
        df_table = df_filtered.sort_values(by='skill_gap_score', ascending=False).reset_index(drop=True)
        # Menentukan urutan daftar kolom yang ingin ditunjukkan
        columns_to_show = ['nama_skill', 'kategori', 'industry_norm', 'academic_norm', 'skill_gap_score']
        # st.dataframe(): Merender data tabel interaktif yang mendukung pencarian dan pengurutan kolom
        st.dataframe(df_table[columns_to_show], use_container_width=True)
else:
    st.warning("Mohon pilih minimal satu kategori di sidebar.")


