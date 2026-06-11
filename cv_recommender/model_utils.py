# ==============================================================================
# NAMA FILE: model_utils.py
# FUNGSI FILE: Berisi seluruh logika inti pipeline Machine Learning — memuat model,
#              mengekstrak skill dari teks, mencari lowongan mirip, dan menghitung
#              skor kesiapan kerja. File ini dipanggil oleh streamlit_app.py.
# ==============================================================================

# Mengimpor modul 'os' untuk memanipulasi path file model
import os

# Mengimpor modul 'json' untuk membaca file konfigurasi dan profil jabatan berformat JSON
import json

# Mengimpor modul 're' untuk mencocokkan nama skill di dalam teks menggunakan regex
import re

# Mengimpor library 'numpy' untuk mengonversi vektor embedding ke format float32 (kebutuhan FAISS)
import numpy as np

# Mengimpor library 'pandas' untuk membaca metadata lowongan kerja dari file CSV
import pandas as pd

# Mengimpor library 'faiss' untuk pencarian kemiripan vektor (tetangga terdekat) secara cepat
import faiss

# Mengimpor 'SentenceTransformer' untuk mengubah teks menjadi vektor numerik 384 dimensi
from sentence_transformers import SentenceTransformer


# ==============================================================================
# KONSTANTA
# Nama model embedding yang digunakan — model BERT ringan dari HuggingFace
# yang menghasilkan vektor 384 dimensi untuk merepresentasikan makna teks
# ==============================================================================
NAMA_MODEL_EMBEDDING = "all-MiniLM-L6-v2"


def muat_model_dan_data(model_dir):
    """
    Memuat semua artefak yang dibutuhkan: model BERT, index FAISS,
    metadata lowongan, taksonomi skill, dan profil jabatan.

    Parameter:
        model_dir (str) -- path folder tempat semua file model disimpan

    Return:
        dict -- berisi semua object yang sudah dimuat:
                model, index, df_jobs, taksonomi_skill, profil_jabatan
    """
    # Memuat model Sentence-BERT ke memori RAM
    model = SentenceTransformer(NAMA_MODEL_EMBEDDING)

    # Membaca index FAISS dari file biner — berisi vektor seluruh lowongan kerja
    index = faiss.read_index(os.path.join(model_dir, "faiss_job_index.bin"))

    # Membaca metadata lowongan (judul, perusahaan, lokasi, deskripsi) dari CSV
    df_jobs = pd.read_csv(os.path.join(model_dir, "job_metadata.csv"))

    # Membaca profil standar kompetensi industri untuk tiap jabatan target
    with open(os.path.join(model_dir, "job_role_profiles.json"), "r", encoding="utf-8") as f:
        profil_jabatan = json.load(f)

    # Membaca taksonomi skill (daftar skill per kategori) dari JSON
    with open(os.path.join(model_dir, "skill_taxonomy.json"), "r", encoding="utf-8") as f:
        taksonomi_raw = json.load(f)

    # Mengubah taksonomi bersarang {kategori: [skill, ...]} menjadi kamus datar
    # {skill: kategori} agar pencarian kategori suatu skill bisa instan (O(1))
    taksonomi_skill = {}
    for kategori, daftar_skill in taksonomi_raw.items():
        for skill in daftar_skill:
            taksonomi_skill[skill.lower()] = kategori

    return {
        "model": model,
        "index": index,
        "df_jobs": df_jobs,
        "profil_jabatan": profil_jabatan,
        "taksonomi_skill": taksonomi_skill,
    }


def ekstrak_skill_dari_teks(teks, taksonomi_skill):
    """
    Mencari skill apa saja yang disebutkan di dalam teks (CV atau lowongan).

    Parameter:
        teks (str) -- teks CV atau deskripsi lowongan yang ingin dicek
        taksonomi_skill (dict) -- kamus {nama_skill: kategori} dari muat_model_dan_data()

    Return:
        set -- kumpulan nama skill (huruf kecil) yang ditemukan di teks
    """
    # Jika teks kosong atau terlalu pendek, kembalikan set kosong
    if not teks or len(teks.strip()) < 10:
        return set()

    teks_lower = teks.lower()
    skill_ditemukan = set()

    for skill in taksonomi_skill:
        # re.escape() mengamankan karakter khusus (misal '+' di 'c++', '#' di 'c#')
        # agar tidak dianggap sebagai operator regex
        # \b adalah word boundary — memastikan 'r' tidak cocok dengan 'react'
        pola = r"\b" + re.escape(skill) + r"\b"

        if re.search(pola, teks_lower):
            skill_ditemukan.add(skill)

    return skill_ditemukan


