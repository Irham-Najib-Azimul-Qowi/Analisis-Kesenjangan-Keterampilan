# ==============================================================================
# 🚀 ENTRY POINT API: REST API Server untuk Sistem CV Recommender (FastAPI Backend)
# Berkas ini mendefinisikan seluruh route/endpoint API, skema request/response (Pydantic),
# serta middleware untuk logging metrik pemantauan, dan skema keamanan API Key.
# ==============================================================================

# Mengimpor modul bawaan Python 'logging' untuk mencatat peristiwa aplikasi di console
import logging

# Mengimpor modul bawaan Python 'os' untuk mengakses variabel lingkungan (Environment Variables)
import os

# Mengimpor modul bawaan Python 'time' untuk mengukur waktu durasi pemrosesan (latensi)
import time

# Mengimpor modul bawaan Python untuk mengetik struktur data kontainer dengan statis
from typing import List, Optional
from collections import defaultdict

# Mengimpor kelas inti dan dependensi keamanan dari pustaka 'fastapi'
# FastAPI: Kelas utama pembuat aplikasi web API
# UploadFile & File: Mengelola kiriman berkas multipart (seperti PDF CV)
# Form: Membaca parameter isian data dari form-data HTTP
# HTTPException: Mengembalikan error HTTP spesifik (seperti 400 Bad Request)
# Depends: Dependency injection untuk menyisipkan fungsi pra-syarat (middleware endpoint)
# Security: Dependency injection khusus untuk memicu otentikasi keamanan
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Security

# Mengimpor middleware CORS untuk mengizinkan lintas domain web browser
from fastapi.middleware.cors import CORSMiddleware

# Mengimpor skema keamanan API Key Header dari modul security FastAPI
from fastapi.security import APIKeyHeader

# Mengimpor kelas 'BaseModel' dari pustaka 'pydantic' untuk validasi skema data masukan JSON
from pydantic import BaseModel

# Mengimpor pustaka 'pdfplumber' untuk melakukan parsing teks dari dokumen PDF
import pdfplumber

# Mengimpor modul 'BytesIO' untuk membaca aliran data byte berkas di memori tanpa menulis ke disk
from io import BytesIO

# Mengimpor pustaka 'numpy' (sebagai np) untuk operasi pemantauan statistik metrik (seperti mean)
import numpy as np

# Mengimpor konfigurasi global settings dari berkas lokal config.py
from .config import settings

# Mengimpor kelas pipeline analisis CV dari berkas lokal pipeline.py
from .pipeline import CVAnalysisPipeline

# Mengatur konfigurasi logging dasar di tingkat INFO
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ==============================================================================
# 🎮 INISIALISASI FASTAPI
# ==============================================================================
app = FastAPI(
    title="CV Recommender & Skill Assessment API",
    description="API untuk analisis CV, rekomendasi pekerjaan, dan penilaian skill",
    version="1.0.0",
)

# Menambahkan middleware CORS (Cross-Origin Resource Sharing) ke aplikasi
# Ini memungkinkan dashboard Streamlit (yang di-host di port/domain berbeda)
# untuk mengirimkan HTTP request ke backend ini tanpa diblokir oleh browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Daftar origin domain yang diperbolehkan
    allow_credentials=True,                  # Mengizinkan kiriman cookies dan otentikasi
    allow_methods=["*"],                     # Mengizinkan semua metode HTTP (GET, POST, dll)
    allow_headers=["*"],                     # Mengizinkan semua HTTP Headers
)


# ==============================================================================
# 🛡️ PENGAMANAN API KEY (Security Header)
# ==============================================================================
# Membaca token API Key dari variabel lingkungan sistem (env). Default kosong untuk pengembangan.
API_KEY = os.getenv("API_KEY", "")
# Menentukan nama header HTTP kustom "X-API-Key" sebagai penampung token otentikasi
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Fungsi verifikasi kunci API Key yang dikirim di header HTTP
async def verify_api_key(api_key: str = Security(api_key_header)):
    # Jika API_KEY di server tidak diaktifkan (dibiarkan kosong), lewati verifikasi keamanan
    if not API_KEY:
        return
    # Jika API Key dari pengirim header tidak cocok dengan kunci server, lempar error HTTP 403 Forbidden
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="API key tidak valid")


# ==============================================================================
# 📊 METRIK MONITORING (Request Analytics)
# ==============================================================================
# Dictionary sederhana di memori RAM (in-memory) untuk mencatat statistik request masuk
request_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "latencies": [],
    "roles_requested": defaultdict(int),
}

# Middleware HTTP untuk menghitung waktu respon dan kesalahan per HTTP request secara otomatis
@app.middleware("http")
async def metrics_middleware(request, call_next):
    # Catat waktu awal mulai request
    start = time.time()
    # Lanjutkan pemrosesan request untuk mendapatkan HTTP response
    response = await call_next(request)
    # Hitung waktu selisih dalam milidetik (latensi)
    latency = (time.time() - start) * 1000

    # Rekam metrik request ke dictionary
    request_metrics["total_requests"] += 1
    request_metrics["latencies"].append(latency)

    # Batasi agar list latensi hanya menyimpan maksimal 1000 data terakhir untuk mencegah kebocoran memori RAM
    if len(request_metrics["latencies"]) > 1000:
        request_metrics["latencies"] = request_metrics["latencies"][-1000:]

    # Jika response menghasilkan status gagal (status code >= 400), tambahkan hitungan error
    if response.status_code >= 400:
        request_metrics["total_errors"] += 1

    return response


# ==============================================================================
# ⚡ EVENT HANDLER STARTUP (Hot-Loading Model AI)
# ==============================================================================
pipeline: Optional[CVAnalysisPipeline] = None

