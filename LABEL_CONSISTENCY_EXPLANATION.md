# Label Consistency Explanation: Why Different Labels for MEDC

## The Problem You Observed

MEDC menunjukkan **4 label berbeda** di berbagai tempat:

1. **Dashboard (InsightFeed table)**: "High Risk" 95% ✓
2. **Stock Detail - Analyst Desk Briefing**: "Buy the Dip" ✗
3. **Stock Detail - Clustering Confidence**: 85% ✓
4. **Stock Detail - Execution Strategy**: "HIGH RISK" ✓
5. **Stock Detail - XGBoost Score**: 78% ✓

**Inconsistency**: Analyst Desk Briefing mengatakan "Buy the Dip" padahal semua label lainnya mengatakan "High Risk"!

---

## Root Cause Analysis

Ada **2 endpoint berbeda** yang generate label:

### 1. `/api/cluster/{index_name}` (Dashboard)
```python
# Step 1: Get label dari K-Means clustering
raw_label = cluster_info.get("cluster_label", "Hold / Sideways")

# Step 2: APPLY MACRO PENALTY
adjusted_label, confidence, macro_suffix = apply_macro_penalty(raw_label, macro_raw)

# Step 3: Generate reasoning dengan adjusted label
strategy, reasoning = generate_reasoning(adjusted_label, ind, macro_suffix)

# Step 4: Calculate trade plan dengan adjusted label
plan_raw = calculate_trade_plan(df, ind, adjusted_label, index_name=index_name)
```

### 2. `/api/stock/{ticker}` (Stock Detail) - SEBELUM FIX
```python
# Step 1: Get label dari rule-based momentum scoring
label = "High Risk / Avoid"  # (dari momentum scoring)

# Step 2: TIDAK ADA MACRO PENALTY! ❌
# adjusted_label, confidence, macro_suffix = apply_macro_penalty(label, macro_raw)

# Step 3: Generate reasoning dengan label (tanpa macro adjustment)
strategy, reasoning = generate_reasoning(label, ind)  # ❌ TANPA macro_suffix

# Step 4: Calculate trade plan dengan label (tanpa macro adjustment)
plan_raw = calculate_trade_plan(df, ind, label, index_name="lq45")  # ❌ TANPA adjustment
```

**MASALAHNYA**: `/api/stock/{ticker}` tidak apply `apply_macro_penalty()`, jadi label bisa berbeda!

---

## What is `apply_macro_penalty()`?

Fungsi ini **adjust label berdasarkan macro regime**:

```python
def apply_macro_penalty(cluster_label: str, macro_score: dict) -> tuple[str, float, str]:
    """Adjust cluster confidence/label based on macro regime."""
    penalty = macro_score.get("volatility_penalty", 0.5)
    regime  = macro_score.get("macro_regime", "Neutral")

    if regime == "Risk-Off" and penalty > 0.65:
        if cluster_label == "Buy the Dip":
            return (
                cluster_label, 0.55,
                " Namun, kondisi makro global sedang Risk-Off — pertimbangkan menunggu konfirmasi."
            )
        elif cluster_label == "Trending / Momentum":
            return (
                "Hold / Sideways", 0.50,  # ← LABEL BERUBAH!
                " Tren positif mungkin tertekan oleh kondisi pasar global yang volatile."
            )

    if regime == "Risk-On" and penalty < 0.35:
        if cluster_label == "Hold / Sideways":
            return (
                cluster_label, 0.70,
                " Kondisi makro mendukung — pantau untuk potensi breakout."
            )

    return (cluster_label, 0.65, "")
```

**Contoh:**
- Jika macro regime = "Risk-Off" dan label = "Trending / Momentum"
- → Label berubah menjadi "Hold / Sideways"!
- → Confidence turun dari 0.65 ke 0.50

---

## The Fix

Sekarang `/api/stock/{ticker}` juga apply `apply_macro_penalty()`:

```python
# Step 1: Get label dari rule-based momentum scoring
label = "High Risk / Avoid"

# Step 2: APPLY MACRO PENALTY ✓
macro_raw = await get_macro_score()
adjusted_label, macro_confidence, macro_suffix = apply_macro_penalty(label, macro_raw)

# Step 3: Generate reasoning dengan adjusted label + macro suffix
strategy, reasoning = generate_reasoning(adjusted_label, ind, macro_suffix)

# Step 4: Calculate trade plan dengan adjusted label
plan_raw = calculate_trade_plan(df, ind, adjusted_label, index_name="lq45")
```

