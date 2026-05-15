# System Architecture

## Overview

LiquidityResearch is a full-stack application that combines machine learning, real-time data processing, and modern web technologies to provide intelligent stock analysis for the Indonesian market.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                          │
│  (Web Browser - Desktop & Mobile)                          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Next.js 15 App Router                               │  │
│  │  - React 19 (Client Components)                      │  │
│  │  - SWR for data fetching                             │  │
│  │  - Tailwind CSS 4                                    │  │
│  │  - Lightweight Charts                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTPS)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (VPS + Docker)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                 │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  API Layer (Routers)                           │  │  │
│  │  │  - /api/market-overview                        │  │  │
│  │  │  - /api/stock/{ticker}                         │  │  │
│  │  │  - /api/clusters                               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Service Layer                                 │  │  │
│  │  │  - Data Fetcher (Yahoo Finance)                │  │  │
│  │  │  - Feature Engineering                         │  │  │
│  │  │  - Clustering Engine (ML)                      │  │  │
│  │  │  - Supervised Model (ML)                       │  │  │
│  │  │  - Backtest Engine                             │  │  │
│  │  │  - Trade Plan Engine                           │  │  │
│  │  │  - Macro Weighting                             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Data Sources                      │
│  - Yahoo Finance API (yfinance)                            │
│  - Real-time OHLCV data                                    │
│  - Historical price data                                   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Architecture

#### Technology Stack
- **Framework**: Next.js 15 with App Router
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **Data Fetching**: SWR (stale-while-revalidate)
- **Charts**: Lightweight Charts by TradingView
- **Animations**: Framer Motion

#### Key Features
1. **Server-Side Rendering (SSR)**: Initial page load optimized
2. **Client-Side Hydration**: Interactive after load
3. **Automatic Code Splitting**: Faster page loads
4. **Image Optimization**: Next.js Image component
5. **Font Optimization**: Google Fonts with next/font

#### Component Structure
```
src/
├── app/                    # App Router pages
│   ├── layout.js          # Root layout
│   ├── page.js            # Homepage
│   └── stock/[ticker]/    # Dynamic stock pages
│       ├── page.jsx       # Stock detail page
│       └── error.jsx      # Error boundary
├── components/
│   ├── dashboard/         # Dashboard components
│   ├── charts/            # Chart components
│   ├── education/         # Educational components
│   ├── layout/            # Layout components
│   └── ui/                # UI primitives
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities
│   ├── api.js            # API client
│   ├── formatters.js     # Data formatters
│   └── mentorContext.js  # Context providers
└── constants/            # Configuration
```

### Backend Architecture

#### Technology Stack
- **Framework**: FastAPI (Python 3.11)
- **ML Libraries**: Scikit-learn, Pandas, NumPy
- **Data Source**: yfinance (Yahoo Finance)
- **Validation**: Pydantic
- **Server**: Uvicorn (ASGI)

#### Service Layer

##### 1. Data Fetcher Service
```python
# Responsibilities:
- Fetch OHLCV data from Yahoo Finance
- Handle API rate limiting
- Cache responses
- Error handling for missing data
```

##### 2. Feature Engineering Service
```python
# Calculates technical indicators:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- EMA (Exponential Moving Average)
- ATR (Average True Range)
- Volume Ratio
- Price momentum
- Volatility metrics
```

##### 3. Clustering Engine (Unsupervised ML)
```python
# K-Means clustering with 6 clusters:
1. Buy the Dip - Oversold with strong fundamentals
2. Momentum - Strong uptrend with volume
3. Breakout - Consolidation breakout
4. Reversal - Trend reversal signals
5. Consolidation - Range-bound trading
6. Avoid - Weak signals

# Features used:
- RSI
- MACD
- Volume ratio
- Price change %
- Volatility
- Trend strength
```

##### 4. Supervised Model (Confidence Scoring)
```python
# Random Forest Classifier:
- Input: Technical indicators
- Output: Confidence score (0-100%)
- Training: Historical labeled data
- Validation: Cross-validation
```

##### 5. Backtest Engine
```python
# Strategy validation:
- Simulate trades over historical data
- Calculate metrics:
  * Win rate
  * Profit factor
  * Max drawdown
  * Total return
  * Sharpe ratio
```

