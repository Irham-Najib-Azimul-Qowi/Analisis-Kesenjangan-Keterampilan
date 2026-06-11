# Panduan Deployment: Multi-App Streamlit dari Satu Repositori

Repositori ini dirancang agar Anda dapat men-deploy **dua aplikasi Streamlit terpisah** dari satu repositori GitHub yang sama.

---

## 🏗️ Struktur Aplikasi

Repositori ini memiliki dua aplikasi utama:
1. **CV Recommender** (`cv_recommender/streamlit_app.py`) — Sistem rekomendasi lowongan kerja berbasis CV.
2. **Gap Analysis** (`gap_analysis/app.py`) — Dashboard analisis kesenjangan skill.

---

## 🔒 Catatan Keamanan Penting
* **Kredensial BigQuery (`*.json`):** File kredensial (seperti `deductive-reach-443812-q3-0eddc382714e.json`) berisi private key yang sangat sensitif. File ini **telah dikecualikan di `.gitignore`** sehingga aman dari commit ke GitHub.
* **Tidak Perlu Kredensial di Cloud:** Aplikasi Streamlit (baik CV Recommender maupun Gap Analysis) **tidak membutuhkan koneksi langsung ke BigQuery** saat dijalankan di cloud. Semua data dan model FAISS telah di-generate secara lokal melalui notebook (`.ipynb`) dan disimpan di folder masing-masing. Sehingga proses deployment menjadi sangat aman dan sederhana!

---

## 📦 Persiapan Git LFS (Large File Storage)
File model `faiss_job_index.bin` (~160MB) melebihi batas ukuran file 100MB di GitHub. Anda harus menggunakan Git LFS agar proses push tidak ditolak oleh GitHub.

### Langkah-langkah setup Git LFS (Lakukan sekali sebelum push):
1. Unduh dan instal Git LFS di komputer Anda jika belum ada (https://git-lfs.github.com/).
2. Buka terminal di folder root (`uas/`) lalu jalankan perintah berikut:
   ```bash
   git lfs install
   ```
3. Konfigurasi LFS untuk file besar sudah otomatis diatur di file `.gitattributes` kita.
4. Lakukan add, commit, dan push seperti biasa:
   ```bash
   git add .
   git commit -m "Refactor: setup deployment dan model terbaru"
   git push origin main
   ```

---

## 🚀 Cara Deploy ke Streamlit Community Cloud

Anda akan membuat **dua aplikasi berbeda** di dashboard Streamlit Cloud menggunakan repositori yang sama.

### App 1: CV Recommender

1. Masuk ke [Streamlit Share](https://share.streamlit.io/) dan klik **Create App**.
2. Masukkan detail berikut:
   * **Repository:** Pilih repositori GitHub Anda (misal: `username/Analisis-Kesenjangan-Keterampilan`).
   * **Branch:** `main` (atau branch utama Anda).
   * **Main file path:** `cv_recommender/streamlit_app.py`
3. Klik **Deploy!**
   * *Streamlit akan otomatis mendeteksi dan menginstal library di `cv_recommender/requirements.txt`.*

### App 2: Gap Analysis Dashboard

1. Klik **Create App** lagi untuk aplikasi baru.
2. Masukkan detail berikut:
   * **Repository:** Pilih repositori GitHub yang sama.
   * **Branch:** `main` (atau branch utama Anda).
   * **Main file path:** `gap_analysis/app.py`
3. Klik **Deploy!**
   * *Streamlit akan otomatis mendeteksi dan menginstal library di `gap_analysis/requirements.txt`.*

---

## 🛠️ Pengembangan Lokal (Cara Menjalankan Aplikasi)

Jika Anda ingin menjalankan aplikasi secara lokal di komputer Anda:

### Menjalankan CV Recommender:
```bash
cd "cv_recommender"
streamlit run streamlit_app.py
```

### Menjalankan Gap Analysis:
```bash
cd "gap_analysis"
streamlit run app.py
```
