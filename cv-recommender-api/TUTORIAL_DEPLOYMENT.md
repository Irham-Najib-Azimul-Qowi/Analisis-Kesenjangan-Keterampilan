# 📦 Tutorial Deployment CV Recommender API

## Panduan Lengkap: Dari Colab → Lokal → Google Cloud Run

Tutorial ini menjelaskan langkah-langkah yang harus dilakukan **setelah Part 1-5 selesai di Google Colab**. Semua file kode sudah disiapkan di folder ini — tugas Anda hanya mengisi artefak model dan menjalankan deployment.

---

## 📋 Daftar Isi

1. [Struktur Folder](#1-struktur-folder)
2. [Download Artefak dari Google Colab](#2-download-artefak-dari-google-colab)
3. [Test Lokal (Tanpa Docker)](#3-test-lokal-tanpa-docker)
4. [Test Lokal dengan Docker](#4-test-lokal-dengan-docker)
5. [Deploy ke Google Cloud Run](#5-deploy-ke-google-cloud-run)
6. [Test Endpoint Setelah Deploy](#6-test-endpoint-setelah-deploy)
7. [Monitoring & Maintenance (Part 7)](#7-monitoring--maintenance-part-7)
8. [Integrasi Frontend Next.js](#8-integrasi-frontend-nextjs)
9. [Estimasi Biaya](#9-estimasi-biaya)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Struktur Folder

Folder `cv-recommender-api/` sudah siap dengan struktur berikut:

```
cv-recommender-api/
├── app/
│   ├── __init__.py              # Package init
│   ├── main.py                  # ✅ FastAPI entry point + monitoring + security
│   ├── pipeline.py              # ✅ CVAnalysisPipeline class
│   ├── skill_utils.py           # ✅ Skill extraction & assessment helpers
│   └── config.py                # ✅ Configuration dari env variables
├── models/                       # ⚠️ KOSONG — isi dari Colab!
│   └── README.md                # Instruksi file apa saja yang diperlukan
├── .env                          # ✅ Environment variables (lokal)
├── .env.example                  # ✅ Template env variables
├── .gitignore                    # ✅ Git ignore
├── Dockerfile                    # ✅ Docker config
├── requirements.txt              # ✅ Python dependencies
└── TUTORIAL_DEPLOYMENT.md        # 📖 File yang sedang Anda baca
```

> **Semua file kode (`app/`) sudah lengkap dan siap pakai.** Anda hanya perlu mengisi folder `models/` dengan artefak dari Colab.

---

## 2. Download Artefak dari Google Colab

### Langkah yang Dilakukan di Google Colab

Setelah Part 1-5 selesai dijalankan, di runtime Colab akan ada beberapa file artefak. **Download semua file berikut:**

| File | Dibuat di Part | Keterangan |
|------|---------------|------------|
| `faiss_job_index.bin` | Part 3 | Indeks FAISS untuk pencarian semantik |
| `job_metadata.csv` | Part 3 | Metadata lowongan (judul, lokasi, dll) |
| `job_role_profiles.json` | Part 4 | Profil skill standar per peran |
| `skill_taxonomy.json` | Part 4 | Kamus skill per kategori |
| `model_config.json` | Part 3 | Konfigurasi model |
| `assessment_config.json` | Part 4 | Konfigurasi penilaian skill |

### Cara Download dari Colab

**Opsi A: Download manual satu per satu**
```python
# Jalankan cell ini di Colab setelah Part 5 selesai
from google.colab import files

files.download("faiss_job_index.bin")
files.download("job_metadata.csv")
files.download("job_role_profiles.json")
files.download("skill_taxonomy.json")
files.download("model_config.json")
files.download("assessment_config.json")
```

**Opsi B: Zip semua lalu download sekali**
```python
# Jalankan cell ini di Colab
import shutil
import os

# Buat folder untuk dizip
os.makedirs("artifacts_for_deploy", exist_ok=True)

artifact_files = [
    "faiss_job_index.bin",
    "job_metadata.csv",
    "job_role_profiles.json",
    "skill_taxonomy.json",
    "model_config.json",
    "assessment_config.json"
]

for f in artifact_files:
    if os.path.exists(f):
        shutil.copy2(f, f"artifacts_for_deploy/{f}")
        print(f"✅ {f} copied")
    else:
        print(f"❌ {f} TIDAK DITEMUKAN — pastikan Part yang relevan sudah dijalankan!")

# Zip
shutil.make_archive("artifacts_for_deploy", "zip", "artifacts_for_deploy")

# Download
from google.colab import files
files.download("artifacts_for_deploy.zip")
print("\n📥 Download artifacts_for_deploy.zip, lalu extract ke folder models/")
```

**Opsi C: Mengunggah dan Mengunduh Lewat Google Cloud Storage (GCS)**

Jika Anda ingin menyimpan cadangan di Google Cloud Storage (GCS) dan mengunduhnya secara otomatis ke komputer lokal, ikuti langkah-langkah berikut:

1. **Jalankan script upload ini di Google Colab** di akhir Part 5 (menggantikan Cell 8 asli):
   ```python
   # ============================================================
   # CELL: Upload Semua Model Artefak ke Google Cloud Storage
   # ============================================================
   from google.colab import auth
   from google.cloud import storage
   import os

   # Autentikasi akun Google Cloud Anda
   auth.authenticate_user()

   PROJECT_ID = "deductive-reach-443812-q3"
   GCS_BUCKET_NAME = "pnm-ml-model-artifacts" # ⚠️ Ganti dengan nama bucket Anda
   GCS_PREFIX = "cv-recommender/v1/artifacts"

   def upload_artifacts_to_gcs(bucket_name: str, gcs_prefix: str):
       client = storage.Client(project=PROJECT_ID)
       
       # Buat bucket jika belum ada
       try:
           bucket = client.get_bucket(bucket_name)
       except Exception:
           print(f"Bucket {bucket_name} tidak ditemukan. Membuat bucket baru...")
           bucket = client.create_bucket(bucket_name, project=PROJECT_ID, location="asia-southeast2") # Jakarta
           
       artifact_files = [
           "faiss_job_index.bin",
           "job_metadata.csv",
           "job_role_profiles.json",
           "skill_taxonomy.json",
           "model_config.json",
           "assessment_config.json"
       ]
       
       print(f"🔄 Memulai upload ke bucket: {bucket_name}...")
       for filename in artifact_files:
           if os.path.exists(filename):
               gcs_path = f"{gcs_prefix}/{filename}" if gcs_prefix else filename
               blob = bucket.blob(gcs_path)
               blob.upload_from_filename(filename)
               print(f"✅ Berhasil upload: {filename} -> gs://{bucket_name}/{gcs_path}")
           else:
               print(f"❌ File {filename} tidak ditemukan di Colab. Jalankan part sebelumnya terlebih dahulu!")

   upload_artifacts_to_gcs(GCS_BUCKET_NAME, GCS_PREFIX)
   ```

2. **Jalankan script download di terminal komputer lokal Anda:**
   
   Pertama, pastikan Anda sudah login menggunakan Google Cloud SDK di terminal Anda:
   ```bash
   gcloud auth application-default login
   ```
   
   Kemudian, jalankan file `download_models.py` yang sudah saya siapkan:
   ```bash
   python download_models.py [nama-bucket-anda]
   # Contoh: python download_models.py pnm-ml-model-artifacts
   ```
   *Script ini otomatis mengunduh semua file dari GCS dan menyimpannya langsung ke dalam folder `models/`.*

### Taruh File ke Folder `models/` (Jika menggunakan Opsi A atau B)

Jika menggunakan Opsi A atau B, pindahkan/copy semua file ke folder `models/` dalam project ini:

```bash
# Jika download satu per satu (dari folder Downloads)
cp ~/Downloads/faiss_job_index.bin     cv-recommender-api/models/
cp ~/Downloads/job_metadata.csv        cv-recommender-api/models/
cp ~/Downloads/job_role_profiles.json  cv-recommender-api/models/
cp ~/Downloads/skill_taxonomy.json     cv-recommender-api/models/
cp ~/Downloads/model_config.json       cv-recommender-api/models/
cp ~/Downloads/assessment_config.json  cv-recommender-api/models/

# Jika download ZIP
cd ~/Downloads
unzip artifacts_for_deploy.zip -d cv-recommender-api/models/
```

### ✅ Verifikasi

Pastikan folder `models/` berisi file-file ini:
```bash
ls -la cv-recommender-api/models/

# Output yang diharapkan:
# faiss_job_index.bin
# job_metadata.csv
# job_role_profiles.json
# skill_taxonomy.json
# model_config.json
# assessment_config.json
# README.md
```

---

## 3. Test Lokal (Tanpa Docker)

### 3.1 Buat Virtual Environment

```bash
cd cv-recommender-api

# Buat virtual environment
python3 -m venv venv

# Aktifkan
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏱️ Instalasi pertama kali bisa memakan waktu 5-10 menit karena `sentence-transformers` dan `torch` cukup besar.

### 3.3 Jalankan API Server

```bash
# Dari dalam folder cv-recommender-api/
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**Output yang diharapkan:**
```
2026-06-05 10:00:00 [INFO] Menginisialisasi pipeline...
2026-06-05 10:00:05 [INFO] Pipeline siap: 108,963 lowongan terindeks
2026-06-05 10:00:05 [INFO] Pipeline siap melayani request!
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 3.4 Test dengan curl

Buka terminal baru dan jalankan:

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

# Lihat metrics (Part 7)
curl -s http://localhost:8080/metrics | python3 -m json.tool
```

### 3.5 Test via Browser

Buka browser ke:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

Anda bisa test semua endpoint langsung dari Swagger UI.

---

## 4. Test Lokal dengan Docker

### 4.1 Prasyarat
- Docker Desktop sudah terinstal dan berjalan

### 4.2 Build Docker Image

```bash
cd cv-recommender-api

docker build -t cv-recommender-api:v1 .
```

> ⏱️ Build pertama kali bisa memakan waktu 10-15 menit (download model ML di dalam image).

### 4.3 Jalankan Container

```bash
docker run -p 8080:8080 \
  -e ALLOWED_ORIGINS="http://localhost:3000" \
  -e MODEL_DIR="models" \
  cv-recommender-api:v1
```

### 4.4 Test

Sama seperti langkah 3.4 — gunakan `curl` ke `http://localhost:8080`.

---

## 5. Deploy ke Google Cloud Run

### 5.1 Prasyarat

- **Google Cloud SDK (`gcloud`)** sudah terinstal di komputer lokal
  ```bash
  # Cek apakah gcloud sudah terinstal
  gcloud --version
  
  # Jika belum, instal dari:
  # https://cloud.google.com/sdk/docs/install
  ```
- Akun Google Cloud dengan billing aktif
- Project ID: `deductive-reach-443812-q3` (atau project Anda)

### 5.2 Login dan Set Project

```bash
# Login ke GCP
gcloud auth login

# Set project
gcloud config set project deductive-reach-443812-q3
```

### 5.3 Aktifkan API yang Diperlukan

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 5.4 Buat Artifact Registry Repository

```bash
gcloud artifacts repositories create cv-recommender \
    --repository-format=docker \
    --location=asia-southeast1 \
    --description="CV Recommender API Docker images"
```

### 5.5 Build dan Push Docker Image

```bash
cd cv-recommender-api

# Build image di cloud (tidak perlu Docker lokal!)
gcloud builds submit \
    --tag asia-southeast1-docker.pkg.dev/deductive-reach-443812-q3/cv-recommender/api:v1 \
    --timeout=1800
```

> ⏱️ Proses ini bisa memakan waktu 15-20 menit. `--timeout=1800` memberikan waktu 30 menit.

### 5.6 Deploy ke Cloud Run

```bash
gcloud run deploy cv-recommender-api \
    --image asia-southeast1-docker.pkg.dev/deductive-reach-443812-q3/cv-recommender/api:v1 \
    --region asia-southeast1 \
    --platform managed \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 120 \
    --port 8080 \
    --allow-unauthenticated \
    --set-env-vars "MODEL_DIR=models,ALLOWED_ORIGINS=https://your-app.vercel.app"
```

### 5.7 Dapatkan URL Endpoint

```bash
gcloud run services describe cv-recommender-api \
    --region asia-southeast1 \
    --format "value(status.url)"
```

**Output contoh:**
```
https://cv-recommender-api-xxxxx-as.a.run.app
```

> 🎉 **Simpan URL ini!** Ini adalah endpoint API yang bisa diakses dari mana saja.

---

## 6. Test Endpoint Setelah Deploy

Ganti `API_URL` dengan URL yang didapat dari langkah 5.7:

```bash
API_URL="https://cv-recommender-api-xxxxx-as.a.run.app"

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

## 7. Monitoring & Maintenance (Part 7)

### 7.1 Monitoring yang Sudah Built-in

File `app/main.py` sudah mengandung fitur monitoring dari Part 7:

| Fitur | Endpoint/Cara Akses | Keterangan |
|-------|---------------------|------------|
| **Health Check** | `GET /health` | Cek apakah API hidup & model loaded |
| **Request Metrics** | `GET /metrics` | Total request, error rate, latensi P95/P99 |
| **API Key Auth** | Header `X-API-Key` | Aktif jika env `API_KEY` diset |

### 7.2 Melihat Logs di GCP Console

```bash
# Lihat log terbaru
gcloud run services logs read cv-recommender-api \
    --region asia-southeast1 \
    --limit 50

# Atau buka di browser:
# https://console.cloud.google.com/run/detail/asia-southeast1/cv-recommender-api/logs
```

### 7.3 Query Logs di Cloud Logging Explorer

Buka [Cloud Logging](https://console.cloud.google.com/logs) dan gunakan filter:

```
resource.type="cloud_run_revision"
resource.labels.service_name="cv-recommender-api"
```

Filter hanya error:
```
resource.type="cloud_run_revision"
resource.labels.service_name="cv-recommender-api"
severity>=ERROR
```

### 7.4 Setup Alerting (Opsional)

```bash
# Buat alert untuk latensi tinggi (>3 detik P95)
gcloud alpha monitoring policies create \
    --display-name="CV API High Latency" \
    --condition-display-name="P95 > 3s" \
    --condition-filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"' \
    --condition-threshold-value=3000 \
    --notification-channels=YOUR_CHANNEL_ID
```

### 7.5 Mengaktifkan API Key Security

Untuk mengamankan endpoint di production:

```bash
# Update Cloud Run dengan API key
gcloud run services update cv-recommender-api \
    --region asia-southeast1 \
    --set-env-vars "API_KEY=rahasia-kunci-api-anda-123"

# Kemudian request harus menyertakan header:
curl -H "X-API-Key: rahasia-kunci-api-anda-123" \
     -X POST $API_URL/analyze/text ...
```

### 7.6 Kapan Harus Retraining?

| Trigger | Kondisi | Tindakan |
|---------|---------|----------|
| **Scheduled** | Setiap 3 bulan | Pull data baru → jalankan Part 1-5 di Colab → redeploy |
| **Data Drift** | Skill baru >5% total request/minggu | Update `skill_taxonomy.json` |
| **Concept Drift** | >30% skill baru di lowongan terbaru | Full retraining Part 1-5 |
| **User Feedback** | Acceptance rate <60% | Evaluasi ulang model |

### 7.7 Langkah Retraining & Redeploy

```bash
# 1. Jalankan ulang Part 1-5 di Colab dengan data terbaru
# 2. Download artefak baru
# 3. Replace file di folder models/
# 4. Build versi baru
gcloud builds submit \
    --tag asia-southeast1-docker.pkg.dev/deductive-reach-443812-q3/cv-recommender/api:v2 \
    --timeout=1800

# 5. Deploy sebagai canary (tanpa traffic)
gcloud run deploy cv-recommender-api \
    --image ...:v2 \
    --tag canary \
    --no-traffic

# 6. Test canary
curl -s https://canary---cv-recommender-api-xxxxx-as.a.run.app/health

# 7. Migrate traffic ke versi baru
gcloud run services update-traffic cv-recommender-api \
    --to-latest \
    --region asia-southeast1
```

---

## 8. Integrasi Frontend Next.js

Setelah API berhasil di-deploy, frontend Next.js bisa memanggil API ini:

### Contoh: `app/api/analyze/route.ts` (Next.js App Router)

```typescript
const API_URL = process.env.CV_RECOMMENDER_API_URL;

export async function POST(request: Request) {
  const body = await request.json();

  const response = await fetch(`${API_URL}/analyze/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.CV_API_KEY || "",
    },
    body: JSON.stringify({
      cv_text: body.cv_text,
      target_role: body.target_role,
      top_k: body.top_k || 5,
    }),
  });

  if (!response.ok) {
    return Response.json(
      { error: "Gagal menganalisis CV" },
      { status: response.status }
    );
  }

  const data = await response.json();
  return Response.json(data);
}
```

### Environment Variables di Vercel

```
CV_RECOMMENDER_API_URL=https://cv-recommender-api-xxxxx-as.a.run.app
CV_API_KEY=rahasia-kunci-api-anda-123
```

---

## 9. Estimasi Biaya

| Komponen | Spesifikasi | Biaya/bulan |
|----------|------------|-------------|
| Cloud Run | 2 vCPU, 2GB RAM, min 0 instance | ~$5-15 |
| Artifact Registry | ~2GB image | ~$0.26 |
| Cloud Build | ~30 min build/bulan | ~$0.12 |
| **Total** | | **~$5-16/bulan** |

> Cloud Run mengenakan biaya hanya saat ada request (scale-to-zero). Sangat efisien untuk project yang belum banyak traffic.

---

## 10. Troubleshooting

### ❌ Error: `ModuleNotFoundError` saat test lokal
**Solusi:** Pastikan virtual environment aktif dan dependencies terinstal:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Error: `FileNotFoundError: faiss_job_index.bin`
**Solusi:** Folder `models/` belum diisi. Download artefak dari Colab (lihat [Langkah 2](#2-download-artefak-dari-google-colab)).

### ❌ Error: `Container failed to start` di Cloud Run
**Solusi:**
1. Pastikan folder `models/` berisi semua file artefak sebelum build Docker
2. Cek logs: `gcloud run services logs read cv-recommender-api --region asia-southeast1`
3. Pastikan port 8080 digunakan

### ❌ Error: `CORS error` dari frontend Vercel
**Solusi:** Update `ALLOWED_ORIGINS` di Cloud Run:
```bash
gcloud run services update cv-recommender-api \
    --region asia-southeast1 \
    --set-env-vars "ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000"
```

### ❌ Error: Docker build timeout
**Solusi:** Gunakan `--timeout=1800` pada `gcloud builds submit`. Download model sentence-transformers bisa memakan waktu.

### ❌ Error: `403 API key tidak valid`
**Solusi:** 
- Jika development: Kosongkan `API_KEY` di `.env` (security dinonaktifkan)
- Jika production: Pastikan header `X-API-Key` sesuai dengan env var `API_KEY`

---

## 📝 Checklist Deployment

Gunakan checklist ini untuk memastikan semua langkah sudah dilakukan:

- [ ] Part 1-5 selesai dijalankan di Google Colab
- [ ] Semua 6 file artefak sudah didownload dari Colab
- [ ] File artefak sudah ditaruh di folder `models/`
- [ ] Test lokal berhasil (`uvicorn app.main:app`)
- [ ] Endpoint `/health` merespons `{"status": "healthy"}`
- [ ] Endpoint `/analyze/text` merespons dengan rekomendasi
- [ ] (Opsional) Docker build lokal berhasil
- [ ] (Opsional) Deploy ke Cloud Run berhasil
- [ ] (Opsional) API key security diaktifkan
- [ ] (Opsional) Frontend Next.js terhubung ke API