# Mengaktifkan event handler yang dieksekusi sekali saat server FastAPI pertama kali dihidupkan
@app.on_event("startup")
async def startup():
    global pipeline
    logger.info("Menginisialisasi pipeline...")
    # Memuat SentenceTransformer BERT dan FAISS Index ke memori RAM sekali di awal (warm-up)
    pipeline = CVAnalysisPipeline(
        model_dir=settings.MODEL_DIR,
        embedding_model_name=settings.EMBEDDING_MODEL,
    )
    logger.info("Pipeline siap melayani request!")


# ==============================================================================
# 📑 SKEMA VALIDASI DATA (Pydantic Models)
# ==============================================================================
# Pydantic memvalidasi tipe data input JSON secara otomatis sebelum diproses oleh route
class TextAnalyzeRequest(BaseModel):
    cv_text: str            # Teks isi CV
    target_role: str        # Nama peran target pekerjaan
    top_k: int = 5          # Jumlah rekomendasi lowongan (default 5)

class StructuredInput(BaseModel):
    skills: List[str]       # List nama keahlian
    experience_years: int   # Jumlah tahun pengalaman
    education: str          # Jenjang pendidikan terakhir
    target_role: str        # Nama peran target pekerjaan
    summary: str = ""       # Ringkasan minat karir opsional


# ==============================================================================
# 🛣️ ENDPOINTS REST API
# ==============================================================================

# Endpoint: GET /health
# Penjelasan: Digunakan untuk memeriksa kesehatan server (Health Check)
@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": pipeline is not None}


# Endpoint: GET /roles
# Penjelasan: Mengembalikan daftar seluruh peran jabatan target yang didukung oleh sistem
@app.get("/roles")
async def list_roles():
    return {"roles": list(pipeline.job_profiles.keys())}


# Endpoint: GET /metrics
# Penjelasan: Mengembalikan ringkasan statistik performa backend (latensi mean, p95, p99)
@app.get("/metrics")
async def get_metrics():
    lats = request_metrics["latencies"]
    # Menghitung nilai mean (rata-rata) dan percentile menggunakan numpy (np.percentile)
    return {
        "total_requests": request_metrics["total_requests"],
        "total_errors": request_metrics["total_errors"],
        "error_rate": (request_metrics["total_errors"] / max(request_metrics["total_requests"], 1)),
        "latency": {
            "mean_ms": round(float(np.mean(lats)), 1) if lats else 0,
            "p95_ms": round(float(np.percentile(lats, 95)), 1) if lats else 0,
            "p99_ms": round(float(np.percentile(lats, 99)), 1) if lats else 0,
        },
        "roles_distribution": dict(request_metrics["roles_requested"]),
    }


# Endpoint: POST /analyze/text
# Penjelasan: Menganalisis CV berdasarkan input teks bebas mentah (JSON Body)
@app.post("/analyze/text", dependencies=[Depends(verify_api_key)])
async def analyze_text(request: TextAnalyzeRequest):
    try:
        # Catat distribusi request peran
        request_metrics["roles_requested"][request.target_role] += 1
        # Panggil pipeline untuk menjalankan analisis ML semantik + skill gap
        result = pipeline.analyze(request.cv_text, request.target_role, request.top_k)
        return result
    except ValueError as e:
        # Mengembalikan error 400 Bad Request jika input data tidak valid
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        # Mengembalikan error 500 Internal Server Error untuk kegagalan sistem lainnya
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint: POST /analyze/pdf
# Penjelasan: Menganalisis CV berdasarkan unggahan file PDF asli (Multipart Form-Data)
@app.post("/analyze/pdf", dependencies=[Depends(verify_api_key)])
async def analyze_pdf(
    file: UploadFile = File(...),         # Parameter berkas file binary
    target_role: str = Form(...),         # Parameter target peran dari form field
    top_k: int = Form(5),                 # Parameter top k rekomendasi dari form field
):
    # Validasi: ekstensi file wajib berakhiran .pdf
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diterima")
    try:
        request_metrics["roles_requested"][target_role] += 1
        
        # Membaca konten biner file secara asinkron dari memory buffer
        content = await file.read()
        text_pages = []
        
        # Membuka biner PDF menggunakan pdfplumber.open() dengan perantara BytesIO
        with pdfplumber.open(BytesIO(content)) as pdf:
            # Melakukan iterasi untuk setiap halaman dokumen PDF
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
                    
        # Menggabungkan seluruh teks antar halaman menggunakan pemisah baris baru (\n)
        cv_text = "\n".join(text_pages)
        if len(cv_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="PDF tidak mengandung teks yang cukup untuk dianalisis.")
            
        # Jalankan pipeline ML terhadap teks hasil ekstraksi PDF
        result = pipeline.analyze(cv_text, target_role, top_k)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint: POST /analyze/structured
# Penjelasan: Menganalisis CV berdasarkan isian formulir profil terstruktur (JSON Body)
@app.post("/analyze/structured", dependencies=[Depends(verify_api_key)])
async def analyze_structured(request: StructuredInput):
    # Merekayasa/merangkai data isian terstruktur menjadi string teks profil deskriptif (pseudo-CV)
    cv_text = f"""
    Professional with {request.experience_years} years of experience.
    Education: {request.education}. Target: {request.target_role}.
    Skills: {", ".join(request.skills)}. {request.summary}
    """
    try:
        request_metrics["roles_requested"][request.target_role] += 1
        # Jalankan analisis pipeline ML
        result = pipeline.analyze(cv_text.strip(), request.target_role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


