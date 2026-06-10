# ==============================================================================
# ⚙️ KONFIGURASI GLOBAL: Modul Konfigurasi Sistem CV Recommender
# Berkas ini digunakan untuk mendefinisikan seluruh konstanta dan pengaturan global
# agar parameter aplikasi (seperti nama model AI dan path folder) terpusat.
# ==============================================================================

# Mendefinisikan kelas 'Settings' untuk menampung konfigurasi aplikasi secara terstruktur
class Settings:
    # 1. Menentukan nama model embedding semantik yang digunakan dari HuggingFace.
    # Parameter 'all-MiniLM-L6-v2' adalah model Sentence-BERT ringan berbasis transformer 
    # yang mengubah teks deskriptif menjadi vektor numerik berdimensi 384 secara sangat cepat.
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # 2. Menentukan jalur direktori penyimpanan seluruh berkas model machine learning.
    # Nilai 'models' menunjuk ke folder lokal tempat berkas indeks FAISS (.bin), 
    # profil standar industri (.json), dan metadata lowongan kerja (.csv) disimpan.
    MODEL_DIR: str = "models"
    
    # 3. Menentukan daftar domain asal (Origin) yang diizinkan untuk melakukan request CORS.
    # Nilai ["*"] (tanda bintang/wildcard) berarti backend mengizinkan semua domain 
    # (seperti web frontend lokal Port 8501/3000) untuk mengakses API FastAPI ini.
    ALLOWED_ORIGINS: list = ["*"]

# Menginisialisasi objek konfigurasi tunggal (pola desain Singleton) dari kelas Settings.
# Objek 'settings' ini siap diimpor dan digunakan secara langsung di seluruh file sistem.
settings = Settings()


