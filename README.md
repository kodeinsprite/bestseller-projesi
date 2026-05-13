# Bestseller & Worstseller Perakende Analiz Dashboard

Yerel ortamda çalışan uçtan uca perakende analiz paneli: **`data/raw_data.csv`** veya **`data/raw_data.xlsx`** FastAPI + Pandas ile işlenir, Vue 3 + Tailwind arayüzünde sunulur.

## Klasör yapısı

```
/data              → raw_data.csv veya raw_data.xlsx buraya konur
/backend           → FastAPI (main.py, requirements.txt)
/frontend          → Vue 3 + Vite + Tailwind
```

## Veri dosyası

**`data/raw_data.csv`** veya **`data/raw_data.xlsx`** (Excel’de ilk sayfa) kullanın. İkisi birden varsa **CSV önceliklidir**. Sütun adları şemanızla **birebir** aynı olmalıdır. `.xlsx` için `openpyxl` gerekir (`requirements.txt` ile kurulur).

“PROJE Bestseller & Worstseller Data” gibi **özet Excel** dosyalarında `Toplam Satış Miktarı`, `Toplam DSS Miktar`, `Ciro`, `Alış Fiyat`, `PSF` sütunları varsa dosya özet modda okunur; **Toplam Kar, SMM, MU, Sell Through** değerleri dosyadan körü körüne alınmaz — backend aşağıdaki iş kurallarıyla yeniden hesaplar.

## İş kuralları (Master Prompt ile uyumlu)

**Ham CSV / çoklu satır:** Grup bazında `Satış Miktarı`, `Satış Tutarı`, `DSS Miktar` **toplamı**; birim **Alış Fiyatı** ve **PSF** için satır öncesi birim değerlerinin **ortalaması** (veya hamda `Alış Fiyatı` / `PSF` sütunu varsa doğrudan mean).

**KPI’lar (her stok satırı):**

- Toplam SMM = birim alış × Toplam Satış Miktarı  
- Initial Ciro = PSF × Toplam Satış Miktarı  
- İndirim Oranı = 1 − (Ciro / Initial Ciro)  
- **Toplam Kar = Initial Ciro − Toplam SMM** (gerçekleşen cirodan düşülmez)  
- MU = Ciro / Toplam SMM  
- Sell Through % = Satış / (Satış + DSS) × 100  

**Sıralama:** Filtre sonrası liste **Toplam Satış Miktarına göre azalan**; Bestseller = ilk 10. Worstseller = **DSS > 0**, satış miktarına göre **artan**, ilk 10.

### Excel sırasını doğrulama

`data/raw_data.xlsx` varken:

```bash
cd backend
source .venv/bin/activate
python validate_ranking.py
```

Özet Excel’deki “Toplam Satış Miktarı DESC” ilk 10 stok kodu ile backend çıktısını karşılaştırır.

## Backend (Python)

Python 3.10+ önerilir.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# .venv klasörünü hariç tutun; aksi halde --reload site-packages değişikliklerinde sürekli yeniden başlar.
uvicorn main:app --reload --host 127.0.0.1 --port 8000 --reload-dir . --reload-exclude ".venv"
```

Excel kullanıyorsanız dosyayı doğrudan **`…/data/raw_data.xlsx`** olarak kaydedebilirsiniz.

### API

- `GET http://127.0.0.1:8000/api/dashboard` — bestseller / worstseller listeleri  
- İsteğe bağlı sorgu parametreleri: `?cinsiyet=...&anagrup=...`

## Frontend (Node.js)

```bash
cd frontend
npm install
npm run dev
```

Varsayılan adres: **http://localhost:5173**

Geliştirme modunda `/api` istekleri Vite proxy ile `http://127.0.0.1:8000` adresine yönlendirilir; önce backend’in çalışıyor olması gerekir.

Üretim önizlemesi:

```bash
cd frontend
npm run build
npm run preview
```

## Hesaplanan metrikler (özet)

Ham veri: grup bazında toplamlar ve birim fiyatların ortalaması; ardından yukarıdaki KPI formülleri. Özet Excel: aynı formüller `Toplam Satış / DSS / Ciro / Alış Fiyat / PSF` üzerinden uygulanır. İsteğe bağlı `Periyot Cover (19 hafta)` sütunu varsa raporda GMROI gösterimi için kullanılabilir.

## Sorun giderme

- **404 / dosya yok:** `data/raw_data.csv` veya `data/raw_data.xlsx` dosyasının varlığını kontrol edin.
- **Eksik sütun:** CSV başlıklarında fazladan boşluk olmamasına dikkat edin; gerekirse UTF-8 ile yeniden kaydedin.
- **`WatchFiles detected changes in '.venv/...'` döngüsü:** Sunucuyu yukarıdaki gibi `--reload-exclude ".venv"` ile başlatın (`.venv` klasörü `backend` içindeyken `--reload` tüm site-packages’ı izleyebilir).

## Deploy Hazırlığı

Proje canlıya alınırken şu adımları takip edin:

- `DEPLOY.md` dosyasındaki adımları uygulayın.
- `frontend/.env.example` dosyasını kendi backend URL'inize göre kullanın.
- `backend/data/raw_data.csv` veya `backend/data/raw_data.xlsx` dosyasının repoda olduğundan emin olun.
# bestseller-projesi
