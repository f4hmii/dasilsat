import joblib
import json
import os

try:
    encoding_dicts = joblib.load('encoding_dictionary.sav')
    
    options = {}
    for key in encoding_dicts.keys():
        if key == 'global_mean':
            continue
        # Ambil semua kunci unik, urutkan secara alfabetis
        unique_vals = sorted(list(encoding_dicts[key].keys()))
        options[key] = unique_vals
        
    # Tentukan path output
    output_dir = os.path.join('..', 'php_frontend', 'assets', 'js')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'car_options.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(options, f, indent=4)
        
    print(f"Berhasil mengekspor opsi ke {output_path}")
    print("Jumlah Brand:", len(options.get('brand', [])))
    print("Jumlah Model:", len(options.get('model', [])))
    print("Jumlah Engine:", len(options.get('engine', [])))
    print("Jumlah Transmisi:", len(options.get('transmission', [])))
    print("Jumlah Ext Color:", len(options.get('ext_col', [])))
    print("Jumlah Int Color:", len(options.get('int_col', [])))
except Exception as e:
    print("Error:", e)
