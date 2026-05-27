import pandas as pd
import os
import re

# Path folder datasets
DATASETS_DIR = r"d:\TUGAS\DataEngineer\datasets"

def standardize_skill_text(text):
    """
    Fungsi untuk membersihkan dan menstandardisasi nama skill.
    Mengubah teks menjadi huruf kecil dan menyamakan beberapa istilah.
    """
    if pd.isna(text):
        return text
    
    # Mengubah ke huruf kecil dan menghapus spasi berlebih
    text = str(text).lower().strip()
    
    # Kamus standardisasi istilah
    replacements = {
        r'\bjs\b': 'javascript',
        r'\bnode\.js\b': 'nodejs',
        r'\bnode js\b': 'nodejs',
        r'\bvue\.js\b': 'vuejs',
        r'\breact\.js\b': 'reactjs',
        r'\bml\b': 'machine learning',
        r'\bai\b': 'artificial intelligence',
        r'\bpython3\b': 'python',
        r'\baws\b': 'amazon web services'
    }
    
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
        
    return text

def calculate_skill_gap_score(merged_df, industry_col, academic_col):
    """
    Menghitung Skill Gap Score berdasarkan frekuensi skill di industri vs akademik.
    
    Parameters:
    merged_df (pd.DataFrame): DataFrame gabungan yang memuat frekuensi skill.
    industry_col (str): Nama kolom untuk frekuensi di dataset industri.
    academic_col (str): Nama kolom untuk frekuensi di dataset akademik.
    
    Returns:
    pd.DataFrame: DataFrame dengan kolom Skill Gap Score, diurutkan dari tertinggi ke terendah.
    """
    df_calc = merged_df[['nama_skill', industry_col, academic_col]].copy()
    
    # Mengisi NaN dengan 0
    df_calc[industry_col] = df_calc[industry_col].fillna(0)
    df_calc[academic_col] = df_calc[academic_col].fillna(0)
    
    # Menghitung probabilitas / proporsi (Normalisasi frekuensi)
    total_ind = df_calc[industry_col].sum()
    total_acad = df_calc[academic_col].sum()
    
    # Mencegah pembagian dengan nol
    total_ind = total_ind if total_ind > 0 else 1
    total_acad = total_acad if total_acad > 0 else 1
    
    df_calc['industry_norm'] = df_calc[industry_col] / total_ind
    df_calc['academic_norm'] = df_calc[academic_col] / total_acad
    
    # Menghitung Skill Gap Score
    # Score positif besar = sangat dicari industri, jarang diajarkan (kesenjangan tertinggi)
    df_calc['skill_gap_score'] = df_calc['industry_norm'] - df_calc['academic_norm']
    
    # Urutkan dari kesenjangan tertinggi ke terendah
    df_result = df_calc.sort_values(by='skill_gap_score', ascending=False).reset_index(drop=True)
    return df_result

def main():
    print(f"Mencari dataset di dalam folder: {DATASETS_DIR}")
    
    file_1 = os.path.join(DATASETS_DIR, 'adzuna_jobs.csv')
    file_2 = os.path.join(DATASETS_DIR, 'postings.csv')
    file_3 = os.path.join(DATASETS_DIR, 'db_30_2_excel', 'Technology Skills.xlsx')
    
    # 1. BACA DATASET
    try:
        df1 = pd.read_csv(file_1) if os.path.exists(file_1) else pd.DataFrame()
        df2 = pd.read_csv(file_2, low_memory=False) if os.path.exists(file_2) else pd.DataFrame()
        df3 = pd.read_excel(file_3) if os.path.exists(file_3) else pd.DataFrame()
        print("Berhasil membaca file dataset.")
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca file: {e}")
        return

    # 2. PEMBERSIHAN DATA DAN HITUNG FREKUENSI (AGREGASI)
    df1_freq = pd.DataFrame(columns=['nama_skill', 'freq_adzuna'])
    if not df1.empty and 'description' in df1.columns:
        df1['nama_skill'] = df1['description'].apply(standardize_skill_text)
        df1_freq = df1.groupby('nama_skill').size().reset_index(name='freq_adzuna')
        
    df2_freq = pd.DataFrame(columns=['nama_skill', 'freq_postings'])
    if not df2.empty and 'skills_desc' in df2.columns:
        df2['nama_skill'] = df2['skills_desc'].apply(standardize_skill_text)
        df2_freq = df2.groupby('nama_skill').size().reset_index(name='freq_postings')
        
    df3_freq = pd.DataFrame(columns=['nama_skill', 'freq_academic'])
    if not df3.empty:
        skill_col_df3 = 'Example' if 'Example' in df3.columns else df3.columns[0]
        df3['nama_skill'] = df3[skill_col_df3].apply(standardize_skill_text)
        df3_freq = df3.groupby('nama_skill').size().reset_index(name='freq_academic')

    print("Proses standardisasi teks dan agregasi frekuensi selesai.")

    # 3. GABUNGKAN KETIGA DATASET FREKUENSI
    # Melakukan merge outer agar data frekuensi dari berbagai dataset tergabung
    merged_df = pd.merge(df1_freq, df2_freq, on='nama_skill', how='outer')
    merged_df = pd.merge(merged_df, df3_freq, on='nama_skill', how='outer')
    
    # Mengisi NaN dengan 0 untuk frekuensi gabungan
    merged_df.fillna(0, inplace=True)
    
    # Asumsikan frekuensi industri adalah gabungan dari freq_adzuna dan freq_postings
    merged_df['freq_industry_total'] = merged_df['freq_adzuna'] + merged_df['freq_postings']
    
    print(f"Penggabungan berhasil. Total skill unik: {len(merged_df)}")
    
    # 4. HITUNG SKILL GAP SCORE
    # Kita menggunakan freq_industry_total sebagai data industri, dan freq_academic sebagai data akademik
    print("Menghitung Skill Gap Score...")
    df_gap = calculate_skill_gap_score(merged_df, industry_col='freq_industry_total', academic_col='freq_academic')
    
    print("\nTop 10 Skill dengan Kesenjangan Tertinggi (Tinggi di Industri, Rendah di Akademik):")
    print(df_gap.head(10))
    
    # 5. SIMPAN HASIL
    output_path = os.path.join(DATASETS_DIR, 'skill_gap_analysis.csv')
    df_gap.to_csv(output_path, index=False)
    print(f"\nDataset hasil analisis Skill Gap disimpan di {output_path}")

    return df_gap

if __name__ == "__main__":
    df_final = main()
