# 📦 Tutorial Deployment CV Recommender API

## Panduan Lengkap: Menjalankan Lokal & Deploy Streamlit Dashboard

Semua artefak model ML sudah tersedia di folder `models/` (diunduh menggunakan Git LFS).
*Catatan: Git LFS (Large File Storage) adalah sistem Git untuk mengunduh file besar dari GitHub ke komputer Anda, bukan nama folder fisik.*
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
CV Recommender/
├── app/
│   ├── __init__.py              # Package init
│   ├── main.py                  # FastAPI entry point + monitoring + security
│   ├── pipeline.py              # CVAnalysisPipeline class
│   ├── skill_utils.py           # Skill extraction & assessment helpers
│   └── config.py                # Configuration dari env variables
├── models/                       # ✅ Artefak model ML (sudah terisi)
│   ├── faiss_job_index.bin      # Indeks FAISS (~160MB, Git LFS)
│   ├── job_metadata.csv         # Metadata lowongan kerja (~15MB, Git LFS)
│   ├── job_role_profiles.json   # Profil skill standar per peran
│   ├── skill_taxonomy.json      # Taksonomi/kamus skill
│   ├── model_config.json        # Konfigurasi model
│   ├── assessment_config.json   # Konfigurasi penilaian
│   └── README.md
├── .env.example                  # Template environment variables
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
cd "Analisis-Kesenjangan-Keterampilan/CV Recommender"
```

> **💡 Catatan Penting tentang Git LFS:** 
> **Git LFS (Large File Storage)** bukanlah nama folder fisik di dalam proyek. Ini adalah sistem Git untuk mengelola berkas berukuran besar. 
> Berkas besar tersebut (seperti `faiss_job_index.bin` ~160MB dan `job_metadata.csv` ~15MB) disimpan di dalam folder **`models/`**.
> Jika Anda mendapati berkas di dalam folder `models/` hanya berukuran beberapa KB (berisi teks hash), silakan unduh berkas aslinya dengan menjalankan perintah berikut di terminal:
> ```bash
> git lfs install
> git lfs pull
> ```


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
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 2.6 Jalankan Streamlit Dashboard (Terminal Kedua)

```bash
# Buka terminal baru, aktifkan venv
source venv/bin/activate

# Jalankan Streamlit
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
    "cv_text": "Data Engineer with 3 years experience in Python, SQL, Apache Spark, Kafka, Docker, AWS.",
    "target_role": "data_engineer",
    "top_k": 3
  }' | python3 -m json.tool
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
cd "CV Recommender"

docker compose up --build
```

Ini akan menjalankan:
- **Backend API** di `http://localhost:8080`
- **Streamlit Dashboard** di `http://localhost:8501`

### 3.3 Jalankan di Background

```bash
docker compose up --build -d
docker compose ps          # Cek status
docker compose logs -f     # Lihat logs
docker compose down        # Hentikan
```

---

## 4. Deploy Streamlit ke Streamlit Community Cloud (Gratis)

Streamlit Community Cloud adalah layanan hosting **gratis** untuk men-deploy aplikasi Streamlit langsung dari repository GitHub.

> **⚠️ Penting:** Streamlit Community Cloud hanya men-host **frontend dashboard**. Backend FastAPI harus di-deploy terpisah (lihat Opsi Backend di bawah).

### 4.1 Langkah Deploy Dashboard

#### Langkah 1: Buka Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Klik **Sign in** dengan akun GitHub
3. Klik **New App**

#### Langkah 2: Isi Form Deployment

| Field | Nilai |
|-------|-------|
| **Repository** | `Irham-Najib-Azimul-Qowi/Analisis-Kesenjangan-Keterampilan` |
| **Branch** | `main` |
| **Main file path** | `CV Recommender/streamlit_app.py` |

#### Langkah 3: Konfigurasi Secrets

1. Klik **Advanced settings...** di bagian bawah form
2. Pilih tab **Secrets**
3. Tambahkan:

```toml
BACKEND_URL = "http://ALAMAT_BACKEND_API:8080"
```

> Ganti `ALAMAT_BACKEND_API` dengan URL publik backend Anda.

#### Langkah 4: Deploy!

Klik **Deploy!** — aplikasi akan aktif dalam beberapa menit di URL seperti `https://your-app.streamlit.app`

