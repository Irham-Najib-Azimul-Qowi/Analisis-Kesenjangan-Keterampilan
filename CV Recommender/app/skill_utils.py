# ==============================================================================
# 🛠️ MODUL UTILITAS SKILL: Ekstraksi Keahlian & Penilaian Kesiapan Kerja (Jaccard)
# Berkas ini berisi fungsi pembantu untuk mendeteksi keahlian (skills) dari teks,
# membandingkannya dengan standar industri, dan menghitung skor gap menggunakan set.
# ==============================================================================

# Mengimpor modul bawaan Python 're' untuk memproses teks menggunakan Regular Expression (Regex)
import re

# Mengimpor modul bawaan Python 'json' untuk membaca dan menulis format data pertukaran JSON
import json


# ==============================================================================
# FUNGSI: load_skill_taxonomy
# Penjelasan: Memuat taksonomi skill (daftar skill terklasifikasi) dari file JSON.
# ==============================================================================
# Parameter path: String berisi alamat path fisik dari file JSON taksonomi skill
def load_skill_taxonomy(path: str):
    # Membuka file JSON dengan fungsi bawaan open()
    # Parameter 'r' untuk membaca file (read), encoding='utf-8' untuk menangani karakter unicode khusus
    with open(path, "r", encoding="utf-8") as f:
        # Pustaka json.load() membaca file JSON aktif dan mengubahnya menjadi objek dictionary Python
        return json.load(f)


# ==============================================================================
# FUNGSI: build_flat_skills
# Penjelasan: Mengubah struktur taksonomi dari kategori -> list skill menjadi kamus datar
# agar proses pencarian kategori untuk suatu skill memiliki kompleksitas O(1) (instant search).
# ==============================================================================
# Parameter taxonomy: Objek dictionary bersarang yang memetakan kategori ke list skill
def build_flat_skills(taxonomy: dict):
    # Membuat dictionary kosong untuk menyimpan hasil pemetaan datar
    flat = {}
    # Melakukan perulangan (loop) untuk mengambil key kategori dan list skill
    for category, skills in taxonomy.items():
        # Melakukan perulangan untuk setiap nama skill di dalam list skills
        for skill in skills:
            # Mengubah nama skill menjadi huruf kecil (lower) dan menyimpannya sebagai key,
            # dengan nilai value berupa nama kategori tempat skill tersebut berasal.
            flat[skill.lower()] = category
    return flat


# ==============================================================================
# FUNGSI: extract_skills
# Penjelasan: Mengekstrak seluruh skill yang terdeteksi di dalam teks CV atau job desk
# menggunakan pencocokan kata Regex Word Boundary (\b) guna menghindari false positive.
# ==============================================================================
# Parameter text: String teks CV atau lowongan yang akan dicari skill-nya
# Parameter flat_skills: Dictionary datar pemetaan skill -> kategori (hasil build_flat_skills)
def extract_skills(text: str, flat_skills: dict):
    # Validasi awal: jika teks kosong atau terlalu pendek, kembalikan dictionary kosong
    if not text or len(text) < 10:
        return {}
    
    # Mengonversi seluruh teks input menjadi huruf kecil menggunakan lower()
    text_lower = text.lower()
    # Membuat dictionary kosong untuk menampung daftar skill yang ditemukan
    found = {}
    
    # Melakukan perulangan untuk setiap skill dan kategorinya dari flat_skills
    for skill, category in flat_skills.items():
        # Menyusun pola regular expression (pattern) dengan pembatas kata (\b)
        # re.escape(): Mengamankan karakter khusus regex (seperti '+' pada C++ atau '#' pada C#) agar dibaca sebagai teks biasa
        pattern = r"\b" + re.escape(skill) + r"\b"
        
        # Mencari pola regex di dalam teks menggunakan re.search()
        # Parameter pertama: Pola regex (pattern) yang dicari
        # Parameter kedua: Teks sumber (text_lower) tempat pencarian dilakukan
        if re.search(pattern, text_lower):
            # Menggunakan setdefault() untuk menginisialisasi list kosong jika key kategori belum ada di dictionary
            found.setdefault(category, [])
            # Memastikan tidak ada duplikasi skill yang sama di dalam kategori
            if skill not in found[category]:
                # Menambahkan skill yang ditemukan ke dalam list kategori terkait
                found[category].append(skill)
    return found


