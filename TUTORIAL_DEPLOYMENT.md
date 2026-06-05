# 📦 Tutorial Deployment CV Recommender API

## Panduan Lengkap: Menjalankan Lokal & Deploy Streamlit Dashboard

Semua artefak model ML sudah tersedia di folder `models/` (dikelola oleh Git LFS).
**Tidak perlu Google Cloud** — cukup clone repo ini dan jalankan.

---

## 📋 Daftar Isi

1. [Struktur Folder](#1-struktur-folder)
2. [Menjalankan API Lokal (Tanpa Docker)](#2-menjalankan-api-lokal-tanpa-docker)
3. [Menjalankan dengan Docker Compose](#3-menjalankan-dengan-docker-compose)
4. [Deploy Streamlit ke Streamlit Community Cloud (Gratis)](#4-deploy-streamlit-ke-streamlit-community-cloud-gratis)
5. [Test Endpoint API](#5-test-endpoint-api)
6. [Monitoring & Maintenance](#6-monitoring--maintenance)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Struktur Folder

```
cv-recommender-api/
├── app/
│   ├── __init__.py              # Package init
│   ├── main.py                  # FastAPI entry point + monitoring + security
│   ├── pipeline.py              # CVAnalysisPipeline class
│   ├── skill_utils.py           # Skill extraction & assessment helpers
│   └── config.py                # Configuration dari env variables
├── models/                       # ✅ Artefak model ML (sudah terisi)
│   ├── faiss_job_index.bin      # Indeks FAISS (~160MB, Git LFS)
│   ├── job_metadata.csv         # Metadata lowongan kerja
│   ├── job_role_profiles.json   # Profil skill standar per peran
│   ├── skill_taxonomy.json      # Taksonomi/kamus skill
│   ├── model_config.json        # Konfigurasi model
│   ├── assessment_config.json   # Konfigurasi penilaian
│   └── README.md
├── .env.example                  # Template environment variables
├── .gitattributes                # Git LFS tracking config
├── .gitignore
├── Dockerfile                    # Docker untuk backend API
├── Dockerfile.streamlit          # Docker untuk dashboard Streamlit
├── docker-compose.yml            # Jalankan backend + frontend sekaligus
├── Machine_Learning.ipynb        # Notebook ML (Part 1-5)
├── streamlit_app.py              # Dashboard Streamlit
├── requirements.txt              # Python dependencies
└── TUTORIAL_DEPLOYMENT.md        # 📖 File yang sedang Anda baca
```

> **Semua file sudah lengkap dan siap pakai.** Tinggal clone → install → jalankan.

---

## 2. Menjalankan API Lokal (Tanpa Docker)

### 2.1 Clone Repository

```bash
git clone https://github.com/Irham-Najib-Azimul-Qowi/Analisis-Kesenjangan-Keterampilan.git
cd Analisis-Kesenjangan-Keterampilan/cv-recommender-api
```

> **Catatan:** Pastikan Git LFS sudah terinstal agar file `faiss_job_index.bin` terdownload.
> Jika belum: `git lfs install && git lfs pull`

### 2.2 Buat Virtual Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏱️ Instalasi pertama kali bisa memakan waktu 5-10 menit karena `sentence-transformers` dan `torch` cukup besar.

### 2.4 (Opsional) Konfigurasi Environment

```bash
# Copy template environment
cp .env.example .env

# Edit jika perlu (default sudah bisa digunakan untuk development)
```

### 2.5 Jalankan API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**Output yang diharapkan:**
```
2026-06-05 10:00:00 [INFO] Menginisialisasi pipeline...
2026-06-05 10:00:05 [INFO] Pipeline siap: 108,963 lowongan terindeks
2026-06-05 10:00:05 [INFO] Pipeline siap melayani request!
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 2.6 Jalankan Streamlit Dashboard (Terminal Kedua)

```bash
# Buka terminal baru, aktifkan venv
source venv/bin/activate

# Jalankan Streamlit (otomatis terhubung ke backend localhost:8080)
streamlit run streamlit_app.py
```

Dashboard akan terbuka di browser: `http://localhost:8501`

### 2.7 Test API dengan curl

```bash
# Health check
curl -s http://localhost:8080/health | python3 -m json.tool

# Daftar role yang didukung
curl -s http://localhost:8080/roles | python3 -m json.tool

# Test analisis CV
curl -s -X POST http://localhost:8080/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Data Engineer with 3 years experience in Python, SQL, Apache Spark, Kafka, Docker, AWS. Strong ETL and data pipeline skills.",
    "target_role": "data_engineer",
    "top_k": 3
  }' | python3 -m json.tool

# Lihat metrics
curl -s http://localhost:8080/metrics | python3 -m json.tool
```

### 2.8 Test via Browser

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

---

## 3. Menjalankan dengan Docker Compose

### 3.1 Prasyarat
- Docker Desktop sudah terinstal dan berjalan

### 3.2 Jalankan Backend + Frontend

```bash
cd cv-recommender-api

# Build dan jalankan semua service
docker compose up --build
```

Ini akan menjalankan:
- **Backend API** di `http://localhost:8080`
- **Streamlit Dashboard** di `http://localhost:8501`

### 3.3 Jalankan di Background

```bash
docker compose up --build -d

# Cek status
docker compose ps

# Lihat logs
docker compose logs -f

# Hentikan
docker compose down
```

---

## 4. Deploy Streamlit ke Streamlit Community Cloud (Gratis)

Streamlit Community Cloud adalah layanan hosting **gratis** dari Streamlit untuk men-deploy aplikasi Streamlit langsung dari repository GitHub.

### 4.1 Prasyarat

- Repository sudah di-push ke GitHub ✅
- Akun GitHub ✅
- Backend API harus berjalan di suatu tempat yang bisa diakses publik (misalnya VPS, Railway, Render, atau komputer lokal dengan tunneling)

> **⚠️ Penting:** Streamlit Community Cloud hanya men-host **frontend dashboard**. Backend FastAPI (`app/main.py`) harus di-deploy terpisah agar dashboard bisa terhubung ke endpoint API.

### 4.2 Langkah Deploy Dashboard

#### Langkah 1: Buka Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Klik **Sign in** dengan akun GitHub Anda
3. Klik tombol **New App**

#### Langkah 2: Isi Form Deployment

| Field | Nilai |
|-------|-------|
| **Repository** | `Irham-Najib-Azimul-Qowi/Analisis-Kesenjangan-Keterampilan` |
| **Branch** | `main` |
| **Main file path** | `cv-recommender-api/streamlit_app.py` |

#### Langkah 3: Konfigurasi Environment Variables

1. Klik **Advanced settings...** di bagian bawah form
2. Pilih tab **Secrets**
3. Tambahkan konfigurasi berikut dalam format TOML:

```toml
BACKEND_URL = "http://ALAMAT_BACKEND_API_ANDA:8080"
```

> **Ganti** `ALAMAT_BACKEND_API_ANDA` dengan URL publik backend API Anda.
>
> Contoh jika menggunakan Railway: `BACKEND_URL = "https://cv-recommender-api-production.up.railway.app"`

#### Langkah 4: Deploy

1. Klik **Deploy!**
2. Tunggu beberapa menit hingga aplikasi selesai di-build
3. Dashboard Anda akan aktif di URL seperti: `https://your-app.streamlit.app`

### 4.3 Opsi Deploy Backend API (Gratis/Murah)

Jika Anda membutuhkan backend yang bisa diakses publik, berikut beberapa opsi:

#### Opsi A: Railway (Recommended — Gratis $5/bulan credit)

1. Buka [railway.app](https://railway.app) dan login dengan GitHub
2. Klik **New Project** → **Deploy from GitHub Repo**
3. Pilih repo `Analisis-Kesenjangan-Keterampilan`
4. Set root directory ke `cv-recommender-api`
5. Railway akan auto-detect Dockerfile dan deploy
6. Set environment variable: `PORT=8080`
7. Dapatkan URL publik dari Railway dashboard

#### Opsi B: Render (Gratis tier tersedia)

1. Buka [render.com](https://render.com) dan login
2. Klik **New** → **Web Service** → **Connect GitHub Repo**
3. Root Directory: `cv-recommender-api`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

#### Opsi C: Ngrok / Cloudflare Tunnel (Development)

Jika hanya untuk demo/testing, Anda bisa ekspose backend lokal ke internet:

```bash
# Install ngrok
# Jalankan backend lokal dulu: uvicorn app.main:app --port 8080

# Ekspose ke internet
ngrok http 8080

# Gunakan URL ngrok sebagai BACKEND_URL di Streamlit Cloud
```

### 4.4 Konfigurasi requirements.txt untuk Streamlit Cloud

Streamlit Community Cloud otomatis menginstal dependencies dari `requirements.txt`. File yang ada sudah kompatibel — tidak perlu perubahan.

### 4.5 Update URL Backend Setelah Deploy

Jika URL backend berubah, update di Streamlit Community Cloud:

1. Buka dashboard di [share.streamlit.io](https://share.streamlit.io)
2. Klik **Settings** pada aplikasi Anda
3. Pilih tab **Secrets**
4. Update nilai `BACKEND_URL`
5. Reboot aplikasi

---

## 5. Test Endpoint API

```bash
# Ganti dengan URL backend Anda
API_URL="http://localhost:8080"

# Health check
curl -s $API_URL/health | python3 -m json.tool

# Test analyze/text
curl -s -X POST $API_URL/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Data Engineer with 3 years experience in Python, SQL, Apache Spark, Kafka, Docker, AWS. Strong ETL and data pipeline skills.",
    "target_role": "data_engineer",
    "top_k": 3
  }' | python3 -m json.tool

# Test analyze/pdf (upload file CV)
curl -s -X POST $API_URL/analyze/pdf \
  -F "file=@my_cv.pdf" \
  -F "target_role=data_engineer" \
  -F "top_k=5" | python3 -m json.tool

# Test analyze/structured
curl -s -X POST $API_URL/analyze/structured \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "SQL", "Docker", "Apache Kafka"],
    "experience_years": 2,
    "education": "S1 Informatika",
    "target_role": "data_engineer",
    "summary": "Experienced in building data pipelines"
  }' | python3 -m json.tool

# Lihat metrics
curl -s $API_URL/metrics | python3 -m json.tool
```

---

## 6. Monitoring & Maintenance

### 6.1 Monitoring Built-in

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| **Health Check** | `GET /health` | Cek apakah API hidup & model loaded |
| **Request Metrics** | `GET /metrics` | Total request, error rate, latensi P95/P99 |
| **API Key Auth** | Header `X-API-Key` | Aktif jika env `API_KEY` diset |

### 6.2 Mengaktifkan API Key Security

Untuk mengamankan endpoint di production, set environment variable `API_KEY`:

```bash
# Di .env file
API_KEY=rahasia-kunci-api-anda-123

# Kemudian request harus menyertakan header:
curl -H "X-API-Key: rahasia-kunci-api-anda-123" \
     -X POST $API_URL/analyze/text ...
```

### 6.3 Kapan Harus Retraining?

| Trigger | Kondisi | Tindakan |
|---------|---------|----------|
| **Scheduled** | Setiap 3 bulan | Jalankan ulang notebook ML → update models/ |
| **Data Drift** | Skill baru >5% total request | Update `skill_taxonomy.json` |
| **Concept Drift** | >30% skill baru di lowongan terbaru | Full retraining |
| **User Feedback** | Acceptance rate <60% | Evaluasi ulang model |

### 6.4 Langkah Retraining

1. Jalankan ulang `Machine_Learning.ipynb` (Part 1-5) dengan data terbaru
2. Download artefak baru dari Colab
3. Replace file di folder `models/`
4. Commit & push ke GitHub
5. Rebuild Docker atau restart service

---

## 7. Troubleshooting

### ❌ Error: `ModuleNotFoundError` saat test lokal
**Solusi:** Pastikan virtual environment aktif dan dependencies terinstal:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Error: `FileNotFoundError: faiss_job_index.bin`
**Solusi:** File besar belum terdownload dari Git LFS:
```bash
git lfs install
git lfs pull
```

### ❌ Error: `Container failed to start` di Docker
**Solusi:**
1. Pastikan Git LFS sudah pull semua file: `git lfs pull`
2. Cek logs: `docker compose logs backend`
3. Pastikan port 8080 tidak digunakan aplikasi lain

### ❌ Error: `CORS error` dari frontend
**Solusi:** Update `ALLOWED_ORIGINS` di `.env`:
```
ALLOWED_ORIGINS=https://your-app.streamlit.app,http://localhost:3000,http://localhost:8501
```

### ❌ Dashboard Streamlit menampilkan "API Offline"
**Solusi:**
1. Pastikan backend API sedang berjalan
2. Cek URL backend di sidebar dashboard
3. Jika deploy ke cloud, pastikan `BACKEND_URL` di Secrets sudah benar

### ❌ Error: `403 API key tidak valid`
**Solusi:**
- Jika development: Kosongkan `API_KEY` di `.env` (security dinonaktifkan)
- Jika production: Pastikan header `X-API-Key` sesuai dengan env var `API_KEY`

### ❌ Git LFS: `Smudge error` saat clone
**Solusi:** Install Git LFS terlebih dahulu:
```bash
# Ubuntu/Debian
sudo apt install git-lfs

# MacOS
brew install git-lfs

# Arch/EndeavourOS
sudo pacman -S git-lfs

# Lalu jalankan
git lfs install
git lfs pull
```

---

## 📝 Checklist Deployment

- [ ] Repository sudah di-clone dengan Git LFS (`git lfs pull`)
- [ ] Folder `models/` berisi 6 file artefak
- [ ] Virtual environment aktif dan dependencies terinstal
- [ ] Backend API berjalan (`uvicorn app.main:app --port 8080`)
- [ ] Endpoint `/health` merespons `{"status": "healthy"}`
- [ ] Endpoint `/analyze/text` merespons dengan rekomendasi
- [ ] Streamlit dashboard berjalan di `localhost:8501`
- [ ] (Opsional) Docker Compose berhasil
- [ ] (Opsional) Streamlit Community Cloud aktif
- [ ] (Opsional) API key security diaktifkan
