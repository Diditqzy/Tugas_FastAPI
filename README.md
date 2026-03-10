# 🏍️ Showroom Motor API - Management Information Systems

Tugas praktikum pembuatan REST API menggunakan framework **FastAPI** untuk pengelolaan data inventaris showroom motor. Proyek ini mendemonstrasikan integrasi antara Python, SQLAlchemy (ORM), dan database SQLite.

## 🚀 Fitur Utama
* **Create Data**: Menambahkan unit motor baru ke database.
* **Read All Data**: Menampilkan daftar seluruh motor yang tersedia.
* **Read Detail Data**: Mencari informasi motor spesifik berdasarkan `idmotor`.
* **Database Persistence**: Menggunakan SQLite untuk penyimpanan data permanen.

## 🛠️ Tech Stack
* **Language**: Python
* **Framework**: FastAPI
* **ORM**: SQLAlchemy
* **Database**: SQLite
* **Validation**: Pydantic

## 📂 Struktur File
* `main.py` - Titik masuk aplikasi dan definisi endpoint.
* `models.py` - Definisi tabel database (Schema SQLAlchemy).
* `schemas.py` - Definisi validasi data dan format respons (Pydantic).
* `database.py` - Konfigurasi koneksi database SQLite.
* `items.db` - File database lokal.

## 📝 Panduan Menjalankan Proyek
Ikuti langkah-langkah berikut di terminal VS Code untuk menjalankan aplikasi:
### 1. Aktivasi Virtual Environment
Pastikan folder `venv` sudah tersedia, lalu jalankan perintah ini untuk mengaktifkan lingkungan kerja:
👉 .\venv\Scripts\activate
### 2. Menjalankan Server API
Gunakan Uvicorn untuk menjalankan aplikasi. Parameter --reload digunakan agar server otomatis mendeteksi perubahan kode:
👉 uvicorn main:app --reload
### 3. Mengakses Dokumentasi & Link Web
Setelah server berjalan (muncul tulisan Uvicorn running on http://127.0.0.1:8000), buka browser dan akses link berikut:
👉 http://127.0.0.1:8000/docs

## 🧑‍💼 Pembuat
Didit Iqbal Alfaruzy
