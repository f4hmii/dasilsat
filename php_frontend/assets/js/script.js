document.addEventListener("DOMContentLoaded", () => {

    // =====================================================================
    // 1. REFERENSI ELEMEN DOM
    // =====================================================================
    const form              = document.getElementById("predictionForm");
    const brandInput        = document.getElementById("brand");
    const brandList         = document.getElementById("brandList");
    const modelInput        = document.getElementById("model");
    const modelList         = document.getElementById("modelList");
    const milageInput       = document.getElementById("milage");
    const accidentSelect    = document.getElementById("accident");
    const cleanTitleSelect  = document.getElementById("clean_title");
    const btnPredict        = document.getElementById("btnPredict");

    const modelSelectorGrid = document.getElementById("modelSelectorGrid");
    const headerAlgoBadge   = document.getElementById("headerAlgoBadge");
    const activeModelNameEl = document.getElementById("activeModelName");

    const resultCard        = document.getElementById("resultCard");
    const stateIdle         = document.querySelector(".state-idle");
    const stateLoading      = document.querySelector(".state-loading");
    const stateSuccess      = document.querySelector(".state-success");
    const stateError        = document.getElementById("errorState");

    const priceUsdEl        = document.getElementById("priceUsd");
    const priceIdrEl        = document.getElementById("priceIdr");
    const resCarNameEl      = document.getElementById("resCarName");
    const resCarYearEl      = document.getElementById("resCarYear");
    const resCarMilageEl    = document.getElementById("resCarMilage");
    const errMessageEl      = document.getElementById("errorMessage");

    const btnReset  = document.getElementById("btnReset");
    const btnRetry  = document.getElementById("btnRetry");

    // =====================================================================
    // 2. KONFIGURASI
    // =====================================================================
    const BASE_URL          = "http://127.0.0.1:8000";
    const API_URL           = `${BASE_URL}/predict`;
    const MODELS_URL        = `${BASE_URL}/models`;
    const IDR_EXCHANGE_RATE = 17905;

    let selectedAlgorithm = "DT";
    let allModels         = [];

    // Data katalog
    let carMappings = {};
    let carOptions  = {};

    // =====================================================================
    // 3a. MUAT DATA JSON (mapping & opsi)
    // =====================================================================
    async function loadAllData() {
        try {
            const [mappingRes, optionsRes] = await Promise.all([
                fetch("assets/js/car_mappings.json"),
                fetch("assets/js/car_options.json")
            ]);
            if (!mappingRes.ok) throw new Error("Gagal car_mappings.json");
            if (!optionsRes.ok) throw new Error("Gagal car_options.json");

            carMappings = await mappingRes.json();
            carOptions  = await optionsRes.json();

            initStaticDropdowns();
            populateBrandList();
        } catch (err) {
            console.error("Kesalahan memuat data JSON:", err);
            showError("Gagal memuat katalog opsi mobil dari server lokal.");
        }
    }

    // =====================================================================
    // 3b. MUAT DAFTAR MODEL DARI API
    // =====================================================================
    async function loadModels() {
        try {
            const res = await fetch(MODELS_URL);
            if (!res.ok) throw new Error("Gagal mengambil daftar model.");
            const data = await res.json();
            allModels = data.models;
            renderModelTabs(allModels);
            const firstAvail = allModels.find(m => m.available);
            if (firstAvail && activeModelNameEl) activeModelNameEl.textContent = firstAvail.short;
        } catch (err) {
            console.error("Gagal memuat model:", err);
            allModels = [
                { key: "DT",  name: "Decision Tree Regressor",  short: "DT",  mae: 4454.57, description: "Model pohon keputusan yang cepat dan mudah diinterpretasikan.", feature_engineering: "Menggunakan Target Encoding untuk data kategorikal berdimensi tinggi dan Log Transform pada harga dasar agar distorsi harga ekstrem tereduksi.", available: true  },
                { key: "SVR", name: "Support Vector Regressor", short: "SVR", mae: null,    description: "Model SVR dengan kernel RBF efektif pada data berdimensi tinggi.", feature_engineering: "Menggunakan Ordinal Encoding manual pada fitur utama terpilih dan pemetaan koordinat kernel RBF tanpa transformasi log pada target.", available: true  },
                { key: "NN",  name: "Neural Network (MLP)",     short: "NN",  mae: null,    description: "Jaringan saraf tiruan multi-lapisan untuk pola non-linear kompleks.", feature_engineering: "Menggunakan kombinasi fitur interaksi (usia-milage, daya-displacement), transformasi non-linear Yeo-Johnson (PowerTransformer), Dummy Encoding (One-Hot), dan standardisasi StandardScaler.", available: false },
            ];
            renderModelTabs(allModels);
        }
    }

    // =====================================================================
    // 3c. RENDER NAVBAR TAB MODEL
    // =====================================================================
    function renderModelTabs(models) {
        modelSelectorGrid.innerHTML = "";
        models.forEach(m => {
            const isActive  = m.key === selectedAlgorithm;
            const isUnavail = !m.available;

            const tab = document.createElement("button");
            tab.type      = "button";
            tab.className = `model-tab${isActive ? " active" : ""}${isUnavail ? " disabled" : ""}`;
            tab.dataset.key = m.key;
            tab.disabled    = isUnavail;
            tab.title       = isUnavail ? `${m.name} — Belum tersedia` : m.name;
            tab.setAttribute("aria-label", m.name);
            tab.innerHTML   = `
                <span class="tab-label">${m.short}</span>
                ${isUnavail ? '<span class="tab-soon">soon</span>' : ""}
            `;
            if (!isUnavail) tab.addEventListener("click", () => selectModel(m.key));
            modelSelectorGrid.appendChild(tab);
        });
    }

    function selectModel(key) {
        selectedAlgorithm = key;
        document.querySelectorAll(".model-tab").forEach(t =>
            t.classList.toggle("active", t.dataset.key === key)
        );
        if (activeModelNameEl) activeModelNameEl.textContent = key;
        const m = allModels.find(x => x.key === key);
        if (m) updateInfoPanel(m);
    }

    function updateInfoPanel(m) {
        const infoAlgoName   = document.getElementById("infoAlgoName");
        const infoAlgoDesc   = document.getElementById("infoAlgoDesc");
        const infoMAE        = document.getElementById("infoMAE");
        const infoFeatureEng = document.getElementById("infoFeatureEng");
        if (infoAlgoName) infoAlgoName.textContent = m.name;
        if (infoAlgoDesc) infoAlgoDesc.textContent = m.description;
        if (infoMAE) infoMAE.textContent = m.mae != null
            ? `$${m.mae.toLocaleString("en-US")}` : "Belum tersedia";
        if (infoFeatureEng) {
            infoFeatureEng.innerHTML = m.feature_engineering || "Spesifikasi rekayasa fitur belum didefinisikan.";
        }
        if (headerAlgoBadge) headerAlgoBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${m.name}`;
    }

    // =====================================================================
    // 4. DROPDOWN STATIS (accident, clean_title)
    // =====================================================================
    function initStaticDropdowns() {
        if (carOptions.accident) {
            accidentSelect.innerHTML =
                `<option value="" disabled selected>Pilih status kecelakaan...</option>` +
                carOptions.accident.map(a => `<option value="${a}">${a}</option>`).join("");
        }
        if (carOptions.clean_title) {
            cleanTitleSelect.innerHTML =
                `<option value="" disabled selected>Pilih status dokumen...</option>` +
                carOptions.clean_title.map(t => `<option value="${t}">${t}</option>`).join("");
        }
    }

    // =====================================================================
    // 5. ISI DATALIST MEREK
    // =====================================================================
    function populateBrandList() {
        brandList.innerHTML = Object.keys(carMappings).sort()
            .map(b => `<option value="${b}"></option>`).join("");
    }

    // =====================================================================
    // 6. RESET FIELD DEPENDEN (model saja)
    // =====================================================================
    function resetDependentFields() {
        modelInput.value       = "";
        modelInput.disabled    = true;
        modelInput.placeholder = "Pilih merek terlebih dahulu...";
        modelList.innerHTML    = "";
    }

    // =====================================================================
    // 7. ISI MODEL BERDASARKAN MEREK
    // =====================================================================
    function populateDependentFields(brand) {
        const data = carMappings[brand];
        if (!data) return;
        modelInput.disabled    = false;
        modelInput.placeholder = "Ketik atau pilih model...";
        modelList.innerHTML    = data.models
            .map(m => `<option value="${m}"></option>`).join("");
    }

    // =====================================================================
    // 8. EVENT: INPUT MEREK
    // =====================================================================
    let lastValidBrand = "";

    brandInput.addEventListener("input", () => {
        const typed = brandInput.value.trim();
        if (carMappings[typed]) {
            if (typed !== lastValidBrand) {
                lastValidBrand = typed;
                resetDependentFields();
                populateDependentFields(typed);
                showBrandToast(`Opsi untuk: ${typed}`);
            }
        } else {
            lastValidBrand = "";
            resetDependentFields();
        }
    });

    // =====================================================================
    // 9. TOAST NOTIFIKASI MEREK
    // =====================================================================
    function showBrandToast(message) {
        let toast = document.getElementById("brandToast");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "brandToast";
            toast.style.cssText = `
                position:fixed; bottom:2rem; left:50%;
                transform:translateX(-50%) translateY(20px);
                background:linear-gradient(135deg,#6c63ff,#3b82f6);
                color:#fff; padding:.6rem 1.4rem; border-radius:999px;
                font-size:.85rem; font-weight:600;
                box-shadow:0 8px 30px rgba(108,99,255,.4);
                z-index:9999; opacity:0;
                transition:opacity .3s ease,transform .3s ease;
                pointer-events:none;
            `;
            document.body.appendChild(toast);
        }
        toast.textContent = "✅ " + message;
        toast.style.opacity   = "1";
        toast.style.transform = "translateX(-50%) translateY(0)";
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => {
            toast.style.opacity   = "0";
            toast.style.transform = "translateX(-50%) translateY(20px)";
        }, 2500);
    }

    // =====================================================================
    // 10. STATE UI HASIL
    // =====================================================================
    function setUIState(state) {
        resultCard.classList.remove("success", "idle");
        stateIdle.classList.add("d-none");
        stateLoading.classList.add("d-none");
        stateSuccess.classList.add("d-none");
        stateError.classList.add("d-none");

        if (state === "idle") {
            resultCard.classList.add("idle");
            stateIdle.classList.remove("d-none");
        } else if (state === "loading") {
            stateLoading.classList.remove("d-none");
        } else if (state === "success") {
            resultCard.classList.add("success");
            stateSuccess.classList.remove("d-none");
        } else if (state === "error") {
            stateError.classList.remove("d-none");
        }
    }

    function showError(msg) {
        errMessageEl.textContent = msg;
        setUIState("error");
    }

    // =====================================================================
    // 11. FORMAT & ANIMASI HARGA
    // =====================================================================
    function formatRupiah(number) {
        return new Intl.NumberFormat("id-ID", {
            style: "currency", currency: "IDR", maximumFractionDigits: 0
        }).format(number);
    }

    function animatePriceCounter(target) {
        let cur = 0;
        const frames = (1200 / 1000) * 60;
        const inc    = target / frames;
        let f = 0;
        const timer = setInterval(() => {
            f++;
            cur += inc;
            if (f >= frames) { cur = target; clearInterval(timer); }
            priceUsdEl.textContent = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(cur);
            priceIdrEl.textContent = formatRupiah(cur * IDR_EXCHANGE_RATE);
        }, 1000 / 60);
    }

    // =====================================================================
    // 12. SUBMIT — AUTO-FILL FIELD TERSEMBUNYI
    // =====================================================================
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const brand = brandInput.value.trim();
        const brandData = carMappings[brand] || {};

        // ── Auto-fill field yang tidak ditampilkan ke user ──────────────
        // Gunakan nilai pertama dari mapping merek, atau fallback ke string
        // yang tidak ada di kamus → backend akan pakai global_mean otomatis
        const autoFuelType    = brandData.fuel_types?.[0]    ?? "Gasoline";
        const autoTransmission= brandData.transmissions?.[0] ?? "Automatic";
        const autoEngine      = brandData.engines?.[0]       ?? "Unknown";
        const autoExtCol      = carOptions.ext_col?.[0]      ?? "Black";
        const autoIntCol      = carOptions.int_col?.[0]      ?? "Black";
        // Tahun: pakai rata-rata tahun untuk merek tersebut
        const years     = brandData.years ?? [2020];
        const autoYear  = Math.round(years.reduce((a, b) => a + b, 0) / years.length);
        // ────────────────────────────────────────────────────────────────

        const payload = {
            brand:        brand,
            model:        modelInput.value.trim(),
            model_year:   autoYear,
            milage:       parseFloat(milageInput.value),
            fuel_type:    autoFuelType,
            engine:       autoEngine,
            transmission: autoTransmission,
            ext_col:      autoExtCol,
            int_col:      autoIntCol,
            accident:     accidentSelect.value,
            clean_title:  cleanTitleSelect.value,
            algorithm:    selectedAlgorithm
        };

        setUIState("loading");
        btnPredict.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Terjadi kesalahan pada respon server.");
            }
            const result = await response.json();
            if (result.status === "success") {
                resCarNameEl.textContent   = `${result.input_data.brand} ${result.input_data.model}`;
                resCarYearEl.textContent   = result.input_data.model_year;
                resCarMilageEl.textContent = new Intl.NumberFormat("en-US").format(result.input_data.milage) + " mil";
                setUIState("success");
                animatePriceCounter(result.predicted_price_usd);
            } else {
                throw new Error("Gagal mendapatkan prediksi harga.");
            }
        } catch (err) {
            console.error("API Error:", err);
            showError(err.message || "Gagal menghubungi server. Pastikan FastAPI berjalan di port 8000.");
        } finally {
            btnPredict.disabled = false;
        }
    });

    // =====================================================================
    // 13. RESET & RETRY
    // =====================================================================
    btnReset.addEventListener("click", () => {
        form.reset();
        lastValidBrand = "";
        resetDependentFields();
        initStaticDropdowns();
        setUIState("idle");
    });

    btnRetry.addEventListener("click", () => setUIState("idle"));

    // =====================================================================
    // MULAI
    // =====================================================================
    loadAllData();
    loadModels();
});