##### 6. Trade Plan Engine
```python
# Generate actionable plans:
- Entry price (optimal entry point)
- Stop loss (risk management)
- Take profit levels (TP1, TP2)
- Position sizing
- Risk/reward ratio
```

##### 7. Macro Weighting Service
```python
# Market sentiment analysis:
- Aggregate market indicators
- Calculate panic meter
- Adjust cluster weights
- Provide market context
```

## Data Flow

### 1. Market Overview Request

```
User → Frontend → API (/api/market-overview?index=lq45)
                    ↓
              Data Fetcher (fetch all LQ45 tickers)
                    ↓
              Feature Engineering (calculate indicators)
                    ↓
              Clustering Engine (assign clusters)
                    ↓
              Supervised Model (confidence scores)
                    ↓
              Macro Weighting (market sentiment)
                    ↓
              Response (aggregated data)
                    ↓
              Frontend (render dashboard)
```

### 2. Stock Detail Request

```
User → Frontend → API (/api/stock/BBCA.JK)
                    ↓
              Data Fetcher (fetch OHLCV + indicators)
                    ↓
              Feature Engineering (calculate all indicators)
                    ↓
              Clustering Engine (assign cluster)
                    ↓
              Supervised Model (confidence + reasoning)
                    ↓
              Trade Plan Engine (generate plan)
                    ↓
              Backtest Engine (validate strategy)
                    ↓
              Response (comprehensive analysis)
                    ↓
              Frontend (render stock detail page)
```

## Machine Learning Pipeline

### Training Phase (Offline)

```
Historical Data → Feature Engineering → Labeling
                                          ↓
                                    Train Models
                                          ↓
                              ┌───────────┴───────────┐
                              ↓                       ↓
                      K-Means Clustering    Random Forest Classifier
                              ↓                       ↓
                        Save Models            Save Models
```

### Inference Phase (Real-time)

```
Live Data → Feature Engineering → Load Models
                                      ↓
                          ┌───────────┴───────────┐
                          ↓                       ↓
                  Predict Cluster         Predict Confidence
                          ↓                       ↓
                          └───────────┬───────────┘
                                      ↓
                              Generate Insights
```

## Deployment Architecture

### Frontend (Vercel)
```
GitHub Push → Vercel Build → Deploy to Edge Network
                                      ↓
                              Global CDN Distribution
                                      ↓
                              User Access (Low Latency)
```

### Backend (VPS + Docker)
```
GitHub Push → Manual Deploy → Docker Build
                                      ↓
                              Docker Compose Up
                                      ↓
                              Nginx Reverse Proxy
                                      ↓
                              SSL/TLS (Cloudflare)
                                      ↓
                              Public API Access
```

## Security Measures

1. **HTTPS Everywhere**: All traffic encrypted
2. **CORS Configuration**: Restricted origins
3. **Input Validation**: Pydantic schemas
4. **Rate Limiting**: Prevent abuse
5. **Error Handling**: No sensitive data in errors
6. **Dependency Scanning**: Regular security audits

## Performance Optimizations

### Frontend
- Code splitting (automatic)
- Image optimization (Next.js)
- Font optimization (next/font)
- SWR caching (10-minute cache)
- Lazy loading (dynamic imports)

### Backend
- Response caching (in-memory)
- Batch processing (multiple tickers)
- Async operations (FastAPI)
- Connection pooling
- Efficient data structures (NumPy arrays)

## Monitoring & Observability

### Metrics Tracked
- API response times
- Error rates
- Cache hit rates
- ML model accuracy
- User engagement

### Logging
- Structured logging (JSON)
- Error tracking
- Performance monitoring
- User analytics

## Scalability Considerations

### Horizontal Scaling
- Frontend: Vercel auto-scales
- Backend: Docker Swarm or Kubernetes ready
- Database: Can add Redis for caching

### Vertical Scaling
- Increase VPS resources
- Optimize ML models
- Database indexing

## Future Enhancements

1. **Real-time WebSocket**: Live price updates
2. **User Accounts**: Portfolio tracking
3. **Alerts**: Price/indicator notifications
4. **Mobile App**: React Native
5. **Advanced ML**: Deep learning models
6. **Backtesting UI**: Interactive strategy builder

---

**Last Updated**: May 15, 2026
