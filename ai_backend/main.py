from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import re

# ============================================================
# DYNAMIC PATCHING UNTUK COMPATIBILITY SCIKIT-LEARN 1.8.0
# ============================================================
import sklearn.compose._column_transformer
from sklearn.impute import SimpleImputer

class FakeRemainderColsList(list):
    pass

sklearn.compose._column_transformer._RemainderColsList = FakeRemainderColsList

if not hasattr(SimpleImputer, '_fill_dtype'):
    SimpleImputer._fill_dtype = property(lambda self: getattr(self, '_fit_dtype', np.float64))
# ============================================================

# Inisialisasi Aplikasi API
app = FastAPI(title="Used Car Price Predictor API")

# Tambahkan Middleware CORS agar Frontend PHP dapat mengakses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direktori dasar & folder model
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# ============================================================
# Metadata setiap model (ditampilkan di frontend)
# ============================================================
MODEL_METADATA = {
    "DT": {
        "name":        "Decision Tree Regressor",
        "short":       "DT",
        "file":        "used_car_model_dt.sav",
        "r2_score":    0.8940,
        "mae":         4454.57,
        "description": "Model pohon keputusan yang cepat dan mudah diinterpretasikan.",
        "feature_engineering": "Menggunakan Target Encoding untuk data kategorikal berdimensi tinggi dan Log Transform pada harga dasar agar distorsi harga ekstrem tereduksi.",
        "available":   False,
    },
    "SVR": {
        "name":        "Support Vector Regressor",
        "short":       "SVR",
        "file":        "svr_car_price_model.sav",
        "r2_score":    None,
        "mae":         None,
        "description": "Model SVR dengan kernel RBF yang efektif pada data berdimensi tinggi.",
        "feature_engineering": "Menggunakan Ordinal Encoding manual pada fitur utama terpilih dan pemetaan koordinat kernel RBF tanpa transformasi log pada target.",
        "available":   False,
    },
    "NN": {
        "name":        "Neural Network (MLP Regressor)",
        "short":       "NN",
        "file":        "used_car_model_nn.sav",
        "r2_score":    0.9100,
        "mae":         3850.20,
        "description": "Jaringan saraf tiruan multi-lapisan yang mampu menangkap pola non-linear kompleks.",
        "feature_engineering": "Menggunakan kombinasi fitur interaksi (usia-milage, daya-displacement), transformasi non-linear Yeo-Johnson (PowerTransformer), Dummy Encoding (One-Hot), dan standardisasi StandardScaler.",
        "available":   False,
    },
}

# ============================================================
# 1. Muat semua file pendukung & model ke RAM saat startup
# ============================================================
loaded_models = {}

try:
    # Memuat list array kategori dan nama fitur baru
    encoding_dicts  = joblib.load(os.path.join(BASE_DIR, "encoding_dictionary2.sav"))
    feature_columns = joblib.load(os.path.join(BASE_DIR, "car_features_list2.sav"))
    print("[OK] Kamus Encoding (v2) dan Daftar Fitur (v2) berhasil dimuat!")
except Exception as e:
    encoding_dicts  = []
    feature_columns = []
    print(f"[ERROR] Error memuat file pendukung: {e}")

for key, meta in MODEL_METADATA.items():
    path = os.path.join(MODELS_DIR, meta["file"])
    try:
        loaded_models[key] = joblib.load(path)
        MODEL_METADATA[key]["available"] = True
        print(f"[OK] Model {key} ({meta['name']}) -- dimuat dari models/{meta['file']}")
    except Exception as e:
        loaded_models[key] = None
        print(f"[WARN] Model {key} tidak ditemukan di models/{meta['file']}: {e}")

# ============================================================
# Pemuatan Scaler dan PowerTransformer untuk Model NN
# ============================================================
loaded_scalers = {}
pt_nn = None
pt_nn_stats = {
    "hp_median": 310.0,
    "engine_size_median": 3.5,
    "cylinders_mode": 6.0
}

# 1. Muat Scaler NN
# Cari di BASE_DIR (ai_backend/) terlebih dahulu, fallback ke MODELS_DIR (ai_backend/models/)
scaler_path_base  = os.path.join(BASE_DIR, "used_car_scaler_nn.sav")
scaler_path_model = os.path.join(MODELS_DIR, "used_car_scaler_nn.sav")
scaler_path = scaler_path_base if os.path.exists(scaler_path_base) else scaler_path_model
try:
    loaded_scalers["NN"] = joblib.load(scaler_path)
    print(f"[OK] Scaler NN berhasil dimuat dari: {scaler_path}")
