# -*- coding: utf-8 -*-
# ==============================================================================
# 🚀 SCRIPT PRE-FETCHING KAFKA: Pengambilan Data Aiven Kafka ke Cache CSV Lokal
# Berkas ini digunakan untuk mengonsumsi data lowongan pekerjaan dari Aiven Kafka,
# kemudian menyimpannya sebagai file CSV lokal agar Dashboard Streamlit dapat 
# merender data secara offline dan instan tanpa latensi jaringan Kafka.
# Politeknik Negeri Madiun - S4 Data Engineering
# ==============================================================================

# Mengimpor modul bawaan Python 'os' untuk interaksi dengan sistem berkas dan path direktori
import os

# Mengimpor modul bawaan Python 'json' untuk memparsing pesan data berformat JSON dari Kafka
import json

# Mengimpor modul bawaan Python 'uuid' untuk membuat ID unik acak (Consumer Group ID)
import uuid

# Mengimpor modul bawaan Python 'time' untuk melakukan penundaan (delay) dan mencatat batas waktu (timeout)
import time

# Mengimpor library 'pandas' (sebagai pd) untuk menyusun data pesan menjadi DataFrame dan mengekspor ke CSV
import pandas as pd

# Mengimpor kelas 'KafkaConsumer' dari pustaka 'kafka-python' untuk membaca aliran data dari broker Kafka
from kafka import KafkaConsumer

# Menampilkan informasi awal proses pengambilan data di konsol/terminal
print("==========================================================")
print("🚀 PRE-FETCHING KAFKA DATA FOR STREAMILIT OFFLINE CACHE 🚀")
print("==========================================================")

# Mendefinisikan alamat broker Aiven Kafka Cloud (URI broker bootstrap)
KAFKA_BROKER = "kafka-90a3cd4-cejors-676945.g.aivencloud.com:28174"

# Nama topik antrean pesan Kafka yang akan dikonsumsi
TOPIC_NAME = "unified_jobs"

# Nama file CSV target tempat menyimpan data cache pekerjaan hasil pre-fetching
CACHE_FILE = "cached_data.csv"

# Menentukan path lokasi sertifikat SSL untuk koneksi aman ke Aiven Kafka
# sertifikat CA (Certificate Authority)
CA_FILE = "ssl/ca.pem"
# sertifikat layanan client
CERT_FILE = "ssl/service.cert"
# kunci privat layanan client
KEY_FILE = "ssl/service.key"

# Membuat Group ID konsumen acak menggunakan uuid4() agar setiap eksekusi script 
# dianggap sebagai consumer baru dan membaca dari awal tanpa mengganggu group lain.
# hex[:8]: Mengambil 8 karakter heksadesimal pertama dari UUID
random_group_id = f"fetch-group-{uuid.uuid4().hex[:8]}"

