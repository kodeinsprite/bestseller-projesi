"""Debug: JM6535 için ham veri → KPI zincirini adım adım yaz."""
import sys
sys.path.insert(0, ".")
import pandas as pd
from main import (
    _normalize_columns, _clean_numeric_values, _aggregate_transactional,
    _apply_kpi_rules, _txt_clean, _to_numeric_series,
    GROUP_COLS, EXPECTED_COLUMNS,
)

path = "../data/raw_data.xlsx"
df = pd.read_excel(path, engine="openpyxl")
df = _normalize_columns(df)

print("=== RAW COLUMNS ===")
print(list(df.columns))
print()

# JM6535 rows
jm = df[df["Stok Kodu"] == "JM6535"]
print(f"=== JM6535 raw rows: {len(jm)} ===")
for col in jm.columns:
    print(f"  {col}: {jm[col].tolist()}")
print()

# Now trace through _load_and_process
num_cols = [
    "Alış Miktarı", "Alış Tutarı", "Satış Miktarı", "Satış Tutarı",
    "DSS Miktar", "Ortalama Stok", "Alış Fiyatı", "Alış Fiyat",
    "PSF", "Ciro", "Toplam Kar", "Toplam SMM", "Toplam Initial Ciro",
]
df2 = _clean_numeric_values(df.copy(), num_cols)

# Check JM6535 after cleaning
jm2 = df2[df2["Stok Kodu"] == "JM6535"]
print("=== JM6535 after clean_numeric ===")
for col in ["Alış Miktarı", "Alış Tutarı", "Satış Miktarı", "Satış Tutarı", "DSS Miktar", "Alış Fiyatı", "Alış Fiyat", "PSF"]:
    if col in jm2.columns:
        print(f"  {col}: {jm2[col].tolist()}")
print()

# Aggregate
for col in GROUP_COLS:
    if col in df2.columns:
        df2[col] = df2[col].map(_txt_clean)

for c in num_cols:
    if c in df2.columns:
        df2[c] = df2[c].fillna(0)

agg = _aggregate_transactional(df2)
jm_agg = agg[agg["Stok Kodu"] == "JM6535"]
print("=== JM6535 after aggregate ===")
print(jm_agg.to_dict(orient="records"))
print()

# KPI
kpi = _apply_kpi_rules(agg)
jm_kpi = kpi[kpi["Stok Kodu"] == "JM6535"]
print("=== JM6535 after KPI ===")
cols = ["Stok Kodu", "Satış Miktarı", "Satış Tutarı", "DSS Miktar", "birim_alis_fiyati", "psf", "smm", "initial_ciro", "brut_kar", "mu", "sell_through_pct"]
for c in cols:
    if c in jm_kpi.columns:
        print(f"  {c}: {jm_kpi[c].values[0]}")