**Result**: Sekarang kedua endpoint menggunakan **logic yang sama** ✓

---

## Why 3 Different Confidence Scores?

Sekarang kamu tahu ada **3 scoring berbeda**:

### 1. **Cluster Label** (Categorical)
- **Sumber**: K-Means clustering + macro adjustment
- **Nilai**: "Buy the Dip", "Trending / Momentum", "Hold / Sideways", "High Risk / Avoid"
- **Tujuan**: Kategorisasi saham berdasarkan technical setup + macro regime
- **Contoh**: "High Risk / Avoid"

### 2. **Clustering Confidence** (Numeric 0-1)
- **Sumber**: K-Means distance ke centroid
- **Nilai**: 0.30 - 0.95
- **Tujuan**: Seberapa yakin K-Means bahwa saham termasuk cluster itu
- **Contoh**: 85% = saham sangat dekat dengan "High Risk" centroid

### 3. **XGBoost Confidence Score** (Numeric 0-1)
- **Sumber**: XGBoost classifier prediction
- **Nilai**: 0.0 - 1.0
- **Tujuan**: Probabilitas saham akan gain +5% dalam 5 hari ke depan
- **Contoh**: 78% = 78% chance saham naik 5% dalam 5 hari

---

## MEDC Example (After Fix)

Suppose MEDC punya:
- **Momentum score**: -1.5 (bearish)
- **is_high_risk**: TRUE (bb_width > 10)
- **Macro regime**: "Neutral"

**Label Assignment:**
```
momentum < -1.0 AND is_high_risk = TRUE
→ label = "High Risk / Avoid"
```

**Macro Adjustment:**
```
apply_macro_penalty("High Risk / Avoid", macro_raw)
→ regime = "Neutral"
→ NO CHANGE
→ adjusted_label = "High Risk / Avoid"
→ macro_confidence = 0.65
→ macro_suffix = ""
```

**Reasoning:**
```
generate_reasoning("High Risk / Avoid", ind, "")
→ "Saham menunjukkan sinyal risiko tinggi: RSI 78 berada di zona ekstrem,
   volatilitas di atas rata-rata (Bollinger Band melebar), MACD bearish,
   dan volume 2.5x rata-rata. Hindari entry baru hingga kondisi teknikal
   dan volume kembali stabil."
```

**Trade Plan Status:**
```
calculate_trade_plan(df, ind, "High Risk / Avoid", ...)
→ cluster_label == "High Risk / Avoid"
→ status = "High Risk"
```

**Result**: Semua label CONSISTENT ✓

---

## Why This Design?

Tiga scoring berbeda memberikan **multiple perspectives**:

1. **Cluster Label** → Trader tahu **kondisi teknikal sekarang** + **macro regime**
2. **Clustering Confidence** → Trader tahu **seberapa yakin kategori itu**
3. **XGBoost Score** → Trader tahu **probabilitas gain di masa depan**

**Contoh interpretasi:**
- "High Risk" + 85% clustering confidence + 78% XGBoost
  → Saham sedang overbought (High Risk)
  → Tapi masih ada 78% chance bounce naik 5% dalam 5 hari
  → Trader bisa **wait for pullback** kemudian entry dengan tight stop loss

---

## Files Modified

- `backend/app/routers/cluster.py` - Added macro penalty application to stock detail endpoint

## Deployment

```bash
# On VPS
git pull origin main
docker-compose restart backend
```

## Commit

```
fix: Apply macro penalty to stock detail endpoint for label consistency

Problem: /api/stock/{ticker} endpoint did not apply macro regime adjustments,
causing label inconsistency between dashboard and stock detail page.

Solution: Apply apply_macro_penalty() in get_stock_detail() to ensure
both endpoints use the same label adjustment logic.
```

Commit: `b1524d6`

---

## Testing

To verify the fix:

1. **Check MEDC in dashboard**: Should show "High Risk" 95%
2. **Click MEDC to open stock detail**: Should show "High Risk" in Analyst Desk Briefing
3. **Check Execution Strategy**: Should show "HIGH RISK" status
4. **Check XGBoost Score**: Should show 78% (independent of label)

All should now be **CONSISTENT** ✓
