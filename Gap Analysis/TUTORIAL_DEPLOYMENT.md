# 📦 Tutorial Deployment: Gap Analysis Dashboard
**Panduan Lengkap: Menjalankan Lokal & Deploy ke Streamlit Cloud**

Dashboard Analisis Kesenjangan (*Skill Gap*) dirancang sepenuhnya menggunakan data lokal yang sudah diproses awal (*pre-processed*). Dashboard ini tidak memerlukan koneksi API database luar ataupun model AI yang berat, sehingga sangat ringan dan cepat dijalankan.

---

## 📋 Struktur Berkas Dashboard

```
Gap Analysis/
├── app.py                      # Berkas Dashboard Streamlit (Frontend + Logika)
├── skill_gap_analysis.csv      # Dataset hasil perbandingan industri vs akademik
├── clean_data.py               # Skrip pembersihan data (Part 1 ETL)
├── fetch_and_save_cache.py     # Skrip pengambil data lowongan
└── TUTORIAL_DEPLOYMENT.md      # Berkas panduan (file yang sedang Anda baca)
```

---

## 1. Menjalankan Dashboard secara Lokal

### Langkah 1: Clone Repository & Masuk ke Folder
Buka Terminal atau Command Prompt, kemudian ketik:
```bash
git clone https://github.com/Irham-Najib-Azimul-Qowi/Analisis-Kesenjangan-Keterampilan.git
cd "Analisis-Kesenjangan-Keterampilan/Gap Analysis"
```

### Langkah 2: Buat & Aktifkan Virtual Environment (Opsional)
```bash
# Membuat environment baru
python -m venv venv

# Mengaktifkan di Windows
venv\Scripts\activate

# Mengaktifkan di Linux/Mac
source venv/bin/activate
```

### Langkah 3: Install Dependensi
Dashboard ini hanya membutuhkan pustaka **Streamlit** dan **Pandas** untuk berjalan:
```bash
pip install streamlit pandas
```

### Langkah 4: Jalankan Aplikasi
```bash
streamlit run app.py
```
Aplikasi web secara otomatis akan terbuka di browser Anda pada alamat: `http://localhost:8501`

---

## 2. Deploy ke Streamlit Community Cloud (Gratis & Online)

Anda dapat mengunggah dashboard ini agar bisa diakses oleh dosen dan teman-teman secara online secara gratis menggunakan Streamlit Community Cloud:

1. Buka [share.streamlit.io](https://share.streamlit.io) dan masuk (Sign in) menggunakan akun **GitHub** Anda.
2. Klik tombol **New App** di kanan atas.
3. Isi kolom formulir deployment dengan konfigurasi berikut:

   | Bidang (Field) | Nilai Konfigurasi |
   |----------------|-------------------|
   | **Repository** | `Irham-Najib-Azimul-Qowi/Analisis-Kesenjangan-Keterampilan` |
   | **Branch**     | `main` |
   | **Main file path** | `Gap Analysis/app.py` |

4. Klik tombol **Deploy!**
5. Tunggu proses instalasi selesai dalam 1-2 menit. Dashboard Anda kini online secara global dan dapat diakses menggunakan tautan unik (contoh: `https://gap-analysis.streamlit.app`).

*Catatan: Dashboard ini membaca data dari `skill_gap_analysis.csv` secara lokal, sehingga Anda tidak perlu menambahkan konfigurasi Secrets/Environment Variables apa pun saat deployment.*
