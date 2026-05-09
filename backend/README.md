# LiquidityResearch Backend

The quantitative engine for **LiquidityResearch**, powered by FastAPI and XGBoost.

## 🧠 Engine Core
- **Market Categorization:** Unsupervised K-Means clustering for price action behavioral analysis.
- **Predictive Modeling:** Supervised XGBoost classification for trade setup validation.
- **Macro Logic:** Automated Z-score normalization for global macro indicators.

## 🛠 Features
- **FastAPI:** High-performance asynchronous API framework.
- **Direct Data Integration:** Real-time OHLCV fetching via direct Yahoo Finance v8 API.
- **Advanced Feature Engineering:** Integrated ATR, RSI, MACD, and Volume Ratio calculation.
- **Validation Suite:** Historical backtesting logic for model accuracy tracking.

## 🚀 Getting Started

1.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## 📡 API Endpoints
- `GET /api/cluster/{index}`: Primary analysis endpoint for market categorization and prediction.
- `GET /api/macro/score`: Global macro-economic risk analysis.
- `GET /api/stock/{ticker}`: Detailed single-stock indicator and trade plan analysis.
