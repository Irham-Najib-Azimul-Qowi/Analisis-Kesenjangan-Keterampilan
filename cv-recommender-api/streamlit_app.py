# -*- coding: utf-8 -*-
# ==============================================================================
# 🔄 REDIRECT/BRIDGE STREAMLIT: Jembatan untuk Folder yang Diganti Namanya
# Berkas ini digunakan sebagai jembatan karena Streamlit Cloud masih terkonfigurasi
# menggunakan path lama 'cv-recommender-api/streamlit_app.py'.
# Berkas ini akan mengarahkan eksekusi ke 'CV Recommender/streamlit_app.py'.
# Politeknik Negeri Madiun - S4 Data Engineering
# ==============================================================================

import sys
import os

# Mengambil path folder saat ini (cv-recommender-api) dan folder induknya
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

# Menentukan path absolut folder baru 'CV Recommender'
cv_rec_dir = os.path.join(parent_dir, "CV Recommender")

# Memasukkan folder 'CV Recommender' ke sistem path agar import modul 'app' dapat ditemukan
sys.path.insert(0, cv_rec_dir)

# Membaca dan mengeksekusi berkas streamlit_app.py yang berada di folder baru
target_file = os.path.join(cv_rec_dir, "streamlit_app.py")
if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        code = f.read()
    # Menyalin global namespace dan mendefinisikan ulang __file__ agar mengarah ke target asli
    globals_dict = globals().copy()
    globals_dict['__file__'] = target_file
    exec(code, globals_dict)
else:
    import streamlit as st
    st.error(f"Berkas target tidak ditemukan di: {target_file}")
