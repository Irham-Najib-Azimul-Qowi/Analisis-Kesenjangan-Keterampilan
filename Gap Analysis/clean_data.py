# ==============================================================================
# PROSES UTAMA: Modul Pembersihan Data dan Analisis Kesenjangan Keterampilan 
# (Skill Gap Analysis) untuk mengidentifikasi gap antara kebutuhan industri dan akademik.
# ==============================================================================

# Mengimpor library 'pandas' (sebagai pd) untuk analisis data dan manipulasi tabel DataFrame
import pandas as pd

# Mengimpor modul bawaan Python 'os' untuk interaksi dengan sistem operasi (seperti path file)
import os

# Mengimpor modul bawaan 're' untuk pemrosesan teks menggunakan Regular Expression (Regex)
import re

# Mendefinisikan lokasi direktori tempat file script ini berada secara absolut
# Parameter pertama dari abspath: Path relatif file (__file__ = file saat ini) untuk dijadikan path absolut
# Parameter pertama dari dirname: Path absolut file, untuk diambil direktori induknya (folder 'Gap Analysis')
DATASETS_DIR = os.path.dirname(os.path.abspath(__file__))


# ==============================================================================
# FUNGSI: standardize_skill_text
# Penjelasan: Fungsi ini digunakan untuk membersihkan teks nama skill, mengubah 
# menjadi huruf kecil, menghapus spasi liar, dan menstandardisasi singkatan istilah teknologi.
# ==============================================================================
# Parameter text: String berisi nama skill yang akan dibersihkan dan distandardisasi
def standardize_skill_text(text):
    # Memeriksa apakah nilai parameter 'text' bernilai kosong (NaN) menggunakan pd.isna()
    # Parameter pertama dari pd.isna: Nilai atau objek yang diperiksa (mengembalikan True jika kosong)
    if pd.isna(text):
        return text
    
    # Mengonversi parameter ke tipe data string, mengubah huruf kecil (lower), dan menghapus spasi awal/akhir (strip)
    text = str(text).lower().strip()
    
    # Kamus pemetaan Regex untuk menstandardisasi singkatan istilah teknologi terpopuler
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
    
    # Melakukan penggantian istilah berdasarkan kamus replacements
    for pattern, repl in replacements.items():
        # Parameter pertama dari re.sub: Pola regular expression (pattern) yang akan dicari
        # Parameter kedua: Istilah pengganti (repl) jika pola tersebut ditemukan
        # Parameter ketiga: Teks sumber (text) tempat pencarian dan penggantian dilakukan
        text = re.sub(pattern, repl, text)
        
    return text


# ==============================================================================
# FUNGSI: calculate_skill_gap_score
# Penjelasan: Fungsi ini digunakan untuk menghitung Skill Gap Score berdasarkan 
# proporsi frekuensi kemunculan skill di dataset industri vs kurikulum akademik.
# ==============================================================================
# Parameter merged_df: DataFrame pandas gabungan frekuensi skill dari industri dan akademik
# Parameter industry_col: Nama kolom string frekuensi total dari dataset industri
# Parameter academic_col: Nama kolom string frekuensi dari dataset akademik
def calculate_skill_gap_score(merged_df, industry_col, academic_col):
    cols_to_keep = ['nama_skill', industry_col, academic_col]
    if 'kategori' in merged_df.columns:
        cols_to_keep.append('kategori')
        
    # Menduplikasi kolom terpilih dari DataFrame masukan menggunakan copy() untuk menghindari SettingWithCopyWarning
    df_calc = merged_df[cols_to_keep].copy()
    
    # Mengisi nilai kosong (NaN) dengan angka 0 pada kolom frekuensi industri menggunakan fillna()
    # Parameter pertama dari fillna: Nilai pengganti untuk data kosong (0)
    df_calc[industry_col] = df_calc[industry_col].fillna(0)
    # Mengisi nilai kosong (NaN) dengan angka 0 pada kolom frekuensi akademik
    df_calc[academic_col] = df_calc[academic_col].fillna(0)
    
    # Menghitung probabilitas/proporsi (Normalisasi frekuensi)
    # Menjumlahkan total frekuensi kolom industri menggunakan sum()
    total_ind = df_calc[industry_col].sum()
    # Menjumlahkan total frekuensi kolom akademik menggunakan sum()
    total_acad = df_calc[academic_col].sum()
    
    # Mencegah pembagian dengan nilai nol (ZeroDivisionError)
    total_ind = total_ind if total_ind > 0 else 1
    total_acad = total_acad if total_acad > 0 else 1
    
    # Menghitung proporsi relatif industri
    df_calc['industry_norm'] = df_calc[industry_col] / total_ind
    # Menghitung proporsi relatif akademik
    df_calc['academic_norm'] = df_calc[academic_col] / total_acad
    
    # Menghitung Skill Gap Score
    # Score positif besar = sangat dicari industri, jarang diajarkan (kesenjangan tertinggi)
    df_calc['skill_gap_score'] = df_calc['industry_norm'] - df_calc['academic_norm']
    
    # Urutkan dari kesenjangan tertinggi ke terendah
    # Parameter by: Kolom utama acuan pengurutan ('skill_gap_score')
    # Parameter ascending: Arah pengurutan (False = terbesar ke terkecil)
    df_result = df_calc.sort_values(by='skill_gap_score', ascending=False).reset_index(drop=True)
    # Parameter drop dari reset_index: Menghapus index kolom lama agar tidak disimpan sebagai kolom baru (True)
    
    return df_result


