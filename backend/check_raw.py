import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd

path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_data.xlsx')
df = pd.read_excel(path, engine='openpyxl')
df.columns = df.columns.str.strip()

print("=== TÜM KOLONLAR ===")
print(list(df.columns))
print()

for kod in ["JN2708", "JN2709", "JM6535"]:
    rows = df[df["Stok Kodu"] == kod]
    print(f"=== {kod} ({len(rows)} satır) ===")
    for col in ["Alış Miktarı", "Alış Tutarı", "Alış Fiyatı", "Alış Fiyat",
                "Satış Miktarı", "Satış Tutarı", "DSS Miktar", "PSF"]:
        if col in df.columns:
            vals = rows[col].tolist()
            print(f"  {col}: {vals}")
    print()
