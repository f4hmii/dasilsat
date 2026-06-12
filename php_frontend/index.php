<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Prediksi harga jual mobil bekas pasar Amerika Serikat secara akurat dengan teknologi Machine Learning — Decision Tree, Neural Network, atau SVM.">
    <title>CarValuate - AI Estimasi Harga Mobil Bekas | DT · NN · SVM</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="assets/css/style.css?v=<?php echo time(); ?>">
</head>
<body>

    <!-- Latar Belakang Gradasi Dinamis -->
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <div class="container">
        <!-- Header -->
        <header class="app-header">
            <div class="logo">
                <h1>Car<span>Valuate</span></h1>
            </div>
            <p class="subtitle">Prediksi harga jual mobil bekas pasar AS secara instan menggunakan kecerdasan buatan.</p>
            <div class="model-badge">
                <span class="badge-item" id="headerAlgoBadge"><i class="fa-solid fa-circle-check"></i> Decision Tree Regressor</span>
            </div>
        </header>

        <!-- ============================================================ -->
        <!-- Navbar Pemilihan Model ML                                    -->
        <!-- ============================================================ -->
        <nav class="model-nav" id="modelNav" aria-label="Pilih Model ML">
            <div class="model-nav-label">
                <i class="fa-solid fa-microchip"></i>
                <span>Model :</span>
            </div>
            <div class="model-nav-tabs" id="modelSelectorGrid">
                <div class="model-tab-skeleton"></div>
                <div class="model-tab-skeleton"></div>
                <div class="model-tab-skeleton"></div>
            </div>
            <div class="model-nav-active-info">
                <span class="active-label">Aktif:</span>
                <span class="active-name" id="activeModelName">DT</span>
            </div>
        </nav>

        <!-- Main Content Grid -->
        <main class="main-grid">
            
            <!-- Section Kiri: Form Input -->
            <section class="card-form-wrapper">
                <div class="glass-card form-card">
                    <div class="card-header">
                        <h2><i class="fa-solid fa-sliders-h"></i> Spesifikasi Kendaraan</h2>
                        <p>Lengkapi formulir di bawah ini dengan spesifikasi detail mobil.</p>
                    </div>

                    <form id="predictionForm" autocomplete="off">
                        <div class="form-grid">

                            <!-- Merek Mobil -->
                            <div class="form-group">
                                <label for="brand"><i class="fa-solid fa-copyright"></i> Merek Mobil</label>
                                <div class="input-wrapper">
                                    <input type="text" id="brand" list="brandList" placeholder="Contoh: Audi, BMW, Toyota..." required>
                                    <datalist id="brandList"></datalist>
                                    <i class="fa-solid fa-chevron-down input-chevron"></i>
                                </div>
                            </div>

                            <!-- Model Mobil -->
                            <div class="form-group">
                                <label for="model"><i class="fa-solid fa-tags"></i> Model Mobil</label>
                                <div class="input-wrapper">
                                    <input type="text" id="model" list="modelList" placeholder="Pilih merek terlebih dahulu..." disabled required>
                                    <datalist id="modelList"></datalist>
                                    <i class="fa-solid fa-chevron-down input-chevron"></i>
                                </div>
                            </div>

                            <!-- Jarak Tempuh -->
                            <div class="form-group full-width">
                                <label for="milage"><i class="fa-solid fa-gauge"></i> Jarak Tempuh (Mileage)</label>
                                <div class="input-wrapper">
                                    <input type="number" id="milage" step="any" min="0" placeholder="Contoh: 15000" required>
                                    <span class="input-unit">mi</span>
                                </div>
                            </div>

                            <!-- Riwayat Kecelakaan -->
                            <div class="form-group">
                                <label for="accident"><i class="fa-solid fa-triangle-exclamation"></i> Riwayat Kecelakaan</label>
                                <div class="input-wrapper">
                                    <select id="accident" required>
                                        <option value="" disabled selected>Pilih status kecelakaan...</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Status Dokumen -->
                            <div class="form-group">
                                <label for="clean_title"><i class="fa-solid fa-file-invoice"></i> Status Dokumen (Clean Title)</label>
                                <div class="input-wrapper">
                                    <select id="clean_title" required>
                                        <option value="" disabled selected>Pilih status dokumen...</option>
                                    </select>
                                </div>
                            </div>

                        </div>

                        <!-- Button Predict -->
                        <button type="submit" class="btn-predict" id="btnPredict">
                            <span class="btn-text">Prediksi Harga Sekarang</span>
                            <i class="fa-solid fa-bolt btn-icon"></i>
                        </button>
                    </form>
                </div>
            </section>

            <!-- Section Kanan: Hasil Prediksi & Info Model -->
            <section class="card-result-wrapper">
                
                <!-- Card Hasil Prediksi (Akan Diubah Statusnya Secara Dinamis oleh JS) -->
                <div class="glass-card result-card idle" id="resultCard">
                    <!-- Idle State -->
                    <div class="result-state state-idle">
                        <div class="pulse-icon">
                            <i class="fa-solid fa-robot"></i>
                        </div>
                        <h3>Menunggu Input Kendaraan</h3>
                        <p>Silakan isi spesifikasi mobil bekas Anda pada formulir sebelah kiri dan klik tombol prediksi.</p>
                    </div>

                    <!-- Loading State -->
                    <div class="result-state state-loading d-none">
                        <div class="car-loading-anim">
                            <i class="fa-solid fa-car-side"></i>
                            <div class="road-lines"></div>
                        </div>
                        <h3>Menganalisis Nilai Pasar...</h3>
                        <p>Kecerdasan Buatan sedang memetakan spesifikasi dengan database pasar...</p>
                    </div>

                    <!-- Success State -->
                    <div class="result-state state-success d-none">
                        <div class="success-icon">
                            <i class="fa-solid fa-circle-check"></i>
                        </div>
                        <span class="result-badge">Estimasi Harga Jual</span>
                        
                        <div class="price-container">
                            <h2 class="price-usd" id="priceUsd">$0.00</h2>
                            <p class="price-sub">USD (Nilai Pasar Amerika Serikat)</p>
                        </div>
                        
                        <!-- Currency Converter (IDR) -->
                        <div class="converter-box">
                            <div class="converter-header">
                                <span><i class="fa-solid fa-money-bill-transfer"></i> Konversi ke Rupiah (IDR)</span>
                                <span class="rate-badge">1 USD = Rp 17.905</span>
                            </div>
                            <h3 class="price-idr" id="priceIdr">Rp 0</h3>
                        </div>

                        <!-- Info Rincian Fitur Utama -->
                        <div class="result-details">
                            <div class="detail-row">
                                <span>Merek & Model</span>
                                <strong id="resCarName">-</strong>
                            </div>
                            <div class="detail-row">
                                <span>Tahun Pembuatan</span>
                                <strong id="resCarYear">-</strong>
                            </div>
                            <div class="detail-row">
                                <span>Jarak Tempuh (Mileage)</span>
                                <strong id="resCarMilage">-</strong>
                            </div>
                        </div>

                        <!-- Reset Button -->
                        <button type="button" class="btn-reset" id="btnReset">
                            <i class="fa-solid fa-rotate-left"></i> Hitung Ulang Prediksi
                        </button>
                    </div>

                    <!-- Error State -->
                    <div class="result-state state-error d-none" id="errorState">
                        <div class="error-icon">
                            <i class="fa-solid fa-triangle-exclamation"></i>
                        </div>
                        <h3>Prediksi Gagal</h3>
                        <p id="errorMessage">Terjadi kesalahan pada koneksi server API FastAPI. Pastikan server python Anda menyala di port 8000.</p>
                        <button type="button" class="btn-retry" id="btnRetry">
                            <i class="fa-solid fa-arrows-rotate"></i> Coba Lagi
                        </button>
                    </div>
                </div>
            </section>

            <!-- Card Informasi Model & Akurasi (Dinamis) -->
            <div class="glass-card info-card">
                <h3><i class="fa-solid fa-brain"></i> Informasi Model Aktif</h3>
                <div class="info-list">
                    <div class="info-item">
                        <div class="info-label">Algoritma Digunakan</div>
                        <div class="info-value" id="infoAlgoName">Decision Tree Regressor</div>
                        <div class="info-desc" id="infoAlgoDesc">Model pohon keputusan yang cepat dan mudah diinterpretasikan.</div>
                    </div>

                    <div class="info-item">
                        <div class="info-label">Mean Absolute Error (MAE)</div>
                        <div class="info-value" id="infoMAE">$4,454.57</div>
                        <div class="info-desc">Rata-rata kesalahan prediksi dibandingkan harga asli di pasar.</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Teknik Rekayasa Fitur</div>
                        <div class="info-desc" id="infoFeatureEng">Menggunakan <strong>Target Encoding</strong> untuk data kategorikal berdimensi tinggi dan <strong>Log Transform</strong> pada harga dasar agar distorsi harga ekstrem tereduksi.</div>
                    </div>
                </div>
            </div>
        </main>
        
        <!-- Footer -->
        <footer class="app-footer">
            <p>&copy; 2026 CarValuate. Proyek Portofolio Machine Learning Terintegrasi (FastAPI & PHP).</p>
        </footer>
    </div>

    <!-- JS Scripts -->
    <script src="assets/js/script.js"></script>
</body>
</html>
