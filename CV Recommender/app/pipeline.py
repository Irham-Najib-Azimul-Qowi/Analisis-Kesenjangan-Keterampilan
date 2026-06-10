# ==============================================================================
# 🧠 PIPELINE UTAMA: Integrasi Pencarian Semantik dan Kesenjangan Skill (BERT + FAISS)
# Berkas ini menggabungkan pencarian semantik teks (BERT) dengan pencarian
# kemiripan cepat (FAISS index) dan logika evaluasi kecocokan skill (Jaccard).
# ==============================================================================

# Mengimpor modul bawaan Python 'time' untuk mengukur latensi waktu respon eksekusi model
import time

# Mengimpor modul bawaan Python 'json' untuk memparsing berkas profil berformat JSON
import json

# Mengimpor modul bawaan Python 'logging' untuk mencatat status proses aplikasi di terminal
import logging

# Mengimpor kelas pendukung pengetikan statis dari modul 'typing'
from typing import Dict, List

# Mengimpor library 'numpy' (sebagai np) untuk manipulasi array numerik berdimensi tinggi
import numpy as np

# Mengimpor library 'pandas' (sebagai pd) untuk membaca metadata lowongan kerja berformat CSV
import pandas as pd

# Mengimpor library 'faiss' untuk pencarian kemiripan vektor berdimensi tinggi secara instan
import faiss

# Mengimpor kelas 'SentenceTransformer' dari pustaka sentence-transformers untuk vektorisasi teks
from sentence_transformers import SentenceTransformer

# Mengimpor fungsi-fungsi utilitas pendukung penilaian skill dari file lokal skill_utils.py
from .skill_utils import extract_skills, assess_skills, load_skill_taxonomy, build_flat_skills

# Mengambil logger standar untuk modul aktif saat ini
logger = logging.getLogger(__name__)


