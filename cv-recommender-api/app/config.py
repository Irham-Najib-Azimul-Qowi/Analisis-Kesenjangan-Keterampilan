"""
Konfigurasi aplikasi CV Recommender API.
File ini bertanggung jawab untuk memuat pengaturan aplikasi dari environment variables (variabel lingkungan)
dengan nilai default sebagai cadangan jika variabel lingkungan tidak diset.
"""
import os


class Settings:
    """
    Kelas Settings menyimpan seluruh konfigurasi global untuk backend API maupun integrasi model.
    Menggunakan os.getenv untuk membaca variabel dari sistem/file .env, sehingga fleksibel 
    saat dideploy ke server lokal maupun cloud (seperti Docker atau GCP).
    """

    # Host IP untuk menjalankan server FastAPI. Default '0.0.0.0' berarti mendengarkan semua interface jaringan.
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    
    # Port untuk server FastAPI. Default adalah 8080 (port standar untuk Cloud Run atau Docker container).
    API_PORT: int = int(os.getenv("API_PORT", "8080"))
    
    # Daftar origin (domain web) yang diizinkan melakukan request CORS. 
    # Sangat penting saat menghubungkan FastAPI backend dengan Next.js / Streamlit yang berjalan di domain berbeda.
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")

    # Nama model embedding dari HuggingFace (SentenceTransformers) yang digunakan.
    # Model 'all-MiniLM-L6-v2' adalah model yang sangat cepat, ringan, dan akurat untuk text embedding (384 dimensi).
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Nilai default untuk jumlah rekomendasi lowongan pekerjaan yang ingin ditampilkan (Top K).
    TOP_K_DEFAULT: int = int(os.getenv("TOP_K_DEFAULT", "5"))

    # Folder tempat menyimpan seluruh berkas model machine learning (FAISS index, metadata, JSON profil, dll).
    MODEL_DIR: str = os.getenv("MODEL_DIR", "models")


# Instansiasi objek settings agar bisa diimpor dan digunakan langsung di seluruh bagian aplikasi.
settings = Settings()