def cari_lowongan_mirip(teks_cv, data_model, top_k=5):
    """
    Mencari lowongan kerja yang paling cocok dengan CV menggunakan kombinasi
    kemiripan makna (BERT) dan kecocokan skill (Jaccard).

    Parameter:
        teks_cv (str) -- teks CV pelamar yang sudah diekstrak
        data_model (dict) -- hasil dari muat_model_dan_data()
        top_k (int) -- jumlah lowongan yang ingin ditampilkan (default 5)

    Return:
        list[dict] -- daftar lowongan, masing-masing berisi judul, perusahaan,
                       lokasi, skor, skill yang cocok, dan skill yang belum ada
    """
    model = data_model["model"]
    index = data_model["index"]
    df_jobs = data_model["df_jobs"]
    taksonomi_skill = data_model["taksonomi_skill"]

    # --- Langkah 1: Ubah teks CV menjadi vektor 384 dimensi ---
    # normalize_embeddings=True membuat panjang vektor = 1, sehingga
    # dot product antar vektor = cosine similarity (kemiripan arah)
    vektor_cv = model.encode(
        [teks_cv], normalize_embeddings=True
    ).astype(np.float32)

    # --- Langkah 2: Cari top_k*3 lowongan terdekat di index FAISS ---
    # Kita ambil 3x lipat karena akan di-ranking ulang berdasarkan skill
    jumlah_cari = min(top_k * 3, index.ntotal)
    skor_bert, indeks_baris = index.search(vektor_cv, jumlah_cari)

    # --- Langkah 3: Ekstrak skill dari CV pelamar ---
    skill_cv = ekstrak_skill_dari_teks(teks_cv, taksonomi_skill)

    # --- Langkah 4: Untuk tiap kandidat lowongan, hitung skor gabungan ---
    kandidat = []

    for skor, idx in zip(skor_bert[0], indeks_baris[0]):
        # Abaikan hasil jika skor terlalu rendah (< 15%) atau indeks tidak valid
        if skor < 0.15 or idx >= len(df_jobs):
            continue

        baris = df_jobs.iloc[idx]

        # Gabungkan deskripsi + skill lowongan untuk ekstraksi skill
        teks_lowongan = str(baris.get("job_description", "")) + " " + str(baris.get("skills_required", ""))
        skill_lowongan = ekstrak_skill_dari_teks(teks_lowongan, taksonomi_skill)

        # Hitung skill yang cocok (irisan) dan yang belum dimiliki (selisih)
        skill_cocok = skill_cv & skill_lowongan
        skill_kurang = skill_lowongan - skill_cv

        # Overlap = proporsi skill lowongan yang dimiliki pelamar
        # max(..., 1) mencegah pembagian dengan nol
        overlap = len(skill_cocok) / max(len(skill_lowongan), 1)

        # Skor Hibrida = 70% kemiripan makna (BERT) + 30% kecocokan skill (Jaccard)
        skor_gabungan = 0.7 * float(skor) + 0.3 * overlap

        kandidat.append({
            "rank": 0,
            "job_title": str(baris.get("job_title", "N/A")),
            "company_name": str(baris.get("company_name", "N/A")),
            "location": str(baris.get("location", "N/A")),
            "confidence_score": round(skor_gabungan, 4),
            "matched_skills": sorted(list(skill_cocok)),
            "missing_skills": sorted(list(skill_kurang))[:8],
            "reasoning": f"Kecocokan semantik {float(skor)*100:.0f}%, {len(skill_cocok)} skill sesuai.",
        })

    # --- Langkah 5: Urutkan berdasarkan skor gabungan (terbesar dulu) ---
    kandidat.sort(key=lambda x: x["confidence_score"], reverse=True)

    # Tetapkan nomor peringkat setelah data terurut
    for i, item in enumerate(kandidat[:top_k]):
        item["rank"] = i + 1

    return kandidat[:top_k]


