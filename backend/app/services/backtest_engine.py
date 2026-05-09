"""
backtest_engine.py — Historical win rate simulation for the cluster strategy.

For each stock, we walk through 6 months of data and simulate:
  - Entry at current price
  - TP at Fib 0.618 of next 20-period high
  - SL at Entry - 2x ATR
Track whether TP is hit before SL for each "signal" and calculate a win rate.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


def run_backtest(df: pd.DataFrame, atr_multiplier: float = 2.0) -> dict:
    """
    Walk-forward backtest on OHLCV data.

    Returns:
        {
          "total_trades": int,
          "winning_trades": int,
          "win_rate": float (0–1),
          "avg_rr_achieved": float,
          "max_drawdown_pct": float,
          "best_trade_pct": float,
          "worst_trade_pct": float,
        }
    """
    if df is None or len(df) < 40:
        return _empty_backtest()

    try:
        closes = df["Close"].values
        highs  = df["High"].values
        lows   = df["Low"].values

        # Compute rolling ATR (14-period)
        tr_list = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i]  - closes[i - 1]),
            )
            tr_list.append(tr)
        tr_arr = np.array([tr_list[0]] + tr_list)
        atr_arr = _rolling_mean(tr_arr, 14)

        total_trades   = 0
        winning_trades = 0
        rr_list        = []
        trade_pcts     = []

        # Step through every 5th bar (weekly cadence) to simulate entries
        lookback = 20
        step     = 5

        for i in range(lookback, len(closes) - lookback, step):
            # Swing levels for Fibonacci from past 20 bars
            swing_high = np.max(highs[i - lookback : i])
            swing_low  = np.min(lows[i  - lookback : i])
            diff       = swing_high - swing_low
            if diff <= 0:
                continue

            entry = closes[i]
            atr   = atr_arr[i] if atr_arr[i] > 0 else entry * 0.02

            sl  = entry - atr_multiplier * atr
            tp1 = swing_low + 0.618 * diff

            # Skip if TP1 is below entry (makes no sense as buy signal)
            if tp1 <= entry:
                tp1 = entry + 0.618 * diff

            risk   = entry - sl
            reward = tp1 - entry
            if risk <= 0:
                continue

            target_rr = reward / risk

            # Simulate forward for next 20 bars
            win = False
            exit_price = entry
            for j in range(i + 1, min(i + lookback + 1, len(closes))):
                if lows[j] <= sl:
                    exit_price = sl
                    break
                if highs[j] >= tp1:
                    exit_price = tp1
                    win = True
                    break
            else:
                exit_price = closes[min(i + lookback, len(closes) - 1)]
                win = exit_price > entry

            pct_change = (exit_price - entry) / entry * 100
            achieved_rr = (exit_price - entry) / risk if risk > 0 else 0

            total_trades   += 1
            winning_trades += 1 if win else 0
            rr_list.append(achieved_rr)
            trade_pcts.append(pct_change)

        if total_trades == 0:
            return _empty_backtest()

        win_rate     = winning_trades / total_trades
        avg_rr       = float(np.mean(rr_list))
        max_drawdown = float(np.min(trade_pcts)) if trade_pcts else 0.0
        best_trade   = float(np.max(trade_pcts)) if trade_pcts else 0.0
        worst_trade  = float(np.min(trade_pcts)) if trade_pcts else 0.0

        return {
            "total_trades":     total_trades,
            "winning_trades":   winning_trades,
            "win_rate":         round(win_rate, 3),
            "avg_rr_achieved":  round(avg_rr, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "best_trade_pct":   round(best_trade, 2),
            "worst_trade_pct":  round(worst_trade, 2),
        }

    except Exception as exc:
        logger.error("Backtest failed: %s", exc, exc_info=True)
        return _empty_backtest()


def _rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    result = np.zeros_like(arr, dtype=float)
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        result[i] = np.mean(arr[start : i + 1])
    return result


def _empty_backtest() -> dict:
    return {
        "total_trades":     0,
        "winning_trades":   0,
        "win_rate":         0.0,
        "avg_rr_achieved":  0.0,
        "max_drawdown_pct": 0.0,
        "best_trade_pct":   0.0,
        "worst_trade_pct":  0.0,
    }