# ==============================================================================
# FUNGSI UTAMA: main
# Penjelasan: Fungsi sentral yang mengontrol alur proses ETL lokal: pembacaan 
# data mentah, pembersihan, agregasi frekuensi skill, penggabungan dataset, 
# perhitungan skor gap, dan ekspor CSV akhir.
# ==============================================================================
def main():
    print(f"Mencari dataset di dalam folder: {DATASETS_DIR}")
    
    # Menggabungkan direktori dataset dengan nama file CSV/Excel masing-masing
    # Parameter pertama dari os.path.join: Direktori dasar (DATASETS_DIR)
    # Parameter kedua/ketiga: Nama subdirektori dan file tujuan yang digabungkan
    file_1 = os.path.join(DATASETS_DIR, 'adzuna_jobs.csv')
    file_2 = os.path.join(DATASETS_DIR, 'postings.csv')
    file_3 = os.path.join(DATASETS_DIR, 'db_30_2_excel', 'Technology Skills.xlsx')
    file_4 = os.path.join(DATASETS_DIR, 'db_30_2_excel', 'Skills.xlsx')
    
    # 1. BACA DATASET
    try:
        # Membaca data jika file ada di sistem lokal menggunakan os.path.exists()
        # Parameter os.path.exists: Path file yang akan diperiksa keberadaannya
        df1 = pd.read_csv(file_1) if os.path.exists(file_1) else pd.DataFrame()
        # Parameter low_memory: Menonaktifkan pembacaan memori bertahap untuk data besar agar tipe kolom akurat (False)
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
    # Mendefinisikan DataFrame kosong df3_freq dengan nama kolom acuan
    # Parameter columns: List nama kolom awal DataFrame
    df3_freq = pd.DataFrame(columns=['nama_skill', 'freq_academic', 'kategori'])
    if not df3.empty:
        # Menentukan nama kolom target untuk skill di df3
        skill_col_df3 = 'Example' if 'Example' in df3.columns else df3.columns[0]
        # Menerapkan fungsi standardisasi teks pada kolom skill akademik
        # Parameter apply: Objek fungsi 'standardize_skill_text' yang diaplikasikan ke setiap baris
        df3['nama_skill'] = df3[skill_col_df3].apply(standardize_skill_text)
        
        # Agregasi jumlah kemunculan per skill akademik teknologi
        # Parameter groupby: Kolom kunci pengelompokan ('nama_skill')
        # Parameter name dari size(): Nama kolom baru hasil perhitungan frekuensi ('freq_academic')
        df3_freq = df3.groupby('nama_skill').size().reset_index(name='freq_academic')
        df3_freq['kategori'] = 'Hard Skill'
        
    # 2a.2. Keterampilan Dasar/Core (Klasifikasikan ke Soft/Hard)
    df4_freq = pd.DataFrame(columns=['nama_skill', 'freq_academic', 'kategori'])
    if not df4.empty:
        # Standardisasi kolom nama skill 'Element Name' di df4
        df4['nama_skill'] = df4['Element Name'].apply(standardize_skill_text)
        # Agregasi jumlah kemunculan per skill dasar O*NET
        df4_freq = df4.groupby('nama_skill').size().reset_index(name='freq_academic')
        
        # Daftar soft skill acuan asli dari 35 core skill O*NET
        soft_skills_list = {
            'active listening', 'writing', 'speaking', 'social perceptiveness', 'coordination', 
            'persuasion', 'negotiation', 'instructing', 'service orientation', 'complex problem solving', 
            'critical thinking', 'active learning', 'learning strategies', 'monitoring', 
            'judgment and decision making', 'time management', 'management of personnel resources',
            'management of financial resources', 'management of material resources'
        }
        
        # Mendefinisikan fungsi penggolong kategori skill O*NET
        # Parameter skill: Nama skill teks yang dikelompokkan
        def assign_core_category(skill):
            if skill in soft_skills_list:
                return 'Soft Skill'
            return 'Hard Skill'
            
        # Menerapkan fungsi penggolong kategori menggunakan apply()
        df4_freq['kategori'] = df4_freq['nama_skill'].apply(assign_core_category)
        
    # Gabungkan data akademik kategori Teknologi dan Core menggunakan pd.concat()
    # Parameter pertama: List DataFrame pandas yang akan digabung secara vertikal (baris)
    # Parameter ignore_index: Mengabaikan indeks lama dan membuat indeks baru berurutan (True)
    academic_combined = pd.concat([df3_freq, df4_freq], ignore_index=True)
    
    # Kelompokkan berdasarkan nama_skill untuk menggabungkan duplikat jika ada
    # Parameter cats: List kategori skill yang akan dilebur
    def merge_categories(cats):
        if 'Soft Skill' in list(cats):
            return 'Soft Skill'
        return 'Hard Skill'
        
    # Melakukan agregasi gabungan data akademik
    # Parameter pertama dari agg: Kamus nama kolom target beserta fungsinya ('sum' untuk menjumlahkan, merge_categories custom)
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
        # Memeriksa apakah nama skill hanya terdiri dari satu kata alfanumerik menggunakan re.match()
        # Parameter pertama: Pola regex pencocokan kata tunggal alfanumerik ('^[a-z0-9]+$')
        # Parameter kedua: String nama skill yang diuji
        if re.match(r'^[a-z0-9]+$', skill):
            single_word_skills.add(skill)
        else:
            # Cari kata pembentuk skill untuk optimasi subset check
            # Parameter pertama: Pola pencarian kata alfanumerik ('\\b[a-z0-9]+\\b')
            # Parameter kedua: Teks nama skill target
            skill_words = set(re.findall(r'\b[a-z0-9]+\b', skill))
            pattern = rf"\b{re.escape(skill)}\b"
            # Melakukan kompilasi pola regex pencocokan kata spesifik menggunakan re.compile()
            # Parameter pertama: String regex pola pencarian kata batas kata batas (\b)
            special_skills.append((skill, re.compile(pattern), skill_words))
            
    # 2b. Hitung frekuensi kemunculan skill akademik di adzuna_jobs (Industri 1)
    counts_adzuna = {skill: 0 for skill in academic_skills}
    if not df1.empty and 'description' in df1.columns:
        desc_adzuna = df1['description'].dropna().astype(str).tolist()
        for desc in desc_adzuna:
            desc_lower = desc.lower()
            # Memisahkan deskripsi pekerjaan ke bentuk kumpulan kata unik
            words_in_desc = set(re.findall(r'\b[a-z0-9]+\b', desc_lower))
            
            # Match single word skills
            for skill in single_word_skills.intersection(words_in_desc):
                counts_adzuna[skill] += 1
                
            # Match special/multi-word skills
            for skill, rx, skill_words in special_skills:
                if skill_words and not skill_words.issubset(words_in_desc):
                    continue
                # Memeriksa pencocokan pola Regex pada teks deskripsi lowongan menggunakan search()
                # Parameter pertama dari search: Teks target yang diperiksa (desc_lower)
                if rx.search(desc_lower):
                    counts_adzuna[skill] += 1
                    
    # Membuat DataFrame frekuensi Adzuna API
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
                    
    # Membuat DataFrame frekuensi LinkedIn postings
    df2_freq = pd.DataFrame({
        'nama_skill': list(counts_postings.keys()),
        'freq_postings': list(counts_postings.values())
    })

    print("Proses standardisasi teks dan agregasi frekuensi selesai.")

    # 3. GABUNGKAN KETIGA DATASET FREKUENSI
    # Melakukan merge outer agar data frekuensi dari berbagai dataset tergabung
    # Parameter pertama dari pd.merge: DataFrame kiri yang digabungkan (df1_freq)
    # Parameter kedua: DataFrame kanan yang digabungkan (df2_freq)
    # Parameter on: Kolom kunci utama dasar penggabungan ('nama_skill')
    # Parameter how: Metode join ('outer' join untuk mempertahankan semua baris dari kedua data)
    merged_df = pd.merge(df1_freq, df2_freq, on='nama_skill', how='outer')
    merged_df = pd.merge(merged_df, df3_freq_combined, on='nama_skill', how='outer')
    
    # Mengisi NaN dengan 0 untuk frekuensi gabungan menggunakan fillna()
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
    # Memanggil fungsi calculate_skill_gap_score
    # Parameter merged_df: DataFrame gabungan frekuensi
    # Parameter industry_col: Nama kolom industri ('freq_industry_total')
    # Parameter academic_col: Nama kolom akademik ('freq_academic')
    df_gap = calculate_skill_gap_score(merged_df, industry_col='freq_industry_total', academic_col='freq_academic')
    
    print("\nTop 10 Skill dengan Kesenjangan Tertinggi (Tinggi di Industri, Rendah di Akademik):")
    # Menampilkan 10 baris teratas hasil analisis gap menggunakan head(10)
    print(df_gap.head(10))
    
    # 5. SIMPAN HASIL
    output_path = os.path.join(DATASETS_DIR, 'skill_gap_analysis.csv')
    # Menyimpan DataFrame ke file CSV
    # Parameter pertama: Path lokasi tujuan penyimpanan file
    # Parameter index: Menyembunyikan index baris DataFrame (False)
    df_gap.to_csv(output_path, index=False)
    print(f"\nDataset hasil analisis Skill Gap disimpan di {output_path}")

    return df_gap

if __name__ == "__main__":
    df_final = main()