# ==============================================================================
# KELAS: CVAnalysisPipeline
# Penjelasan: Kelas utama yang menyatukan alur pencarian lowongan kerja
# berbasis makna semantik BERT & FAISS, dengan analisis audit kesiapan kerja.
# ==============================================================================
class CVAnalysisPipeline:
    
    # Inisialisasi/Constructor kelas
    # Parameter model_dir: Path folder tempat seluruh berkas model diletakkan
    # Parameter embedding_model_name: Nama model embedding HuggingFace (all-MiniLM-L6-v2)
    def __init__(self, model_dir: str, embedding_model_name: str):
        # 1. Memuat model NLP SentenceTransformer ke dalam memori RAM.
        # Parameter embedding_model_name menentukan model BERT ringan yang diunduh/dimuat.
        self.embed_model = SentenceTransformer(embedding_model_name)
        
        # 2. Membaca indeks vektor biner FAISS dari penyimpanan disk menggunakan faiss.read_index()
        # Berkas 'faiss_job_index.bin' memuat koordinat vektor dari seluruh deskripsi lowongan kerja.
        self.faiss_index = faiss.read_index(f"{model_dir}/faiss_job_index.bin")
        
        # 3. Membaca metadata deskripsi detail lowongan kerja dari CSV menggunakan pd.read_csv()
        self.df_jobs = pd.read_csv(f"{model_dir}/job_metadata.csv")
        
        # 4. Membuka dan memparsing berkas JSON profil standar kompetensi industri
        # Parameter encoding='utf-8' untuk menangani pembacaan karakter unicode khusus
        with open(f"{model_dir}/job_role_profiles.json", "r", encoding="utf-8") as f:
            self.job_profiles = json.load(f)
            
        # 5. Memuat taksonomi skill terdaftar dan menyusunnya menjadi bentuk datar (flat dictionary)
        taxonomy = load_skill_taxonomy(f"{model_dir}/skill_taxonomy.json")
        self.flat_skills = build_flat_skills(taxonomy)


    # ==============================================================================
    # FUNGSI: analyze
    # Penjelasan: Menerima teks CV pelamar dan peran target, mengembalikan lowongan 
    # terdekat dan ringkasan gap assessment beserta metrik waktu respon.
    # ==============================================================================
    def analyze(self, cv_text: str, target_role: str, top_k: int = 5) -> Dict:
        # Mencatat timestamp awal mulai eksekusi menggunakan time.time()
        start = time.time()
        
        # Validasi: Memeriksa apakah teks CV kosong atau kurang dari 20 karakter
        if not cv_text or len(cv_text.strip()) < 20:
            raise ValueError("Teks CV terlalu pendek untuk dianalisis.")
        # Validasi: Memeriksa apakah peran yang diinput didukung di dalam profil standar
        if target_role not in self.job_profiles:
            raise ValueError(f"Target peran '{target_role}' tidak didukung.")
            
        # Langkah A: Memanggil fungsi internal rekomendasi lowongan kerja semantik hibrida
        recommendations = self._recommend(cv_text, top_k)
        
        # Langkah B: Menganalisis gap kesiapan kompetensi pelamar berdasarkan standar industri
        assessment = assess_skills(cv_text, target_role, self.job_profiles, self.flat_skills)
        
        # Menghitung latensi: selisih waktu saat ini dikurangi waktu mulai, dikalikan 1000 (milidetik)
        latency = (time.time() - start) * 1000
        
        # Mengembalikan dictionary respon hasil analisis lengkap
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


    # ==============================================================================
    # FUNGSI: _recommend
    # Penjelasan: Melakukan pencarian kemiripan semantik (FAISS) dan mencocokkan
    # skill set (Jaccard Overlap) untuk menyusun skor hibrida akhir.
    # ==============================================================================
    def _recommend(self, cv_text: str, top_k: int) -> List[Dict]:
        # 1. Mengubah string teks CV menjadi vektor numerik 384 dimensi (L2-normalized)
        # Parameter [cv_text]: Mengirimkan teks dalam bentuk list
        # Parameter normalize_embeddings=True: Menormalisasi vektor agar panjang L2 = 1 (sehingga dot-product = cosine similarity)
        # .astype(np.float32): Mengonversi tipe data ke float32 karena FAISS wajib menggunakan float32
        emb = self.embed_model.encode([cv_text], normalize_embeddings=True).astype(np.float32)
        
        # 2. Melakukan pencarian tetangga terdekat (K-Nearest Neighbors) di indeks FAISS
        # Mengambil 3x lipat dari jumlah target (top_k * 3) untuk diranking ulang berdasarkan kecocokan skill
        # self.faiss_index.search(): Fungsi pencarian FAISS (mengembalikan nilai skor kemiripan dan indeks baris lowongan)
        scores, indices = self.faiss_index.search(emb, min(top_k * 3, self.faiss_index.ntotal))
        
        # 3. Mendeteksi dan mendata seluruh skill yang ada di dalam CV pelamar
        cv_skills = set()
        for v in extract_skills(cv_text, self.flat_skills).values():
            cv_skills.update(s.lower() for s in v)
            
        recs = []
        # Melakukan perulangan untuk mengevaluasi setiap hasil pencarian dari FAISS
        # scores[0]: List nilai skor kesamaan semantik untuk query ke-0
        # indices[0]: List indeks baris lowongan kerja terkait untuk query ke-0
        for score, idx in zip(scores[0], indices[0]):
            # Mengabaikan hasil jika skor semantik terlalu rendah (< 15%) atau indeks tidak valid
            if score < 0.15 or idx >= len(self.df_jobs):
                continue
            # Mengambil baris data metadata lowongan terkait di DataFrame menggunakan iloc[]
            row = self.df_jobs.iloc[idx]
            
            # 4. Mendeteksi seluruh skill yang diminta oleh lowongan kerja tersebut
            job_text = str(row.get("job_description", "")) + " " + str(row.get("skills_required", ""))
            job_skills = set()
            for v in extract_skills(job_text, self.flat_skills).values():
                job_skills.update(s.lower() for s in v)
                
            # 5. Menghitung kesamaan skill nyata (Jaccard Overlap Coefficient)
            # Operasi iris (intersection &): skill pelamar yang cocok dengan lowongan
            matched = cv_skills & job_skills
            # Rumus overlap: jumlah skill yang cocok dibagi total kebutuhan lowongan
            overlap = len(matched) / max(len(job_skills), 1)
            
            # 6. Menghitung Skor Hibrida: 70% kesamaan arti semantik (BERT) + 30% kecocokan skill langsung (Jaccard)
            combined = 0.7 * float(score) + 0.3 * overlap
            
            # Memasukkan data ke list rekomendasi
            recs.append({
                "rank": 0, # Diurutkan ulang di langkah berikutnya
                "job_title": str(row.get("job_title", "N/A")),
                "company_name": str(row.get("company_name", "N/A")),
                "location": str(row.get("location", "N/A")),
                "confidence_score": round(combined, 4),
                "matched_skills": sorted(list(matched)),
                "missing_skills": sorted(list(job_skills - cv_skills))[:8], # Sisa skill yang belum dimiliki pelamar (maksimal 8)
                "reasoning": f"Kecocokan semantik {float(score)*100:.0f}%, {len(matched)} skill sesuai.",
            })
            
        # 7. Mengurutkan ulang (sorting) list rekomendasi berdasarkan combined_score terbesar (Descending)
        # Parameter key=lambda x: Menunjuk kolom acuan pengurutan (confidence_score)
        # Parameter reverse=True: Mengurutkan dari besar ke kecil (Descending)
        recs.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        # Menetapkan nomor peringkat (rank) setelah data terurut
        for i, r in enumerate(recs[:top_k]):
            r["rank"] = i + 1
            
        # Mengembalikan potongan list lowongan kerja teratas sebanyak top_k
        return recs[:top_k]


