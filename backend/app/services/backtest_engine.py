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


# ---------------------------------------------------------------------------
# Enhanced Backtest Engine — TradingSimulator + run_enhanced_backtest
# ---------------------------------------------------------------------------

from math import sqrt as _sqrt


class TradingSimulator:
    """Simulates trading based on cluster labels with stop-loss and trailing-stop risk management."""

    def __init__(self, initial_capital: float = 100_000_000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position: Optional[dict] = None  # dict or None
        self.trades: list = []
        self.equity_curve: list = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_buy(self, date: str, price: float, label: str):
        """Allocate 95% of capital to a long position."""
        if price <= 0:
            return
        shares = int(self.capital * 0.95 / price)
        if shares <= 0:
            return
        cost = shares * price
        self.capital -= cost
        self.position = {
            "entry_date": date,
            "entry_price": price,
            "entry_label": label,
            "shares": shares,
            "stop_loss": price * 0.97,
            "trailing_stop": None,   # activated after 5% profit
            "highest_price": price,
        }

    def _check_stop_loss(self, price: float) -> bool:
        """Returns True if price <= position stop_loss."""
        if self.position is None:
            return False
        return price <= self.position["stop_loss"]

    def _check_trailing_stop(self, price: float) -> bool:
        """Returns True if trailing stop is set and price <= trailing_stop."""
        if self.position is None:
            return False
        ts = self.position.get("trailing_stop")
        if ts is None:
            return False
        return price <= ts

    def _update_trailing_stop(self, price: float):
        """Activate trailing stop after 5% profit; update on each new high."""
        if self.position is None:
            return
        entry = self.position["entry_price"]
        # Activate when price exceeds entry by 5%
        if price > entry * 1.05:
            if price > self.position["highest_price"]:
                self.position["highest_price"] = price
                self.position["trailing_stop"] = price * 0.95

    def _execute_sell(self, date: str, price: float, reason: str):
        """Close the open position, record the trade, and return capital."""
        if self.position is None:
            return
        pos = self.position
        entry_price = pos["entry_price"]
        shares = pos["shares"]
        proceeds = shares * price
        self.capital += proceeds

        pnl_abs = proceeds - (shares * entry_price)
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0.0

        # Calculate holding days
        try:
            entry_dt = pd.Timestamp(pos["entry_date"])
            exit_dt = pd.Timestamp(date)
            holding_days = max(0, (exit_dt - entry_dt).days)
        except Exception:
            holding_days = 0

        trade_record = {
            "entry_date": pos["entry_date"],
            "entry_price": float(entry_price),
            "entry_label": pos["entry_label"],
            "exit_date": date,
            "exit_price": float(price),
            "exit_label": "",          # filled by caller if needed
            "shares": shares,
            "pnl": float(pnl_abs),
            "pnl_pct": float(pnl_pct),
            "holding_days": holding_days,
            "exit_reason": reason,
            "stop_loss_triggered": reason == "stop_loss",
            "trailing_stop_triggered": reason == "trailing_stop",
        }
        self.trades.append(trade_record)
        self.position = None

    def _calculate_equity(self, price: float) -> float:
        """Returns current equity: capital + market value of open position."""
        if self.position is None:
            return self.capital
        return self.capital + self.position["shares"] * price

    # ------------------------------------------------------------------
    # Main day-processing loop
    # ------------------------------------------------------------------

    # Buy signals
    _BUY_LABELS = frozenset([
        "Beli Saat Turun",
        "Momentum",
        "Buy the Dip",
        "Trending / Momentum",
    ])

    # Sell signals
    _SELL_LABELS = frozenset([
        "High Risk",
        "Konsolidasi",
        "High Risk / Avoid",
        "Hold / Sideways",
    ])

    def process_day(self, date: str, price: float, label: str):
        """Process a single trading day."""
        if price <= 0:
            self.equity_curve.append({
                "date": date,
                "equity": self._calculate_equity(price),
                "position": bool(self.position),
            })
            return

        # 1. Check stop loss first
        if self.position and self._check_stop_loss(price):
            self._execute_sell(date, price, reason="stop_loss")

        # 2. Check trailing stop
        elif self.position and self._check_trailing_stop(price):
            self._execute_sell(date, price, reason="trailing_stop")

        else:
            # 3. Update trailing stop (only if still in position)
            if self.position:
                self._update_trailing_stop(price)

            # 4. Buy signal — only if no open position
            if label in self._BUY_LABELS and self.position is None:
                self._execute_buy(date, price, label)

            # 5. Sell signal — only if position is open
            elif label in self._SELL_LABELS and self.position is not None:
                self._execute_sell(date, price, reason="signal")

        # 6. Record equity
        self.equity_curve.append({
            "date": date,
            "equity": self._calculate_equity(price),
            "position": bool(self.position),
        })

    def close_position(self, date: str, price: float):
        """Close any open position at end of backtest period."""
        if self.position is not None:
            self._execute_sell(date, price, reason="end_of_period")

    def get_performance_metrics(self) -> dict:
        """Delegate to standalone calculate_performance_metrics."""
        return calculate_performance_metrics(self.trades, self.equity_curve)


# ---------------------------------------------------------------------------
# Standalone performance metrics helper
# ---------------------------------------------------------------------------

def calculate_performance_metrics(trades: list, equity_curve: list) -> dict:
    """
    Calculate comprehensive performance metrics from trades and equity curve.

    Args:
        trades: List of trade record dicts.
        equity_curve: List of {date, equity, position} dicts.

    Returns:
        {cumulative_returns, sharpe_ratio, maximum_drawdown, win_rate}
    """
    if not equity_curve:
        return {
            "cumulative_returns": 0.0,
            "sharpe_ratio": 0.0,
            "maximum_drawdown": 0.0,
            "win_rate": 0.0,
        }

    initial_equity = equity_curve[0]["equity"]
    final_equity = equity_curve[-1]["equity"]

    # 1. Cumulative returns
    cumulative_returns = (
        (final_equity - initial_equity) / initial_equity
        if initial_equity > 0
        else 0.0
    )

    # 2. Sharpe ratio (annualised, risk-free = 0)
    daily_returns = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i - 1]["equity"]
        curr = equity_curve[i]["equity"]
        if prev > 0:
            daily_returns.append((curr - prev) / prev)

    if len(daily_returns) > 1:
        arr = np.array(daily_returns, dtype=float)
        mean_ret = float(np.mean(arr))
        std_ret = float(np.std(arr, ddof=1))
        sharpe_ratio = (mean_ret / std_ret) * _sqrt(252) if std_ret > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    # 3. Maximum drawdown
    peak = equity_curve[0]["equity"]
    max_drawdown = 0.0
    for point in equity_curve:
        eq = point["equity"]
        if eq > peak:
            peak = eq
        if peak > 0:
            drawdown = (peak - eq) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

    # 4. Win rate
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

    return {
        "cumulative_returns": round(cumulative_returns, 4),
        "sharpe_ratio": round(sharpe_ratio, 3),
        "maximum_drawdown": round(max_drawdown, 4),
        "win_rate": round(win_rate, 3),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_enhanced_backtest(
    df: pd.DataFrame,
    cluster_labels_timeline: dict,
    initial_capital: float = 100_000_000.0,
) -> dict:
    """
    Run a comprehensive cluster-signal-driven backtest with risk management.

    Args:
        df: OHLCV DataFrame with DatetimeIndex (at least 40 rows required).
        cluster_labels_timeline: Mapping of date string (YYYY-MM-DD) -> cluster label.
        initial_capital: Starting capital in IDR.

    Returns:
        dict with ticker, start_date, end_date, initial_capital, final_equity,
        cumulative_returns, sharpe_ratio, maximum_drawdown, total_trades,
        winning_trades, win_rate, trades, equity_curve.
    """
    _empty = {
        "ticker": "",
        "start_date": "",
        "end_date": "",
        "initial_capital": initial_capital,
        "final_equity": initial_capital,
        "cumulative_returns": 0.0,
        "sharpe_ratio": 0.0,
        "maximum_drawdown": 0.0,
        "total_trades": 0,
        "winning_trades": 0,
        "win_rate": 0.0,
        "trades": [],
        "equity_curve": [],
    }

    if df is None or len(df) < 40:
        return _empty

    try:
        simulator = TradingSimulator(initial_capital=initial_capital)

        start_date = str(df.index[0].date()) if hasattr(df.index[0], "date") else str(df.index[0])
        end_date = str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1])

        for ts, row in df.iterrows():
            try:
                date_str = str(ts.date()) if hasattr(ts, "date") else str(ts)
            except Exception:
                date_str = str(ts)

            price = float(row.get("Close", row.get("close", 0)))
            label = cluster_labels_timeline.get(date_str, "")

            simulator.process_day(date_str, price, label)

        # Close any open position at end of period
        if simulator.position is not None:
            last_ts = df.index[-1]
            last_date = str(last_ts.date()) if hasattr(last_ts, "date") else str(last_ts)
            last_price = float(df.iloc[-1].get("Close", df.iloc[-1].get("close", 0)))
            simulator.close_position(last_date, last_price)

        metrics = calculate_performance_metrics(simulator.trades, simulator.equity_curve)
        winning_trades = sum(1 for t in simulator.trades if t.get("pnl", 0) > 0)
        final_equity = simulator.equity_curve[-1]["equity"] if simulator.equity_curve else initial_capital

        return {
            "ticker": "",
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "final_equity": final_equity,
            "cumulative_returns": metrics["cumulative_returns"],
            "sharpe_ratio": metrics["sharpe_ratio"],
            "maximum_drawdown": metrics["maximum_drawdown"],
            "total_trades": len(simulator.trades),
            "winning_trades": winning_trades,
            "win_rate": metrics["win_rate"],
            "trades": simulator.trades,
            "equity_curve": simulator.equity_curve,
        }

    except Exception as exc:
        logger.error("Enhanced backtest failed: %s", exc, exc_info=True)
        return _empty
