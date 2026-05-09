"""
supervised_model.py — Supervised Learning Predictor for LiquidityResearch.

Pipeline:
  1. Historical Labeling  : A trade is "Success" (1) if price hits +5% within 5 trading days.
  2. Feature Vector       : RSI, MACD, Volume Ratio, EMA Cross, + DXY, US10Y macro features.
  3. Classifier           : XGBoost (primary) or Random Forest (fallback).
  4. Output               : Confidence_Score (0.0–1.0) = P(success).
  5. Validation           : 30-day walk-forward comparison of predicted vs actual outcomes.

Macro features are injected per-stock at inference time using the latest DXY/US10Y values
fetched via yfinance in macro_weighting.py.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature names (must match order in build_supervised_features())
# ---------------------------------------------------------------------------

FEATURE_NAMES = [
    "rsi",
    "macd_strength",
    "ema20_gap_pct",
    "ema50_gap_pct",
    "bb_position",
    "bb_width",
    "volume_ratio",
    "atr_pct",
    "dxy_zscore",      # macro: DXY z-score vs 30-day mean
    "us10y_zscore",    # macro: US10Y z-score vs 30-day mean
]

N_FEATURES = len(FEATURE_NAMES)

# ---------------------------------------------------------------------------
# Labeling
# ---------------------------------------------------------------------------


def label_historical_trades(
    df: pd.DataFrame,
    target_pct: float = 5.0,
    window_days: int = 5,
) -> pd.Series:
    """
    Binary labeling: 1 if price hits +target_pct within window_days, else 0.

    Args:
        df           : OHLCV DataFrame (index = date, columns include 'High', 'Close').
        target_pct   : Target gain % to constitute a "success".
        window_days  : Forward-looking window in trading days.

    Returns:
        pd.Series of {0, 1} labels aligned with df.index.
    """
    close = df["Close"].values
    high  = df["High"].values
    n     = len(close)
    labels = np.zeros(n, dtype=int)

    for i in range(n - window_days):
        entry   = close[i]
        if entry <= 0:
            continue
        target  = entry * (1.0 + target_pct / 100.0)
        # Check if any High in forward window hits target
        future_highs = high[i + 1 : i + 1 + window_days]
        labels[i] = int(np.any(future_highs >= target))

    # Last `window_days` rows are unlabeled (set to -1 = unknown)
    labels[-window_days:] = -1
    return pd.Series(labels, index=df.index, name="label")


# ---------------------------------------------------------------------------
# Feature vector builder (per-bar, for training)
# ---------------------------------------------------------------------------


def build_supervised_features(
    df: pd.DataFrame,
    dxy_zscore: float = 0.0,
    us10y_zscore: float = 0.0,
) -> pd.DataFrame:
    """
    Compute a full feature DataFrame aligned to df.index.

    Columns: FEATURE_NAMES (10 dimensions).

    Args:
        df           : OHLCV DataFrame (≥ 60 rows recommended).
        dxy_zscore   : Current DXY z-score (scalar, broadcast to all rows).
        us10y_zscore : Current US10Y z-score (scalar, broadcast to all rows).

    Returns:
        pd.DataFrame with columns = FEATURE_NAMES.
    """
    if df is None or len(df) < 30:
        return pd.DataFrame(columns=FEATURE_NAMES)

    try:
        close  = df["Close"].astype(float)
        high   = df["High"].astype(float)
        low    = df["Low"].astype(float)
        volume = df["Volume"].astype(float)

        rsi_s   = RSIIndicator(close=close, window=14).rsi()
        macd_i  = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        macd_s  = macd_i.macd() - macd_i.macd_signal()
        ema20   = EMAIndicator(close=close, window=20).ema_indicator()
        ema50   = EMAIndicator(close=close, window=50).ema_indicator()
        bb      = BollingerBands(close=close, window=20, window_dev=2)
        bb_pos  = ((close - bb.bollinger_lband()) /
                   (bb.bollinger_hband() - bb.bollinger_lband() + 1e-9)).clip(0, 1)
        bb_wid  = bb.bollinger_wband()
        atr_s   = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

        vol_avg = volume.rolling(20, min_periods=5).mean()
        vol_r   = (volume / vol_avg).replace([np.inf, -np.inf], np.nan)

        ema20_gap = ((close - ema20) / ema20 * 100).replace([np.inf, -np.inf], np.nan)
        ema50_gap = ((close - ema50) / ema50 * 100).replace([np.inf, -np.inf], np.nan)
        atr_pct   = (atr_s / close * 100).replace([np.inf, -np.inf], np.nan)

        feat_df = pd.DataFrame({
            "rsi":           rsi_s,
            "macd_strength": macd_s,
            "ema20_gap_pct": ema20_gap,
            "ema50_gap_pct": ema50_gap,
            "bb_position":   bb_pos,
            "bb_width":      bb_wid,
            "volume_ratio":  vol_r,
            "atr_pct":       atr_pct,
            "dxy_zscore":    dxy_zscore,    # scalar → broadcast
            "us10y_zscore":  us10y_zscore,  # scalar → broadcast
        }, index=df.index)

        return feat_df.fillna(0.0)

    except Exception as exc:
        logger.error("build_supervised_features failed: %s", exc, exc_info=True)
        return pd.DataFrame(columns=FEATURE_NAMES)


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------


def train_predictor(
    ohlcv_map: dict[str, pd.DataFrame],
    dxy_zscore: float = 0.0,
    us10y_zscore: float = 0.0,
):
    """
    Train an XGBoost (or RF fallback) classifier on historical data from all tickers.

    Returns:
        Trained sklearn-compatible classifier, or None on failure.
    """
    X_rows, y_rows = [], []

    for ticker, df in ohlcv_map.items():
        if df is None or len(df) < 60:
            continue

        labels  = label_historical_trades(df, target_pct=5.0, window_days=5)
        feat_df = build_supervised_features(df, dxy_zscore, us10y_zscore)

        # Align and drop unknowns
        combined = feat_df.join(labels, how="inner")
        combined = combined[combined["label"] >= 0].dropna()

        if len(combined) < 10:
            continue

        X_rows.append(combined[FEATURE_NAMES].values)
        y_rows.append(combined["label"].values)

    if not X_rows:
        logger.warning("[supervised] No training data available — model skipped.")
        return None

    X = np.vstack(X_rows).astype(float)
    y = np.concatenate(y_rows).astype(int)

    # Guard: need at least both classes
    unique = np.unique(y)
    if len(unique) < 2:
        logger.warning("[supervised] Only one class in training set — skipping model.")
        return None

    try:
        model = Pipeline([
            ("scaler", RobustScaler()),
            ("clf", xgb.XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1,
                verbosity=0,
            )),
        ])
        model.fit(X, y)
        logger.info("[supervised] XGBoost trained on %d samples, %d tickers.",
                    len(X), len(ohlcv_map))
        return model

    except ImportError:
        logger.warning("[supervised] XGBoost not installed — falling back to RandomForest.")

    try:
        model = Pipeline([
            ("scaler", RobustScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=300,
                max_depth=6,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            )),
        ])
        model.fit(X, y)
        logger.info("[supervised] RandomForest trained on %d samples, %d tickers.",
                    len(X), len(ohlcv_map))
        return model

    except Exception as exc:
        logger.error("[supervised] Model training failed: %s", exc, exc_info=True)
        return None


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------


def predict_confidence(
    model,
    indicator_map: dict[str, dict],
    dxy_zscore: float = 0.0,
    us10y_zscore: float = 0.0,
) -> dict[str, float]:
    """
    Run the trained model on the current indicator snapshot for each ticker.

    Returns:
        dict[ticker] -> confidence_score (0.0–1.0)
    """
    if model is None:
        return {}

    results: dict[str, float] = {}

    for ticker, ind in indicator_map.items():
        try:
            row = [
                ind.get("rsi")          or 50.0,
                ind.get("macd_strength") or 0.0,
                ind.get("ema20_gap_pct") or 0.0,
                ind.get("ema50_gap_pct") or 0.0,
                ind.get("bb_position")  or 0.5,
                ind.get("bb_width")     or 0.0,
                ind.get("volume_ratio") or 1.0,
                _atr_pct(ind),
                dxy_zscore,
                us10y_zscore,
            ]
            X = np.array(row, dtype=float).reshape(1, -1)

            # Replace NaN/Inf
            X = np.nan_to_num(X, nan=0.0, posinf=3.0, neginf=-3.0)

            proba = model.predict_proba(X)[0]
            # Class 1 = success
            classes = list(model.classes_) if hasattr(model, "classes_") else [0, 1]
            if 1 in classes:
                conf = float(proba[classes.index(1)])
            else:
                conf = float(proba[-1])

            results[ticker] = round(float(np.clip(conf, 0.0, 1.0)), 3)

        except Exception as exc:
            logger.warning("[supervised] Predict failed for %s: %s", ticker, exc)
            results[ticker] = 0.5

    return results


# ---------------------------------------------------------------------------
# 30-Day Backtest Validation
# ---------------------------------------------------------------------------


def validate_30day(
    model,
    ohlcv_map: dict[str, pd.DataFrame],
    dxy_zscore: float = 0.0,
    us10y_zscore: float = 0.0,
    lookback_days: int = 30,
) -> dict:
    """
    Walk-forward validation: compare predicted confidence against actual 5% hit
    outcomes for the past 30 calendar days.

    Returns:
        {
          "total_predictions": int,
          "correct_predictions": int,
          "accuracy": float,
          "high_conviction_precision": float,  # precision when conf > 0.75
          "avg_confidence": float,
          "details": list[dict]                # per-prediction detail
        }
    """
    if model is None:
        return _empty_validation()

    all_preds, all_actuals = [], []
    hc_preds, hc_actuals   = [], []
    details: list[dict]    = []

    for ticker, df in ohlcv_map.items():
        if df is None or len(df) < 60:
            continue

        # Use the last `lookback_days` bars as the validation window
        n    = len(df)
        val_start = max(30, n - lookback_days - 5)  # leave 5 forward bars
        val_end   = n - 5                            # need 5 forward bars for label

        feat_df = build_supervised_features(df, dxy_zscore, us10y_zscore)
        labels  = label_historical_trades(df, target_pct=5.0, window_days=5)

        for i in range(val_start, val_end):
            try:
                row = feat_df.iloc[i][FEATURE_NAMES].values.astype(float)
                row = np.nan_to_num(row, nan=0.0, posinf=3.0, neginf=-3.0)

                proba   = model.predict_proba(row.reshape(1, -1))[0]
                classes = list(model.classes_) if hasattr(model, "classes_") else [0, 1]
                conf    = float(proba[classes.index(1)]) if 1 in classes else float(proba[-1])
                actual  = int(labels.iloc[i])

                if actual < 0:
                    continue  # unknown label, skip

                predicted_success = conf >= 0.5
                correct = int(predicted_success == bool(actual))

                all_preds.append(predicted_success)
                all_actuals.append(actual)

                if conf > 0.75:
                    hc_preds.append(1)
                    hc_actuals.append(actual)

                details.append({
                    "ticker":     ticker,
                    "date":       str(df.index[i].date()),
                    "confidence": round(conf, 3),
                    "actual":     actual,
                    "correct":    correct,
                })

            except Exception:
                continue

    if not all_preds:
        return _empty_validation()

    accuracy = float(np.mean([int(p == a) for p, a in zip(all_preds, all_actuals)]))
    hc_prec  = (float(np.mean(hc_actuals)) if hc_actuals else 0.0)
    avg_conf = float(np.mean([d["confidence"] for d in details]))

    return {
        "total_predictions":       len(all_preds),
        "correct_predictions":     int(sum(int(p == a) for p, a in zip(all_preds, all_actuals))),
        "accuracy":                round(accuracy, 3),
        "high_conviction_precision": round(hc_prec, 3),
        "avg_confidence":          round(avg_conf, 3),
        "details":                 details[-50:],  # return at most 50 records
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _atr_pct(ind: dict) -> float:
    atr   = ind.get("atr")
    price = ind.get("ema_20")  # proxy for price if close not stored
    if atr and price and price > 0:
        return float(atr / price * 100)
    return 0.0


def _empty_validation() -> dict:
    return {
        "total_predictions":         0,
        "correct_predictions":       0,
        "accuracy":                  0.0,
        "high_conviction_precision": 0.0,
        "avg_confidence":            0.0,
        "details":                   [],
    }
