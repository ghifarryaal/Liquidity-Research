"""
feature_engineering.py — Technical indicator calculation pipeline.

Indicators computed:
- RSI (14)
- MACD (12, 26, 9)
- EMA (20, 50)
- Bollinger Bands (20, 2σ)
- ATR (14)
- Volume Ratio (current / 20-day avg)

All values are calculated using the `ta` library for correctness and speed.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core feature engineering
# ---------------------------------------------------------------------------


def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Compute all technical indicators for a single ticker's OHLCV DataFrame.

    Returns:
        dict with latest values for all indicators,
        plus a 'feature_vector' key for clustering.
    """
    if df is None or len(df) < 30:
        return {}

    close  = df["Close"].astype(float)
    high   = df["High"].astype(float)
    low    = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    try:
        # ── RSI ────────────────────────────────────────────────────────────
        rsi_series = RSIIndicator(close=close, window=14).rsi()

        # ── MACD ───────────────────────────────────────────────────────────
        macd_ind    = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        macd_line   = macd_ind.macd()
        macd_signal = macd_ind.macd_signal()
        macd_hist   = macd_ind.macd_diff()

        # ── EMA ────────────────────────────────────────────────────────────
        ema20 = EMAIndicator(close=close, window=20).ema_indicator()
        ema50 = EMAIndicator(close=close, window=50).ema_indicator()

        # ── Bollinger Bands ────────────────────────────────────────────────
        bb_ind    = BollingerBands(close=close, window=20, window_dev=2)
        bb_upper  = bb_ind.bollinger_hband()
        bb_middle = bb_ind.bollinger_mavg()
        bb_lower  = bb_ind.bollinger_lband()
        bb_width  = bb_ind.bollinger_wband()  # % width

        # ── ATR ────────────────────────────────────────────────────────────
        atr = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

        # ── Volume Ratio ────────────────────────────────────────────────────
        vol_avg_20   = volume.rolling(20).mean()
        volume_ratio = (volume / vol_avg_20).replace([np.inf, -np.inf], np.nan)

        # ── Latest scalar values ────────────────────────────────────────────
        latest_close        = _safe_float(close.iloc[-1])
        latest_rsi          = _safe_float(rsi_series.iloc[-1])
        latest_macd         = _safe_float(macd_line.iloc[-1])
        latest_macd_signal  = _safe_float(macd_signal.iloc[-1])
        latest_macd_hist    = _safe_float(macd_hist.iloc[-1])
        latest_ema20        = _safe_float(ema20.iloc[-1])
        latest_ema50        = _safe_float(ema50.iloc[-1])
        latest_bb_upper     = _safe_float(bb_upper.iloc[-1])
        latest_bb_middle    = _safe_float(bb_middle.iloc[-1])
        latest_bb_lower     = _safe_float(bb_lower.iloc[-1])
        latest_bb_width     = _safe_float(bb_width.iloc[-1])
        latest_atr          = _safe_float(atr.iloc[-1])
        latest_vol_ratio    = _safe_float(volume_ratio.iloc[-1])

        if latest_close is None:
            return {}

        # ── Derived / normalised features for clustering ────────────────────
        bb_position  = _bb_position(latest_close, latest_bb_upper, latest_bb_lower)
        ema20_gap    = _pct_gap(latest_close, latest_ema20)
        ema50_gap    = _pct_gap(latest_close, latest_ema50)

        # FIX: use explicit None check so 0.0 MACD values are preserved
        if latest_macd is not None and latest_macd_signal is not None:
            macd_strength = latest_macd - latest_macd_signal
        else:
            macd_strength = 0.0

        # ── ATR % of price ──────────────────────────────────────────────────
        if latest_atr is not None and latest_close and latest_close > 0:
            atr_pct = (latest_atr / latest_close) * 100
        else:
            atr_pct = 0.0

        # ── Feature vector for K-Means ──────────────────────────────────────
        # FIX: use explicit None coalesce instead of `or` to preserve 0.0
        feature_vector = [
            latest_rsi       if latest_rsi is not None       else 50.0,
            macd_strength,
            ema20_gap        if ema20_gap is not None         else 0.0,
            ema50_gap        if ema50_gap is not None         else 0.0,
            bb_position,
            latest_bb_width  if latest_bb_width is not None  else 0.0,
            latest_vol_ratio if latest_vol_ratio is not None else 1.0,
            atr_pct,
        ]

        # Guard: if any feature is still NaN, zero it out rather than poisoning the matrix
        feature_vector = [0.0 if (v is None or np.isnan(v)) else float(v)
                          for v in feature_vector]

        # ── Chart series (last N bars) ────────────────────────────────────
        def _to_series(s: pd.Series) -> list[dict]:
            out = []
            for idx, v in s.dropna().items():
                # Handle both tz-aware and tz-naive DatetimeIndex
                try:
                    date_str = str(idx.date())
                except AttributeError:
                    date_str = str(idx)[:10]
                out.append({"time": date_str, "value": round(float(v), 4)})
            return out

        return {
            # Latest scalar values
            "rsi":           latest_rsi,
            "macd":          latest_macd,
            "macd_signal":   latest_macd_signal,
            "macd_hist":     latest_macd_hist,
            "ema_20":        latest_ema20,
            "ema_50":        latest_ema50,
            "bb_upper":      latest_bb_upper,
            "bb_middle":     latest_bb_middle,
            "bb_lower":      latest_bb_lower,
            "bb_width":      latest_bb_width,
            "atr":           latest_atr,
            "volume_ratio":  latest_vol_ratio,
            # Derived metrics
            "bb_position":   bb_position,
            "ema20_gap_pct": ema20_gap,
            "ema50_gap_pct": ema50_gap,
            "macd_strength": macd_strength,
            # Feature vector for K-Means (order must match clustering_engine)
            "feature_vector": feature_vector,
            # Chart series (for /stock/{ticker} endpoint)
            "series": {
                "ema_20":    _to_series(ema20),
                "ema_50":    _to_series(ema50),
                "bb_upper":  _to_series(bb_upper),
                "bb_middle": _to_series(bb_middle),
                "bb_lower":  _to_series(bb_lower),
            },
        }

    except Exception as exc:
        logger.error("Feature engineering failed: %s", exc, exc_info=True)
        return {}


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------


