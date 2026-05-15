# API Documentation

Base URL: `https://api-quant.indonesiastockanalyst.my.id`

## Authentication

No authentication required. All endpoints are publicly accessible.

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per IP

## Endpoints

### 1. Market Overview

Get aggregated market data with AI clustering.

**Endpoint:** `GET /api/market-overview`

**Query Parameters:**
- `index` (required): Market index (`lq45` or `kompas100`)

**Example Request:**
```bash
curl "https://api-quant.indonesiastockanalyst.my.id/api/market-overview?index=lq45"
```

**Example Response:**
```json
{
  "stocks": [
    {
      "ticker": "BBCA.JK",
      "name": "Bank Central Asia",
      "current_price": 10250,
      "price_change_pct": 1.5,
      "cluster_label": "Momentum",
      "confidence": 0.85,
      "indicators": {
        "rsi": 65.2,
        "macd": 125.5,
        "volume_ratio": 1.3
      }
    }
  ],
  "macro_sentiment": {
    "score": 0.65,
    "label": "Bullish",
    "description": "Market showing positive momentum"
  },
  "panic_meter": {
    "score": 25,
    "label": "Low Fear",
    "color": "green"
  }
}
```

---

### 2. Stock Detail

Get comprehensive analysis for a single stock.

**Endpoint:** `GET /api/stock/{ticker}`

**Path Parameters:**
- `ticker` (required): Stock ticker symbol (e.g., `BBCA.JK`)

**Query Parameters:**
- `period_days` (optional): Analysis period in days (default: 180)

**Example Request:**
```bash
curl "https://api-quant.indonesiastockanalyst.my.id/api/stock/BBCA.JK?period_days=180"
```

**Example Response:**
```json
{
  "ticker": "BBCA.JK",
  "name": "Bank Central Asia",
  "sector": "Financials",
  "current_price": 10250,
  "price_change_pct": 1.5,
  "cluster_label": "Momentum",
  "confidence": 0.85,
  "reasoning": "Strong uptrend with increasing volume...",
  "trading_style": "Swing Trading",
  "indicators": {
    "rsi": 65.2,
    "macd": 125.5,
    "macd_signal": 115.3,
    "bb_upper": 10500,
    "bb_middle": 10200,
    "bb_lower": 9900,
    "ema_20": 10150,
    "ema_50": 10000,
    "atr": 250,
    "volume_ratio": 1.3
  },
  "trade_plan": {
    "action": "BUY",
    "entry_price": 10200,
    "stop_loss": 9950,
    "take_profit_1": 10500,
    "take_profit_2": 10800,
    "position_size": "2-3% of portfolio",
    "risk_reward_ratio": 2.5
  },
  "backtest": {
    "total_trades": 15,
    "win_rate": 66.7,
    "profit_factor": 2.1,
    "max_drawdown": -8.5,
    "total_return": 25.3
  },
  "ohlcv": [
    {
      "date": "2024-01-01",
      "open": 10000,
      "high": 10100,
      "low": 9950,
      "close": 10050,
      "volume": 5000000
    }
  ],
  "ema_20_series": [...],
  "ema_50_series": [...],
  "bb_upper_series": [...],
  "bb_middle_series": [...],
  "bb_lower_series": [...]
}
```

---

### 3. Clusters

Get all stocks grouped by AI clusters.

**Endpoint:** `GET /api/clusters`

**Query Parameters:**
- `index` (required): Market index (`lq45` or `kompas100`)

**Example Request:**
```bash
curl "https://api-quant.indonesiastockanalyst.my.id/api/clusters?index=lq45"
```

**Example Response:**
```json
{
  "clusters": [
    {
      "label": "Buy the Dip",
      "description": "Oversold stocks with strong fundamentals",
      "count": 8,
      "stocks": [
        {
          "ticker": "BBRI.JK",
          "name": "Bank Rakyat Indonesia",
          "confidence": 0.82
        }
      ]
    },
    {
      "label": "Momentum",
      "description": "Strong uptrend with volume confirmation",
      "count": 12,
      "stocks": [...]
    }
  ]
}
```

---

### 4. Health Check

Check API health status.

**Endpoint:** `GET /health`

**Example Request:**
```bash
curl "https://api-quant.indonesiastockanalyst.my.id/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-15T07:00:00Z",
  "version": "1.0.0"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Data Sources

- **Market Data**: Yahoo Finance API
- **Technical Indicators**: Calculated using TA-Lib and Pandas
- **ML Models**: Scikit-learn (K-Means, Random Forest)

---

## Supported Tickers

### LQ45 (45 stocks)
BBCA.JK, BBRI.JK, BMRI.JK, TLKM.JK, ASII.JK, and more...

### KOMPAS100 (100 stocks)
All LQ45 stocks plus additional 55 stocks

---

## Notes

- All prices in Indonesian Rupiah (IDR)
- Timestamps in ISO 8601 format (UTC)
- Data updated every 15 minutes during market hours
- Historical data available up to 2 years

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/ghifarryaal/Liquidity-Research/issues
- Email: [your-email]

---

**Disclaimer**: This API provides data for educational purposes only. Not financial advice.
