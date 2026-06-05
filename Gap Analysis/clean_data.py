import pandas as pd
import os
import re

# Path folder datasets
DATASETS_DIR = os.path.dirname(os.path.abspath(__file__))


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
    cols_to_keep = ['nama_skill', industry_col, academic_col]
    if 'kategori' in merged_df.columns:
        cols_to_keep.append('kategori')
        
    df_calc = merged_df[cols_to_keep].copy()
    
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
    file_4 = os.path.join(DATASETS_DIR, 'db_30_2_excel', 'Skills.xlsx')
    
    # 1. BACA DATASET
    try:
        df1 = pd.read_csv(file_1) if os.path.exists(file_1) else pd.DataFrame()
        df2 = pd.read_csv(file_2, low_memory=False) if os.path.exists(file_2) else pd.DataFrame()
        df3 = pd.read_excel(file_3) if os.path.exists(file_3) else pd.DataFrame()
        df4 = pd.read_excel(file_4) if os.path.exists(file_4) else pd.DataFrame()
        print("Berhasil membaca file dataset.")
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca file: {e}")
        return

    # 2. PEMBERSIHAN DATA DAN HITUNG FREKUENSI (AGREGASI)
    
    # 2a. Hitung frekuensi untuk dataset akademik (O*NET)
    
    # 2a.1. Kategori Teknologi (Semua Hard Skill)
    df3_freq = pd.DataFrame(columns=['nama_skill', 'freq_academic', 'kategori'])
    if not df3.empty:
        skill_col_df3 = 'Example' if 'Example' in df3.columns else df3.columns[0]
        df3['nama_skill'] = df3[skill_col_df3].apply(standardize_skill_text)
        df3_freq = df3.groupby('nama_skill').size().reset_index(name='freq_academic')
        df3_freq['kategori'] = 'Hard Skill'
        
    # 2a.2. Keterampilan Dasar/Core (Klasifikasikan ke Soft/Hard)
    df4_freq = pd.DataFrame(columns=['nama_skill', 'freq_academic', 'kategori'])
    if not df4.empty:
        df4['nama_skill'] = df4['Element Name'].apply(standardize_skill_text)
        df4_freq = df4.groupby('nama_skill').size().reset_index(name='freq_academic')
        
        # Daftar soft skill asli dari 35 core skill O*NET
        soft_skills_list = {
            'active listening', 'writing', 'speaking', 'social perceptiveness', 'coordination', 
            'persuasion', 'negotiation', 'instructing', 'service orientation', 'complex problem solving', 
            'critical thinking', 'active learning', 'learning strategies', 'monitoring', 
            'judgment and decision making', 'time management', 'management of personnel resources',
            'management of financial resources', 'management of material resources'
        }
        
        def assign_core_category(skill):
            if skill in soft_skills_list:
                return 'Soft Skill'
            return 'Hard Skill'
            
        df4_freq['kategori'] = df4_freq['nama_skill'].apply(assign_core_category)
        
    # Gabungkan data akademik Teknologi dan Core
    academic_combined = pd.concat([df3_freq, df4_freq], ignore_index=True)
    
    # Kelompokkan berdasarkan nama_skill untuk menggabungkan duplikat jika ada
    def merge_categories(cats):
        if 'Soft Skill' in list(cats):
            return 'Soft Skill'
        return 'Hard Skill'
        
    df3_freq_combined = academic_combined.groupby('nama_skill').agg({
        'freq_academic': 'sum',
        'kategori': merge_categories
    }).reset_index()
    
    # Ambil semua skill unik yang terdaftar di akademik sebagai referensi standar
    academic_skills = df3_freq_combined['nama_skill'].dropna().unique()
    
    # Kategori skill untuk pencarian cepat
    single_word_skills = set()
    special_skills = []
    
    for skill in academic_skills:
        if not skill:
            continue
        if re.match(r'^[a-z0-9]+$', skill):
            single_word_skills.add(skill)
        else:
            # Cari kata pembentuk skill untuk optimasi subset check
            skill_words = set(re.findall(r'\b[a-z0-9]+\b', skill))
            pattern = rf"\b{re.escape(skill)}\b"
            special_skills.append((skill, re.compile(pattern), skill_words))
            
    # 2b. Hitung frekuensi kemunculan skill akademik di adzuna_jobs (Industri 1)
    counts_adzuna = {skill: 0 for skill in academic_skills}
    if not df1.empty and 'description' in df1.columns:
        desc_adzuna = df1['description'].dropna().astype(str).tolist()
        for desc in desc_adzuna:
            desc_lower = desc.lower()
            words_in_desc = set(re.findall(r'\b[a-z0-9]+\b', desc_lower))
            
            # Match single word skills
            for skill in single_word_skills.intersection(words_in_desc):
                counts_adzuna[skill] += 1
                
            # Match special/multi-word skills
            for skill, rx, skill_words in special_skills:
                if skill_words and not skill_words.issubset(words_in_desc):
                    continue
                if rx.search(desc_lower):
                    counts_adzuna[skill] += 1
                    
    df1_freq = pd.DataFrame({
        'nama_skill': list(counts_adzuna.keys()),
        'freq_adzuna': list(counts_adzuna.values())
    })
    
    # 2c. Hitung frekuensi kemunculan skill akademik di postings (Industri 2)
    counts_postings = {skill: 0 for skill in academic_skills}
    if not df2.empty and 'skills_desc' in df2.columns:
        desc_postings = df2['skills_desc'].dropna().astype(str).tolist()
        for desc in desc_postings:
            desc_lower = desc.lower()
            words_in_desc = set(re.findall(r'\b[a-z0-9]+\b', desc_lower))
            
            # Match single word skills
            for skill in single_word_skills.intersection(words_in_desc):
                counts_postings[skill] += 1
                
            # Match special/multi-word skills
            for skill, rx, skill_words in special_skills:
                if skill_words and not skill_words.issubset(words_in_desc):
                    continue
                if rx.search(desc_lower):
                    counts_postings[skill] += 1
                    
    df2_freq = pd.DataFrame({
        'nama_skill': list(counts_postings.keys()),
        'freq_postings': list(counts_postings.values())
    })

    print("Proses standardisasi teks dan agregasi frekuensi selesai.")

    # 3. GABUNGKAN KETIGA DATASET FREKUENSI
    # Melakukan merge outer agar data frekuensi dari berbagai dataset tergabung
    merged_df = pd.merge(df1_freq, df2_freq, on='nama_skill', how='outer')
    merged_df = pd.merge(merged_df, df3_freq_combined, on='nama_skill', how='outer')
    
    # Mengisi NaN dengan 0 untuk frekuensi gabungan
    merged_df['freq_adzuna'] = merged_df['freq_adzuna'].fillna(0)
    merged_df['freq_postings'] = merged_df['freq_postings'].fillna(0)
    merged_df['freq_academic'] = merged_df['freq_academic'].fillna(0)
    
    # Asumsikan frekuensi industri adalah gabungan dari freq_adzuna dan freq_postings
    merged_df['freq_industry_total'] = merged_df['freq_adzuna'] + merged_df['freq_postings']
    
    # Mengisi kategori yang hilang dengan "Hard Skill"
    merged_df['kategori'] = merged_df['kategori'].fillna('Hard Skill')
    
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
