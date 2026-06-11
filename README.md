# DATA-ENGINEERING  
# Proyek: Intelligence Analisis Kesenjangan Keterampilan & Rekomendasi Lowongan Kerja (Skill Gap & CV Matcher)

---

## Kontributor

| Nama Lengkap                       | NIM         | Peran                |
|------------------------------------|-------------|----------------------|
| Irham Najib Azimul Qowi            | 244311045   | Data Engineer        |
| Andrian Maulana                    | 244311036   | Project Manager      |
| Raufa Hafid Widodo                 | 244311052   | Data Analyst         |

---

## Deskripsi Proyek  
Proyek ini dikembangkan sebagai sistem cerdas terintegrasi untuk membantu pencari kerja mengidentifikasi kesenjangan keterampilan (*skill gap*) mereka terhadap standar industri, sekaligus memberikan rekomendasi lowongan pekerjaan yang paling cocok dengan profil CV mereka. 

Proyek ini terdiri dari dua modul dashboard interaktif:
1. **Gap Analysis Dashboard:** Memetakan gap kompetensi antara standar kurikulum akademik (O*NET) dengan tuntutan riil pasar kerja (Adzuna).
2. **CV Recommender System:** Mencari lowongan pekerjaan yang paling relevan dengan CV pelamar menggunakan kombinasi kemiripan makna (*semantik BERT*) dan pencocokan keahlian (*Jaccard Similarity*).

---

## 🚀 Live Demo Aplikasi (Streamlit Share)
Aplikasi ini dideploy sebagai dua layanan terpisah yang saling melengkapi:
* 📊 **Dashboard Analisis Kesenjangan Skill (Gap Analysis):** [https://gapskillsanalysis.streamlit.app/](https://gapskillsanalysis.streamlit.app/)
* 💼 **Sistem Pencocokan & Rekomendasi Lowongan (CV Recommender):** [https://jobrecommenderai.streamlit.app/](https://jobrecommenderai.streamlit.app/)

---

## 🏗️ Alur Data & Pipeline ETL

### 1. Extract (Pengambilan Data)
* **Data Akademik:** Diambil dari database O*NET (file Excel dalam `gap_analysis/db_30_2_excel/` seperti `Skills.xlsx` dan `Technology Skills.xlsx`).
* **Data Industri:** Menggunakan database lowongan kerja Adzuna (`gap_analysis/adzuna_jobs.csv`) dan data lowongan kerja gabungan dari BigQuery.

### 2. Transform (Pembersihan & Pengolahan)
* **Gap Analysis Pipeline:** Seluruh pembersihan data akademik, ekstraksi kata kunci keahlian dari deskripsi pekerjaan, kalkulasi skor kesenjangan (*industry_norm - academic_norm*), hingga ekspor data hasil akhir diolah melalui notebook [gap_analysis/analysis.ipynb](file:///d:/folder_pnm/s4%20-%20data%20engineering/Team%20Projek/uas/gap_analysis/analysis.ipynb).
* **Machine Learning Pipeline:** Pengunduhan data 108.940 baris lowongan kerja dari GCP BigQuery, pembersihan teks, pembuatan representasi vektor numerik 384 dimensi (*sentence embedding*) menggunakan model BERT `all-MiniLM-L6-v2`, hingga evaluasi model diolah di notebook [cv_recommender/Machine_Learning.ipynb](file:///d:/folder_pnm/s4%20-%20data%20engineering/Team%20Projek/uas/cv_recommender/Machine_Learning.ipynb).

### 3. Load & Serving
* Data kesenjangan disimpan ke `gap_analysis/skill_gap_analysis.csv` untuk divisualisasikan oleh dashboard `gap_analysis/app.py`.
* Indeks pencarian semantik cepat disimpan ke file biner index FAISS `cv_recommender/models/faiss_job_index.bin` beserta metadata lowongannya di `cv_recommender/models/job_metadata.csv` untuk disajikan oleh `cv_recommender/streamlit_app.py`.

---

## 🛠️ Struktur Repositori Kode

```directory
uas/
├── cv_recommender/               # Modul Sistem Rekomendasi CV
│   ├── .gitattributes            # Konfigurasi LFS untuk model biner besar
│   ├── DOCUMENTATION.md          # Dokumentasi teknis model AI
│   ├── Machine_Learning.ipynb    # Notebook pelatihan & pembuatan model
│   ├── model_utils.py            # Logika inti ML (BERT & FAISS)
│   ├── streamlit_app.py          # Dashboard antarmuka pengguna
│   ├── requirements.txt          # Dependensi library python
│   └── models/                   # Folder hasil training model (FAISS, Metadata CSV)
│
├── gap_analysis/                 # Modul Dashboard Kesenjangan Skill
│   ├── README.md                 # Dokumentasi pendukung analisis
│   ├── analysis.ipynb            # Notebook pembersihan & pemrosesan data
│   ├── app.py                    # Dashboard visualisasi interaktif
│   ├── requirements.txt          # Dependensi dashboard analisis
│   ├── adzuna_jobs.csv           # Sumber data mentah industri
│   ├── skill_gap_analysis.csv    # Output data kesenjangan terhitung
│   └── db_30_2_excel/            # Database data referensi O*NET
│
├── Pipeline/                     # Pipeline ETL ke Aiven Kafka (Tidak Diubah)
├── DEPLOY.md                     # Panduan lengkap deployment cloud
└── README.md                     # Dokumentasi utama proyek
```

---

## 💻 Cara Menjalankan Secara Lokal

### Menjalankan Dashboard Gap Analysis:
```bash
cd gap_analysis
streamlit run app.py
```

### Menjalankan CV Recommender:
```bash
cd cv_recommender
streamlit run streamlit_app.py
```
