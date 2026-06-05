import os
import sys
from google.cloud import storage

def download_artifacts_from_gcs(bucket_name: str, gcs_prefix: str, local_dir: str):
    """
    Mengunduh semua model ML artefak dari bucket GCS ke direktori lokal 'models/'.
    """
    try:
        client = storage.Client()
    except Exception as e:
        print("\n❌ Gagal membuat storage client.")
        print("Pastikan Anda sudah login menggunakan Google Cloud SDK di terminal Anda:")
        print("👉 gcloud auth application-default login")
        print(f"Error detail: {e}")
        sys.exit(1)

    bucket = client.bucket(bucket_name)
    
    artifact_files = [
        "faiss_job_index.bin",
        "job_metadata.csv",
        "job_role_profiles.json",
        "skill_taxonomy.json",
        "model_config.json",
        "assessment_config.json"
    ]
    
    os.makedirs(local_dir, exist_ok=True)
    
    print(f"\n🔄 Menghubungkan ke bucket GCS: '{bucket_name}'...")
    
    success_count = 0
    for filename in artifact_files:
        gcs_blob_path = f"{gcs_prefix}/{filename}" if gcs_prefix else filename
        blob = bucket.blob(gcs_blob_path)
        local_file_path = os.path.join(local_dir, filename)
        
        if blob.exists():
            print(f"📥 Mengunduh {filename} -> {local_file_path}...")
            blob.download_to_filename(local_file_path)
            print(f"✅ Berhasil mengunduh {filename}")
            success_count += 1
        else:
            print(f"⚠️ Warning: File {filename} tidak ditemukan di GCS pada path: gs://{bucket_name}/{gcs_blob_path}")
            
    if success_count == len(artifact_files):
        print("\n🎉 Semua artefak model berhasil diunduh dan siap digunakan!")
    else:
        print(f"\n⚠️ Selesai dengan catatan: Hanya {success_count}/{len(artifact_files)} file yang berhasil diunduh.")

if __name__ == "__main__":
    # ⚙️ Ganti dengan nama bucket GCS yang Anda gunakan
    BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "pnm-ml-model-artifacts")
    PREFIX = "cv-recommender/v1/artifacts"
    LOCAL_MODEL_DIR = "models"
    
    # Anda juga bisa membaca nama bucket dari argumen terminal: python download_models.py nama-bucket-anda
    if len(sys.argv) > 1:
        BUCKET_NAME = sys.argv[1]
        
    download_artifacts_from_gcs(BUCKET_NAME, PREFIX, LOCAL_MODEL_DIR)
