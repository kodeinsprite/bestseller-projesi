#!/usr/bin/env python3
"""
Özet Excel / ham veri sıralamasının backend ile uyumunu kontrol eder.

Kullanım (proje kökünden veya backend klasöründen):
  python validate_ranking.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_XLSX = ROOT / "data" / "raw_data.xlsx"


def main() -> None:
    if not DATA_XLSX.is_file():
        print(f"[atlandı] {DATA_XLSX} bulunamadı.")
        return

    df = pd.read_excel(DATA_XLSX, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Özet dosya: Excel'deki doğrudan sıra ile backend'in Satış Miktarı sırasını karşılaştır
    if {"Toplam Satış Miktarı", "Stok Kodu"}.issubset(df.columns):
        excel_top10 = (
            df.sort_values("Toplam Satış Miktarı", ascending=False, kind="mergesort")
            .head(10)["Stok Kodu"]
            .astype(str)
            .tolist()
        )

        import main as m

        dfn = m._normalize_columns(df)
        metrics = m._process_summary_export(dfn)
        backend_top10 = (
            metrics.sort_values("Satış Miktarı", ascending=False, kind="mergesort")
            .head(10)["Stok Kodu"]
            .astype(str)
            .tolist()
        )

        print("Excel (Toplam Satış Miktarı DESC) ilk 10 Stok Kodu:")
        print(excel_top10)
        print("Backend (aynı qty ile sıralı) ilk 10 Stok Kodu:")
        print(backend_top10)
        print("Bestseller sıra eşleşmesi:", excel_top10 == backend_top10)

        # Örnek: ilk satırda Toplam Kar dosya vs kural
        if {"Toplam Kar", "Toplam SMM", "Toplam Initial Ciro"}.issubset(df.columns):
            r0 = df.iloc[0]
            qty = float(pd.to_numeric(r0["Toplam Satış Miktarı"], errors="coerce") or 0)
            alis = float(pd.to_numeric(r0["Alış Fiyat"], errors="coerce") or 0)
            psf = float(pd.to_numeric(r0["PSF"], errors="coerce") or 0)
            smm_kural = qty * alis
            init_kural = qty * psf
            kar_kural = init_kural - smm_kural
            print(
                "\nİlk satır kontrol (örnek): Initial_Ciro − SMM = Toplam Kar (kural)",
                f"\n  kural kar={kar_kural:.2f} | dosya Toplam Kar={float(pd.to_numeric(r0['Toplam Kar'], errors='coerce') or 0):.2f}",
            )
    else:
        print("Özet sütunları yok; ham CSV şeması için manuel doğrulama gerekir.")


if __name__ == "__main__":
    main()
