"""
Ham datadan Worstseller sıralamasını analiz et.
MA5672-UFC neden Excel listesinde YOK, VN000H4WEMJ1 neden VAR?
"""
import pandas as pd

PATH = "/Users/mustafabotan/Desktop/Bestseller_Projesi/data/raw_data.xlsx"
REPORT = "/Users/mustafabotan/Desktop/Bestseller_Projesi/backend/worst_analysis_report.txt"

lines = []


def write(text=""):
    lines.append(str(text))

df = pd.read_excel(PATH, engine="openpyxl")
df.columns = df.columns.str.strip()

write("=== TÜM KOLONLAR ===")
for c in df.columns:
    write(f"  {c}")

# Aggregate: stok kodu bazında
num_cols = ["Satış Miktarı", "Satış Tutarı", "DSS Miktar", "Alış Miktarı", "Alış Tutarı", "Ortalama Stok"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ".").str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0)

agg_dict = {c: "sum" for c in num_cols if c in df.columns}
first_cols = [c for c in df.columns if c not in num_cols and c != "Stok Kodu"]
for c in first_cols:
    agg_dict[c] = "first"

grp = df.groupby("Stok Kodu", as_index=False).agg(agg_dict)

# KPI hesapla
qty = grp["Satış Miktarı"].fillna(0)
dss = grp["DSS Miktar"].fillna(0)
grp["sell_through_pct"] = qty / (qty + dss).replace(0, float("nan")) * 100
grp["cover"] = dss / qty.replace(0, float("nan")) * 19
grp.loc[qty == 0, "cover"] = 1000

# Worstseller havuzu: DSS > 0
pool = grp[grp["DSS Miktar"] > 0].copy()

# E-TİCARET RENK kontrolü
if "E-TİCARET RENK" in pool.columns:
    renk = pool["E-TİCARET RENK"].fillna("").astype(str).str.strip()
    pool_with_renk = pool[renk != ""]
    pool_without_renk = pool[renk == ""]
    write(f"\n=== RENK FİLTRESİ ===")
    write(f"E-TİCARET RENK dolu: {len(pool_with_renk)}")
    write(f"E-TİCARET RENK boş:  {len(pool_without_renk)}")
    write("\nRENK BOŞ OLAN ilk 10 (bunlar havuzdan çıkar):")
    write(pool_without_renk[["Stok Kodu", "Satış Miktarı", "DSS Miktar", "sell_through_pct", "cover"]].head(10).to_string())

TARGET = ["MA5672-UFC", "MA5672-023", "VN000H4WEMJ1", "NF0A3VXF0IT1", "EK0003721091", "JX9076", "9118109"]

write("\n=== HEDEF ÜRÜN METRİKLERİ ===")
cols = ["Stok Kodu", "DSS Miktar", "Satış Miktarı", "sell_through_pct", "cover"]
if "E-TİCARET RENK" in grp.columns:
    cols.append("E-TİCARET RENK")
if "Mevcut Sezon Kodu" in grp.columns:
    cols.append("Mevcut Sezon Kodu")
if "E-TİCARET CİNSİYET" in grp.columns:
    cols.append("E-TİCARET CİNSİYET")
sub = grp[grp["Stok Kodu"].isin(TARGET)][cols]
write(sub.to_string())

# Tam worstseller sıralaması — tüm olası kombinasyonlar dene
write("\n=== SIRALAMA DENEMELERİ ===")

# 1. Sadece ST ASC
ws1 = pool.sort_values("sell_through_pct", ascending=True).head(15)
write("\n[1] Sadece ST ASC:")
write(ws1[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

# 2. ST ASC + Cover DESC
ws2 = pool.sort_values(["sell_through_pct", "cover"], ascending=[True, False]).head(15)
write("\n[2] ST ASC + Cover DESC:")
write(ws2[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

# 3. ST ASC + DSS DESC
ws3 = pool.sort_values(["sell_through_pct", "DSS Miktar"], ascending=[True, False]).head(15)
write("\n[3] ST ASC + DSS DESC:")
write(ws3[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

# 4. ST ASC + Cover DESC + DSS DESC
ws4 = pool.sort_values(["sell_through_pct", "cover", "DSS Miktar"], ascending=[True, False, False]).head(15)
write("\n[4] ST ASC + Cover DESC + DSS DESC:")
write(ws4[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

# 5. Cover DESC (tek başına)
ws5 = pool.sort_values("cover", ascending=False).head(15)
write("\n[5] Sadece Cover DESC:")
write(ws5[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

# 6. E-TİCARET RENK filtresi ile ST ASC
if "E-TİCARET RENK" in pool.columns:
    filtered_pool = pool[pool["E-TİCARET RENK"].fillna("").astype(str).str.strip() != ""]
    ws6 = filtered_pool.sort_values(["sell_through_pct", "DSS Miktar"], ascending=[True, False]).head(15)
    write("\n[6] RENK dolu + ST ASC + DSS DESC:")
    write(ws6[["Stok Kodu", "sell_through_pct", "cover", "DSS Miktar"]].to_string())

write("\n=== BİTTİ ===")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
