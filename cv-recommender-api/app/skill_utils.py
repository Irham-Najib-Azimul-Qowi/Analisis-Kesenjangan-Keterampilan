"""
Utilitas ekstraksi dan penilaian skill.
File ini berisi fungsi-fungsi pembantu untuk mengelola taksonomi skill (daftar kata kunci skill),
mengekstraksi skill dari teks CV atau deskripsi pekerjaan, serta menghitung kesenjangan (gap)
dan skor kesiapan kerja (readiness score).
"""
import re
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def load_skill_taxonomy(path: str) -> Dict[str, List[str]]:
    """
    Fungsi untuk memuat berkas kamus/taksonomi skill dari file JSON.
    
    Parameter:
    - path (str): Path absolut atau relatif ke file JSON taksonomi.
    
    Return:
    - Dict[str, List[str]]: Dictionary yang memetakan kategori (misal: 'database') 
      ke daftar skill terkait (misal: ['PostgreSQL', 'MySQL', 'MongoDB']).
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Gagal memuat taksonomi skill dari {path}: {e}")
        raise


def build_flat_skills(taxonomy: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Mengonversi taksonomi berhierarki (kategori -> daftar skill) menjadi dictionary datar (flat).
    Ini dilakukan agar proses pencarian kata kunci skill menjadi lebih efisien.
    
    Contoh input:
    {
        "programming": ["Python", "Java"],
        "database": ["SQL", "MongoDB"]
    }
    
    Contoh output (kunci diubah ke lowercase agar pencarian bersifat case-insensitive):
    {
        "python": "programming",
        "java": "programming",
        "sql": "database",
        "mongodb": "database"
    }
    
    Parameter:
    - taxonomy (Dict): Taksonomi berhierarki hasil dari load_skill_taxonomy.
    
    Return:
    - Dict[str, str]: Dictionary datar yang memetakan 'nama_skill_lowercase' ke 'nama_kategori'.
    """
    flat = {}
    for cat, skills in taxonomy.items():
        for skill in skills:
            # Mengubah nama skill menjadi lowercase agar matching nanti bersifat case-insensitive
            flat[skill.lower()] = cat
    return flat


