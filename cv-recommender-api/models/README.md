# Model Artifacts

Folder ini berisi artefak model ML yang dihasilkan dari notebook `Machine_Learning.ipynb` (Part 1-5).

## Daftar File

| File | Sumber | Keterangan |
|------|--------|------------|
| `faiss_job_index.bin` | Part 3 | Indeks FAISS untuk pencarian semantik lowongan |
| `job_metadata.csv` | Part 3 | Metadata lowongan kerja (judul, lokasi, dll) |
| `job_role_profiles.json` | Part 4 | Profil skill standar per peran pekerjaan |
| `skill_taxonomy.json` | Part 4 | Kamus/taksonomi skill per kategori |
| `model_config.json` | Part 3 | Konfigurasi model embedding |
| `assessment_config.json` | Part 4 | Konfigurasi penilaian skill |

> **Catatan:** File `faiss_job_index.bin` dan `job_metadata.csv` disimpan menggunakan Git LFS karena ukurannya besar.
