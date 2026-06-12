import joblib

try:
    encoding_dicts = joblib.load('encoding_dictionary.sav')
    feature_columns = joblib.load('car_features_list.sav')
    print("Features:", feature_columns)
    print("\nKeys in encoding dictionary:", list(encoding_dicts.keys()))
    
    # Cetak sampel dari beberapa kategori
    for key in ['brand', 'fuel_type', 'transmission', 'accident', 'clean_title']:
        if key in encoding_dicts:
            print(f"\nSample values for {key} (top 15):")
            # encoding_dicts[key] adalah dictionary yang memetakan string ke target encoding value
            items = list(encoding_dicts[key].keys())
            print(items[:15])
            print("Total unique values:", len(items))
            
except Exception as e:
    print("Error:", e)
