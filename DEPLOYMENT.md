# Deployment Guide

## Arsitektur

```
Browser (HTTPS)
    │
    ├── Cloudflare Pages → quant.indonesiastockanalyst.my.id  (Frontend)
    │
    └── Cloudflare DNS  → api-quant.indonesiastockanalyst.my.id (Backend API)
                              │
                         Hostinger VPS
                         nginx (port 80/443)
                              │
                         Docker: FastAPI (port 8001)
```

## Root Cause: Mixed Content Error

Cloudflare Pages selalu serve via **HTTPS**. Jika frontend memanggil backend via
`http://IP:8001`, browser akan **memblokir** request tersebut karena Mixed Content.

**Solusi:** Backend harus bisa diakses via HTTPS menggunakan domain.

---

## Setup VPS (Hostinger) — Pilih salah satu cara:

### Cara 1: Cloudflare Proxy (PALING MUDAH, Recommended)

1. Di Cloudflare DNS, tambahkan A record:
   - Name: `api-quant`
   - Content: `72.60.74.199` (IP VPS kamu)
   - Proxy: **ON** (orange cloud ☁️)

2. Di Cloudflare SSL/TLS settings → set ke **"Full"**

3. Di VPS, install nginx:
   ```bash
   apt-get install -y nginx
   cp nginx-cloudflare.conf /etc/nginx/sites-available/api-quant
   ln -s /etc/nginx/sites-available/api-quant /etc/nginx/sites-enabled/
   rm -f /etc/nginx/sites-enabled/default
   nginx -t && systemctl reload nginx
   ```

4. Jalankan backend:
   ```bash
   docker compose up -d --build
   ```

5. Test:
   ```bash
   curl https://api-quant.indonesiastockanalyst.my.id/health
   ```

### Cara 2: Let's Encrypt SSL (tanpa Cloudflare proxy)

```bash
chmod +x setup-ssl.sh
./setup-ssl.sh
```

---

## Environment Variables

### Backend (`backend/.env` atau docker-compose environment):
```
GEMINI_API_KEY=your_key_here
ALLOWED_ORIGINS=https://quant.indonesiastockanalyst.my.id
```

### Frontend (Cloudflare Pages → Settings → Environment Variables):
```
NEXT_PUBLIC_API_URL=https://api-quant.indonesiastockanalyst.my.id
```

> ⚠️ Pastikan variable ini di-set di **Cloudflare Pages dashboard** untuk production build,
> bukan hanya di file `.env.production` lokal.

---

## Cloudflare Pages — Set Environment Variable

1. Buka Cloudflare Pages dashboard
2. Pilih project kamu
3. Settings → Environment Variables
4. Add variable:
   - Variable name: `NEXT_PUBLIC_API_URL`
   - Value: `https://api-quant.indonesiastockanalyst.my.id`
   - Environment: **Production**
5. Trigger redeploy

---

## Checklist Debug

- [ ] `curl https://api-quant.indonesiastockanalyst.my.id/health` → `{"status":"healthy"}`
- [ ] `curl https://api-quant.indonesiastockanalyst.my.id/api/stock/BBCA.JK` → JSON response
- [ ] Browser console tidak ada CORS error
- [ ] Browser console tidak ada Mixed Content error
- [ ] `NEXT_PUBLIC_API_URL` di Cloudflare Pages sudah di-set ke HTTPS domain
