# LiquidityResearch: Hybrid ML Market Intelligence

### 🚀 Stop Guessing. Start Calculating.
**LiquidityResearch** is a professional-grade quantitative engine and dashboard designed to eliminate emotional trading through the synergy of **Unsupervised Clustering**, **Supervised Prediction**, and **Real-Time Global Macro Awareness**.

---

## 📉 The "Why"
Emotional trading is the primary cause of retail capital loss. Most traders struggle with "Analysis Paralysis"—the inability to synthesize global macro trends, sectoral rotation, and technical volatility into a single, executable decision. 

**LiquidityResearch** solves this by providing a high-conviction "Command Center" that processes 600+ tickers (LQ45, Kompas 100, and DBX Second-Liners) to find institutional accumulation phases and high-probability trade setups.

---

## 🧠 Core Pillars

### 1. ML Intelligence (The Engine)
- **K-Means Clustering:** Categorizes the market into behavioral regimes (Trending, Mean Reversion, Panic, or Sideways) using high-dimensional feature vectors.
- **XGBoost Confidence Scores:** A secondary supervised layer trained on historical IDX data to predict the probability of a 5% gain within 5 trading days.
- **Dynamic Walk-Forward Validation:** Real-time accuracy tracking to ensure the model adapts to current market regimes.

### 2. Supported Indices
- **LQ45:** The 45 most liquid and high-capitalization stocks on the IDX.
- **Kompas 100:** 100 stocks with high liquidity and good fundamentals.
- **DBX (Second-Liners):** Comprehensive coverage of Indonesian second-liner stocks (400+ tickers) for alpha-seeking traders.

### 3. Technical Precision (The Execution)
- **3.0x ATR Stop-Loss:** Professional risk management using Average True Range (ATR) multipliers.
- **Fibonacci-Optimized Targets:** Dynamic Take-Profit levels based on liquidity clusters.
- **Macro-Awareness:** Integrated Z-score analysis of **DXY (U.S. Dollar Index)** and **US10Y (U.S. 10-Year Treasury Yield)**.

### 4. AI Mentorship (The Learning Layer)
- **Gemini 1.5 Flash Integration:** An on-board AI Mentor that explains the "Why" behind every trade setup. 
- **Contextual Awareness:** The mentor understands the current cluster, macro sentiment, and stock-specific indicators to provide actionable insights.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Next.js 15, React 19, Framer Motion, SWR, Tailwind CSS 4 |
| **Backend** | FastAPI, Uvicorn, Httpx |
| **Machine Learning** | XGBoost 2.0, Scikit-Learn, Pandas, NumPy |
| **AI Architecture** | Google Gemini 1.5 Flash |
| **Data Logic** | Direct Yahoo Finance v8 API Integration |
| **Deployment** | Docker, Docker Compose, Nginx |

---

## 📦 Project Structure

```text
.
├── backend/                # FastAPI Quantitative Engine
│   ├── app/
│   │   ├── constants/      # Ticker definitions (LQ45, Kompas 100, DBX)
│   │   ├── models/         # Pydantic Schemas & Data Structures
│   │   ├── routers/        # API Endpoints (Cluster, Macro, Stock)
│   │   └── services/       # ML Logic (XGBoost, K-Means, Macro Weighting)
│   ├── requirements.txt    # ML Stack Dependencies
│   └── Dockerfile          # Backend Containerization
├── frontend/               # Next.js Analytics Dashboard
│   ├── src/
│   │   ├── app/            # Main Pages & Stock Deep Dives
│   │   ├── components/     # High-Density UI Widgets
│   │   └── hooks/          # Real-time SWR Data Fetchers
│   ├── package.json        # Frontend Dependencies
│   └── Dockerfile          # Frontend Containerization
├── docker-compose.yml      # Production Orchestration
├── nginx.conf              # Reverse Proxy Configuration
└── README.md               # Main Documentation
```

---

## ⚙️ Installation & Setup (Local Development)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
*Create a `.env` file in `/backend` with:*
`GEMINI_API_KEY=your_key_here`

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Running the Project
- **Backend:** `uvicorn app.main:app --reload` (Runs on port 8000)
- **Frontend:** `npm run dev` (Runs on port 3000)

---

## 🚢 Production Deployment (Docker)

To deploy the entire stack using Docker Compose:

```bash
docker-compose up -d --build
```

The stack includes:
- **Frontend:** Next.js application (Port 3001)
- **Backend:** FastAPI application (Port 8001)
- **Nginx:** Reverse proxy for domain routing (Port 80)

---

## 🖼️ Screenshot Preview

1.  **The Command Center:** A macro-aware overview of the IDX, showing the Panic Meter, Sector Momentum, and Macro Sentiment Gauge.
2.  **ML Confidence Matrix:** The XGBoost validation panel showing real-time precision and high-conviction flags.
3.  **The Interactive Trade Plan:** Deep-dive view of a single stock with automated ATR-based risk management and AI mentorship.

---

## ✨ Why LiquidityResearch?
**LiquidityResearch** represents an elegant bridge between **Traditional Quantitative Finance** and **Modern Generative AI**. We don't just "chat" with an LLM; we feed the LLM processed, high-quality technical data from our own ML engines. The result is an AI that doesn't just hallucinate—it calculates, validates, and educates.

---

## ⚖️ Disclaimer
*LiquidityResearch is an analytical tool. Trading involves risk. Use this data as a supplement to, not a replacement for, your own professional judgment.*

