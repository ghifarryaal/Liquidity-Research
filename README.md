# 📈 LiquidityResearch — AI-Powered Indonesian Stock Analysis

> Platform analisis saham Indonesia (LQ45, KOMPAS100, DBX) berbasis Machine Learning — clustering otomatis, trade plan AI, dan backtesting real-time. **Tanpa login. Gratis. Open source.**

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Now-brightgreen)](https://quant.indonesiastockanalyst.my.id)

**🔗 [Live Demo](https://quant.indonesiastockanalyst.my.id) · [API Docs](https://api-quant.indonesiastockanalyst.my.id/docs) · [Architecture](docs/ARCHITECTURE.md) · [Innovation](docs/INNOVATION.md)**

## 🌟 Features

### 🤖 AI-Powered Conversational Assistant (NEW!)
- **Ask Questions in Natural Language**: "Why is this stock classified as Momentum?"
- **Context-Aware Responses**: AI understands your stock's technical indicators and ML classification
- **Multi-Intent Recognition**: Handles questions about risk, timing, strategy, and more
- **Confidence Scoring**: Know how certain the AI is about each answer
- **Educational**: Learn while you analyze

### 🧠 Hybrid Machine Learning
- **Unsupervised Learning (K-Means)**: Discovers natural patterns in stock behavior
- **Supervised Learning (Random Forest)**: Validates classifications with confidence scores
- **Transparent Reasoning**: Understand WHY stocks are classified, not just HOW

### 📊 Intelligent Stock Clustering
- **Buy the Dip**: Oversold stocks with strong fundamentals
- **Momentum**: Strong uptrend with volume confirmation
- **Breakout**: Consolidation breakout patterns
- **Reversal**: Trend reversal signals
- **Consolidation**: Range-bound trading opportunities
- **Avoid**: Weak signals, better opportunities elsewhere

### 📈 Comprehensive Technical Analysis
- **20+ Technical Indicators**: RSI, MACD, Bollinger Bands, EMA, ATR, Volume Ratio
- **Interactive Charts**: Real-time candlestick charts with technical overlays
- **Historical Data**: 180-day analysis window
- **Real-Time Backtesting**: See historical performance for each recommendation

### 💼 Automated Trade Planning
- **AI-Generated Plans**: Entry, stop-loss, and take-profit levels
- **Risk Management**: Position sizing and risk/reward calculations
- **Strategy Recommendations**: Customized for each stock's characteristics
- **Execution Guidance**: Step-by-step trading instructions

### 🌍 Adaptive Macro Weighting
- **Market Sentiment Analysis**: Aggregate market-wide indicators
- **Panic Meter**: Real-time fear/greed index
- **Dynamic Adjustments**: Recommendations adapt to market conditions

### 🎓 Educational First
- **Transparent AI**: Understand the reasoning behind every recommendation
- **Learning Resources**: Built-in explanations and strategy guides
- **No "Buy/Sell" Buttons**: Encourages informed decision-making
- **Risk Education**: Learn proper risk management

### 🔒 Privacy-First Design
- **No Login Required**: Zero-friction access to all features
- **No Data Collection**: Your analysis stays private
- **No Tracking**: Respects user privacy
- **Open Access**: Democratizing sophisticated analysis

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
- **API Docs**: https://api-quant.indonesiastockanalyst.my.id/docs

> Coba langsung: buka dashboard → pilih saham LQ45 → lihat analisis AI + trade plan otomatis

## 📸 Screenshots

### Dashboard — Market Overview
Tampilan utama dengan 9 widget: Macro Sentiment, Market Momentum, Market Breadth, Sector Leadership, World Indices, Commodities, XGBoost Validation, Panic Meter, dan AI Clustering.

### Stock Detail — Analisis Lengkap
Setiap saham memiliki halaman detail dengan:
- Candlestick chart interaktif + EMA 20/50 + Bollinger Bands
- Technical Snapshot (RSI, MACD, Volume Ratio, ATR)
- AI Analyst Desk Briefing dengan reasoning transparan
- Trade Plan otomatis (Entry, Stop Loss, TP1, TP2, R:R)
- Backtest Scorecard historis 6 bulan

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
