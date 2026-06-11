# Skill Gap Analytics Dashboard

Proyek ini adalah platform visualisasi data interaktif untuk menganalisis kesenjangan keterampilan (Skill Gap Analysis) antara standar kurikulum akademis dengan tuntutan riil pasar kerja industri.

Analisis dilakukan dengan membandingkan:
1. **Kurikulum Akademis (Standar O*NET)**: Mewakili rujukan profesi dan kurikulum pengajaran.
2. **Kebutuhan Industri (Adzuna API)**: Data lowongan kerja aktual yang mencerminkan permintaan pasar kerja terkini.

---

## Struktur Folder Aplikasi

| File | Fungsi |
|------|--------|
| `analysis.ipynb` | Notebook analisis — membaca data mentah, menghitung skor gap, menyimpan `skill_gap_analysis.csv` |
| `app.py` | Dashboard Streamlit yang menampilkan hasil `skill_gap_analysis.csv` |
| `adzuna_jobs.csv` | Data lowongan kerja dari Adzuna API (sumber data industri) |
| `cached_data.csv` | Cache data industri dari Aiven Kafka (hasil `fetch_and_save_cache.py`) |
| `skill_gap_analysis.csv` | Hasil akhir analisis, dibaca oleh `app.py` |
| `fetch_and_save_cache.py` | Script terpisah untuk update cache dari Kafka (jalankan manual saat perlu data terbaru) |
| `db_30_2_excel/` | Folder berisi file referensi standar O*NET (Technology Skills, Skills, dll.) |

---

## Cara Menjalankan

### 1. Jalankan Notebook Analisis (Pertama Kali)
Buka `analysis.ipynb` di Jupyter Notebook dan jalankan semua cell. Notebook ini akan membaca data mentah, menghitung skor gap, dan menyimpan hasilnya ke `skill_gap_analysis.csv`.

### 2. Jalankan Dashboard
```bash
cd gap_analysis
streamlit run app.py
```

---

## Fitur Dashboard

1. **Top 3 Kesenjangan Tertinggi** — Menampilkan 3 skill dengan gap terbesar menggunakan metrik Streamlit.
2. **Grafik Perbandingan** — Grouped bar chart proporsi kemunculan skill di industri vs akademik.
3. **Tabel Data Lengkap** — Seluruh data analisis dalam tabel interaktif.
4. **Filter Kategori** — Pilih antara Hard Skill dan Soft Skill di sidebar.
