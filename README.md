# 📈 LiquidityResearch - AI-Powered Indonesian Stock Analysis Platform

> Intelligent stock analysis platform for Indonesian market (LQ45 & KOMPAS100) powered by Machine Learning clustering, technical indicators, and automated backtesting.

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Features

### 🤖 AI-Powered Analysis
- **Machine Learning Clustering**: Automatically groups stocks into actionable strategies (Buy the Dip, Momentum, Breakout, etc.)
- **Supervised Learning**: Confidence scoring for each recommendation
- **Macro Sentiment Weighting**: Adjusts strategies based on market conditions

### 📊 Technical Analysis
- **20+ Technical Indicators**: RSI, MACD, Bollinger Bands, EMA, ATR, Volume Ratio
- **Interactive Charts**: Real-time candlestick charts with technical overlays
- **Historical Data**: 180-day analysis window

### 💼 Trading Intelligence
- **Automated Trade Plans**: Entry, stop-loss, and take-profit levels
- **Backtesting Engine**: Historical performance validation
- **Risk Management**: Position sizing and risk/reward calculations

### 🎓 Educational Features
- **AI Reasoning**: Transparent explanations for each recommendation
- **Strategy Insights**: Learn why stocks are categorized in specific clusters
- **No Login Required**: Accessible to all Indonesian retail investors

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │ ◄─────► │   FastAPI    │ ◄─────► │  Yahoo      │
│   Frontend  │  REST   │   Backend    │  API    │  Finance    │
│             │         │              │         │             │
│  - React 19 │         │  - Sklearn   │         │  - OHLCV    │
│  - Tailwind │         │  - Pandas    │         │  - Real-time│
│  - SWR      │         │  - NumPy     │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │
      │                        │
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│   Vercel    │         │     VPS      │
│   Hosting   │         │   (Docker)   │
└─────────────┘         └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker (optional)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at `http://localhost:8001`

### Docker Setup (Recommended)

```bash
docker-compose up -d
```

## 📁 Project Structure

```
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks (SWR)
│   │   ├── lib/             # Utilities & API client
│   │   └── constants/       # Configuration
│   └── public/              # Static assets
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   │   ├── clustering_engine.py    # ML clustering
│   │   │   ├── supervised_model.py     # Confidence scoring
│   │   │   ├── backtest_engine.py      # Strategy validation
│   │   │   ├── trade_plan_engine.py    # Trade planning
│   │   │   └── feature_engineering.py  # Technical indicators
│   │   ├── models/         # Data schemas
│   │   └── constants/      # Stock tickers
│   └── requirements.txt
│
└── docker-compose.yml      # Container orchestration
```

## 🔧 Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19, Tailwind CSS 4
- **Charts**: Lightweight Charts
- **Data Fetching**: SWR (stale-while-revalidate)
- **Animations**: Framer Motion

### Backend
- **Framework**: FastAPI
- **ML**: Scikit-learn, Pandas, NumPy
- **Data**: Yahoo Finance API (yfinance)
- **Validation**: Pydantic

### Infrastructure
- **Frontend Hosting**: Vercel
- **Backend Hosting**: VPS with Docker
- **Reverse Proxy**: Nginx
- **SSL**: Cloudflare

## 📊 Machine Learning Pipeline

### 1. Data Collection
- Fetch 180 days of OHLCV data from Yahoo Finance
- Calculate 20+ technical indicators
- Normalize features for ML processing

### 2. Clustering (Unsupervised)
```python
# K-Means clustering with 6 strategies
- Buy the Dip (oversold, strong fundamentals)
- Momentum (strong uptrend)
- Breakout (consolidation breakout)
- Reversal (trend reversal signals)
- Consolidation (range-bound)
- Avoid (weak signals)
```

### 3. Supervised Learning
- Random Forest classifier for confidence scoring
- Features: RSI, MACD, volume, price action
- Output: Confidence percentage (0-100%)

### 4. Backtesting
- Simulate trades over historical data
- Calculate win rate, profit factor, max drawdown
- Validate strategy effectiveness

## 🎯 API Endpoints

### Market Overview
```http
GET /api/market-overview?index=lq45
```

### Stock Detail
```http
GET /api/stock/{ticker}?period_days=180
```

### Cluster Analysis
```http
GET /api/clusters?index=lq45
```

## 🌐 Live Demo

- **Frontend**: https://quant.indonesiastockanalyst.my.id
- **API**: https://api-quant.indonesiastockanalyst.my.id/docs

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Market overview with AI-powered stock clustering*

### Stock Detail
![Stock Detail](docs/screenshots/stock-detail.png)
*Comprehensive analysis with charts and trade plans*

### Technical Analysis
![Technical Analysis](docs/screenshots/technical.png)
*Interactive candlestick charts with indicators*

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
pytest tests/
```

## 📈 Performance

- **First Load**: < 2 seconds
- **API Response**: < 500ms average
- **Lighthouse Score**: 95+ (Performance, Accessibility, Best Practices)

## 🔐 Security

- HTTPS enforced
- CORS configured
- Input validation with Pydantic
- Rate limiting on API endpoints
- No sensitive data stored

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ghifar Ryal**
- GitHub: [@ghifarryaal](https://github.com/ghifarryaal)

## 🙏 Acknowledgments

- Yahoo Finance for market data
- Indonesian Stock Exchange (IDX)
- Scikit-learn community
- Next.js team

## 📞 Contact

For questions or feedback, please open an issue or contact via GitHub.

---

**⚠️ Disclaimer**: This platform is for educational purposes only. Not financial advice. Always do your own research before investing.
