# Career Readiness Analytics & Intelligent Job Matcher

Proyek Akhir Data Engineering: Sistem Analisis Kesenjangan Keterampilan (*Skill Gap Analysis*) & Rekomendasi Pekerjaan Berbasis AI (*CV Matcher*).

---

## 👥 Tim Pengembang (Kontributor)

| Nama Lengkap | NIM | Peran |
| :--- | :--- | :--- |
| **Irham Najib Azimul Qowi** | 244311045 | Data Engineer |
| **Andrian Maulana** | 244311036 | Project Manager |
| **Raufa Hafid Widodo** | 244311052 | Data Analyst |

---

## 🌐 Live Demo Aplikasi (Streamlit Share)

Aplikasi dideploy secara terpisah di Streamlit Community Cloud untuk kemudahan akses dan performa optimal:

* 📊 **Dashboard Analisis Kesenjangan Skill (Gap Analysis):**  
  👉 [https://gapskillsanalysis.streamlit.app/](https://gapskillsanalysis.streamlit.app/)
* 💼 **Sistem Pencocokan & Rekomendasi Lowongan (CV Recommender):**  
  👉 [https://jobrecommenderai.streamlit.app/](https://jobrecommenderai.streamlit.app/)

---

## 📝 Deskripsi Proyek

Proyek ini dibangun untuk menjawab tantangan kesenjangan kompetensi antara lulusan akademik dengan kebutuhan nyata industri kerja. Sistem terintegrasi ini menyediakan dua solusi utama:

1. **Analisis Kesenjangan Keterampilan (*Skill Gap Analysis*):**  
   Memetakan dan mengukur perbedaan (*gap*) antara standar kurikulum akademis (**O*NET**) dan kriteria keahlian yang dicari di pasar kerja industri saat ini (**Adzuna API**). Hasil analisis membantu institusi pendidikan memperbarui materi ajar agar sesuai tren industri.
   
2. **Sistem Rekomendasi Lowongan Kerja (*CV Recommender*):**  
   Menganalisis teks CV pelamar kerja menggunakan model NLP (**Sentence-BERT**) dan algoritma pencarian kemiripan cepat (**FAISS**) untuk mencocokkan profil pelamar dengan puluhan ribu lowongan aktif. Sistem ini juga memberikan evaluasi kesiapan kerja pelamar (*Readiness Score*) per kategori skill.

---

## 🛠️ Arsitektur & Struktur Repositori

Struktur repositori kode telah disederhanakan tanpa spasi pada nama folder agar kompatibel dengan sistem build Streamlit Community Cloud:

```directory
career-readiness-analytics/
├── cv_recommender/               # Modul Sistem Rekomendasi CV
│   ├── .streamlit/               # Konfigurasi tampilan Streamlit
│   ├── models/                   # Folder model AI & metadata (FAISS index, CSV)
│   ├── Machine_Learning.ipynb    # Notebook pelatihan model & ekstraksi profil
│   ├── model_utils.py            # Logika inti pemrosesan ML (BERT & FAISS)
│   ├── streamlit_app.py          # Antarmuka dashboard pencocokan CV
│   ├── DOCUMENTATION.md          # Dokumentasi teknis alur model AI
│   └── requirements.txt          # Dependensi Python untuk modul ML
│
├── gap_analysis/                 # Modul Dashboard Kesenjangan Skill
│   ├── db_30_2_excel/            # Database standar akademik O*NET (Excel)
│   ├── analysis.ipynb            # Notebook analisis & kalkulasi gap
│   ├── app.py                    # Antarmuka dashboard visualisasi gap
│   ├── adzuna_jobs.csv           # Sumber data mentah industri (Adzuna)
│   ├── skill_gap_analysis.csv    # Output hasil kalkulasi kesenjangan skill
│   ├── fetch_and_save_cache.py   # Script pengambil data dari Aiven Kafka
│   ├── PROSES_PENGEMBANGAN_ANALISIS.md # Catatan proses pengembangan
│   ├── README.md                 # Panduan teknis dashboard gap
│   └── requirements.txt          # Dependensi Python untuk modul visualisasi
│
├── Pipeline/                     # Modul Pipeline Data Engineering
│   └── pipeline etl to aiven.ipynb # ETL Pipeline mengirim data ke Aiven Kafka
│
├── DEPLOY.md                     # Panduan detail cara deploy ke Cloud
├── README.md                     # Dokumentasi utama proyek (file ini)
└── requirements.txt              # Kumpulan seluruh library python (lokal)
```

---

## 🏗️ Alur Data & Pipeline ETL

```mermaid
flowchart TD
    subgraph Pengambilan Data
        ONET["Database O*NET Excel"] -->|Ekstraksi Standar Akademik| AnalysisNB["analysis.ipynb"]
        Adzuna["Adzuna Jobs CSV"] -->|Ekstraksi Keahlian Industri| AnalysisNB
        BigQuery["GCP BigQuery"] -->|Query Lowongan Kerja| MLNB["Machine_Learning.ipynb"]
    end

    subgraph Pemrosesan & Modelling
        AnalysisNB -->|Kalkulasi Gap Score| GapCSV["skill_gap_analysis.csv"]
        MLNB -->|Sentence-BERT Embedding| FAISS["faiss_job_index.bin"]
        MLNB -->|Extract Metadata| JobMeta["job_metadata.csv"]
    end

    subgraph Penyajian (Serving)
        GapCSV -->|Visualisasi Data| GapApp["gap_analysis/app.py"]
        FAISS -->|Pencarian Semantik| CVApp["cv_recommender/streamlit_app.py"]
        JobMeta -->|Detil Lowongan| CVApp
    end

    style ONET fill:#e1f5fe,stroke:#01579b
    style Adzuna fill:#e8f5e9,stroke:#1b5e20
    style BigQuery fill:#fff3e0,stroke:#e65100
    style GapCSV fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style FAISS fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style JobMeta fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style GapApp fill:#0288d1,color:#fff
    style CVApp fill:#e65100,color:#fff
```

### 1. Extract (Pengambilan Data)
* **Data Akademik:** Diambil dari O*NET Database (file excel seperti `Skills.xlsx` dan `Technology Skills.xlsx` di `gap_analysis/db_30_2_excel/`).
* **Data Industri:** Menggunakan dataset lowongan kerja dari Adzuna API (`gap_analysis/adzuna_jobs.csv`) dan database gabungan lowongan kerja di GCP BigQuery.

### 2. Transform (Transformasi & AI Modelling)
* **Gap Analysis:** Membersihkan keahlian akademis, memetakan frekuensi keahlian industri, menghitung skor kesenjangan (`industry_norm - academic_norm`), dan menyimpan output data ke `gap_analysis/skill_gap_analysis.csv`.
* **CV Matcher ML:** Mengambil data lowongan kerja dari BigQuery, memproses deskripsi teks lowongan, membuat embedding vektor 384-dimensi menggunakan Sentence-Transformer (`all-MiniLM-L6-v2`), serta melatih indeks FAISS untuk pencarian semantik cepat.

### 3. Load & Serving
* Dashboard **Gap Analysis** menyajikan visualisasi perbandingan proporsi keahlian industri vs akademis dari file CSV.
* Dashboard **CV Recommender** memuat indeks FAISS secara langsung di server Streamlit Cloud untuk pencarian lowongan kerja real-time dan pencocokan CV berbasis kesamaan makna.

---

## 💻 Panduan Menjalankan Secara Lokal

### Prasyarat
Pastikan Anda menggunakan Python versi **3.9 ke atas** (Direkomendasikan **3.11**).

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/Irham-Najib-Azimul-Qowi/career-readiness-analytics.git
   cd career-readiness-analytics
   ```

2. **Instal Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Dashboard Gap Analysis:**
   ```bash
   cd gap_analysis
   streamlit run app.py
   ```

4. **Jalankan CV Recommender:**
   ```bash
   cd ../cv_recommender
   streamlit run streamlit_app.py
   ```

---

## 🚀 Panduan Deployment Cloud

Seluruh konfigurasi deploy ke Streamlit Community Cloud (tanpa memerlukan file kredensial JSON BigQuery di server cloud) telah didokumentasikan secara rinci di file [DEPLOY.md](file:///d:/folder_pnm/s4%20-%20data%20engineering/Team%20Projek/uas/DEPLOY.md). Silakan rujuk file tersebut untuk langkah demi langkah setup di dashboard Streamlit Share.
