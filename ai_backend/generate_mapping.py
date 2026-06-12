import pandas as pd
import json
import os

# Path ke dataset
csv_path = r"C:\Users\fahmi\Downloads\used_cars.csv"

if not os.path.exists(csv_path):
    print(f"Error: Dataset tidak ditemukan di {csv_path}")
    # Fallback ke pencarian alternatif
    alt_paths = [
        r"C:\Users\fahmi\Downloads\archive (11)\used_cars.csv",
        "used_cars.csv"
    ]
    for path in alt_paths:
        if os.path.exists(path):
            csv_path = path
            print(f"Menggunakan dataset alternatif di: {csv_path}")
            break

try:
    df = pd.read_csv(csv_path, sep=';')
    print("Kolom yang ada di dataset:", df.columns.tolist())

    
    # Bersihkan spasi kosong pada kolom string
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    mappings = {}
    
    # Kelompokkan berdasarkan brand
    grouped = df.groupby('brand')
    
    for brand, group in grouped:
        # Filter nilai unik, hilangkan nan/null/string kosong
        models = sorted(list(group['model'].unique()))
        
        fuel_types = sorted(list(group['fuel_type'].dropna().unique()))
        fuel_types = [f for f in fuel_types if f not in ['nan', 'None', '']]
        
        transmissions = sorted(list(group['transmission'].dropna().unique()))
        transmissions = [t for t in transmissions if t not in ['nan', 'None', '']]
        
        engines = sorted(list(group['engine'].dropna().unique()))
        engines = [e for e in engines if e not in ['nan', 'None', '']]
        
        years = sorted(list(group['model_year'].dropna().unique()))
        # Konversi ke int standard
        years = [int(y) for y in years]
        
        mappings[brand] = {
            "models": models,
            "fuel_types": fuel_types,
            "transmissions": transmissions,
            "engines": engines,
            "years": years
        }
        
    # Tulis ke file JSON
    output_dir = os.path.join('..', 'php_frontend', 'assets', 'js')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'car_mappings.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=4)
        
    print(f"Berhasil membuat pemetaan dan menyimpannya di {output_path}")
    print(f"Total Brand yang terpetakan: {len(mappings)}")
    
except Exception as e:
    print("Terjadi kesalahan saat membuat pemetaan:", e)