except Exception as e:
    loaded_scalers["NN"] = None
    print(f"[WARN] Scaler NN tidak ditemukan atau gagal dimuat: {e}")

# 2. Muat atau Fit PowerTransformer NN
pt_path = os.path.join(MODELS_DIR, "used_car_pt_nn.sav")
if os.path.exists(pt_path):
    try:
        pt_data = joblib.load(pt_path)
        if isinstance(pt_data, dict):
            pt_nn = pt_data["pt"]
            pt_nn_stats["hp_median"] = pt_data.get("hp_median", 310.0)
            pt_nn_stats["engine_size_median"] = pt_data.get("engine_size_median", 3.5)
            pt_nn_stats["cylinders_mode"] = pt_data.get("cylinders_mode", 6.0)
        else:
            # Fallback jika hanya objek PowerTransformer saja yang disimpan
            pt_nn = pt_data
        print(f"[OK] PowerTransformer NN berhasil dimuat dari models/used_car_pt_nn.sav")
    except Exception as e:
        print(f"[WARN] Gagal memuat PowerTransformer dari file: {e}. Akan mencoba fitting ulang...")
        pt_nn = None

if pt_nn is None:
    csv_path = r"C:\Users\fahmi\Downloads\used_cars.csv"
    if os.path.exists(csv_path):
        try:
            print("[INFO] Melakukan fitting PowerTransformer secara dinamis dari used_cars.csv...")
            from sklearn.preprocessing import PowerTransformer
            
            # Load dataset
            df_temp = pd.read_csv(csv_path, sep=';')
            df_temp['milage'] = df_temp['milage'].astype(str).str.replace(' mi.', '', regex=False).str.replace(',', '', regex=False)
            df_temp['milage'] = pd.to_numeric(df_temp['milage'], errors='coerce')
            df_temp['price'] = df_temp['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df_temp['price'] = pd.to_numeric(df_temp['price'], errors='coerce')
            df_temp.dropna(subset=['model_year', 'milage', 'price', 'brand'], inplace=True)
            
            df_clean = df_temp[(df_temp['price'] >= 2000) & (df_temp['price'] <= 160000)]
            df_clean = df_clean[df_clean['milage'] <= 280000]
            df_clean['car_age'] = 2024 - df_clean['model_year']
            
            def parse_engine_temp(x):
                x = str(x)
                hp_m = re.search(r'(\d+\.?\d*)HP', x)
                lt_m = re.search(r'(\d+\.\d+)L', x)
                cy_m = re.search(r'(\d+)\s*Cylinder', x)
                return pd.Series([
                    float(hp_m.group(1)) if hp_m else np.nan,
                    float(lt_m.group(1)) if lt_m else np.nan,
                    float(cy_m.group(1)) if cy_m else np.nan
                ])
                
            df_clean[['hp', 'engine_size', 'cylinders']] = df_clean['engine'].apply(parse_engine_temp)
            
            hp_med = float(df_clean['hp'].median())
            es_med = float(df_clean['engine_size'].median())
            cy_mod = float(df_clean['cylinders'].mode()[0])
            
            pt_nn_stats["hp_median"] = hp_med if not np.isnan(hp_med) else 310.0
            pt_nn_stats["engine_size_median"] = es_med if not np.isnan(es_med) else 3.5
            pt_nn_stats["cylinders_mode"] = cy_mod if not np.isnan(cy_mod) else 6.0
            
            df_clean['hp'] = df_clean['hp'].fillna(pt_nn_stats["hp_median"])
            df_clean['engine_size'] = df_clean['engine_size'].fillna(pt_nn_stats["engine_size_median"])
            df_clean['cylinders'] = df_clean['cylinders'].fillna(pt_nn_stats["cylinders_mode"])
            
            df_clean['age_milage_inter'] = df_clean['car_age'] * df_clean['milage']
            df_clean['hp_engine_inter'] = df_clean['hp'] * df_clean['engine_size']
            
            pt_nn = PowerTransformer(method='yeo-johnson')
            pt_cols = ['milage', 'hp', 'engine_size', 'car_age', 'age_milage_inter', 'hp_engine_inter']
            pt_nn.fit(df_clean[pt_cols])
            
            # Simpan agar startup berikutnya cepat
            joblib.dump({
                "pt": pt_nn,
                "hp_median": pt_nn_stats["hp_median"],
                "engine_size_median": pt_nn_stats["engine_size_median"],
                "cylinders_mode": pt_nn_stats["cylinders_mode"]
            }, pt_path)
            print(f"[OK] PowerTransformer berhasil di-fit dan disimpan ke models/used_car_pt_nn.sav")
        except Exception as e:
            print(f"[ERROR] Gagal mem-fit PowerTransformer secara dinamis: {e}")
    else:
        print(f"[WARN] File dataset {csv_path} tidak ditemukan untuk fitting PowerTransformer.")


# ============================================================
# 2. Skema Input (Pydantic)
# ============================================================
class CarInput(BaseModel):
    brand:        str
    model:        str
    model_year:   int
    milage:       float
    fuel_type:    str
    engine:       str
    transmission: str
    ext_col:      str
    int_col:      str
    accident:     str
    clean_title:  str
    algorithm:    str = "DT"   # Pilihan: "DT" | "SVR" | "NN"


# ============================================================
# 3. Fungsi Helper Preprocessing & Feature Engineering
# ============================================================

def extract_engine_features(engine_str: str):
    """Ekstraksi fitur engine menggunakan regex matching."""
    engine_str = str(engine_str)
    
    # 1. Horsepower (HP)
    hp_match = re.search(r'(\d+(?:\.\d+)?)\s*HP', engine_str, re.IGNORECASE)
    hp = float(hp_match.group(1)) if hp_match else 250.0
    
    # 2. Displacement (Volume L / Liter)
    disp_match = re.search(r'(\d+(?:\.\d+)?)\s*L', engine_str, re.IGNORECASE)
    if not disp_match:
        disp_match = re.search(r'(\d+(?:\.\d+)?)\s*LITER', engine_str, re.IGNORECASE)
    disp = float(disp_match.group(1)) if disp_match else 3.0
    
    # 3. Cylinders
    cyl_match = re.search(r'(?i)\b(\d+)\s*(?:cyl|cylinder)', engine_str)
    if cyl_match:
        cylinders = float(cyl_match.group(1))
    else:
        v_match = re.search(r'(?i)\b[VI]\s*(\d+)\b', engine_str)
        cylinders = float(v_match.group(1)) if v_match else 6.0
        
    # 4. Booleans
    is_v = bool(re.search(r'V\d+', engine_str, re.IGNORECASE))
    is_turbo = 'turbo' in engine_str.lower()
    is_super = 'supercharged' in engine_str.lower()
    
    return hp, disp, cylinders, is_v, is_turbo, is_super


def ordinal_encode(col_name: str, value: str) -> float:
    """Ordinal encoding manual menggunakan index kategori di encoding_dictionary2.sav"""
    col_mapping = {
        "brand": 0,
        "model": 1,
        "fuel_type": 2,
        "engine": 3,
        "transmission": 4,
        "ext_col": 5,
        "int_col": 6,
        "accident": 7,
        "clean_title": 8,
        "is_v_engine": 9,
        "is_turbo": 10,
        "is_supercharged": 11
    }
    idx = col_mapping.get(col_name)
    if idx is None or not isinstance(encoding_dicts, list) or idx >= len(encoding_dicts):
        return 0.0
    
    arr = encoding_dicts[idx]
    val_str = str(value).strip()
    
    try:
        # Cari value di array numpy
        pos = np.where(arr == val_str)[0]
        if len(pos) > 0:
            return float(pos[0])
            
        # Coba case-insensitive jika tidak ketemu
        arr_lower = np.char.lower(arr.astype(str))
        pos_lower = np.where(arr_lower == val_str.lower())[0]
        if len(pos_lower) > 0:
            return float(pos_lower[0])
            
        # Handle Boolean jika array bertipe boolean
        if val_str.lower() in ['true', '1', 'yes', 'y']:
            pos_bool = np.where(arr == True)[0]
            if len(pos_bool) > 0: return float(pos_bool[0])
        elif val_str.lower() in ['false', '0', 'no', 'n']:
            pos_bool = np.where(arr == False)[0]
            if len(pos_bool) > 0: return float(pos_bool[0])
    except Exception:
        pass
    return 0.0


# ============================================================
# 4. Endpoint: Root / Health Check
# ============================================================
@app.get("/")
def root():
    return {
        "status":        "success",
        "message":       "Used Car Price Predictor API is online",
        "features":      feature_columns,
        "loaded_models": {k: v is not None for k, v in loaded_models.items()},
    }


# ============================================================
# 5. Endpoint: Daftar Model yang Tersedia
# ============================================================
@app.get("/models")
def get_models():
    result = []
    for key, meta in MODEL_METADATA.items():
        result.append({
            "key":         key,
            "name":        meta["name"],
            "short":       meta["short"],
            "r2_score":    meta["r2_score"],
            "mae":         meta["mae"],
            "description": meta["description"],
            "feature_engineering": meta.get("feature_engineering", ""),
            "available":   meta["available"],
        })
    return {"status": "success", "models": result}


# ============================================================
# 6. Endpoint: Prediksi Harga
# ============================================================
@app.post("/predict")
def predict_price(car: CarInput):
    algo = car.algorithm.upper()

    # Validasi pilihan algoritma
    if algo not in loaded_models:
        raise HTTPException(
            status_code=400,
            detail=f"Algoritma '{algo}' tidak dikenal. Pilih salah satu: {', '.join(MODEL_METADATA.keys())}."
        )

    selected_model = loaded_models[algo]
    if selected_model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{algo}' belum tersedia di server. Harap upload file model terlebih dahulu."
        )

    data = car.dict()

    # Ekstraksi Fitur Tambahan (Engine Features)
    hp, engine_displacement, cylinders, is_v_engine, is_turbo, is_supercharged = extract_engine_features(data["engine"])
    car_age = 2025 - data["model_year"]
    if car_age <= 0:
        car_age = 1
    miles_per_year = data["milage"] / car_age

    # =========================================================================
    # PROSES PREDIKSI ADAPTIF BERDASARKAN ALGORITMA MODEL
    # =========================================================================
    try:
        if algo == "DT":
            # Model DT Baru (used_car_model_dt.sav) adalah Pipeline.
            # Ia membutuhkan DataFrame berisi 19 fitur mentah (teks & angka).
            processed_data = {
                # Numerik
                "model_year":          int(data["model_year"]),
                "milage":              float(data["milage"]),
                "hp":                  float(hp),
                "engine_displacement": float(engine_displacement),
                "cylinders":           float(cylinders),
                "car_age":             float(car_age),
                "miles_per_year":      float(miles_per_year),
                # Kategorikal
                "brand":               str(data["brand"]),
                "model":               str(data["model"]),
                "fuel_type":           str(data["fuel_type"]),
                "engine":              str(data["engine"]),
                "transmission":        str(data["transmission"]),
                "ext_col":             str(data["ext_col"]),
                "int_col":             str(data["int_col"]),
                "accident":            str(data["accident"]),
                "clean_title":         str(data["clean_title"]),
                "is_v_engine":         bool(is_v_engine),
                "is_turbo":            bool(is_turbo),
                "is_supercharged":     bool(is_supercharged),
            }
            # Susun dataframe sesuai urutan kolom yang diharapkan
            cols_order = [
                'model_year', 'milage', 'hp', 'engine_displacement', 'cylinders', 'car_age', 'miles_per_year',
                'brand', 'model', 'fuel_type', 'engine', 'transmission', 'ext_col', 'int_col', 'accident',
                'clean_title', 'is_v_engine', 'is_turbo', 'is_supercharged'
            ]
            df_input = pd.DataFrame([processed_data])[cols_order]
            
            # Predict (Output skala Log)
            log_price = selected_model.predict(df_input)[0]
            real_price = np.expm1(log_price)

        elif algo == "SVR":
            # Model SVR Baru (svr_car_price_model.sav) membutuhkan 7 fitur ordinal-encoded.
            # Kolom: ['brand', 'model', 'model_year', 'milage', 'fuel_type', 'transmission', 'accident']
            processed_data = {
                "brand":        ordinal_encode("brand", data["brand"]),
                "model":        ordinal_encode("model", data["model"]),
                "model_year":   float(data["model_year"]),
                "milage":       float(data["milage"]),
                "fuel_type":    ordinal_encode("fuel_type", data["fuel_type"]),
                "transmission": ordinal_encode("transmission", data["transmission"]),
                "accident":     ordinal_encode("accident", data["accident"]),
            }
            cols_order = ['brand', 'model', 'model_year', 'milage', 'fuel_type', 'transmission', 'accident']
            df_input = pd.DataFrame([processed_data])[cols_order]
            
            # Predict (Output model SVR baru langsung skala harga asli USD, bukan log)
            real_price = selected_model.predict(df_input)[0]
            
        elif algo == "NN":
            # Model NN (used_car_model_nn.sav)
            # Membutuhkan preprocessing PowerTransformer, categorical dummy variables, dan StandardScaler.
            scaler_nn = loaded_scalers.get("NN")
            if scaler_nn is None or pt_nn is None:
                raise HTTPException(
                    status_code=503,
                    detail="Model NN belum siap digunakan karena scaler atau PowerTransformer belum berhasil dimuat."
                )
            
            # 1. Parse Engine dengan fallback statistik
            engine_str = str(data["engine"])
            hp_m = re.search(r'(\d+\.?\d*)HP', engine_str, re.IGNORECASE)
            lt_m = re.search(r'(\d+\.\d+)L', engine_str, re.IGNORECASE)
            cy_m = re.search(r'(\d+)\s*Cylinder', engine_str, re.IGNORECASE)
            
            hp_val = float(hp_m.group(1)) if hp_m else pt_nn_stats["hp_median"]
            engine_size_val = float(lt_m.group(1)) if lt_m else pt_nn_stats["engine_size_median"]
            cylinders_val = float(cy_m.group(1)) if cy_m else pt_nn_stats["cylinders_mode"]
            
            # 2. Fitur Tambahan & Interaksi
            car_age_val = max(1, 2024 - int(data["model_year"]))
            milage_val = float(data["milage"])
            
            age_milage_inter_val = car_age_val * milage_val
            hp_engine_inter_val = hp_val * engine_size_val
            
            # Boolean features
            is_automatic_val = 1 if re.search(r'Automatic|A/T|CVT', str(data["transmission"]), re.IGNORECASE) else 0
            accident_reported_val = 1 if re.search(r'accident|damage', str(data["accident"]), re.IGNORECASE) else 0
            clean_title_status_val = 1 if str(data["clean_title"]).strip().lower() == "yes" else 0
            
            # 3. Transformasi PowerTransformer
            pt_cols = ['milage', 'hp', 'engine_size', 'car_age', 'age_milage_inter', 'hp_engine_inter']
            df_pt_in = pd.DataFrame([{
                'milage': milage_val,
                'hp': hp_val,
                'engine_size': engine_size_val,
                'car_age': float(car_age_val),
                'age_milage_inter': age_milage_inter_val,
                'hp_engine_inter': hp_engine_inter_val
            }])[pt_cols]
            
            pt_transformed = pt_nn.transform(df_pt_in)[0]
            
            # 4. Bangun DataFrame 71 kolom dummy
            feature_cols = list(scaler_nn.feature_names_in_)
            scaled_input_dict = {col: 0.0 for col in feature_cols}
            
            # Isi kolom numerik hasil PT
            scaled_input_dict['milage_pt'] = pt_transformed[0]
            scaled_input_dict['hp_pt'] = pt_transformed[1]
            scaled_input_dict['engine_size_pt'] = pt_transformed[2]
            scaled_input_dict['age_pt'] = pt_transformed[3]
            scaled_input_dict['inter_1'] = pt_transformed[4]
            scaled_input_dict['inter_2'] = pt_transformed[5]
            
            # Isi kolom numerik non-PT
            scaled_input_dict['cylinders'] = float(cylinders_val)
            scaled_input_dict['is_automatic'] = float(is_automatic_val)
            scaled_input_dict['accident_reported'] = float(accident_reported_val)
            
            # Isi kolom kategori dummy (One-Hot)
            brand_col = f"brand_{data['brand']}"
            if brand_col in scaled_input_dict:
                scaled_input_dict[brand_col] = 1.0
                
            fuel_col = f"fuel_type_{data['fuel_type']}"
            if fuel_col in scaled_input_dict:
                scaled_input_dict[fuel_col] = 1.0
                
            if clean_title_status_val:
                scaled_input_dict['clean_title_status_Yes'] = 1.0
                
            # Susun dataframe sesuai urutan fitur scaler
            df_scaled_in = pd.DataFrame([scaled_input_dict])[feature_cols]
            
            # Lakukan scaling & prediksi
            X_scaled = scaler_nn.transform(df_scaled_in)
            log_price = selected_model.predict(X_scaled)[0]
            real_price = np.expm1(log_price)
            
        else:
            raise HTTPException(status_code=400, detail=f"Algoritma '{algo}' tidak didukung.")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memproses prediksi dengan model {algo}: {str(e)}"
        )

    return {
        "status":              "success",
        "algorithm_used":      algo,
        "algorithm_name":      MODEL_METADATA[algo]["name"],
        "input_data":          data,
        "predicted_price_usd": round(real_price, 2),
        "formatted_price":     f"${real_price:,.2f}",
    }