# ==============================================================================
# FUNGSI: assess_skills
# Penjelasan: Menilai tingkat kesesuaian skill pelamar dengan standar kebutuhan industri
# menggunakan perhitungan matematika berbobot (weighted average) per kategori skill.
# ==============================================================================
# Parameter cv_text: Teks isi CV pelamar kerja
# Parameter target_role: String peran jabatan target (seperti 'data_engineer')
# Parameter job_profiles: Dictionary profil standar skill untuk tiap jabatan target
# Parameter flat_skills: Dictionary flat pencarian skill
def assess_skills(cv_text: str, target_role: str, job_profiles: dict, flat_skills: dict):
    # 1. Mengambil profil standar kompetensi industri untuk jabatan yang dipilih
    profile = job_profiles[target_role]
    
    # 2. Mengekstrak skill yang terkandung di dalam CV pelamar
    cv_skills_dict = extract_skills(cv_text, flat_skills)
    
    # 3. Mengubah hasil ekstraksi menjadi set data tunggal yang datar (flat set) untuk operasi matematika set
    cv_flat = set()
    for cat_skills in cv_skills_dict.values():
        # Mengonversi nama skill ke huruf kecil dan memasukkannya ke dalam set menggunakan update()
        cv_flat.update(s.lower() for s in cat_skills)
        
    # 4. Mendefinisikan profil kompetensi standar industri beserta bobot nilainya masing-masing
    # Total akumulasi bobot: 0.40 (Core) + 0.30 (Expected) + 0.15 (Nice to have) + 0.15 (Soft) = 1.0 (100%)
    categories = {
        "core_skills": (set(s.lower() for s in profile["core_skills"]), 0.40),
        "expected_skills": (set(s.lower() for s in profile["expected_skills"]), 0.30),
        "nice_to_have": (set(s.lower() for s in profile["nice_to_have"]), 0.15),
        "soft_skills": (set(s.lower() for s in profile["soft_skills"]), 0.15),
    }
    
    # Inisialisasi variabel penampung analisis breakdown, skor akhir, skill terpenuhi, dan gap
    breakdown = {}
    overall = 0.0
    all_met = set()
    all_gap = set()
    
    # 5. Menghitung persentase kecocokan skill untuk setiap kategori
    for name, (required, weight) in categories.items():
        # Operasi iris (intersection &): mengambil skill yang ada di CV sekaligus terdaftar di standar industri
        met = cv_flat & required
        # Operasi selisih (difference -): mengambil skill standar industri yang TIDAK ada di CV pelamar
        gap = required - cv_flat
        
        # Rumus Jaccard Kategori: (jumlah skill terpenuhi / total skill wajib di kategori tersebut) * 100%
        # max(..., 1) digunakan untuk menghindari pembagian dengan nilai nol (ZeroDivisionError)
        score = len(met) / max(len(required), 1) * 100
        # Menambahkan nilai rata-rata tertimbang (skor kategori dikali bobot kategori)
        overall += score * weight
        
        # Memasukkan hasil ke set keseluruhan menggunakan update()
        all_met.update(met)
        all_gap.update(gap)
        
        # Menyimpan hasil detail kategori ke dalam dictionary breakdown
        breakdown[name] = {
            "score": round(score, 1), # Pembulatan 1 angka di belakang koma dengan round()
            "weight": f"{int(weight*100)}%",
            "met": sorted(list(met)), # Mengurutkan alfabet menggunakan sorted()
            "gap": sorted(list(gap)),
            "total_required": len(required),
        }
        
    # 6. Menentukan Kategori Kesiapan Kerja berdasarkan total rata-rata skor kesiapan akhir (overall)
    if overall >= 80:
        level, emoji = "SANGAT SIAP", "🟢"
    elif overall >= 60:
        level, emoji = "CUKUP SIAP", "🟡"
    elif overall >= 40:
        level, emoji = "PERLU PENINGKATAN", "🟠"
    else:
        level, emoji = "BELUM SIAP", "🔴"
        
    # 7. Menyusun prioritas rekomendasi belajar (up-skilling) untuk menutup skill gap
    priority = []
    # Kesenjangan pada Core Skills (skill inti) dimasukkan terlebih dahulu dengan prioritas TINGGI
    for s in sorted(breakdown["core_skills"]["gap"]):
        priority.append({"skill": s, "priority": "TINGGI"})
    # Kesenjangan pada Expected Skills dimasukkan dengan prioritas SEDANG
    for s in sorted(breakdown["expected_skills"]["gap"]):
        # Mencegah duplikasi skill yang sama di dalam list prioritas
        if s not in [p["skill"] for p in priority]:
            priority.append({"skill": s, "priority": "SEDANG"})
            
    # Mengembalikan data dictionary hasil analisis kesiapan kerja
    return {
        "overall_readiness_score": round(overall, 1),
        "readiness_level": level,
        "readiness_emoji": emoji,
        "breakdown": breakdown,
        "met": sorted(list(all_met)),
        "gap": sorted(list(all_gap)),
        "priority_learning": priority[:10], # Memotong list hingga maksimal 10 rekomendasi
    }


