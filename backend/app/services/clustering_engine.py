"""
clustering_engine.py — K-Means clustering + rule-based label mapping.

Aligned with the reference clustering.py methodology:
- StandardScaler (reference standard)  — kept as RobustScaler for financial outlier robustness
- K-Means n_clusters=4, random_state=42, n_init=20
- Full cluster quality metrics: Silhouette, Davies-Bouldin, Calinski-Harabasz
- Rule-based centroid-to-label mapping (stable across runs)

Feature vector (8 dimensions, same order as feature_engineering.py):
  [0] RSI(14)
  [1] MACD strength (MACD - Signal)
  [2] EMA20 gap %
  [3] EMA50 gap %
  [4] Bollinger Band position (0=lower band, 1=upper band)
  [5] Bollinger Band width %
  [6] Volume ratio (vs 20-day avg)
  [7] ATR % of price
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

N_CLUSTERS   = 4
RANDOM_STATE = 42

CLUSTER_CONFIG: dict[str, dict] = {
    "Buy the Dip": {
        "color":             "#00FFB2",
        "icon":              "📉",
        "short_strategy_id": "buy_dip",
    },
    "Trending / Momentum": {
        "color":             "#3B82F6",
        "icon":              "🚀",
        "short_strategy_id": "momentum",
    },
    "Hold / Sideways": {
        "color":             "#F59E0B",
        "icon":              "⏸️",
        "short_strategy_id": "hold",
    },
    "High Risk / Avoid": {
        "color":             "#EF4444",
        "icon":              "⚠️",
        "short_strategy_id": "avoid",
    },
}


# ---------------------------------------------------------------------------
# Main clustering function
# ---------------------------------------------------------------------------


def run_clustering(
    tickers: list[str],
    feature_matrix: np.ndarray,
) -> dict[str, dict]:
    """
    Run K-Means on the feature matrix (aligned with reference clustering.py).

    Steps:
      1. RobustScaler — handles financial outliers better than StandardScaler
      2. KMeans(n_clusters=4, random_state=42, n_init=20, max_iter=500)
      3. Evaluate: Silhouette, Davies-Bouldin, Calinski-Harabasz scores
      4. Map cluster IDs → human labels via centroid heuristics
      5. Compute per-stock confidence from normalised centroid distance

    Returns:
        dict[ticker] -> {cluster_id, cluster_label, cluster_color, confidence}
    """
    if len(tickers) < N_CLUSTERS:
        logger.warning(
            "Too few tickers (%d) for %d clusters — returning empty",
            len(tickers), N_CLUSTERS,
        )
        return {}

    # ── 1. Scale features (RobustScaler: robust to price-scale outliers) ──
    scaler   = RobustScaler()
    X_scaled = scaler.fit_transform(feature_matrix)

    # ── 2. K-Means (aligned with reference: random_state=42, n_init=10+) ─
    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=RANDOM_STATE,
        n_init=20,           # reference uses 10; we use 20 for more stability
        max_iter=500,
        algorithm="lloyd",
    )
    labels  = kmeans.fit_predict(X_scaled)
    centers = scaler.inverse_transform(kmeans.cluster_centers_)  # original scale

    # ── 3. Cluster quality metrics (as per reference clustering.py) ───────
    cluster_metrics = _compute_cluster_metrics(X_scaled, labels)
    logger.info(
        "Cluster metrics | Silhouette: %.4f | Davies-Bouldin: %.4f | "
        "Calinski-Harabasz: %.2f",
        cluster_metrics["silhouette"],
        cluster_metrics["davies_bouldin"],
        cluster_metrics["calinski_harabasz"],
    )

    # ── 4. Map cluster IDs → semantic labels via centroid heuristics ──────
    cluster_id_to_label = _map_centroids_to_labels(centers)

    # ── 5. Per-stock confidence: 1 - (dist_to_own / max_dist) ────────────
    distances = kmeans.transform(X_scaled)   # shape (n_stocks, n_clusters)
    max_dist  = distances.max() + 1e-9

    result: dict[str, dict] = {}
    for i, ticker in enumerate(tickers):
        cid   = int(labels[i])
        label = cluster_id_to_label.get(cid, "Hold / Sideways")
        cfg   = CLUSTER_CONFIG[label]

        dist_to_own = distances[i, cid]
        confidence  = float(np.clip(1.0 - dist_to_own / max_dist, 0.30, 0.95))

        result[ticker] = {
            "cluster_id":    cid,
            "cluster_label": label,
            "cluster_color": cfg["color"],
            "cluster_icon":  cfg["icon"],
            "confidence":    round(confidence, 3),
        }

    return result


# ---------------------------------------------------------------------------
# Cluster quality metrics  (mirrors reference clustering.py evaluate functions)
# ---------------------------------------------------------------------------


def _compute_cluster_metrics(X_scaled: np.ndarray, labels: np.ndarray) -> dict:
    """
    Compute the three standard cluster evaluation metrics used in clustering.py:
      - Silhouette Score       (higher is better, range [-1, 1])
      - Davies-Bouldin Index   (lower is better)
      - Calinski-Harabasz Index (higher is better)
    """
    try:
        sil = silhouette_score(X_scaled, labels)
    except Exception:
        sil = 0.0

    try:
        db  = davies_bouldin_score(X_scaled, labels)
    except Exception:
        db  = 0.0

    try:
        ch  = calinski_harabasz_score(X_scaled, labels)
    except Exception:
        ch  = 0.0

    return {
        "silhouette":         round(float(sil), 4),
        "davies_bouldin":     round(float(db),  4),
        "calinski_harabasz":  round(float(ch),  2),
    }


# ---------------------------------------------------------------------------
# Rule-based centroid → label mapping
# ---------------------------------------------------------------------------


def _map_centroids_to_labels(centers: np.ndarray) -> dict[int, str]:
    """
    Map cluster IDs to human-readable labels by inspecting centroid values.

    Financial logic (aligned with reference analyze_clusters output):
      - High RSI (>65) + positive MACD + near BB upper + trending → Momentum
      - Low RSI (<40) + near BB lower + negative EMA gap    → Buy the Dip
      - High BB width + extreme RSI + high ATR              → High Risk / Avoid
      - Everything else (RSI neutral, flat MACD)            → Hold / Sideways

    Feature indices:
        0=RSI, 1=MACD_strength, 2=EMA20_gap%, 3=EMA50_gap%,
        4=BB_position, 5=BB_width%, 6=vol_ratio, 7=ATR%
    """
    n      = len(centers)
    scores = {}

    for i, c in enumerate(centers):
        rsi         = float(c[0])
        macd_str    = float(c[1])
        ema20_gap   = float(c[2])
        ema50_gap   = float(c[3])
        bb_pos      = float(c[4])
        bb_width    = float(c[5])
        vol_ratio   = float(c[6])
        atr_pct     = float(c[7])

        # ── Momentum score: positive = bullish uptrend ───────────────────
        momentum = 0.0

        # RSI: overbought zone = momentum, oversold = potential dip
        if rsi > 60:
            momentum += 1.5
        elif rsi > 50:
            momentum += 0.5
        elif rsi < 35:
            momentum -= 1.5  # deep oversold
        else:
            momentum -= 0.3  # slightly below neutral

        # MACD cross above signal = bullish
        momentum += float(np.clip(macd_str * 3, -1.5, 1.5))

        # Price above EMAs = uptrend
        momentum += float(np.clip(ema20_gap / 5.0, -1.0, 1.0))
        momentum += float(np.clip(ema50_gap / 8.0, -0.8, 0.8))

        # Near upper Bollinger Band = strong price action
        momentum += (bb_pos - 0.5) * 1.5

        # ── Volatility / risk flag ────────────────────────────────────────
        # Wide BB + high ATR + high volume = heightened uncertainty
        is_high_risk = (bb_width > 10.0) or (atr_pct > 4.0) or (vol_ratio > 3.0)

        # ── Dip flag: low RSI + near lower band + below EMAs ─────────────
        is_dip = (rsi < 42) and (bb_pos < 0.35) and (ema20_gap < -1.0)

        scores[i] = {
            "momentum":     momentum,
            "rsi":          rsi,
            "bb_pos":       bb_pos,
            "macd_str":     macd_str,
            "high_risk":    is_high_risk,
            "dip":          is_dip,
        }

    # Sort clusters by momentum score ascending
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x]["momentum"])
    label_map: dict[int, str] = {}

    if n == 4:
        # ── Two extremes first ────────────────────────────────────────────
        # Highest momentum = Trending / Momentum
        label_map[sorted_ids[3]] = "Trending / Momentum"

        # Lowest momentum = check if it qualifies as Buy the Dip or High Risk
        lowest_id = sorted_ids[0]
        if scores[lowest_id]["dip"] or scores[lowest_id]["rsi"] < 40:
            label_map[lowest_id] = "Buy the Dip"
        elif scores[lowest_id]["high_risk"]:
            label_map[lowest_id] = "High Risk / Avoid"
        else:
            label_map[lowest_id] = "Buy the Dip"  # default: low score = dip

        # ── Two middle clusters ───────────────────────────────────────────
        mid1, mid2 = sorted_ids[1], sorted_ids[2]

        # The more volatile middle cluster → High Risk / Avoid
        # The calmer middle cluster → Hold / Sideways
        if scores[mid2]["high_risk"] and not scores[mid1]["high_risk"]:
            label_map[mid2] = "High Risk / Avoid"
            label_map[mid1] = "Hold / Sideways"
        elif scores[mid1]["high_risk"] and not scores[mid2]["high_risk"]:
            label_map[mid1] = "High Risk / Avoid"
            label_map[mid2] = "Hold / Sideways"
        else:
            # Neither or both are risky: assign by momentum score
            label_map[mid1] = "Hold / Sideways"
            label_map[mid2] = "High Risk / Avoid"

        # ── Sanity check: ensure all 4 labels are assigned ───────────────
        assigned = set(label_map.values())
        missing  = set(CLUSTER_CONFIG.keys()) - assigned
        if missing:
            # Find the unassigned cluster id and give it the missing label
            unassigned_ids = [sid for sid in sorted_ids if sid not in label_map]
            for uid, mlabel in zip(unassigned_ids, missing):
                label_map[uid] = mlabel

    else:
        # Fallback for non-4-cluster edge cases
        label_list = list(CLUSTER_CONFIG.keys())
        for j, cid in enumerate(sorted_ids):
            label_map[cid] = label_list[j % 4]

    logger.debug("Centroid label map: %s", label_map)
    return label_map


# ---------------------------------------------------------------------------
# Reasoning generator  (Indonesian analyst brief)
# ---------------------------------------------------------------------------


def generate_reasoning(
    label: str,
    ind: dict,
    macro_suffix: str = "",
) -> tuple[str, str]:
    """
    Generate a human-readable strategy and reasoning in Indonesian.

    FIX: uses explicit `is not None` checks instead of truthiness so that
    indicator values of 0.0 are handled correctly.

    Returns:
        (strategy_str, reasoning_str)
    """
    rsi        = ind.get("rsi")
    macd       = ind.get("macd")
    macd_sig   = ind.get("macd_signal")
    ema20      = ind.get("ema_20")
    ema50      = ind.get("ema_50")
    bb_pos     = ind.get("bb_position", 0.5)
    vol_ratio  = ind.get("volume_ratio")

    # ── Safe formatted strings ────────────────────────────────────────────
    rsi_str = f"RSI {rsi:.1f}" if rsi is not None else "RSI tidak tersedia"

    # FIX: explicit None check — 0.0 MACD is valid and should not be "bearish" by default
    if macd is not None and macd_sig is not None:
        macd_cross = "bullish (MACD > Signal)" if macd > macd_sig else "bearish (MACD < Signal)"
    else:
        macd_cross = "tidak tersedia"

    vol_str = f"{vol_ratio:.1f}x rata-rata" if vol_ratio is not None else "normal"

    # ── Label-specific reasoning ──────────────────────────────────────────
    if label == "Buy the Dip":
        strategy = "Pertimbangkan akumulasi bertahap di area support."
        bb_note  = "mendekati batas bawah Bollinger Band" if (bb_pos is not None and bb_pos < 0.35) else "di area support teknikal"
        reasoning = (
            f"Saham ini berada di zona {rsi_str} yang mengindikasikan tekanan jual berlebihan, "
            f"dan posisi harga {bb_note} — sinyal potensi technical bounce. "
            f"Sinyal MACD saat ini {macd_cross}. "
            f"Volume perdagangan {vol_str}. "
            f"Strategi: akumulasi bertahap dengan manajemen risiko ketat (stop-loss di bawah support).{macro_suffix}"
        )

    elif label == "Trending / Momentum":
        if ema20 is not None and ema50 is not None:
            above_ema = "harga berada di atas EMA20 dan EMA50"
        elif ema20 is not None:
            above_ema = "harga berada di atas EMA20"
        else:
            above_ema = "saham dalam tren naik"
        strategy  = "Ikuti tren — pertahankan posisi dengan trailing stop."
        reasoning = (
            f"Saham menunjukkan momentum bullish kuat: {above_ema}, "
            f"MACD {macd_cross}, dan {rsi_str} masih dalam zona sehat. "
            f"Volume perdagangan {vol_str} mengkonfirmasi tren ini. "
            f"Strategi: pertahankan posisi dengan trailing stop untuk proteksi profit.{macro_suffix}"
        )

    elif label == "Hold / Sideways":
        strategy  = "Tahan posisi — tunggu konfirmasi arah sebelum menambah."
        reasoning = (
            f"Saham bergerak sideways dengan {rsi_str} di zona netral. "
            f"MACD {macd_cross} tanpa sinyal kuat. "
            f"Bollinger Band menyempit mengindikasikan volatilitas rendah — "
            f"potensi breakout di depan. Volume perdagangan {vol_str}. "
            f"Tunggu konfirmasi arah yang jelas sebelum menambah posisi.{macro_suffix}"
        )

    else:  # High Risk / Avoid
        strategy  = "Hindari atau kurangi eksposur — risiko tinggi."
        reasoning = (
            f"Saham menunjukkan sinyal risiko tinggi: {rsi_str} berada di zona ekstrem, "
            f"volatilitas di atas rata-rata (Bollinger Band melebar), "
            f"MACD {macd_cross}, dan volume {vol_str}. "
            f"Hindari entry baru hingga kondisi teknikal dan volume kembali stabil.{macro_suffix}"
        )

    return strategy, reasoning


def calculate_risk_management(
    label: str, 
    price: float, 
    atr: Optional[float]
) -> dict:
    """
    Calculate TP/SL levels with 1:2 Risk/Reward ratio and recommend trading style.
    
    Logic:
      - SL distance = 2.0 * ATR (volatility buffer)
      - TP distance = 2.0 * SL distance (1:2 ratio)
      - If ATR is missing, fallback to % based (3% SL, 6% TP)
    """
    # ── 1. Recommended Style ──────────────────────────────────────────────
    style_map = {
        "Trending / Momentum": "Swing / Day Trade",
        "Buy the Dip":          "Swing / Investasi",
        "Hold / Sideways":      "Wait & See / Swing",
        "High Risk / Avoid":    "Avoid / Scalping",
    }
    style = style_map.get(label, "Swing Trade")

    # ── 2. TP / SL (1:2 Ratio) ────────────────────────────────────────────
    if atr and price > 0:
        sl_dist = atr * 2.0
        # Guard: SL shouldn't be more than 15% for normal stocks
        max_sl = price * 0.15
        if sl_dist > max_sl:
            sl_dist = max_sl
            
        tp_dist = sl_dist * 2.0
        
        sl = price - sl_dist
        tp = price + tp_dist
    else:
        # Fallback to fixed percentages
        sl = price * 0.97
        tp = price * 1.06

    return {
        "trading_style": style,
        "stop_loss":     round(float(sl), 2),
        "take_profit":   round(float(tp), 2),
    }


def get_buy_hold_sell_signal(
    label: str,
    confidence_score: float,
) -> dict:
    """
    Convert cluster label + XGBoost confidence to Buy/Hold/Sell signal.
    
    Args:
        label: Cluster label ("Buy the Dip", "Trending / Momentum", etc)
        confidence_score: XGBoost probability (0.0-1.0)
    
    Returns:
        {
            "signal": "STRONG BUY" | "BUY" | "HOLD" | "SELL" | "STRONG SELL",
            "base_signal": "BUY" | "HOLD" | "SELL",
            "strength": "STRONG" | "MODERATE" | "WEAK",
            "confidence": float (0.0-1.0),
            "recommendation": str (human-readable)
        }
    """
    # ── 1. Base signal dari label ──────────────────────────────────────────
    if label in ["Buy the Dip", "Trending / Momentum"]:
        base_signal = "BUY"
    elif label == "Hold / Sideways":
        base_signal = "HOLD"
    else:  # High Risk / Avoid
        base_signal = "SELL"
    
    # ── 2. Strength dari XGBoost confidence ────────────────────────────────
    if confidence_score > 0.75:
        strength = "STRONG"
    elif confidence_score > 0.60:
        strength = "MODERATE"
    else:
        strength = "WEAK"
    
    # ── 3. Combine base signal + strength ──────────────────────────────────
    if strength == "STRONG":
        final_signal = f"STRONG {base_signal}"
    elif strength == "WEAK":
        # Downgrade weak signals
        if base_signal == "SELL":
            final_signal = "HOLD"  # Weak sell → hold
        elif base_signal == "BUY":
            final_signal = "HOLD"  # Weak buy → hold
        else:
            final_signal = "HOLD"
    else:  # MODERATE
        final_signal = base_signal
    
    # ── 4. Recommendation text ─────────────────────────────────────────────
    confidence_pct = round(confidence_score * 100)
    
    if final_signal == "STRONG BUY":
        recommendation = f"🟢 STRONG BUY - Confidence {confidence_pct}% | Akumulasi dengan posisi penuh"
    elif final_signal == "BUY":
        recommendation = f"🟢 BUY - Confidence {confidence_pct}% | Pertimbangkan entry bertahap"
    elif final_signal == "HOLD":
        recommendation = f"🟡 HOLD - Confidence {confidence_pct}% | Tunggu konfirmasi atau entry point lebih baik"
    elif final_signal == "SELL":
        recommendation = f"🔴 SELL - Confidence {confidence_pct}% | Pertimbangkan exit atau reduce posisi"
    else:  # STRONG SELL
        recommendation = f"🔴 STRONG SELL - Confidence {confidence_pct}% | Exit posisi atau hindari entry"
    
    return {
        "signal": final_signal,
        "base_signal": base_signal,
        "strength": strength,
        "confidence": round(confidence_score, 3),
        "recommendation": recommendation,
    }