def extract_skills(text: str, flat_skills: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Mengekstraksi kata kunci skill yang ada di dalam sebuah teks (CV atau lowongan) 
    menggunakan metode Regex Keyword Matching (Pencocokan Kata Kunci).
    
    Fungsi ini menggunakan pencarian berbasis kata utuh (word boundary `\\b`) agar 
    misalnya kata 'java' tidak mencocokkan kata 'javascript'.
    
    Parameter:
    - text (str): Teks dokumen CV atau deskripsi pekerjaan yang akan diperiksa.
    - flat_skills (Dict): Dictionary datar hasil dari build_flat_skills.
    
    Return:
    - Dict[str, List[str]]: Hasil ekstraksi berupa pemetaan Kategori -> Daftar skill yang ditemukan.
      Contoh: {"programming": ["python"], "database": ["sql"]}
    """
    if not text or len(text) < 10:
        return {}
        
    text_lower = text.lower()
    found: Dict[str, List[str]] = {}
    
    # Lakukan loop untuk setiap kata kunci skill yang terdaftar di taksonomi
    for skill, category in flat_skills.items():
        # \\b memastikan pencocokan kata utuh (word boundaries) untuk menghindari false positive
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            # Inisialisasi list jika kategori baru pertama kali ditemukan
            found.setdefault(category, [])
            if skill not in found[category]:
                found[category].append(skill)
                
    return found


def assess_skills(
    cv_text: str,
    target_role: str,
    job_profiles: Dict,
    flat_skills: Dict[str, str]
) -> Dict:
    """
    Melakukan penilaian kesesuaian skill pelamar (CV) terhadap profil standar industri
    untuk posisi target yang dipilih (misal: data_engineer).
    
    Alur Perhitungan:
    1. Ekstrak seluruh skill yang terdeteksi di CV pelamar.
    2. Bandingkan skill pelamar dengan skill yang dibutuhkan standar industri pada 4 kategori:
       - core_skills (bobot 40%) - Skill wajib yang harus dimiliki.
       - expected_skills (bobot 30%) - Skill penunjang yang sangat diharapkan.
       - nice_to_have (bobot 15%) - Nilai tambah / skill opsional.
       - soft_skills (bobot 15%) - Keterampilan interpersonal/sosial.
    3. Hitung persentase terpenuhi pada tiap kategori, lalu kalikan dengan bobotnya masing-masing.
    4. Tentukan level kesiapan kerja berdasarkan total nilai (overall_readiness_score).
    5. Rekomendasikan daftar prioritas belajar (gap skill utama/core yang belum dimiliki pelamar).
    
    Parameter:
    - cv_text (str): Teks isi CV pelamar.
    - target_role (str): Posisi target jabatan (contoh: 'data_engineer').
    - job_profiles (Dict): Profil standar kebutuhan skill untuk setiap jabatan.
    - flat_skills (Dict): Kamus pencarian skill datar.
    
    Return:
    - Dict: Laporan asesmen lengkap berisi skor, level kesiapan, rincian terpenuhi/gap per kategori,
            dan daftar rekomendasi prioritas up-skilling.
    """
    # Validasi apakah target_role yang diminta ada di dalam profil standar industri
    if target_role not in job_profiles:
        raise ValueError(f"Peran tidak tersedia: {target_role}")

    profile = job_profiles[target_role]
    
    # 1. Ekstrak skill yang dimiliki pelamar dari teks CV
    cv_skills_dict = extract_skills(cv_text, flat_skills)
    cv_flat = set()
    for cat_skills in cv_skills_dict.values():
        cv_flat.update(s.lower() for s in cat_skills)

    # 2. Definisikan standar kebutuhan skill berdasarkan profil industri beserta bobotnya
    categories = {
        "core_skills": (set(s.lower() for s in profile["core_skills"]), 0.40),
        "expected_skills": (set(s.lower() for s in profile["expected_skills"]), 0.30),
        "nice_to_have": (set(s.lower() for s in profile["nice_to_have"]), 0.15),
        "soft_skills": (set(s.lower() for s in profile["soft_skills"]), 0.15),
    }

    breakdown = {}
    overall = 0.0
    all_met, all_gap = set(), set()

    # 3. Hitung skor per kategori dan akumulasikan ke skor keseluruhan (overall score)
    for name, (required, weight) in categories.items():
        # met = Irisan (intersection) antara skill CV dan skill yang dibutuhkan standar industri
        met = cv_flat & required
        # gap = Selisih (difference) skill industri yang belum dimiliki di CV
        gap = required - cv_flat
        
        # Hitung skor kategori (persentase kecocokan)
        score = len(met) / max(len(required), 1) * 100
        
        # Akumulasikan ke skor kesiapan total dengan mengalikan bobot kategori
        overall += score * weight
        
        # Gabungkan ke daftar global untuk laporan akhir
        all_met.update(met)
        all_gap.update(gap)
        
        breakdown[name] = {
            "score": round(score, 1),
            "weight": f"{int(weight*100)}%",
            "met": sorted(list(met)),
            "gap": sorted(list(gap)),
            "total_required": len(required),
        }

    # 4. Tentukan kategori Kesiapan Kerja (Readiness Level) berdasarkan skor akhir
    if overall >= 80:
        level, emoji = "SANGAT SIAP", "🟢"
    elif overall >= 60:
        level, emoji = "CUKUP SIAP", "🟡"
    elif overall >= 40:
        level, emoji = "PERLU PENINGKATAN", "🟠"
    else:
        level, emoji = "BELUM SIAP", "🔴"

    # 5. Tentukan Prioritas Belajar (Up-skilling Priority)
    # Skill wajib (core) yang masih kurang masuk ke prioritas TINGGI
    priority = []
    for s in sorted(breakdown["core_skills"]["gap"]):
        priority.append({"skill": s, "priority": "TINGGI"})
    # Skill expected yang masih kurang masuk ke prioritas SEDANG
    for s in sorted(breakdown["expected_skills"]["gap"]):
        if s not in [p["skill"] for p in priority]:
            priority.append({"skill": s, "priority": "SEDANG"})

    # Return dictionary terstruktur yang dikirimkan ke frontend untuk dirender
    return {
        "overall_readiness_score": round(overall, 1),
        "readiness_level": level,
        "readiness_emoji": emoji,
        "breakdown": breakdown,
        "met": sorted(list(all_met)),
        "gap": sorted(list(all_gap)),
        "priority_learning": priority[:10],  # Ambil maksimal 10 rekomendasi teratas
    }

