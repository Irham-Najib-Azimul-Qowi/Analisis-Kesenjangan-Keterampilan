# Skill Gap Analytics Dashboard

Proyek ini adalah sebuah platform visualisasi data interaktif profesional yang dirancang untuk menganalisis kesenjangan keterampilan (Skill Gap Analysis) antara standar kurikulum akademis dengan tuntutan riil pasar kerja industri secara real-time.

Analisis dilakukan dengan membandingkan:
1. **Kurikulum Akademis (Standar O*NET)**: Mewakili rujukan profesi dan kurikulum pengajaran.
2. **Kebutuhan Industri (LinkedIn & Adzuna API)**: Diambil dari broker data stream real-time untuk mencerminkan permintaan pasar kerja terkini.

Proyek ini dikembangkan sebagai bagian dari sistem evaluasi CV dan rekomendasi pekerjaan (CV Evaluation and Job Recommendation System).

---

## Tampilan Utama Dashboard dan Fitur

Dashboard ini menggunakan visualisasi berstandar eksekutif untuk memudahkan pengambilan keputusan:
1. **KPI Cards**: Informasi ringkasan total data terintegrasi, jumlah standar kurikulum, total lowongan aktif, dan indikator defisit skill kritis secara instan.
2. **Grouped Bar Chart**: Komparasi proporsi kemunculan keterampilan di dunia akademik (O*NET) vs industri (LinkedIn/Adzuna) secara berdampingan.
3. **Diverging Skill Gap Index**: Grafik deviasi untuk mengidentifikasi keterampilan yang mengalami defisit (sangat dituntut industri tetapi kurang diakomodasi kurikulum) maupun surplus.
4. **Technology Mismatch Matrix**: Tabel data interaktif lengkap dengan pemetaan warna kondisional (conditional formatting).
5. **Interactive Job Explorer**: Fitur pencarian lowongan kerja aktif dan profil tingkat pengalaman secara langsung dari stream broker data.
6. **Sistem Muat Data Ganda**:
   * **Offline Cache**: Memuat data pekerjaan pra-unduh secara instan untuk efisiensi performa.
   * **Aiven Kafka Real-Time Stream**: Sinkronisasi langsung ke broker Aiven Kafka Cloud menggunakan enkripsi SSL untuk menarik data terbaru.

---

## Struktur Folder Aplikasi (`pnm_dashboard_app`)

Repositori mandiri ini berisi seluruh komponen yang dibutuhkan untuk deployment:
* `app.py`: File aplikasi utama Streamlit dengan visualisasi premium.
* `fetch_and_save_cache.py`: Script mandiri untuk memperbarui offline cache lokal dari broker Kafka.
* `cached_data.csv`: File cache lokal berisi data pekerjaan siap pakai.
* `requirements.txt`: Daftar pustaka Python yang dibutuhkan.
* `ssl/`: Folder sertifikat SSL untuk akses aman ke broker Aiven Kafka Cloud (`ca.pem`, `service.cert`, `service.key`).

---

## Panduan Menjalankan Secara Lokal

Untuk menguji dashboard di komputer lokal Anda:

1. Masuk ke direktori folder dashboard:
   ```bash
   cd pnm_dashboard_app
   ```

2. Jalankan aplikasi Streamlit menggunakan virtual environment Anda:
   ```bash
   ../venv/bin/streamlit run app.py
   ```

---

## Panduan Deploy ke Streamlit Cloud dan GitHub

Dashboard ini dapat dideploy secara gratis menggunakan Streamlit Cloud melalui langkah-langkah berikut:

### Langkah 1: Push ke Repositori GitHub
1. Buat sebuah repositori baru di GitHub Anda (disarankan memilih opsi **Private Repository** untuk melindungi kredensial broker Kafka Anda).
2. Jalankan perintah berikut di terminal komputer Anda:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of skill gap dashboard"
   git branch -M main
   git remote add origin https://github.com/USERNAME_ANDA/REPOSiTORI_ANDA.git
   git push -u origin main
   ```

### Langkah 2: Deploy di Streamlit Cloud
1. Masuk ke [Streamlit Community Cloud](https://share.streamlit.io/) menggunakan akun GitHub Anda.
2. Klik tombol **New App** di kanan atas.
3. Konfigurasikan detail deployment:
   * **Repository**: Pilih repositori GitHub yang baru Anda push.
   * **Branch**: Pilih `main`.
   * **Main file path**: Ketik `app.py`.
4. Klik **Deploy!**

Aplikasi akan dibangun otomatis dalam beberapa menit dan siap diakses secara online.
