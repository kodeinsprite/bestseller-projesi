"""
Veri teşhis scripti — birim_alis_fiyati neden bazı ürünlerde patlıyor?
Çalıştırma: python backend/diagnose.py
"""
import sys, pandas as pd, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "raw_data.xlsx"

def _to_num(s):
    text = s.astype(str).str.strip()
    text = text.str.replace(r"\s*(adet|pcs|ad\.|piece|units?)\s*", "", regex=True, flags=re.IGNORECASE)
    text = text.str.replace(r"[^\d,.\-]", "", regex=True)
    text = text.str.replace(r"\.(?=\d{3}(?:[,.]|$))", "", regex=True)
    text = text.str.replace(",", ".", regex=False)
    text = text.replace({"": pd.NA, "-": pd.NA, ".": pd.NA})
    return pd.to_numeric(text, errors="coerce")

df = pd.read_excel(DATA, engine="openpyxl")
df.columns = df.columns.str.strip()

print(f"TOPLAM SATIR: {len(df)}")
print(f"BENZERSİZ STOK KODU: {df['Stok Kodu'].nunique()}")
print(f"SÜTUNLAR: {list(df.columns)}\n")

# Ham veri örneği: Vans + Adidas karşılaştır
test_skus = ["VN000H4YBRD1", "VN000H4XBA51", "VN000H4YBLK1", "IP9878", "IT5360"]
cols = ["Stok Kodu", "Stok Kodu Açıklama", "Alış Miktarı", "Alış Tutarı",
        "Satış Miktarı", "Satış Tutarı", "DSS Miktar"]

for sku in test_skus:
    rows = df[df["Stok Kodu"].astype(str).str.strip() == sku]
    print(f"=== {sku} ({len(rows)} satır) ===")
    if rows.empty:
        print("  BULUNAMADI\n")
        continue
    for _, r in rows.iterrows():
        for c in cols:
            if c in df.columns:
                raw = r[c]
                parsed = _to_num(pd.Series([raw])).iloc[0]
                print(f"  {c}: RAW={repr(raw)} → PARSED={parsed}")
    # Birim alış hesabı
    alis_m = _to_num(rows["Alış Miktarı"])
    alis_t = _to_num(rows["Alış Tutarı"])
    satis_m = _to_num(rows["Satış Miktarı"])
    satis_t = _to_num(rows["Satış Tutarı"])
    dss = _to_num(rows["DSS Miktar"])
    total_alis_qty = alis_m.sum()
    total_alis_tutar = alis_t.sum()
    total_satis_qty = satis_m.sum()
    total_ciro = satis_t.sum()
    total_dss = dss.sum()
    birim_alis = total_alis_tutar / total_alis_qty if total_alis_qty != 0 else None
    smm = birim_alis * total_satis_qty if birim_alis else None
    mu = total_ciro / smm if smm and smm != 0 else None
    st = total_satis_qty / (total_satis_qty + total_dss) * 100 if (total_satis_qty + total_dss) != 0 else 0
    toplam_kar = (total_ciro / 1.20 - smm) if smm else None
    print(f"  --- HESAPLANAN ---")
    print(f"  sum(Alış Miktarı)={total_alis_qty}, sum(Alış Tutarı)={total_alis_tutar}")
    print(f"  birim_alis={birim_alis}")
    print(f"  SMM={smm}, MU={mu}, ST={st:.1f}%")
    print(f"  toplam_kar={toplam_kar}")
    print()

# Satış Oranı vs hesaplanan Sell Through karşılaştırması
if "Satış Oranı" in df.columns:
    print("=== SATIŞ ORANI vs HESAPLANAN SELL THROUGH ===")
    sample = df[df["Stok Kodu"].astype(str).str.strip().isin(test_skus)].head(5)
    for _, r in sample.iterrows():
        sku = str(r["Stok Kodu"]).strip()
        raw_oran = r["Satış Oranı"]
        sq = _to_num(pd.Series([r["Satış Miktarı"]])).iloc[0] or 0
        ds = _to_num(pd.Series([r["DSS Miktar"]])).iloc[0] or 0
        computed = sq / (sq + ds) * 100 if (sq + ds) else 0
        print(f"  {sku}: Excel Satış Oranı={repr(raw_oran)}, Hesaplanan ST={computed:.2f}%")