def compute_all_indicators(
    ohlcv_map: dict[str, pd.DataFrame]
) -> dict[str, dict]:
    """Process all tickers in the index batch."""
    results: dict[str, dict] = {}
    for ticker, df in ohlcv_map.items():
        ind = compute_indicators(df)
        if ind:
            results[ticker] = ind
        else:
            logger.warning("Skipping %s — insufficient indicator data", ticker)
    return results


def build_feature_matrix(
    indicator_map: dict[str, dict]
) -> tuple[list[str], np.ndarray]:
    """
    Build a 2D numpy feature matrix from indicator results.

    Returns:
        (tickers, matrix) where matrix.shape = (n_tickers, n_features)
    """
    tickers = []
    vectors = []
    for ticker, ind in indicator_map.items():
        fv = ind.get("feature_vector")
        if fv and len(fv) == 8:
            # FIX: convert to float first, then check for NaN
            arr = [float(x) for x in fv]
            if not any(np.isnan(x) or np.isinf(x) for x in arr):
                tickers.append(ticker)
                vectors.append(arr)

    if not vectors:
        return [], np.array([])

    return tickers, np.array(vectors, dtype=float)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_float(val) -> Optional[float]:
    try:
        f = float(val)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 4)
    except (TypeError, ValueError):
        return None


def _bb_position(price: float, upper: Optional[float], lower: Optional[float]) -> float:
    """Returns 0.0 (at lower band) to 1.0 (at upper band)."""
    if upper is None or lower is None or upper == lower:
        return 0.5
    return float(np.clip((price - lower) / (upper - lower), 0.0, 1.0))


def _pct_gap(price: float, ema: Optional[float]) -> float:
    """% distance of price from EMA. Positive = price above EMA."""
    # FIX: check `is None` instead of `not ema` so ema=0.0 doesn't return 0.0
    if ema is None or ema == 0.0:
        return 0.0
    return round((price - ema) / ema * 100, 4)


# ---------------------------------------------------------------------------
# Enhanced Feature Engineering (4D feature vector for advanced K-Means)
# ---------------------------------------------------------------------------


