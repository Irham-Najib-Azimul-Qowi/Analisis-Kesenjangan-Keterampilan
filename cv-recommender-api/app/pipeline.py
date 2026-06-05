"""Pipeline inferensi CV Analysis."""
import time
import json
import logging
from typing import Dict, List

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

from .skill_utils import extract_skills, assess_skills, load_skill_taxonomy, build_flat_skills

logger = logging.getLogger(__name__)


class CVAnalysisPipeline:
    """Pipeline terpadu untuk analisis CV dan rekomendasi pekerjaan."""

    def __init__(self, model_dir: str, embedding_model_name: str):
        logger.info("Menginisialisasi CVAnalysisPipeline...")

        # Muat model embedding
        self.embed_model = SentenceTransformer(embedding_model_name)

        # Muat indeks FAISS
        self.faiss_index = faiss.read_index(f"{model_dir}/faiss_job_index.bin")

        # Muat metadata
        self.df_jobs = pd.read_csv(f"{model_dir}/job_metadata.csv")

        # Muat profil dan taxonomy
        with open(f"{model_dir}/job_role_profiles.json") as f:
            self.job_profiles = json.load(f)

        taxonomy = load_skill_taxonomy(f"{model_dir}/skill_taxonomy.json")
        self.flat_skills = build_flat_skills(taxonomy)

        logger.info(f"Pipeline siap: {self.faiss_index.ntotal:,} lowongan terindeks")

    def analyze(self, cv_text: str, target_role: str, top_k: int = 5) -> Dict:
        """Analisis CV: rekomendasi pekerjaan + penilaian skill."""
        start = time.time()

        # Validasi
        if not cv_text or len(cv_text.strip()) < 20:
            raise ValueError("Teks CV terlalu pendek (min 20 karakter)")
        if target_role not in self.job_profiles:
            raise ValueError(f"Peran tidak tersedia. Pilihan: {list(self.job_profiles.keys())}")

        # Rekomendasi pekerjaan
        recommendations = self._recommend(cv_text, top_k)

        # Penilaian skill
        assessment = assess_skills(cv_text, target_role, self.job_profiles, self.flat_skills)

        latency = (time.time() - start) * 1000

        return {
            "status": "success",
            "target_role": target_role,
            "recommended_jobs": recommendations,
            "skill_assessment": assessment,
            "overall_readiness_score": assessment["overall_readiness_score"],
            "metadata": {
                "model_version": "1.0.0",
                "latency_ms": round(latency, 1),
                "supported_roles": list(self.job_profiles.keys()),
            },
        }

    def _recommend(self, cv_text: str, top_k: int) -> List[Dict]:
        """Cari lowongan pekerjaan terdekat secara semantik."""
        emb = self.embed_model.encode([cv_text], normalize_embeddings=True).astype(np.float32)
        scores, indices = self.faiss_index.search(emb, min(top_k * 3, self.faiss_index.ntotal))

        cv_skills = set()
        for v in extract_skills(cv_text, self.flat_skills).values():
            cv_skills.update(s.lower() for s in v)

        recs = []
        for score, idx in zip(scores[0], indices[0]):
            if score < 0.15 or idx >= len(self.df_jobs):
                continue
            row = self.df_jobs.iloc[idx]
            job_text = str(row.get("job_description", "")) + " " + str(row.get("skills_required", ""))
            job_skills = set()
            for v in extract_skills(job_text, self.flat_skills).values():
                job_skills.update(s.lower() for s in v)

            matched = cv_skills & job_skills
            overlap = len(matched) / max(len(job_skills), 1)
            combined = 0.7 * float(score) + 0.3 * overlap

            recs.append({
                "rank": 0,
                "job_title": str(row.get("job_title", "N/A")),
                "company_name": str(row.get("company_name", "N/A")),
                "location": str(row.get("location", "N/A")),
                "confidence_score": round(combined, 4),
                "matched_skills": sorted(list(matched)),
                "missing_skills": sorted(list(job_skills - cv_skills))[:8],
                "reasoning": f"Kecocokan {float(score)*100:.0f}%, {len(matched)} skill cocok",
            })

        recs.sort(key=lambda x: x["confidence_score"], reverse=True)
        for i, r in enumerate(recs[:top_k]):
            r["rank"] = i + 1
        return recs[:top_k]
