
### Langkah : Mempersiapkan Dataset Pendukung (PowerTransformer)
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
