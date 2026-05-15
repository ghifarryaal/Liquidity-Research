# Cluster Label Consistency Fix

## Problem

Ada inconsistency antara cluster label dan analyst reasoning di stock detail page:

**Contoh MEDC:**
- Cluster label (header): **"High Risk / Avoid"** ⚠️
- Analyst desk briefing: **"Buy the Dip"** 📉

Ini terjadi karena `get_stock_detail()` menggunakan **rule-based logic yang berbeda** dari K-Means clustering engine.

## Root Cause

### Sebelumnya (Simplified Logic)
```python
# get_stock_detail() - LAMA
if rsi > 60 and bb_pos > 0.6:
    label = "Trending / Momentum"
elif rsi < 40 and bb_pos < 0.4:
    label = "Buy the Dip"
elif rsi > 75 or ind.get("bb_width", 0) > 15:
    label = "High Risk / Avoid"
else:
    label = "Hold / Sideways"
```

**Masalah:**
- Hanya mempertimbangkan RSI dan BB position
- Tidak mempertimbangkan MACD, EMA gap, volume, ATR
- Kondisi "High Risk" terlalu ketat (hanya `rsi > 75 OR bb_width > 15`)
- Tidak aligned dengan clustering_engine.py logic

### Clustering Engine Logic (Correct)
```python
# clustering_engine.py - BENAR
momentum = 0.0
momentum += rsi_score        # +1.5 (>60), +0.5 (>50), -1.5 (<35), -0.3 (else)
momentum += macd_score       # (MACD - Signal) * 3
momentum += ema_gap_score    # gap / 5.0
momentum += bb_position_score # (bb_pos - 0.5) * 1.5

is_high_risk = (bb_width > 10) or (atr_pct > 4) or (vol_ratio > 3)
is_dip = (rsi < 42) and (bb_pos < 0.35) and (ema20_gap < -1.0)

# Label assignment
if momentum > 1.0:
    label = "Trending / Momentum"
elif momentum < -1.0:
    if is_dip or rsi < 40:
        label = "Buy the Dip"
    elif is_high_risk:
        label = "High Risk / Avoid"
    else:
        label = "Buy the Dip"
else:
    if is_high_risk:
        label = "High Risk / Avoid"
    else:
        label = "Hold / Sideways"
```

## Solution

Implement the **same momentum scoring algorithm** dari clustering_engine di `get_stock_detail()`:

### Momentum Scoring Components

1. **RSI Scoring**
   - RSI > 60: +1.5 (overbought, bullish)
   - RSI 50-60: +0.5 (slightly bullish)
   - RSI < 35: -1.5 (oversold, bearish)
   - RSI 35-50: -0.3 (slightly bearish)

2. **MACD Scoring**
   - `(MACD - Signal) * 3`, clipped to [-1.5, 1.5]
   - Positive = bullish cross, Negative = bearish cross

3. **EMA Gap Scoring**
   - `ema20_gap / 5.0`, clipped to [-1.0, 1.0]
   - Positive = price above EMA (uptrend), Negative = price below EMA (downtrend)

4. **Bollinger Band Position Scoring**
   - `(bb_pos - 0.5) * 1.5`
   - bb_pos = 0 (lower band), 1 (upper band)
   - Near upper band = bullish, Near lower band = bearish

### Risk & Dip Flags

**High Risk Flag:**
```python
is_high_risk = (bb_width > 10.0) or (atr_pct > 4.0) or (vol_ratio > 3.0)
```
- Wide Bollinger Bands (>10%) = high volatility
- High ATR (>4% of price) = large price swings
- High volume ratio (>3x average) = unusual activity

**Dip Flag:**
```python
is_dip = (rsi < 42) and (bb_pos < 0.35) and (ema20_gap < -1.0)
```
- RSI < 42 (oversold)
- Price near lower Bollinger Band (<35%)
- Price below EMA20 (>1% gap)

### Label Assignment Logic

```
if momentum > 1.0:
    → "Trending / Momentum" (strong bullish)
elif momentum < -1.0:
    if is_dip or rsi < 40:
        → "Buy the Dip" (oversold, potential bounce)
    elif is_high_risk:
        → "High Risk / Avoid" (oversold but risky)
    else:
        → "Buy the Dip" (default for low momentum)
else:  # momentum between -1.0 and 1.0
    if is_high_risk:
        → "High Risk / Avoid" (neutral momentum + high risk)
    else:
        → "Hold / Sideways" (neutral, calm)
```

## Example: MEDC Case

Suppose MEDC has:
- RSI = 78 (overbought)
- MACD = -0.5 (bearish cross)
- EMA20 gap = +2.5% (above EMA)
- BB position = 0.85 (near upper band)
- BB width = 12% (wide)
- ATR% = 3.5%
- Volume ratio = 2.5x

**Momentum Calculation:**
```
momentum = 0.0
momentum += 1.5      (RSI > 60)
momentum += -1.5     (MACD * 3 = -0.5 * 3 = -1.5, clipped)
momentum += 0.5      (EMA gap / 5 = 2.5 / 5 = 0.5)
momentum += 0.525    ((0.85 - 0.5) * 1.5 = 0.525)
momentum = 0.525
```

**Risk Flags:**
```
is_high_risk = (12 > 10) OR (3.5 > 4) OR (2.5 > 3)
             = TRUE OR FALSE OR FALSE
             = TRUE

is_dip = (78 < 42) AND (0.85 < 0.35) AND (2.5 < -1.0)
       = FALSE AND FALSE AND FALSE
       = FALSE
```

**Label Assignment:**
```
momentum = 0.525 (between -1.0 and 1.0)
is_high_risk = TRUE

→ "High Risk / Avoid" ✓
```

**Reasoning Generated:**
```
"Saham menunjukkan sinyal risiko tinggi: RSI 78 berada di zona ekstrem,
volatilitas di atas rata-rata (Bollinger Band melebar), MACD bearish,
dan volume 2.5x rata-rata. Hindari entry baru hingga kondisi teknikal
dan volume kembali stabil."
```

✅ **Cluster label dan reasoning sekarang CONSISTENT!**

## Files Modified

- `backend/app/routers/cluster.py` - Updated `get_stock_detail()` with aligned momentum scoring

## Deployment

```bash
# On VPS
git pull origin main
docker-compose restart backend
```

## Commit

```
fix: Align single-stock cluster label logic with K-Means clustering engine

Problem: get_stock_detail() used simplified rule-based logic that differed from
the clustering_engine.py momentum scoring, causing inconsistencies.

Solution: Implement the same momentum scoring algorithm from clustering_engine
in get_stock_detail() to ensure analyst reasoning always matches cluster label.
```

Commit: `f3e6536`

## Testing

To verify the fix works:

1. **Check a stock with high RSI (>75):**
   - Should show "High Risk / Avoid" in header
   - Reasoning should warn about overbought conditions

2. **Check a stock with low RSI (<40) + near lower BB:**
   - Should show "Buy the Dip" in header
   - Reasoning should suggest accumulation

3. **Check a stock with wide BB + high ATR:**
   - Should show "High Risk / Avoid" even if momentum is neutral
   - Reasoning should warn about volatility

All three should now be **consistent** between cluster label and analyst reasoning.