try:
    print("-> Connecting to Aiven Kafka Cloud broker...")
    # Instansiasi objek KafkaConsumer untuk melakukan koneksi aman berbasis SSL
    # Parameter TOPIC_NAME: Topik target yang dilanggan
    # Parameter bootstrap_servers: Alamat broker Kafka cloud
    # Parameter security_protocol: Protokol keamanan yang digunakan ("SSL")
    # Parameter ssl_cafile/certfile/keyfile: File sertifikat SSL untuk otentikasi
    # Parameter auto_offset_reset: Membaca dari pesan paling awal ('earliest') jika offset belum ada
    # Parameter enable_auto_commit: Menonaktifkan commit otomatis (False) agar status offset tidak tergeser permanen
    # Parameter group_id: Penanda kelompok konsumen unik
    # Parameter value_deserializer: Fungsi lambda untuk mendecode bytes ke teks UTF-8 lalu di-load sebagai dictionary JSON
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        security_protocol="SSL",
        ssl_cafile=CA_FILE,
        ssl_certfile=CERT_FILE,
        ssl_keyfile=KEY_FILE,
        auto_offset_reset='earliest', 
        enable_auto_commit=False,
        group_id=random_group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    # Inisialisasi list penampung partisi yang teralokasi
    assigned_partitions = []
    # Mencatat waktu awal mulai mencoba alokasi partisi
    start_time = time.time()
    
    # Loop untuk menunggu Kafka broker mengalokasikan partisi (partition assignment) ke konsumen baru ini
    while not assigned_partitions:
        # Memicu polling pesan singkat untuk mengaktifkan koneksi dan memicu assignment
        # Parameter timeout_ms: Waktu tunggu polling dalam milidetik (1000ms)
        consumer.poll(timeout_ms=1000)
        # Mengambil daftar partisi yang ditugaskan ke consumer saat ini menggunakan assignment()
        assigned_partitions = list(consumer.assignment())
        if not assigned_partitions:
            print("   -> Waiting for partition assignments...")
            # Menunda eksekusi selama 1 detik menggunakan time.sleep()
            time.sleep(1)
        # Memeriksa apakah batas waktu tunggu alokasi partisi melebihi 15 detik
        if time.time() - start_time > 15:
            print("   ⚠️ Partition allocation timed out.")
            break
            
    # Jika setelah 15 detik tetap tidak mendapatkan partisi, hentikan proses dengan status error
    if not assigned_partitions:
        print("❌ Failed to get partitions.")
        # Menutup koneksi consumer menggunakan close()
        consumer.close()
        # Mengakhiri script dengan kode keluar 1 (error)
        exit(1)
        
    print(f"✅ Connected to partitions: {[tp.partition for tp in assigned_partitions]}")
    # Mengambil koordinat offset akhir (pesan terbaru) untuk setiap partisi menggunakan end_offsets()
    # Parameter assigned_partitions: List partisi yang akan dicari offset akhirnya
    end_offsets = consumer.end_offsets(assigned_partitions)
    
    # List kosong untuk mengumpulkan pesan lowongan pekerjaan
    records = []
    # Mencatat waktu mulai proses polling penarikan pesan dari broker
    poll_start_time = time.time()
    
    # Loop utama untuk menarik seluruh pesan hingga mencapai offset akhir (end offset)
    while True:
        all_completed = True
        # Memeriksa apakah posisi baca konsumen saat ini sudah menyentuh atau melampaui offset akhir di setiap partisi
        for tp in assigned_partitions:
            # consumer.position(): Mengambil offset posisi baca saat ini untuk partisi tertentu (tp)
            if consumer.position(tp) < end_offsets[tp]:
                all_completed = False
                break
                
        # Jika semua partisi sudah terbaca habis sampai offset terbaru, hentikan loop
        if all_completed:
            print("✅ Reached the end offset of all partitions!")
            break
            
        # Mengambil batch pesan dari broker Kafka menggunakan poll()
        # Parameter timeout_ms: Waktu tunggu maksimal jika tidak ada pesan baru (2500ms)
        msg_pack = consumer.poll(timeout_ms=2500)
        if msg_pack:
            batch_count = 0
            # Melakukan perulangan pada partisi dan daftar pesan yang diterima
            for tp, messages in msg_pack.items():
                batch_count += len(messages)
                for message in messages:
                    # Menambahkan isi payload pesan (message.value) ke list records
                    records.append(message.value)
            print(f"   -> Consumed {batch_count} messages (Total so far: {len(records)})...")
        else:
            # Jika tidak ada pesan baru yang masuk dalam polling, tunggu sejenak sebelum mencoba lagi
            print("   -> Waiting for next segment load...")
            time.sleep(1)
            
        # Batasan pengaman (safety timeout): Jika proses memakan waktu lebih dari 120 detik, hentikan penarikan
        if time.time() - poll_start_time > 120:
            print("   ⚠️ Maximum fetch timeout of 2 minutes reached.")
            break
            
    # Menutup koneksi ke Kafka broker
    consumer.close()
    
    # Jika ada data records yang berhasil ditarik, ubah menjadi CSV
    if records:
        # Mengubah kumpulan dictionary records menjadi DataFrame pandas
        df = pd.DataFrame(records)
        # Menyimpan DataFrame ke file CSV lokal
        # Parameter CACHE_FILE: Nama file output tujuan penyimpanan
        # Parameter index=False: Menghilangkan kolom index default DataFrame saat disimpan
        df.to_csv(CACHE_FILE, index=False)
        print(f"🎉 SUCCESS: Saved {len(df)} records into '{CACHE_FILE}'!")
    else:
        print("⚠️ No messages were fetched.")
        
except Exception as e:
    # Menangkap dan menampilkan error jika koneksi atau pemrosesan gagal
    print(f"❌ Error occurred during Kafka consume: {e}")
