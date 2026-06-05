"""FastAPI entry point untuk CV Recommender API."""
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

# CORS untuk Next.js/Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API Key Security (opsional — aktif jika env API_KEY diset)
# ============================================================
API_KEY = os.getenv("API_KEY", "")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifikasi API key dari header request."""
    if not API_KEY:
        return  # Skip jika API_KEY tidak diset (development mode)
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="API key tidak valid")


# ============================================================
# In-memory Metrics (Part 7: Monitoring)
# ============================================================
request_metrics = {
    "total_requests": 0,
    "total_errors": 0,
    "latencies": [],
    "roles_requested": defaultdict(int),
}


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Catat metrik untuk setiap request."""
    start = time.time()
    response = await call_next(request)
    latency = (time.time() - start) * 1000

    request_metrics["total_requests"] += 1
    request_metrics["latencies"].append(latency)

    # Simpan hanya 1000 latensi terakhir
    if len(request_metrics["latencies"]) > 1000:
        request_metrics["latencies"] = request_metrics["latencies"][-1000:]

    if response.status_code >= 400:
        request_metrics["total_errors"] += 1

    return response


# ============================================================
# Inisialisasi pipeline saat startup
# ============================================================
pipeline: Optional[CVAnalysisPipeline] = None


@app.on_event("startup")
async def startup():
    global pipeline
    logger.info("Menginisialisasi pipeline...")
    pipeline = CVAnalysisPipeline(
        model_dir=settings.MODEL_DIR,
        embedding_model_name=settings.EMBEDDING_MODEL,
    )
    logger.info("Pipeline siap melayani request!")


# ============================================================
# Request/Response Models
# ============================================================
class TextAnalyzeRequest(BaseModel):
    cv_text: str
    target_role: str
    top_k: int = 5


class StructuredInput(BaseModel):
    skills: List[str]
    experience_years: int
    education: str
    target_role: str
    summary: str = ""


# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": pipeline is not None}


@app.get("/roles")
async def list_roles():
    """Daftar peran pekerjaan yang didukung."""
    return {"roles": list(pipeline.job_profiles.keys())}


@app.get("/metrics")
async def get_metrics():
    """Endpoint internal untuk melihat metrik performa (Part 7)."""
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
    """Analisis CV dari teks langsung."""
    try:
        request_metrics["roles_requested"][request.target_role] += 1
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
    """Analisis CV dari file PDF yang diunggah."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diterima")
    try:
        request_metrics["roles_requested"][target_role] += 1
        content = await file.read()
        text_pages = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
        cv_text = "\n".join(text_pages)
        if len(cv_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="PDF tidak mengandung teks yang cukup")
        result = pipeline.analyze(cv_text, target_role, top_k)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze/structured", dependencies=[Depends(verify_api_key)])
async def analyze_structured(request: StructuredInput):
    """Analisis dari input terstruktur (tanpa PDF)."""
    cv_text = f"""
    Professional with {request.experience_years} years of experience.
    Education: {request.education}. Target: {request.target_role}.
    Skills: {", ".join(request.skills)}. {request.summary}
    """
    try:
        request_metrics["roles_requested"][request.target_role] += 1
        result = pipeline.analyze(cv_text.strip(), request.target_role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
