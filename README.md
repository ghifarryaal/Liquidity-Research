# 📈 LiquidityResearch — AI-Powered Indonesian Stock Analysis

> Platform analisis saham Indonesia (LQ45, KOMPAS100, DBX) berbasis Machine Learning — K-Means clustering 4D, trade plan otomatis, backtest engine dengan stop loss & trailing stop, dan AI Mentor berbasis Gemini. **Tanpa login. Gratis. Open source.**

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Now-brightgreen)](https://quant.indonesiastockanalyst.my.id)

**🔗 [Live Demo](https://quant.indonesiastockanalyst.my.id) · [API Docs](https://api-quant.indonesiastockanalyst.my.id/docs)**

---

## 🌟 Fitur Utama

### 🧠 Advanced K-Means Clustering (4D Feature Vector)
- **4 dimensi fitur**: Log Returns, Volatility (20-day), RSI Relative, Volume Impact
- **Automated labeling** dengan priority rules: `High Risk` → `Beli Saat Turun` → `Momentum` → `Konsolidasi`
- **Training window 90 hari** terpisah dari backtest window 180 hari
- **Winsorization** otomatis untuk outlier (Z-score > 3)
- **Backward-compatible**: semua field API lama tetap tersedia

### 📊 Enhanced Backtest Engine
- **Stop Loss** otomatis di 3% bawah entry
- **Trailing Stop** aktif setelah profit 5%, update di setiap high baru
- **Metrik lengkap**: Sharpe Ratio (annualized), Max Drawdown, Win Rate, Equity Curve
- **Visualisasi PNG**: price chart dengan cluster background + equity curve panel
- Simulasi modal awal Rp 100 juta

### 🤖 AI Mentor (Gemini Streaming)
- Chat real-time dengan konteks saham yang sedang dilihat
- Suggested questions per cluster label
- Streaming response dengan markdown rendering
- Rate limiting & session management

### 📈 Dashboard Real-Time (10+ Widget)
- **Macro Sentiment**: DXY, US10Y, Risk-On/Off regime
- **Panic Meter**: Fear/Greed index dari macro + market breadth
- **Market Breadth**: Advance/Decline ratio
- **Sector Momentum**: Performa rata-rata per sektor
- **World Indices & Commodities**: Live dari Yahoo Finance
- **XGBoost Validation**: Akurasi 30-hari supervised model
- **Signal Distribution Bar**: Distribusi BUY/HOLD/SELL real-time

### 💼 Trade Plan Otomatis
- Entry price, Stop Loss (ATR-based), Take Profit 1 & 2 (Fibonacci)
- Risk/Reward ratio kalkulasi otomatis
- Disesuaikan per cluster label dan kondisi makro

### 🔬 Property-Based Testing
- 14 properties via Hypothesis (max_examples=100)
- 57 unit + integration tests, semua passing
- Coverage: feature engineering, clustering, backtest engine, API endpoints

---

## 🏗️ Arsitektur

```
Browser (HTTPS)
    │
    ├── Cloudflare Pages → quant.indonesiastockanalyst.my.id  (Next.js 15)
    │
    └── Cloudflare DNS  → api-quant.indonesiastockanalyst.my.id
                              │
                         Hostinger VPS
                         Nginx (reverse proxy)
                              │
                         Docker: FastAPI (port 8001)
```

```
┌─────────────────────────────────────────────────────────┐
│                    ML Pipeline                          │
│                                                         │
│  yfinance OHLCV → Feature Engineering (4D) →           │
│  K-Means Clustering → Automated Labeling →             │
│  XGBoost Confidence → Trade Plan → Backtest            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ dan npm
- Python 3.12+

### Frontend

```bash
cd frontend
npm install
npm run dev
# Buka http://localhost:3000
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Buat file .env
echo "GEMINI_API_KEY=your_key_here" > .env
echo "ALLOWED_ORIGINS=http://localhost:3000" >> .env

uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### Docker

```bash
docker-compose up -d --build
```

---

## 📁 Struktur Project

```
├── frontend/
│   └── src/
│       ├── app/                    # Next.js App Router
│       ├── components/
│       │   ├── dashboard/          # MarketOverview, InsightFeed, BacktestScorecard, dll
│       │   ├── charts/             # CandlestickChart (lightweight-charts)
│       │   └── ui/                 # ChatWidget (AI Mentor)
│       ├── hooks/                  # useClusterData, useStockDetail (SWR)
│       ├── lib/                    # api.js, formatters.js
│       └── constants/              # clusterConfig.js (single source of truth)
│
├── backend/
│   └── app/
│       ├── routers/
│       │   └── cluster.py          # GET /cluster/{index}, POST /cluster/backtest
│       ├── services/
│       │   ├── clustering_engine.py    # K-Means + automated labeling
│       │   ├── feature_engineering.py  # 4D feature vector
│       │   ├── backtest_engine.py      # TradingSimulator + run_enhanced_backtest
│       │   ├── visualization.py        # Matplotlib backtest charts
│       │   ├── supervised_model.py     # XGBoost confidence scoring
│       │   ├── trade_plan_engine.py    # ATR + Fibonacci trade plan
│       │   ├── macro_weighting.py      # DXY, US10Y, world indices
│       │   └── ai_assistant.py         # Gemini integration
│       └── models/schemas.py           # Pydantic models
│
└── backend/tests/
    ├── test_services.py            # Unit tests
    ├── test_api.py                 # Integration tests
    └── property/                   # Hypothesis property-based tests
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS 4, Framer Motion |
| Charts | Lightweight Charts v5, Matplotlib (backtest PNG) |
| Data Fetching | SWR (stale-while-revalidate) |
| Backend | FastAPI, Uvicorn |
| ML | Scikit-learn (K-Means, RobustScaler), XGBoost, ta |
| Data | yfinance, Pandas, NumPy |
| AI | Google Gemini (gemini-flash-latest) |
| Testing | pytest, Hypothesis, pytest-asyncio |
| Infrastructure | Docker, Nginx, Cloudflare Pages, Hostinger VPS |

---

## 🎯 API Endpoints

```http
GET  /api/cluster/{lq45|kompas100|dbx}?period_days=180
GET  /api/stock/{ticker}?period_days=180
GET  /api/macro
GET  /api/cluster/training-window-info
POST /api/cluster/backtest
GET  /api/chat  (SSE streaming)
GET  /docs      (Swagger UI)
```

---

## 🧪 Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
# 57 tests, semua passing dalam ~23 detik
```

---

## 🌐 Live Demo

- **App**: https://quant.indonesiastockanalyst.my.id
- **API Docs**: https://api-quant.indonesiastockanalyst.my.id/docs

---

## 👨‍💻 Author

**Ghifar Ryal** · [@ghifarryaal](https://github.com/ghifarryaal)

---

**⚠️ Disclaimer**: Platform ini hanya untuk tujuan edukasi. Bukan saran investasi. Selalu lakukan riset mandiri sebelum berinvestasi.
