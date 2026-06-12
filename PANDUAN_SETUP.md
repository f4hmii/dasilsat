# Panduan Instalasi dan Setup Project (Dari Nol)

Dokumen ini berisi panduan lengkap bagi pengguna baru yang ingin menyalin (clone) proyek ini dari GitHub dan menjalankannya di komputer lokal.

---

## 🛠️ Prasyarat (Prerequisites)
Sebelum memulai, pastikan komputer Anda telah terinstal perangkat lunak berikut:
1. **Git**: Untuk melakukan kloning repositori ([Unduh Git](https://git-scm.com/)).
2. **XAMPP**: Untuk menjalankan web server Apache (PHP) lokal ([Unduh XAMPP](https://www.apachefriends.org/)).
3. **Python (Versi 3.8 s.d 3.12)**: Untuk menjalankan backend kecerdasan buatan ([Unduh Python](https://www.python.org/downloads/)).
   > [!IMPORTANT]
   > Pastikan Anda mencentang opsi **"Add Python to PATH"** saat melakukan instalasi Python.

---

## 🚀 Langkah demi Langkah

### Langkah 1: Kloning Repositori ke Folder XAMPP
Agar program PHP dapat diakses langsung oleh server web lokal Apache, Anda harus mengkloning repositori ini ke dalam direktori `htdocs` dari XAMPP.

1. Buka Terminal (Git Bash, Command Prompt, atau PowerShell).
2. Pindah ke direktori `htdocs` XAMPP Anda:
   ```bash
   cd C:\xampp\htdocs
   ```
3. Lakukan kloning repositori dengan perintah berikut:
   ```bash
   git clone https://github.com/f4hmii/dasilsat.git hargamobil
   ```
   *Perintah di atas akan mendownload semua berkas proyek ke dalam folder baru bernama `hargamobil`.*

---

### Langkah 2: Mempersiapkan Dataset Pendukung (PowerTransformer)
Backend AI menggunakan modul `PowerTransformer` (Yeo-Johnson) untuk menormalkan data realtime. Model membutuhkan data pembanding dari dataset asli agar dapat di-fit di awal.

1. Unduh dataset `used_cars.csv`.
2. Letakkan berkas tersebut di folder **Downloads** komputer Anda pada jalur berikut:
   ```text
   C:\Users\<Nama_Pengguna_Windows>\Downloads\used_cars.csv
   ```
   > [!NOTE]
   > Gantilah `<Nama_Pengguna_Windows>` sesuai nama akun Windows Anda. Backend akan otomatis mencari file ini saat server pertama kali dijalankan untuk membuat model transformasi `used_car_pt_nn.sav`.

---

### Langkah 3: Setup dan Menjalankan Backend (FastAPI)
Layanan backend bertugas untuk memuat model Machine Learning dan melayani permintaan prediksi harga.

1. Buka terminal baru dan masuk ke folder backend:
   ```bash
   cd C:\xampp\htdocs\hargamobil\ai_backend
   ```
2. *(Opsional tetapi Sangat Direkomendasikan)* Buat dan aktifkan virtual environment Python agar tidak bentrok dengan library lain:
   ```bash
   # Membuat virtual environment
   python -m venv venv

   # Mengaktifkan di Windows (Command Prompt)
   venv\Scripts\activate.bat

   # Mengaktifkan di Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   ```
3. Install seluruh dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server API menggunakan Uvicorn:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *Tunggu beberapa saat. Pada startup pertama, backend akan membaca dataset `used_cars.csv` untuk mem-fit PowerTransformer. Setelah sukses, server API akan aktif di alamat `http://127.0.0.1:8000`.*

---

### Langkah 4: Menjalankan Frontend (PHP Apache)
1. Buka aplikasi **XAMPP Control Panel**.
2. Klik tombol **Start** pada modul **Apache**.
3. Buka browser internet Anda (Chrome, Edge, Firefox, dll), lalu akses alamat berikut:
   ```http
   http://localhost/hargamobil/php_frontend/index.php
   ```
4. Aplikasi siap digunakan! Anda sekarang dapat memilih antara model **Decision Tree (DT)**, **Support Vector Regressor (SVR)**, atau **Neural Network (NN)** untuk melakukan estimasi harga mobil.

---

## 🔍 Troubleshooting (Penyelesaian Masalah)
* **Error: Port 8000 sudah digunakan**: Jika port `8000` bentrok dengan aplikasi lain, Anda bisa menggantinya ke port lain saat menjalankan uvicorn (misal `--port 8001`), lalu jangan lupa perbarui variabel `BASE_URL` di dalam berkas [script.js](file:///c:/xampp/htdocs/hargamobil/php_frontend/assets/js/script.js) agar mengarah ke port baru tersebut.
* **Tampilan Web Tidak Berubah (CSS Cache)**: Jika CSS tidak langsung terupdate di browser, lakukan *hard refresh* dengan menekan kombinasi tombol `Ctrl + F5` pada browser Anda.
