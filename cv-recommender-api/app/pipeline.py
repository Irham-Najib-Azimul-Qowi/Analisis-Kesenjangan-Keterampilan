"""
Pipeline inferensi CV Analysis.
File ini menyatukan model NLP (SentenceTransformers / BERT), indeks pencarian cepat FAISS,
dan modul evaluasi skill agar dapat digunakan secara terpadu baik di API maupun langsung di Streamlit.
"""
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
    """
    Pipeline terpadu untuk analisis CV dan rekomendasi pekerjaan.
    Kelas ini menggabungkan pencarian semantik lowongan kerja (FAISS + SentenceTransformer)
    dengan analisis kesenjangan kompetensi standar industri (Skill Gap Assessment).
    """

    def __init__(self, model_dir: str, embedding_model_name: str):
        """
        Inisialisasi pipeline: Memuat model embedding BERT, membaca indeks FAISS,
        membuat database metadata lowongan, serta membaca standar profil keahlian industri.
        
        Parameter:
        - model_dir (str): Folder tempat menyimpan file model dan metadata.
        - embedding_model_name (str): Nama model SentenceTransformer (misalnya 'all-MiniLM-L6-v2').
        """
        logger.info("Menginisialisasi CVAnalysisPipeline...")

        # 1. Memuat model embedding SentenceTransformer (BERT-based) untuk konversi teks ke vektor numerik
        self.embed_model = SentenceTransformer(embedding_model_name)

        # 2. Memuat indeks FAISS (.bin) yang berisi vektor representasi dari ribuan deskripsi lowongan kerja
        self.faiss_index = faiss.read_index(f"{model_dir}/faiss_job_index.bin")

        # 3. Memuat data metadata pekerjaan (seperti job_title, company_name, dll.) yang berkorespondensi dengan indeks FAISS
        self.df_jobs = pd.read_csv(f"{model_dir}/job_metadata.csv")

        # 4. Memuat profil standar keahlian industri untuk setiap jabatan target (misal: core_skills, expected_skills, dll.)
        with open(f"{model_dir}/job_role_profiles.json") as f:
            self.job_profiles = json.load(f)

        # 5. Memuat kamus taksonomi skill global dan meratakannya (flattening) agar pencarian kata kunci menjadi cepat
        taxonomy = load_skill_taxonomy(f"{model_dir}/skill_taxonomy.json")
        self.flat_skills = build_flat_skills(taxonomy)

        logger.info(f"Pipeline siap: {self.faiss_index.ntotal:,} lowongan terindeks")

    def analyze(self, cv_text: str, target_role: str, top_k: int = 5) -> Dict:
        """
        Menjalankan alur analisis lengkap terhadap CV pelamar:
        1. Memberikan rekomendasi lowongan pekerjaan semantik terdekat (hybrid search).
        2. Menilai kesesuaian skill pelamar terhadap standar profesi target.
        
        Parameter:
        - cv_text (str): Teks isi CV pelamar.
        - target_role (str): Jabatan target yang ingin dianalisis kecocokannya.
        - top_k (int): Jumlah lowongan kerja rekomendasi yang ingin dihasilkan.
        
        Return:
        - Dict: Gabungan hasil rekomendasi lowongan dan assessment skill beserta metrik latensi.
        """
        start = time.time()

        # Validasi Input
        if not cv_text or len(cv_text.strip()) < 20:
            raise ValueError("Teks CV terlalu pendek (min 20 karakter)")
        if target_role not in self.job_profiles:
            raise ValueError(f"Peran tidak tersedia. Pilihan: {list(self.job_profiles.keys())}")

        # Langkah A: Panggil pencarian lowongan kerja rekomendasi berbasis kemiripan semantik & kecocokan skill
        recommendations = self._recommend(cv_text, top_k)

        # Langkah B: Panggil evaluasi skill gap pelamar terhadap peran target
        assessment = assess_skills(cv_text, target_role, self.job_profiles, self.flat_skills)

        # Hitung durasi pemrosesan (latensi) dalam milidetik
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
        """
        Fungsi internal untuk melakukan pencarian rekomendasi lowongan pekerjaan terdekat secara hibrida.
        
        Algoritma Pencarian Hibrida (Hybrid Search):
        1. Encode teks CV pelamar menjadi vektor embedding 384 dimensi.
        2. Lakukan pencarian K-Nearest Neighbors (KNN) menggunakan indeks FAISS berdasarkan Cosine Similarity.
        3. Dapatkan kandidat awal (mengambil top_k * 3 kandidat untuk disaring kembali).
        4. Lakukan perangkingan ulang (re-ranking) menggunakan kombinasi linear (Hybrid Score):
           Skor Akhir = (0.7 * Skor Semantik BERT) + (0.3 * Skor Overlap Skill Jaccard)
           Ini menjamin lowongan yang disarankan tidak hanya memiliki kemiripan deskripsi (kontekstual),
           tetapi juga memiliki kecocokan secara eksplisit pada kata kunci skill teknis yang dibutuhkan.
        
        Parameter:
        - cv_text (str): Teks CV pelamar.
        - top_k (int): Jumlah rekomendasi akhir yang ingin ditampilkan.
        
        Return:
        - List[Dict]: Daftar lowongan teratas yang diurutkan berdasarkan Skor Akhir.
        """
        # 1. Mengubah teks CV menjadi vektor embedding BERT, dinormalisasi agar bisa menggunakan cosine similarity
        emb = self.embed_model.encode([cv_text], normalize_embeddings=True).astype(np.float32)
        
        # 2. Cari kandidat awal di indeks FAISS (mengambil 3 kali lipat dari top_k untuk kebutuhan filter/ranking ulang)
        scores, indices = self.faiss_index.search(emb, min(top_k * 3, self.faiss_index.ntotal))

        # 3. Ekstrak skill dari CV pelamar sekali saja untuk perbandingan overlap nanti
        cv_skills = set()
        for v in extract_skills(cv_text, self.flat_skills).values():
            cv_skills.update(s.lower() for s in v)

        recs = []
        # 4. Iterasi hasil pencarian awal FAISS
        for score, idx in zip(scores[0], indices[0]):
            # Abaikan jika skor semantik terlalu rendah (di bawah threshold 0.15) atau indeks di luar rentang metadata
            if score < 0.15 or idx >= len(self.df_jobs):
                continue
                
            row = self.df_jobs.iloc[idx]
            
            # Satukan deskripsi lowongan dan skill yang diminta untuk diekstraksi kata kuncinya
            job_text = str(row.get("job_description", "")) + " " + str(row.get("skills_required", ""))
            job_skills = set()
            for v in extract_skills(job_text, self.flat_skills).values():
                job_skills.update(s.lower() for s in v)

            # Hitung skill yang cocok (irisan) dan persentase overlap skill
            matched = cv_skills & job_skills
            overlap = len(matched) / max(len(job_skills), 1)
            
            # Hitung nilai gabungan Hybrid Score (70% semantic similarity + 30% Jaccard skill overlap)
            combined = 0.7 * float(score) + 0.3 * overlap

            # Masukkan kandidat ke daftar rekomendasi
            recs.append({
                "rank": 0,  # Akan diisi setelah diurutkan ulang
                "job_title": str(row.get("job_title", "N/A")),
                "company_name": str(row.get("company_name", "N/A")),
                "location": str(row.get("location", "N/A")),
                "confidence_score": round(combined, 4),
                "matched_skills": sorted(list(matched)),
                "missing_skills": sorted(list(job_skills - cv_skills))[:8], # Batasi maksimal 8 skill yang kurang untuk tampilan UI
                "reasoning": f"Kecocokan {float(score)*100:.0f}%, {len(matched)} skill cocok",
            })

        # 5. Urutkan ulang kandidat berdasarkan Hybrid Score secara descending (terbesar ke terkecil)
        recs.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        # 6. Berikan nomor peringkat (rank) untuk lowongan teratas sejumlah top_k
        for i, r in enumerate(recs[:top_k]):
            r["rank"] = i + 1
            
        return recs[:top_k]