def hitung_skor_kesiapan(teks_cv, target_role, data_model):
    """
    Menghitung skor kesiapan kerja pelamar dibanding standar industri
    untuk peran target tertentu, menggunakan rata-rata berbobot 4 kategori.

    Parameter:
        teks_cv (str) -- teks CV pelamar
        target_role (str) -- nama peran target, contoh "data_engineer"
        data_model (dict) -- hasil dari muat_model_dan_data()

    Return:
        dict -- berisi skor total (overall_readiness_score), level kesiapan,
                daftar skill yang sudah dipenuhi (met) dan yang masih kurang (gap),
                serta detail per kategori (breakdown)
    """
    profil = data_model["profil_jabatan"][target_role]
    taksonomi_skill = data_model["taksonomi_skill"]

    # Ekstrak skill dari CV pelamar (set datar)
    skill_cv = ekstrak_skill_dari_teks(teks_cv, taksonomi_skill)

    # Definisikan 4 kategori kompetensi beserta bobotnya
    # Total bobot: 0.40 + 0.30 + 0.15 + 0.15 = 1.00 (100%)
    kategori = {
        "core_skills": (set(s.lower() for s in profil["core_skills"]), 0.40),
        "expected_skills": (set(s.lower() for s in profil["expected_skills"]), 0.30),
        "nice_to_have": (set(s.lower() for s in profil["nice_to_have"]), 0.15),
        "soft_skills": (set(s.lower() for s in profil["soft_skills"]), 0.15),
    }

    breakdown = {}
    skor_total = 0.0
    semua_met = set()
    semua_gap = set()

    for nama, (skill_wajib, bobot) in kategori.items():
        # Irisan (intersection): skill yang ada di CV DAN di standar industri
        met = skill_cv & skill_wajib
        # Selisih (difference): skill standar industri yang TIDAK ada di CV
        gap = skill_wajib - skill_cv

        # Skor kategori = (jumlah skill terpenuhi / total skill wajib) × 100%
        skor_kategori = len(met) / max(len(skill_wajib), 1) * 100

        # Tambahkan ke skor total dengan pembobotan
        # Contoh: skor core 80% × bobot 0.40 = kontribusi 32 poin ke total
        skor_total += skor_kategori * bobot

        semua_met.update(met)
        semua_gap.update(gap)

        breakdown[nama] = {
            "score": round(skor_kategori, 1),
            "weight": f"{int(bobot * 100)}%",
            "met": sorted(list(met)),
            "gap": sorted(list(gap)),
        }

    # Tentukan level kesiapan berdasarkan skor total
    if skor_total >= 80:
        level, emoji = "SANGAT SIAP", "🟢"
    elif skor_total >= 60:
        level, emoji = "CUKUP SIAP", "🟡"
    elif skor_total >= 40:
        level, emoji = "PERLU PENINGKATAN", "🟠"
    else:
        level, emoji = "BELUM SIAP", "🔴"

    return {
        "overall_readiness_score": round(skor_total, 1),
        "readiness_level": level,
        "readiness_emoji": emoji,
        "breakdown": breakdown,
        "met": sorted(list(semua_met)),
        "gap": sorted(list(semua_gap)),
    }


def analisis_cv(teks_cv, target_role, data_model, top_k=5):
    """
    Fungsi utama yang dipanggil dari Streamlit — menggabungkan pencarian
    lowongan dan perhitungan skor kesiapan dalam satu hasil.

    Parameter:
        teks_cv (str) -- teks CV pelamar
        target_role (str) -- peran target, contoh "data_engineer"
        data_model (dict) -- hasil dari muat_model_dan_data()
        top_k (int) -- jumlah lowongan rekomendasi

    Return:
        dict -- {"lowongan_rekomendasi": [...], "skor_kesiapan": {...}}
    """
    # Validasi: teks CV harus minimal 20 karakter agar bisa dianalisis
    if not teks_cv or len(teks_cv.strip()) < 20:
        raise ValueError("Teks CV terlalu pendek untuk dianalisis (minimal 20 karakter).")

    # Validasi: peran target harus tersedia di profil jabatan
    if target_role not in data_model["profil_jabatan"]:
        raise ValueError(f"Peran '{target_role}' tidak tersedia di profil jabatan.")

    # Panggil kedua fungsi inti
    lowongan = cari_lowongan_mirip(teks_cv, data_model, top_k)
    kesiapan = hitung_skor_kesiapan(teks_cv, target_role, data_model)

    return {
        "lowongan_rekomendasi": lowongan,
        "skor_kesiapan": kesiapan,
    }
