"""
trade_plan_engine.py — Dynamic Trade Plan calculation logic.
Calculates Fibonacci levels, ATR-based Stop Loss, and Capital Allocation.
"""

from __future__ import annotations
import logging
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def get_price_fraction(price: float) -> int:
    """
    Returns the IDX standard price fraction (tick size) based on the stock price.
    """
    if price < 200:
        return 1
    elif price < 500:
        return 2
    elif price < 2000:
        return 5
    elif price < 5000:
        return 10
    else:
        return 25

def round_to_fraction(price: float, fraction: int, direction: str = 'nearest') -> int:
    """
    Rounds a price to the nearest IDX fraction.
    direction: 'up', 'down', or 'nearest'
    """
    if fraction <= 0:
        return int(round(price))
        
    if direction == 'up':
        return int(np.ceil(price / fraction) * fraction)
    elif direction == 'down':
        return int(np.floor(price / fraction) * fraction)
    else:
        return int(round(price / fraction) * fraction)

def calculate_trade_plan(
    df: pd.DataFrame, 
    indicators: dict, 
    cluster_label: str,
    total_capital: float = 1_000_000.0,
    index_name: str = "lq45"
) -> dict:
    """
    Translates technical data into a structured trade plan with IDX fractions.
    """
    if df is None or df.empty or not indicators:
        return {}

    try:
        latest = df.iloc[-1]
        price = float(latest["Close"])
        fraction = get_price_fraction(price)
        
        # ── 1. Fibonacci Logic (20-period Swing) ──────────────────────────
        lookback = df.iloc[-20:]
        swing_high = float(lookback["High"].max())
        swing_low = float(lookback["Low"].min())
        diff = swing_high - swing_low
        
        if diff <= 0:
            diff = price * 0.05 # Default 5% range fallback
            swing_high = price + diff
            swing_low = price - diff

        # Default TP calculations
        tp1_raw = swing_low + (0.618 * diff)
        tp2_raw = swing_low + (1.0 * diff)
        
        # If price is already above swing high, adjust Fibonacci for extension
        if price > swing_high:
            tp1_raw = swing_high + (0.618 * (price - swing_low))
            tp2_raw = swing_high + (1.0 * (price - swing_low))

        # ── 2. Volatility-Based Stop Loss (ATR) ───────────────────────────
        atr = indicators.get("atr")
        
        # DBX Rule: 2.5x to 3x ATR, RR 1:3
        is_dbx = index_name.lower() == "dbx"
        atr_multiplier = 2.5 if is_dbx else 2.0
        
        if atr and atr > 0:
            sl_raw = price - (atr_multiplier * atr)
        else:
            sl_raw = price * 0.95 # Fallback 5%
            
        # Round Entry/SL/TP to valid IDX fractions
        entry_price = round_to_fraction(price, fraction)
        sl = round_to_fraction(sl_raw, fraction, direction='down')
        
        # Risk calculation for RR logic
        risk = entry_price - sl
        if risk <= 0: risk = entry_price * 0.01
        
        if is_dbx:
            # Forced RR 1:3 for DBX
            tp1 = round_to_fraction(entry_price + (3.0 * risk), fraction, direction='up')
            tp2 = round_to_fraction(entry_price + (5.0 * risk), fraction, direction='up')
        else:
            tp1 = round_to_fraction(tp1_raw, fraction, direction='up')
            tp2 = round_to_fraction(tp2_raw, fraction, direction='up')

        # ── 3. Confirmation Logic ─────────────────────────────────────────
        ema20 = indicators.get("ema_20")
        ema50 = indicators.get("ema_50")
        rsi = indicators.get("rsi")
        
        is_confirmed = False
        if ema20 is not None and ema50 is not None and rsi is not None:
            is_confirmed = (ema20 > ema50) and (rsi > 50)
            
        # ── 4. Risk/Reward Ratio ──────────────────────────────────────────
        reward = tp1 - entry_price
        rr_ratio = reward / risk
        
        status = "Speculative"
        if rr_ratio >= 2.0 and is_confirmed:
            status = "Strong Buy"
        elif rr_ratio < 1.0 or cluster_label == "High Risk / Avoid":
            status = "High Risk"

        # ── 5. Capital Allocation & Scaling ───────────────────────────────
        entry_capital = total_capital * 0.4
        shares_per_lot = 100
        lot_price = entry_price * shares_per_lot
        
        lot_rec = int(entry_capital // lot_price) if lot_price > 0 else 0
        if lot_rec == 0 and lot_price > 0 and total_capital >= lot_price:
            lot_rec = 1

        # ── 6. Scaling Strategy Description ───────────────────────────────
        if cluster_label == "Buy the Dip":
            scaling_note = f"Entry 40% di {format_price_no_sym(entry_price)}. Cicil 30% jika drop ke {format_price_no_sym(round_to_fraction(swing_low, fraction))}. Sisanya 30% saat Reversal (RSI > 45)."
        elif cluster_label == "Trending / Momentum":
            scaling_note = f"Entry 40% di {format_price_no_sym(entry_price)}. Cicil 30% jika break {format_price_no_sym(round_to_fraction(swing_high, fraction))}. Sisanya 30% via Trailing Stop."
        else:
            scaling_note = f"Cicil 40% (Entry), 30% (Naik 5%), 30% (Konfirmasi tren)."

        logic_text = (
            f"Analisis Teknikal: TP1 di {format_price_no_sym(tp1)} "
            f"({'RR 1:3' if is_dbx else 'Fibo 0.618'}) — area target profit. "
            f"TP2 di {format_price_no_sym(tp2)} "
            f"({'RR 1:5' if is_dbx else 'Fibo 1.0'}) — target ekstensi. "
            f"SL di {format_price_no_sym(sl)} ({atr_multiplier}x ATR) dibulatkan ke fraksi {fraction}."
        )

        return {
            "entry_range": f"{format_price_no_sym(round_to_fraction(entry_price * 0.995, fraction))} - {format_price_no_sym(round_to_fraction(entry_price * 1.005, fraction))}",
            "stop_loss": sl,
            "take_profit_1": tp1,
            "take_profit_2": tp2,
            "rr_ratio": f"1:{round(rr_ratio, 1)}",
            "status": status,
            "lot_recommendation": lot_rec,
            "scaling_strategy": scaling_note,
            "is_confirmed": is_confirmed,
            "logic_explanation": logic_text
        }

    except Exception as exc:
        logger.error("Trade plan calculation failed: %s", exc, exc_info=True)
        return {}

def format_price_no_sym(val):
    return "{:,.0f}".format(val).replace(",", ".")