### 4.2 Opsi Deploy Backend API (Gratis/Murah)

#### Opsi A: Railway (Recommended — Gratis $5/bulan credit)

1. Buka [railway.app](https://railway.app), login dengan GitHub
2. **New Project** → **Deploy from GitHub Repo**
3. Pilih repo `Analisis-Kesenjangan-Keterampilan`
4. Set root directory ke `CV Recommender`
5. Set environment: `PORT=8080`
6. Dapatkan URL publik dari Railway dashboard

#### Opsi B: Render (Gratis tier tersedia)

1. Buka [render.com](https://render.com), login
2. **New** → **Web Service** → Connect repo
3. Root Directory: `CV Recommender`
4. Start Command: `gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

#### Opsi C: Ngrok (Development/Demo saja)

```bash
# Jalankan backend lokal dulu
uvicorn app.main:app --port 8080

# Di terminal lain, ekspose ke internet
ngrok http 8080

# Gunakan URL ngrok sebagai BACKEND_URL di Streamlit Cloud
```

### 4.3 Update URL Backend

Jika URL backend berubah:
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. **Settings** → **Secrets**
3. Update `BACKEND_URL`
4. Reboot aplikasi

---

## 5. Test Endpoint API

```bash
API_URL="http://localhost:8080"   # Ganti dengan URL Anda

# Health check
curl -s $API_URL/health | python3 -m json.tool

# Analisis teks CV
curl -s -X POST $API_URL/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Data Engineer with 3 years experience in Python, SQL, Apache Spark, Kafka, Docker, AWS.",
    "target_role": "data_engineer",
    "top_k": 3
  }' | python3 -m json.tool

# Upload PDF CV
curl -s -X POST $API_URL/analyze/pdf \
  -F "file=@my_cv.pdf" \
  -F "target_role=data_engineer" \
  -F "top_k=5" | python3 -m json.tool

# Profil terstruktur
curl -s -X POST $API_URL/analyze/structured \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "SQL", "Docker", "Apache Kafka"],
    "experience_years": 2,
    "education": "S1 Informatika",
    "target_role": "data_engineer",
    "summary": "Experienced in building data pipelines"
  }' | python3 -m json.tool

# Metrics
curl -s $API_URL/metrics | python3 -m json.tool
```

---

## 6. Monitoring & Maintenance

### 6.1 Monitoring Built-in

| Fitur | Endpoint | Keterangan |
|-------|----------|------------|
| **Health Check** | `GET /health` | Cek API hidup & model loaded |
| **Metrics** | `GET /metrics` | Total request, error rate, latensi P95/P99 |
| **API Key** | Header `X-API-Key` | Aktif jika env `API_KEY` diset |

### 6.2 Kapan Retraining?

| Trigger | Kondisi | Tindakan |
|---------|---------|----------|
| Scheduled | Setiap 3 bulan | Jalankan ulang notebook → update models/ |
| Data Drift | Skill baru >5% | Update `skill_taxonomy.json` |
| User Feedback | Acceptance <60% | Full retraining |

---

## 7. Troubleshooting

| Error | Solusi |
|-------|--------|
| `ModuleNotFoundError` | Aktifkan venv: `source venv/bin/activate && pip install -r requirements.txt` |
| `FileNotFoundError: faiss_job_index.bin` | Jalankan `git lfs install && git lfs pull` |
| `Container failed to start` | Pastikan `git lfs pull` sudah jalan sebelum build Docker |
| Dashboard: "API Offline" | Pastikan backend berjalan dan URL benar |
| `CORS error` | Update `ALLOWED_ORIGINS` di `.env` |
| `403 API key tidak valid` | Kosongkan `API_KEY` di `.env` (dev) atau cocokkan header |
| Git LFS smudge error | Install Git LFS: `sudo pacman -S git-lfs` (Arch) / `sudo apt install git-lfs` (Ubuntu) |

---

## 📝 Checklist

- [ ] Clone repo dengan Git LFS (`git lfs pull`)
- [ ] Folder `models/` berisi 6 file artefak
- [ ] Dependencies terinstal (`pip install -r requirements.txt`)
- [ ] Backend API berjalan (`/health` → `healthy`)
- [ ] Streamlit dashboard berjalan di `localhost:8501`
- [ ] (Opsional) Docker Compose berhasil
- [ ] (Opsional) Streamlit Community Cloud aktif
