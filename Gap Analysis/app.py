import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Skill Gap Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan modern
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Path data
DATA_PATH = r"d:\TUGAS\DataEngineer\datasets\skill_gap_analysis.csv"

@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        # Data dummy jika file belum di-generate
        df = pd.DataFrame({
            'nama_skill': ['python', 'komunikasi', 'sql', 'kepemimpinan', 'machine learning'],
            'industry_norm': [0.4, 0.2, 0.35, 0.1, 0.5],
            'academic_norm': [0.1, 0.3, 0.2, 0.2, 0.05],
            'skill_gap_score': [0.3, -0.1, 0.15, -0.1, 0.45]
        })
    
    # Membuat kategori Hard Skill / Soft Skill jika belum ada
    if 'kategori' not in df.columns:
        soft_skills_keywords = ['komunikasi', 'kepemimpinan', 'manajemen', 'kerja sama', 'analitis', 'problem solving', 'leadership', 'communication']
        
        def assign_category(skill):
            for ss in soft_skills_keywords:
                if isinstance(skill, str) and ss in skill.lower():
                    return 'Soft Skill'
            return 'Hard Skill'
        
        df['kategori'] = df['nama_skill'].apply(assign_category)
        
    return df

df = load_data()

# ================= SIDEBAR =================
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Pilih kategori skill yang ingin dianalisis.")
kategori_pilihan = st.sidebar.multiselect(
    "Pilih Kategori:",
    options=df['kategori'].unique(),
    default=df['kategori'].unique()
)

# Filter dataframe berdasarkan pilihan di sidebar
if kategori_pilihan:
    df_filtered = df[df['kategori'].isin(kategori_pilihan)]
else:
    df_filtered = df

# ================= HEADER =================
st.title("📊 Dashboard Analisis Skill Gap")
st.markdown("""
Dashboard ini dirancang untuk membandingkan porsi kemunculan sebuah skill antara **Kebutuhan Industri** dan **Kurikulum Akademik**. 
Tujuannya adalah menemukan *Skill Gap* (kesenjangan), di mana skill tertentu mungkin sangat banyak dicari di industri, namun masih kurang terwakili di kurikulum pendidikan.
""")
st.divider()

# ================= METRIC SCORECARD =================
st.subheader("🏆 Top 3 Skill dengan Gap Tertinggi")
st.markdown("Skill di bawah ini adalah yang paling dibutuhkan industri namun jarang diajarkan/muncul pada data akademik.")

# Mengambil top 3
top_3 = df_filtered.sort_values(by='skill_gap_score', ascending=False).head(3)

if not top_3.empty:
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3.iterrows()):
        skill_name = str(row['nama_skill']).title()
        score = row['skill_gap_score']
        
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Peringkat {i+1}</div>
                <div class="metric-value">{skill_name}</div>
                <div style="color: {'green' if score > 0 else 'red'}; font-weight: 500;">
                    Gap Score: {score:.4f}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Tidak ada data untuk ditampilkan.")

st.write("")
st.write("")

# ================= HORIZONTAL BAR CHART =================
st.subheader("📈 Perbandingan Akademik vs Industri")

# Ambil top N untuk divisualisasikan agar chart tidak terlalu penuh
n_skills = st.slider("Jumlah skill untuk ditampilkan pada chart", min_value=5, max_value=50, value=15)
df_chart = df_filtered.sort_values(by='skill_gap_score', ascending=False).head(n_skills)

if not df_chart.empty:
    # Menggabungkan data Industri dan Akademik ke format panjang (long format) sambil membawa kolom jumlah asli
    # Amankan kolom frekuensi jika tidak ada
    if 'freq_industry_total' not in df_chart.columns:
        df_chart['freq_industry_total'] = 0
    if 'freq_academic' not in df_chart.columns:
        df_chart['freq_academic'] = 0

    df_ind = df_chart[['nama_skill', 'industry_norm', 'freq_industry_total']].copy()
    df_ind.rename(columns={'industry_norm': 'Proporsi', 'freq_industry_total': 'Frekuensi Asli'}, inplace=True)
    df_ind['Sumber'] = 'Industri'
    df_ind['Asal Dataset'] = 'adzuna_jobs & postings'
    
    df_acad = df_chart[['nama_skill', 'academic_norm', 'freq_academic']].copy()
    df_acad.rename(columns={'academic_norm': 'Proporsi', 'freq_academic': 'Frekuensi Asli'}, inplace=True)
    df_acad['Sumber'] = 'Akademik'
    df_acad['Asal Dataset'] = 'Technology Skills (O*NET)'
    
    df_melted = pd.concat([df_ind, df_acad], ignore_index=True)

    fig = px.bar(
        df_melted, 
        y='nama_skill', 
        x='Proporsi', 
        color='Sumber',
        barmode='group',
        orientation='h',
        hover_data={'Frekuensi Asli': True, 'Asal Dataset': True, 'Sumber': False},
        color_discrete_sequence=['#1f77b4', '#ff7f0e'],
        title=f"Perbandingan Proporsi {n_skills} Skill (Diurutkan berdasarkan Gap)",
        labels={'nama_skill': 'Nama Skill', 'Proporsi': 'Persentase Relatif'}
    )
    
    # Modifikasi hover template untuk lebih rapi
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Proporsi: %{x:.4f}<br>Frekuensi Asli: %{customdata[0]:,}<br>Dataset Asal: %{customdata[1]}<extra></extra>"
    )
    
    # Mengurutkan dari atas ke bawah berdasarkan data awal
    fig.update_layout(yaxis={'categoryorder':'array', 'categoryarray': df_chart['nama_skill'][::-1]})
    
    st.plotly_chart(fig, use_container_width=True)

    # Menampilkan tabel data mentah
    with st.expander("Tampilkan Data Tabel"):
        st.dataframe(df_filtered.sort_values(by='skill_gap_score', ascending=False).reset_index(drop=True), use_container_width=True)
else:
    st.warning("Silakan pilih minimal satu kategori dari sidebar.")