def compute_enhanced_features(df: pd.DataFrame) -> dict:
    """
    Compute 4-dimension feature vector for advanced K-Means clustering.

    Features:
        - log_returns:    ln(Pt / Pt-1), latest value
        - volatility:     20-day rolling std of pct_change, latest value (winsorized)
        - rsi_relative:   RSI(14) / 100, clipped to [0, 1]
        - volume_impact:  Volume / MA(Volume, 20), clipped to [0, 10]

    Args:
        df: OHLCV DataFrame with DatetimeIndex. Expected columns:
            Close, Volume (case-sensitive).

    Returns:
        dict with keys: log_returns, volatility, rsi_relative,
        volume_impact, feature_vector (list of 4 floats).
        Returns neutral values on failure rather than raising.
    """
    # Neutral / safe defaults
    NEUTRAL = {
        "log_returns": 0.0,
        "volatility": 0.0,
        "rsi_relative": 0.5,
        "volume_impact": 1.0,
        "feature_vector": [0.0, 0.0, 0.5, 1.0],
    }

    if df is None or len(df) < 21:
        return NEUTRAL.copy()

    try:
        # ── Prepare series ──────────────────────────────────────────────────
        close  = df["Close"].astype(float).ffill().dropna()
        volume = df["Volume"].astype(float).ffill().dropna()

        if len(close) < 21 or len(volume) < 21:
            return NEUTRAL.copy()

        # ── Log Returns ─────────────────────────────────────────────────────
        log_ret_series = np.log(close / close.shift(1))
        log_returns_raw = log_ret_series.iloc[-1]
        log_returns = _safe_enhanced_float(log_returns_raw, neutral=0.0)

        # ── Volatility (20-day rolling std of pct_change) ───────────────────
        pct_returns = close.pct_change()
        vol_series  = pct_returns.rolling(20).std()
        vol_raw     = vol_series.iloc[-1]
        volatility  = _safe_enhanced_float(vol_raw, neutral=0.0)

        # Winsorization: clip to 99th percentile when Z-score > 3
        vol_values = vol_series.dropna()
        if len(vol_values) >= 2:
            vol_mean = float(vol_values.mean())
            vol_std  = float(vol_values.std())
            if vol_std > 0:
                z_score = abs((volatility - vol_mean) / vol_std)
                if z_score > 3:
                    p99 = float(np.percentile(vol_values, 99))
                    volatility = min(volatility, p99)

        # ── RSI Relative ────────────────────────────────────────────────────
        rsi_series   = RSIIndicator(close=close, window=14).rsi()
        rsi_raw      = rsi_series.iloc[-1]
        rsi_relative = _safe_enhanced_float(rsi_raw, neutral=50.0)
        rsi_relative = float(np.clip(rsi_relative / 100.0, 0.0, 1.0))

        # ── Volume Impact ───────────────────────────────────────────────────
        vol_ma_series  = volume.rolling(20).mean()
        vol_impact_raw = (volume / vol_ma_series).iloc[-1]
        volume_impact  = _safe_enhanced_float(vol_impact_raw, neutral=1.0)
        volume_impact  = float(np.clip(volume_impact, 0.0, 10.0))

        # ── Final NaN/Inf guard ─────────────────────────────────────────────
        log_returns   = _safe_enhanced_float(log_returns,   neutral=0.0)
        volatility    = _safe_enhanced_float(volatility,    neutral=0.0)
        rsi_relative  = _safe_enhanced_float(rsi_relative,  neutral=0.5)
        volume_impact = _safe_enhanced_float(volume_impact, neutral=1.0)

        feature_vector = [log_returns, volatility, rsi_relative, volume_impact]

        return {
            "log_returns":    log_returns,
            "volatility":     volatility,
            "rsi_relative":   rsi_relative,
            "volume_impact":  volume_impact,
            "feature_vector": feature_vector,
        }

    except Exception as exc:
        logger.error("compute_enhanced_features failed: %s", exc, exc_info=True)
        return NEUTRAL.copy()


def compute_enhanced_features_batch(ohlcv_map: dict) -> dict:
    """
    Compute enhanced 4D features for a batch of tickers.

    Args:
        ohlcv_map: dict mapping ticker -> OHLCV DataFrame

    Returns:
        dict mapping ticker -> enhanced feature dict (same shape as
        compute_enhanced_features). Tickers with insufficient data are
        omitted from the result.
    """
    results: dict[str, dict] = {}
    for ticker, df in ohlcv_map.items():
        features = compute_enhanced_features(df)
        # Only include tickers that produced a valid (non-neutral-fallback) result.
        # We detect a valid result by checking that the feature_vector is present
        # and has exactly 4 elements.
        if features and len(features.get("feature_vector", [])) == 4:
            results[ticker] = features
        else:
            logger.warning(
                "compute_enhanced_features_batch: skipping %s — insufficient data",
                ticker,
            )
    return results


def build_enhanced_feature_matrix(
    indicator_map: dict,
) -> tuple[list[str], np.ndarray]:
    """
    Build a 2D numpy feature matrix from enhanced indicator results.

    Args:
        indicator_map: dict mapping ticker -> dict returned by
            compute_enhanced_features (or compute_enhanced_features_batch).

    Returns:
        (tickers, matrix) where matrix.shape == (n_tickers, 4).
        Returns ([], np.array([])) when no valid tickers are found.
    """
    tickers: list[str] = []
    vectors: list[list[float]] = []

    for ticker, ind in indicator_map.items():
        fv = ind.get("feature_vector")
        if not fv or len(fv) != 4:
            logger.warning(
                "build_enhanced_feature_matrix: skipping %s — invalid feature_vector",
                ticker,
            )
            continue

        arr = [float(x) for x in fv]
        if any(np.isnan(x) or np.isinf(x) for x in arr):
            logger.warning(
                "build_enhanced_feature_matrix: skipping %s — NaN/Inf in feature_vector",
                ticker,
            )
            continue

        tickers.append(ticker)
        vectors.append(arr)

    if not vectors:
        return [], np.array([])

    return tickers, np.array(vectors, dtype=float)


# ---------------------------------------------------------------------------
# Enhanced helpers (private)
# ---------------------------------------------------------------------------


def _safe_enhanced_float(val, neutral: float = 0.0) -> float:
    """
    Convert *val* to float, returning *neutral* for NaN / Inf / None.
    Unlike _safe_float(), this always returns a float (never None).
    """
    try:
        f = float(val)
        return neutral if (np.isnan(f) or np.isinf(f)) else f
    except (TypeError, ValueError):
        return neutral
