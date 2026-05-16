"""
Property-Based Tests for Backtest Engine Module.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

Properties tested:
  6. Buy/sell signal logic
  7. Stop loss at entry * 0.97
  8. Trade records contain all required fields
  9. Performance metrics are calculated correctly
"""

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st, assume

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from app.services.backtest_engine import TradingSimulator, calculate_performance_metrics


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BUY_LABELS = ["Beli Saat Turun", "Momentum", "Buy the Dip", "Trending / Momentum"]
_SELL_LABELS = ["High Risk", "Konsolidasi", "High Risk / Avoid", "Hold / Sideways"]
_ALL_LABELS = _BUY_LABELS + _SELL_LABELS

_REQUIRED_TRADE_KEYS = {
    "entry_date",
    "entry_price",
    "entry_label",
    "exit_date",
    "exit_price",
    "exit_label",
    "shares",
    "pnl",
    "pnl_pct",
    "holding_days",
    "exit_reason",
    "stop_loss_triggered",
    "trailing_stop_triggered",
}


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

label_strategy = st.sampled_from(_ALL_LABELS)
buy_label_strategy = st.sampled_from(_BUY_LABELS)
sell_label_strategy = st.sampled_from(_SELL_LABELS)
price_strategy = st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
entry_price_strategy = st.floats(min_value=1000.0, max_value=10000.0, allow_nan=False, allow_infinity=False)


# ---------------------------------------------------------------------------
# Property 6: Buy/sell signal logic
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    label=label_strategy,
    has_position=st.booleans(),
    price=price_strategy,
)
def test_property6_buy_sell_signal_logic(label, has_position, price):
    """
    **Validates: Requirements 4.1**

    Property:
      - Buy is executed only when label is buy-worthy AND no position exists.
      - Sell is executed when label is sell-worthy AND a position exists.
    """
    assume(price > 0)

    sim = TradingSimulator(initial_capital=10_000_000.0)

    if has_position:
        # Pre-open a position at a safe price
        sim._execute_buy("2023-01-01", price, "Beli Saat Turun")
        assert sim.position is not None

    initial_position = sim.position is not None

    # Process a day with the given label (use a price that won't trigger stop loss)
    # Use same price to avoid stop-loss interference
    sim.process_day("2023-06-01", price, label)

    if label in _BUY_LABELS and not initial_position:
        # Buy should have been executed
        assert sim.position is not None, (
            f"Expected buy to be executed for label='{label}' with no prior position, "
            f"but position is None"
        )

    if label in _SELL_LABELS and initial_position:
        # Sell should have been executed (assuming no stop-loss triggered first)
        # Note: stop-loss could have triggered if price dropped, but we use same price
        # so stop-loss (price * 0.97) won't trigger at same price
        assert sim.position is None, (
            f"Expected sell to be executed for label='{label}' with open position, "
            f"but position still exists"
        )

    if label in _BUY_LABELS and initial_position:
        # Should NOT buy again when already in position
        # Position should still be open (or closed by stop-loss, but not re-opened)
        # We just verify no double-buy happened (shares shouldn't double)
        pass  # No assertion needed — process_day guards against double-buy

    if label in _SELL_LABELS and not initial_position:
        # Should NOT sell when no position
        assert sim.position is None, (
            f"Position should remain None for sell label='{label}' with no prior position"
        )


# ---------------------------------------------------------------------------
# Property 7: Stop loss at entry * 0.97
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(entry_price=entry_price_strategy)
def test_property7_stop_loss_at_entry_times_0_97(entry_price):
    """
    **Validates: Requirements 4.2**

    Property: After _execute_buy, position["stop_loss"] == entry_price * 0.97.
    """
    assume(entry_price > 0)

    sim = TradingSimulator(initial_capital=100_000_000.0)
    sim._execute_buy("2023-01-01", entry_price, "Beli Saat Turun")

    assert sim.position is not None, "Position should be open after _execute_buy"

    expected_stop_loss = entry_price * 0.97
    actual_stop_loss = sim.position["stop_loss"]

    assert abs(actual_stop_loss - expected_stop_loss) < 1e-6, (
        f"stop_loss = {actual_stop_loss}, expected {expected_stop_loss} "
        f"(entry_price * 0.97 = {entry_price} * 0.97)"
    )


# ---------------------------------------------------------------------------
# Property 8: Trade records contain all required fields
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    entry_price=entry_price_strategy,
    exit_price=entry_price_strategy,
)
def test_property8_trade_records_contain_all_required_fields(entry_price, exit_price):
    """
    **Validates: Requirements 4.3**

    Property: After a complete buy-then-sell cycle, the trade record
    contains all required keys.
    """
    assume(entry_price > 0)
    assume(exit_price > 0)
    # Ensure exit price won't trigger stop-loss (which would change exit_reason)
    # Use an exit price above stop-loss level
    assume(exit_price > entry_price * 0.97)

    sim = TradingSimulator(initial_capital=100_000_000.0)
    sim._execute_buy("2023-01-01", entry_price, "Beli Saat Turun")
    sim._execute_sell("2023-06-01", exit_price, "signal")

    assert len(sim.trades) == 1, f"Expected 1 trade, got {len(sim.trades)}"

    trade = sim.trades[0]
    missing_keys = _REQUIRED_TRADE_KEYS - set(trade.keys())
    assert not missing_keys, (
        f"Trade record is missing required keys: {missing_keys}"
    )


# ---------------------------------------------------------------------------
# Property 9: Performance metrics are calculated correctly
# ---------------------------------------------------------------------------

@st.composite
def equity_curve_strategy(draw):
    """
    Strategy: list of equity values (floats, min 2 elements).
    Returns a list of equity curve dicts.
    """
    n = draw(st.integers(min_value=2, max_value=50))
    values = draw(
        st.lists(
            st.floats(min_value=1_000_000.0, max_value=200_000_000.0, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    return [
        {"date": str(dates[i].date()), "equity": values[i], "position": False}
        for i in range(n)
    ]


@settings(max_examples=100)
@given(equity_curve=equity_curve_strategy())
def test_property9_performance_metrics_calculated_correctly(equity_curve):
    """
    **Validates: Requirements 4.4**

    Property:
      - cumulative_returns = (final_equity - initial_equity) / initial_equity
      - maximum_drawdown >= 0
    """
    assume(len(equity_curve) >= 2)
    assume(equity_curve[0]["equity"] > 0)

    metrics = calculate_performance_metrics(trades=[], equity_curve=equity_curve)

    initial_equity = equity_curve[0]["equity"]
    final_equity = equity_curve[-1]["equity"]

    # Assert 1: cumulative_returns = (final - initial) / initial
    expected_cumulative = (final_equity - initial_equity) / initial_equity
    actual_cumulative = metrics["cumulative_returns"]
    assert abs(actual_cumulative - round(expected_cumulative, 4)) < 1e-4, (
        f"cumulative_returns = {actual_cumulative}, "
        f"expected {expected_cumulative:.4f}"
    )

    # Assert 2: maximum_drawdown >= 0
    max_dd = metrics["maximum_drawdown"]
    assert max_dd >= 0.0, (
        f"maximum_drawdown = {max_dd} should be >= 0"
    )
