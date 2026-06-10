"""
FastAPI entry point untuk CV Recommender API.
File ini mendefinisikan seluruh route/endpoint REST API, skema request/response (Pydantic),
serta middleware untuk logging metrik, dan skema keamanan API Key.
"""
import logging
import os
import time
from typing import List, Optional
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import pdfplumber
from io import BytesIO
import numpy as np

from .config import settings
from .pipeline import CVAnalysisPipeline

# Konfigurasi logging standar untuk mencatat log aplikasi di console/terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# Inisialisasi FastAPI
# ============================================================
app = FastAPI(
    title="CV Recommender & Skill Assessment API",
    description="API untuk analisis CV, rekomendasi pekerjaan, dan penilaian skill",
    version="1.0.0",
)

# CORS (Cross-Origin Resource Sharing) Middleware. 
# Berguna agar web frontend (seperti Next.js / Streamlit) yang berada di domain/host 
# berbeda dapat mengirimkan HTTP request ke backend API ini tanpa diblokir browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API Key Security (Keamanan API Key)
# ============================================================
# Membaca kunci API dari environment variables. Jika tidak diset, maka mode pengamanan dinonaktifkan.
API_KEY = os.getenv("API_KEY", "")
# Menentukan header kustom bernama "X-API-Key" untuk otentikasi request
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Fungsi Dependency Injection untuk memverifikasi kecocokan API Key yang dikirimkan di header HTTP.
    Jika API_KEY di server tidak kosong dan header tidak cocok, maka kirim HTTP 403 Forbidden.
    """
    if not API_KEY:
        return  # Lewati verifikasi jika API_KEY tidak didefinisikan (mode pengembangan/dev)
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="API key tidak valid")


# ============================================================
# In-memory Metrics (Metrik Pemantauan / Monitoring)
# ============================================================
# Dictionary sederhana untuk menyimpan riwayat request, kesalahan, latensi, dan sebaran peran target.
request_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "latencies": [],
    "roles_requested": defaultdict(int),
}


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """
    Middleware HTTP untuk mencatat statistik performa sistem:
    - Menghitung jumlah total request masuk.
    - Mengukur waktu respon (latensi) dalam milidetik.
    - Mencatat jika ada error (status code >= 400).
    """
    start = time.time()
    response = await call_next(request)
    latency = (time.time() - start) * 1000

    # Rekam metrik request
    request_metrics["total_requests"] += 1
    request_metrics["latencies"].append(latency)

    # Batasi agar list latensi hanya menyimpan maksimal 1000 data terakhir untuk efisiensi memori RAM
    if len(request_metrics["latencies"]) > 1000:
        request_metrics["latencies"] = request_metrics["latencies"][-1000:]

    # Jika response gagal/error, tambahkan hitungan error
    if response.status_code >= 400:
        request_metrics["total_errors"] += 1

    return response


# ============================================================
# Inisialisasi pipeline saat startup (Startup Event)
# ============================================================
pipeline: Optional[CVAnalysisPipeline] = None


@app.on_event("startup")
async def startup():
    """
    Event Handler yang dijalankan sekali saja saat server FastAPI pertama kali dinyalakan.
    Digunakan untuk memuat model BERT dan indeks FAISS ke dalam RAM agar saat request masuk,
    proses prediksi berjalan secara instan (hot-loaded).
    """
    global pipeline
    logger.info("Menginisialisasi pipeline...")
    pipeline = CVAnalysisPipeline(
        model_dir=settings.MODEL_DIR,
        embedding_model_name=settings.EMBEDDING_MODEL,
    )
    logger.info("Pipeline siap melayani request!")


# ============================================================
# Request/Response Models (Skema Validasi Pydantic)
# ============================================================
class TextAnalyzeRequest(BaseModel):
    """Skema input untuk analisis berbasis teks mentah."""
    cv_text: str
    target_role: str
    top_k: int = 5


class StructuredInput(BaseModel):
    """Skema input untuk profil kompetensi terstruktur (isian formulir manual)."""
    skills: List[str]
    experience_years: int
    education: str
    target_role: str
    summary: str = ""


# ============================================================
# API Endpoints (Daftar Route API)
# ============================================================

@app.get("/health")
async def health():
    """
    Endpoint sederhana untuk memeriksa kesehatan sistem (Health Check).
    Digunakan oleh server monitor / load balancer untuk memastikan server dalam kondisi aktif.
    """
    return {"status": "healthy", "model_loaded": pipeline is not None}


@app.get("/roles")
async def list_roles():
    """
    Endpoint untuk mendapatkan daftar seluruh peran pekerjaan standar yang didukung oleh model.
    """
    return {"roles": list(pipeline.job_profiles.keys())}


@app.get("/metrics")
async def get_metrics():
    """
    Endpoint internal untuk memantau metrik performa API (Part 7: Monitoring).
    Menghasilkan nilai rata-rata latensi, percentile 95% (p95), percentile 99% (p99), 
    serta distribusi request jabatan target.
    """
    lats = request_metrics["latencies"]
    return {
        "total_requests": request_metrics["total_requests"],
        "total_errors": request_metrics["total_errors"],
        "error_rate": (request_metrics["total_errors"] /
                       max(request_metrics["total_requests"], 1)),
        "latency": {
            "mean_ms": round(float(np.mean(lats)), 1) if lats else 0,
            "p95_ms": round(float(np.percentile(lats, 95)), 1) if lats else 0,
            "p99_ms": round(float(np.percentile(lats, 99)), 1) if lats else 0,
        },
        "roles_distribution": dict(request_metrics["roles_requested"]),
    }


@app.post("/analyze/text", dependencies=[Depends(verify_api_key)])
async def analyze_text(request: TextAnalyzeRequest):
    """
    Endpoint untuk menganalisis CV dari kiriman teks string langsung.
    Akses dilindungi oleh otentikasi verify_api_key.
    """
    try:
        # Catat distribusi request peran
        request_metrics["roles_requested"][request.target_role] += 1
        
        # Panggil pipeline machine learning untuk menganalisis teks
        result = pipeline.analyze(request.cv_text, request.target_role, request.top_k)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze/pdf", dependencies=[Depends(verify_api_key)])
async def analyze_pdf(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    top_k: int = Form(5),
):
    """
    Endpoint untuk menganalisis CV dari berkas PDF yang diunggah.
    Fungsi ini melakukan parsing teks dari PDF menggunakan library pdfplumber sebelum dikirim ke pipeline.
    """
    # Validasi ekstensi file harus berupa PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diterima")
    try:
        request_metrics["roles_requested"][target_role] += 1
        
        # Baca konten file secara asinkron
        content = await file.read()
        text_pages = []
        
        # Parsing teks per halaman dari buffer PDF
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
                    
        # Gabungkan teks halaman dengan baris baru
        cv_text = "\n".join(text_pages)
        if len(cv_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="PDF tidak mengandung teks yang cukup")
            
        # Jalankan pipeline ML terhadap hasil ekstraksi teks PDF
        result = pipeline.analyze(cv_text, target_role, top_k)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze/structured", dependencies=[Depends(verify_api_key)])
async def analyze_structured(request: StructuredInput):
    """
    Endpoint untuk menganalisis profil pelamar dari isian formulir manual (input terstruktur).
    Mengonversi atribut isian (pengalaman, pendidikan, skill) menjadi format teks ringkas (pseudo-CV)
    lalu mengirimkannya ke pipeline ML.
    """
    # Rekayasa teks pseudo-CV berdasarkan parameter form
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

