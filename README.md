# 🎓 PNM Skill Gap Analytics Dashboard

Proyek ini adalah sebuah platform visualisasi data interaktif kelas profesional (Enterprise-Grade) yang dirancang untuk menganalisis kesenjangan keterampilan (Skill Gap Analysis) antara **Kurikulum Akademis (Standar O*NET)** dengan **Tuntutan Riil Pasar Kerja Industri (LinkedIn & Adzuna API)** secara real-time.

Dashboard ini dibuat sebagai bagian dari proyek **CV Evaluation and Job Recommendation System** oleh mahasiswa Semester 4 Politeknik Negeri Madiun.

---

## 🎨 Tampilan Utama Dashboard & Fitur Premium

Berbeda dengan visualisasi radar chart konvensional yang sulit dibaca untuk data berdimensi banyak, dashboard ini mengusung visualisasi standar eksekutif:
1. **Glassmorphic KPI Cards**: Informasi ringkasan total data terintegrasi, standar kurikulum, total lowongan aktif, dan alarm defisit skill kritis secara instan.
2. **Side-by-Side Grouped Bar Chart**: Komparasi proporsi kemunculan keterampilan di dunia akademik vs industri secara side-by-side menggunakan palette warna modern (neon orange & sleek sky blue).
3. **Diverging Skill Gap Index**: Grafik horizontal komparasi deviasi/gap. Keterampilan yang **Defisit (sangat dituntut industri tetapi kurang diajarkan)** ditandai dengan warna merah tegas, sedangkan **Surplus** ditandai dengan warna hijau emerald.
4. **Technology Mismatch Matrix**: Tabel data interaktif lengkap dengan penyorotan warna kondisional otomatis (conditional formatting).
5. **Interactive Job Explorer**: Fitur pencarian lowongan kerja aktif dan profil tingkat pengalaman secara langsung dari stream broker data.
6. **Double-Engine Data Loading**:
   * **Engine 1 (Ultra-Fast Cache)**: Secara instan memuat **4.716 data pekerjaan** pra-unduh dalam waktu kurang dari 1 detik.
   * **Engine 2 (Aiven Kafka Real-Time Stream)**: Tombol sinkronisasi langsung ke broker Aiven Kafka Cloud Anda menggunakan enkripsi SSL yang aman untuk menarik data terbaru!

---

## 📁 Struktur Folder Aplikasi (`pnm_dashboard_app`)

Repositori mandiri (self-contained) ini berisi semua file yang dibutuhkan untuk dideploy secara instan:
* `app.py` — File aplikasi utama Streamlit dengan visualisasi premium.
* `fetch_and_save_cache.py` — Script mandiri untuk memperbarui offline cache lokal dari broker Kafka.
* `cached_data.csv` — File cache lokal berisi 4.716 data pekerjaan matang (siap pakai).
* `requirements.txt` — Daftar pustaka Python yang dibutuhkan oleh Streamlit Cloud.
* `ssl/` — Folder berisi sertifikat SSL akses broker Aiven Kafka Cloud Anda (`ca.pem`, `service.cert`, `service.key`).

---

## 🚀 Panduan Menjalankan Secara Lokal

Untuk menguji dashboard di komputer lokal Anda:

1. Masuk ke direktori folder dashboard:
   ```bash
   cd pnm_dashboard_app
   ```

2. Jalankan aplikasi Streamlit menggunakan virtual environment Anda:
   ```bash
   # Jika menggunakan Fish Shell:
   ../venv/bin/streamlit run app.py
   
   # Jika menggunakan Bash/Zsh standar:
   ../venv/bin/streamlit run app.py
   ```

---

## ☁️ Panduan Deploy ke Streamlit Cloud & GitHub (3 Langkah Mudah!)

Dashboard ini sudah siap 100% untuk dideploy ke internet secara gratis menggunakan Streamlit Cloud. Ikuti langkah-langkah berikut:

### Langkah 1: Push ke Repositori GitHub Baru
1. Buat sebuah repositori baru di GitHub Anda (misal namanya: `pnm-skill-gap-dashboard`).
   > [!IMPORTANT]
   > Karena folder `ssl/` berisi sertifikat akses pribadi ke broker Aiven Cloud Anda, pastikan Anda memilih opsi **PRIVATE REPOSITORY** saat membuat repositori di GitHub untuk menjaga keamanan kredensial Anda!
2. Masuk ke folder `pnm_dashboard_app` di komputer Anda, lalu inisialisasi git dan push kodenya ke GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of corporate-grade skill gap dashboard"
   git branch -M main
   git remote add origin https://github.com/USERNAME_ANDA/pnm-skill-gap-dashboard.git
   git push -u origin main
   ```

### Langkah 2: Deploy ke Streamlit Cloud
1. Masuk ke situs [Streamlit Community Cloud](https://share.streamlit.io/) dan masuk menggunakan akun GitHub Anda.
2. Klik tombol **New App** di kanan atas.
3. Konfigurasikan detail deployment:
   * **Repository**: Pilih repositori GitHub `USERNAME_ANDA/pnm-skill-gap-dashboard` yang baru Anda push.
   * **Branch**: Pilih `main`.
   * **Main file path**: Ketik `app.py`.
4. Klik **Deploy!**

Aplikasi Anda akan ter-build otomatis dalam 1-2 menit dan dapat langsung diakses secara online di seluruh dunia menggunakan URL unik yang disediakan oleh Streamlit!
