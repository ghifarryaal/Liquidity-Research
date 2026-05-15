# XGBoost ML Implementation Fix

## Problem Identified

The XGBoost confidence score in the `/api/stock/{ticker}` endpoint was **hardcoded** instead of running actual predictions:

```python
# BEFORE (hardcoded)
confidence_score=0.78,
is_high_conviction=True,
```

This meant the ML model was trained but never actually used for predictions on individual stocks.

## Solution Implemented

### Backend Changes (`backend/app/routers/cluster.py`)

The `get_stock_detail()` function now:

1. **Fetches macro features** (DXY/US10Y z-scores) for the current market regime
2. **Trains XGBoost model** on the single ticker's historical data (180 days)
3. **Runs real prediction** using the trained model
4. **Sets `is_high_conviction`** dynamically based on actual confidence score (> 0.75)

```python
# AFTER (real predictions)
macro_feats = await get_macro_features()
dxy_zscore   = macro_feats.get("dxy_zscore",   0.0)
us10y_zscore = macro_feats.get("us10y_zscore", 0.0)

# Train on this single ticker's data
predictor = train_predictor(
    {ticker: df},
    dxy_zscore=dxy_zscore,
    us10y_zscore=us10y_zscore
)

# Get real XGBoost confidence score
raw_conf_score = 0.5  # default fallback
if predictor:
    conf_dict = predict_confidence(
        predictor,
        {ticker: ind},
        dxy_zscore=dxy_zscore,
        us10y_zscore=us10y_zscore
    )
    raw_conf_score = conf_dict.get(ticker, 0.5)

is_high_conviction = raw_conf_score > 0.75
```

### Frontend Changes (`frontend/src/app/stock/[ticker]/StockDetailClient.jsx`)

Updated the header section to clearly distinguish between two confidence metrics:

1. **Clustering Confidence** (K-Means distance) - shown in header
2. **XGBoost Confidence Score** (probability of +5% gain in 5 days) - shown in Trade Plan table

```jsx
// Header now shows:
<div className="flex flex-col items-start lg:items-end gap-1">
  <div className="flex items-center gap-2 md:gap-3">
    <span className="text-[9px] sm:text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">
      Clustering Confidence
    </span>
    <span className="font-data-mono text-xs sm:text-sm text-primary font-bold">
      {Math.round((stock.confidence ?? 0) * 100)}%
    </span>
  </div>
  <span className="text-[8px] sm:text-[9px] text-on-surface-variant/70 font-data-mono italic">
    K-Means cluster distance
  </span>
</div>
```

The Trade Plan table already had clear labeling for XGBoost score:
- Label: "XGBoost Confidence Score"
- Description: "P(+5% gain in 5 days)"

## How XGBoost Works in This Context

### Classification Task
- **Target**: Binary classification (1 = stock gains ≥5% within 5 trading days, 0 = does not)
- **Features** (10 dimensions):
  - RSI (14)
  - MACD strength
  - EMA 20/50 gap %
  - Bollinger Bands position & width
  - Volume ratio
  - ATR %
  - DXY z-score (macro)
  - US10Y z-score (macro)

### Training Process
1. Historical labeling: For each bar, check if price hits +5% target in next 5 days
2. Feature computation: Calculate all 10 indicators for each bar
3. Model training: XGBoost with 200 trees, max_depth=4, learning_rate=0.05
4. Validation: 30-day walk-forward validation to measure accuracy

### Prediction Output
- **Confidence Score**: Probability (0.0–1.0) that stock will gain ≥5% in next 5 days
- **High Conviction**: Automatically flagged when confidence > 0.75
- **Interpretation**: 
  - 0.75–1.0 = High conviction setup (strong buy signal)
  - 0.50–0.75 = Moderate conviction
  - 0.0–0.50 = Low conviction (avoid or wait)

## Why This Matters for Competition

1. **Real ML Integration**: The model is now actually used for predictions, not just trained
2. **Dynamic Scoring**: Each stock gets a unique confidence score based on its technical setup
3. **Macro-Aware**: Predictions incorporate current DXY/US10Y regime
4. **Transparent Metrics**: Two distinct confidence scores help users understand:
   - How well the stock fits the cluster (K-Means)
   - How likely it is to gain 5% in 5 days (XGBoost)

## Testing the Fix

### Local Testing
```bash
# Backend syntax check
python -m py_compile backend/app/routers/cluster.py

# Test endpoint
curl http://localhost:8000/api/stock/BBCA.JK
```

### Expected Response
```json
{
  "confidence_score": 0.68,
  "is_high_conviction": false,
  "cluster_label": "Trending / Momentum",
  "confidence": 0.85,
  ...
}
```

Note: `confidence_score` (0.68) is now dynamic based on XGBoost prediction, not hardcoded.

## Deployment

After pushing to GitHub:
```bash
# On VPS
git pull origin main
docker-compose restart backend
```

The frontend will automatically pick up the new labels on next deployment to Vercel.

## Files Modified

- `backend/app/routers/cluster.py` - Implemented real XGBoost predictions
- `frontend/src/app/stock/[ticker]/StockDetailClient.jsx` - Added clear confidence labels

## Commit

```
fix: Implement real XGBoost predictions in stock detail endpoint

- Train XGBoost model on single ticker's historical data
- Replace hardcoded confidence_score (0.78) with actual XGBoost prediction
- Set is_high_conviction based on real confidence score (> 0.75)
- Include macro features (DXY/US10Y z-scores) in prediction
- Update frontend labels to distinguish:
  * 'Clustering Confidence' (K-Means distance)
  * 'XGBoost Confidence Score' (probability of +5% gain in 5 days)
- Add descriptive subtexts for clarity
```

Commit: `f86b42d`
