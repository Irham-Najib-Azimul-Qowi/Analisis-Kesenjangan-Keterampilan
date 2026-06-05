# DATA-ENGINEERING  
# Proyek : Analisis Kesenjangan Keterampilan (Skill Gap Analysis) Berbasis ATS

---

## Kontributor

| Nama Lengkap                       | NIM         | Peran                |
|------------------------------------|-------------|----------------------|
| Irham Najib Azimul Qowi   | 244311045   | Data Engineer        |
| Andrian Maulana           | 244311036   | Project Manager      |
| Raufa Hafid Widodo        | 244311052   | Data Analyst         |

---

## Deskripsi Proyek  
Proyek ini dikembangkan untuk mengevaluasi CV pencari kerja menggunakan sistem berbasis ATS (Applicant Tracking System) dan membandingkannya dengan kebutuhan pasar kerja. Tujuan utamanya adalah untuk mengidentifikasi kesenjangan keterampilan (skill gap) pelamar dengan menganalisis data kompetensi O*NET dan data lowongan pekerjaan aktual dari Adzuna. Selain itu, proyek ini dirancang untuk memberikan insight terperinci mengenai keterampilan spesifik yang perlu ditingkatkan oleh pengguna agar sesuai dengan posisi yang dilamar.

---

## Manfaat Data / Use Case  
- **Tujuan Proyek:** Menyediakan platform evaluasi CV terintegrasi yang mampu membedah keahlian pelamar dan mendeteksi kesenjangan keterampilan secara sistematis berdasarkan standar industri.
- **Manfaat:**  
  - Memberikan umpan balik langsung kepada pencari kerja mengenai kelemahan dan kelebihan profil mereka.  
  - Membantu pencari kerja mengidentifikasi keterampilan spesifik yang harus dipelajari.
  - Hasil pemrosesan data (ETL) mendukung dasbor visualisasi interaktif pada aplikasi Streamlit, dirancang dengan memperhatikan prinsip aksesibilitas UI/UX seperti kemudahan navigasi dan mode gelap (*dark mode*).

---

## Serving Analisis  
Data hasil ETL (Extract, Transform, Load) disimpan dalam format CSV yang terstruktur (termasuk `cached_data.csv` dan `adzuna_jobs.csv`) dan divisualisasikan melalui framework **Streamlit**. Pendekatan ini memungkinkan pengguna untuk berinteraksi langsung melalui antarmuka web, melihat visualisasi perbandingan keterampilan, dan membaca laporan analisis secara *real-time*.

## Serving Machine Learning  
Dataset bersih yang berisi daftar keterampilan dan persyaratan lowongan digunakan sebagai dasar algoritma pencocokan teks (Text Matching) dan ekstraksi informasi. Sistem menggunakan teknik pemrosesan bahasa alami (NLP) untuk melakukan parsing pada CV, mengidentifikasi entitas keterampilan, lalu menghitung tingkat kecocokan (*similarity score*) antara profil pengguna dengan dataset pekerjaan untuk menentukan skor akhir.

---

# Pipeline
## Extract ( Pengambilan Data ) 
- **Sumber Data:**  
  - Data Keterampilan & Kompetensi – Database O*NET (File Excel di dalam folder `db_30_2_excel/` seperti `Abilities.xlsx`, `Abilities to Work Activities.xlsx`, dll).
  - Data Lowongan Pekerjaan – Dataset Adzuna Jobs (`adzuna_jobs.csv`).

- **Metode Pengambilan:**  
**Local Data Extraction:**  
    - Membaca file `.csv` dan `.xlsx` secara lokal menggunakan pustaka `pandas`.
    - Data di-*load* ke dalam DataFrame untuk memetakan hubungan antara jenis pekerjaan, taksonomi keterampilan O*NET, dan frekuensi kemunculan keterampilan di lowongan pasar.

---

## Transform ( Pembersihan & Transformasi )   
- **Pembersihan:**  
  - Skrip pembersihan terdedikasi (`clean_data.py`) digunakan untuk membuang duplikasi, mengatasi baris kosong (`missing values`), dan menstandarkan format teks.
  - Penyelarasan format agar data struktural dari O*NET selaras dengan format deskripsi dari sumber Adzuna.

- **Transformasi:**  
  - Menggabungkan berbagai atribut keterampilan menjadi satu dataset referensi tunggal.
  - Mengkonversi format mentah ke dalam bentuk ringkasan (cache) yang lebih ringan agar dapat dieksekusi dengan cepat oleh model pencocokan.

---

## Load ( Pemindahan ke Target ) 
- **Target:**  
  - Hasil pembersihan dan transformasi dimuat ke dalam file `cached_data.csv`. File ini bertindak sebagai basis data statis *in-memory* yang memicu visualisasi di aplikasi Streamlit.

- **Metode:**  
  - Menggunakan fungsi `to_csv()` dari pandas untuk menyimpan dataset bersih.
  - Saat aplikasi dijalankan, data diload menggunakan konfigurasi *caching* Streamlit untuk menghindari pemrosesan ulang setiap kali ada interaksi pengguna di UI, sehingga performa *load* aplikasi menjadi sangat ringan.

---

## Arsitektur / Workflow ETL  
- **Alur Modular:**  
  - Proses ETL dienkapsulasi dalam file `clean_data.py`.
  - Data keluaran kemudian dikonsumsi secara langsung oleh `app.py` yang menjadi *entry-point* aplikasi web Streamlit.
  - Direktori `.streamlit/` memuat file `config.toml` untuk mengatur tampilan estetika (UI) dari arsitektur aplikasi (seperti penerapan tema gelap).

- **Tools yang Digunakan:**  
  - Python 3.x
  - Library: `pandas`, `numpy`, `streamlit` (untuk UI), dan pustaka NLP/Machine Learning terkait.
  - Platform: Localhost Streamlit

---

## Kode Program  
- **Struktur Kode:**  
  - `app.py`: File utama aplikasi Streamlit.
  - `clean_data.py`: Pipeline untuk transformasi dan pembersihan data.
  - `adzuna_jobs.csv` & `cached_data.csv`: File data operasional.
  - `db_30_2_excel/`: Repositori file referensi dari O*NET.
    
- **Machine Learning:**  
  - Model Utama: NLP berbasis Similarity Matching.
  - Fitur Ekstraksi: Mengidentifikasi kata kunci (keterampilan teknis dan *soft skill*) dari input teks CV.
  - Logika Kesenjangan: Menampilkan perbedaan matematis antara keterampilan yang terdeteksi dengan tuntutan dataset pekerjaan.

- **Link Projek:** 
  - (Silakan tambahkan link repository Github atau deployment Streamlit di sini)

---
