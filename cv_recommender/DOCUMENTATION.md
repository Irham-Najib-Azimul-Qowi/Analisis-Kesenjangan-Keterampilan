# Dokumentasi CV Recommender (Versi Sederhana)

## 1. Apa yang Dilakukan Sistem Ini

Sistem ini menerima CV pelamar kerja (dalam format PDF atau teks), lalu menganalisis kecocokan CV tersebut terhadap standar kompetensi industri untuk jabatan tertentu. Hasilnya berupa **skor kesiapan kerja** (seberapa siap pelamar) dan **daftar rekomendasi lowongan kerja** yang paling relevan berdasarkan kemiripan semantik dan kecocokan skill.

---

## 2. Struktur File

| File | Fungsi |
|------|--------|
| `streamlit_app.py` | Dashboard Streamlit — antarmuka upload CV dan tampilan hasil analisis |
| `model_utils.py` | Logika inti ML — memuat model, ekstrak skill, cari lowongan, hitung skor kesiapan |
| `Machine_Learning.ipynb` | Notebook pelatihan — proses dari data mentah sampai model siap pakai |
| `models/` | Folder artefak model (index FAISS, metadata CSV, profil jabatan JSON, taksonomi skill) |
| `requirements.txt` | Daftar pustaka Python yang dibutuhkan |
| `.streamlit/config.toml` | Konfigurasi tampilan Streamlit |

---

## 3. Cara Kerja Singkat (Alur)

1. Pengguna membuka dashboard, memilih jabatan target, lalu mengunggah file PDF CV.
2. `pdfplumber` mengekstrak teks dari PDF ke dalam string.
3. Teks CV diubah menjadi **vektor numerik 384 dimensi** oleh model Sentence-BERT (`all-MiniLM-L6-v2`).
4. FAISS mencari lowongan yang vektornya paling mirip dengan vektor CV (pencarian tetangga terdekat).
5. Untuk tiap kandidat lowongan, dihitung **skor hibrida** = 70% kemiripan semantik + 30% kecocokan skill langsung.
6. Skill CV dibandingkan dengan profil standar industri untuk menghitung **skor kesiapan kerja** berbobot.
7. Dashboard menampilkan metrik, daftar skill gap, dan rekomendasi lowongan teratas.

---

## 4. Penjelasan Model AI

### Sentence-BERT (all-MiniLM-L6-v2)
Model deep learning ringan (~120MB) yang mengubah teks menjadi vektor 384 dimensi. Vektor ini merepresentasikan **makna kontekstual** teks — sehingga dua teks yang artinya mirip akan memiliki vektor yang dekat satu sama lain meskipun kata-katanya berbeda.

### FAISS (Facebook AI Similarity Search)
Library pencarian kemiripan vektor berkinerja tinggi. Kita menggunakan `IndexFlatIP` (Inner Product) yang menghitung **cosine similarity** antar vektor. Karena vektor sudah dinormalisasi (panjang L2 = 1), inner product = cosine similarity.

### Rumus Skor Hibrida
```
Skor Akhir = 0.7 × Skor Semantik BERT + 0.3 × Skor Overlap Skill
```
- **Skor Semantik BERT**: Seberapa mirip makna teks CV dengan deskripsi lowongan (0.0 - 1.0).
- **Skor Overlap Skill**: Proporsi skill lowongan yang dimiliki pelamar (jumlah skill cocok / total skill lowongan).

### Skor Kesiapan Kerja (Readiness Score)
Rata-rata tertimbang dari 4 kategori skill:
- **Core Skills**: bobot 40% — skill inti yang wajib dimiliki
- **Expected Skills**: bobot 30% — skill yang umum diharapkan
- **Nice to Have**: bobot 15% — skill tambahan yang menjadi nilai plus
- **Soft Skills**: bobot 15% — kemampuan non-teknis (komunikasi, teamwork)

---

## 5. Cara Menjalankan

```bash
# Masuk ke folder CV Recommender
cd cv_recommender

# Jalankan dashboard Streamlit
streamlit run streamlit_app.py
```

Pastikan folder `models/` berisi file artefak yang diperlukan (`faiss_job_index.bin`, `job_metadata.csv`, `job_role_profiles.json`, `skill_taxonomy.json`).
