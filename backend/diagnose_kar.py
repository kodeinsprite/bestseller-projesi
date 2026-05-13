"""
Toplam Kar formül teşhisi — hangi formül doğru değerleri üretiyor?
Çalıştırma: python backend/diagnose_kar.py
"""
import pandas as pd, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "raw_data.xlsx"

def _to_num(s):
    if pd.api.types.is_numeric_dtype(s):
        return s
    text = s.astype(str).str.strip()
    text = text.str.replace(r"\s*(adet|pcs|ad\.|piece|units?)\s*", "", regex=True, flags=re.IGNORECASE)
    text = text.str.replace(r"[^\d,.\-]", "", regex=True)
    text = text.str.replace(r"\.(?=\d{3}(?:[,.]|$))", "", regex=True)
    text = text.str.replace(",", ".", regex=False)
    text = text.replace({"": pd.NA, "-": pd.NA, ".": pd.NA})
    return pd.to_numeric(text, errors="coerce")

df = pd.read_excel(DATA, engine="openpyxl")
df.columns = df.columns.str.strip()

print(f"SUTUNLAR: {list(df.columns)}")
print(f"TOPLAM SATIR: {len(df)}")
print(f"'Toplam Kar' sutunu var mi: {'Toplam Kar' in df.columns}")
print()

# Bestseller ilk 5 SKU
test_skus = ["JM6535", "IX3178", "JX8743", "JW8669", "JX1256"]

for sku in test_skus:
    rows = df[df["Stok Kodu"].astype(str).str.strip() == sku]
    print(f"=== {sku} ({len(rows)} satir) ===")
    if rows.empty:
        print("  BULUNAMADI\n")
        continue

    alis_m = _to_num(rows["Alis Miktari"] if "Alis Miktari" in df.columns else rows["Alış Miktarı"]).sum()
    alis_t = _to_num(rows["Alis Tutari"] if "Alis Tutari" in df.columns else rows["Alış Tutarı"]).sum()
    satis_m = _to_num(rows["Satis Miktari"] if "Satis Miktari" in df.columns else rows["Satış Miktarı"]).sum()
    satis_t = _to_num(rows["Satis Tutari"] if "Satis Tutari" in df.columns else rows["Satış Tutarı"]).sum()
    dss = _to_num(rows["DSS Miktar"]).sum()

    birim_alis = alis_t / alis_m if alis_m else None
    smm = birim_alis * satis_m if birim_alis else None

    print(f"  Alis Miktari (sum) = {alis_m}")
    print(f"  Alis Tutari (sum)  = {alis_t}")
    print(f"  Satis Miktari (sum)= {satis_m}")
    print(f"  Satis Tutari (sum) = {satis_t}")
    print(f"  DSS Miktar (sum)   = {dss}")
    print(f"  birim_alis         = {birim_alis}")
    print(f"  SMM (birim_alis*satis_m) = {smm}")
    print()
    print(f"  FORMUL A: Satis Tutari - Alis Tutari           = {satis_t - alis_t:.2f}")
    if smm:
        print(f"  FORMUL B: Satis Tutari - SMM                   = {satis_t - smm:.2f}")
    print(f"  FORMUL C: Satis Tutari/1.20 - Alis Tutari      = {satis_t/1.20 - alis_t:.2f}")
    if smm:
        print(f"  FORMUL D: Satis Tutari/1.20 - SMM              = {satis_t/1.20 - smm:.2f}")
    print(f"  FORMUL E: (Satis Tutari - Alis Tutari)/1.20    = {(satis_t - alis_t)/1.20:.2f}")
    print(f"  FORMUL F: Satis Tutari/1.10 - Alis Tutari      = {satis_t/1.10 - alis_t:.2f}")
    print(f"  FORMUL G: Satis Tutari/1.08 - Alis Tutari      = {satis_t/1.08 - alis_t:.2f}")

    if "Toplam Kar" in df.columns:
        tk = _to_num(rows["Toplam Kar"]).sum()
        print(f"  EXCEL Toplam Kar (sum) = {tk}")
    print()
