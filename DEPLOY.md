# Deploy Rehberi

Bu proje iki parçadan oluşuyor:

- `backend`: FastAPI Python API
- `frontend`: Vue 3 + Vite UI

## 1) Projeyi GitHub'a yükleme

1. GitHub hesabı açın.
2. Yeni bir repository oluşturun.
3. Proje kökünde terminal açın:

```bash
git init
git add .
git commit -m "deploy ready"
git branch -M main
git remote add origin https://github.com/<kullanici>/<repo>.git
git push -u origin main
```

> Eğer `data/raw_data.csv` veya `data/raw_data.xlsx` projenin içinde değilse, Firebase vs. ile değil, öncelikle bu dosyanın repoda olduğunu doğrulayın.

## 2) Backend deploy (Render önerisi)

1. `https://render.com` adresine kaydolun.
2. `New` → `Web Service` seçin.
3. GitHub hesabınızı bağlayın.
4. repo ve `main` branch seçin.
5. Root Directory olarak `backend` seçin.
6. Build Command olarak:

```bash
pip install -r requirements.txt
```

7. Start Command olarak:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

8. Deploy başlatın.
9. Deploy sonrası size verilen backend URL'ini kopyalayın.

## 3) Frontend deploy

### Seçenek A: Render Static Site

1. Render'da `New` → `Static Site` seçin.
2. Aynı repo'yu seçin.
3. Root Directory `frontend` seçin.
4. Build Command olarak:

```bash
npm install && npm run build
```

5. Publish Directory olarak:

```bash
dist
```

6. Environment Variables kısmına aşağıyı ekleyin:

```bash
VITE_API_BASE=https://<backend-url>
```

7. Deploy edin.

### Seçenek B: Vercel

1. `https://vercel.com` adresine kaydolun.
2. `New Project` → GitHub repo seçin.
3. Framework olarak `Vite`/`Vue` seçin.
4. Root Directory `frontend` olarak belirleyin.
5. Build Command:

```bash
npm install && npm run build
```

6. Output Directory:

```bash
dist
```

7. Environment Variable ekleyin:

```bash
VITE_API_BASE=https://<backend-url>
```

8. Deploy edin.

## 4) Yerelde test etme

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Access

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

## 5) Canlıda yapmanız gerekenler

1. GitHub repo açmak ve kodu push etmek.
2. Render veya Vercel hesabı açarak backend ve frontend deploy etmek.
3. Frontend deploy ayarına `VITE_API_BASE` olarak canlı backend URL'ini girmek.

## 6) Önemli notlar

- Backend `data/raw_data.csv` veya `data/raw_data.xlsx` dosyasını `../data/` dizininde bekler.
- `frontend/.env.example` dosyası sadece örnektir; canlıya alırken kendi backend URL'inizi burada veya deploy servisi üzerindeki environment değişkeni olarak ayarlayın.
