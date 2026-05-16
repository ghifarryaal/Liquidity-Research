"""
Property-Based Tests for Clustering Engine Module.

**Validates: Requirements 2.1, 2.2**

Properties tested:
  4. _map_enhanced_centroids_to_labels() assigns all 4 labels exactly once
  5. TrainingWindowManager.validate_window() returns True iff len(df) >= 60
"""

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st, assume

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from app.services.clustering_engine import (
    _map_enhanced_centroids_to_labels,
    TrainingWindowManager,
)

# Expected labels for the enhanced 4D clustering
_EXPECTED_LABELS = {"Beli Saat Turun", "Momentum", "High Risk", "Konsolidasi"}


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

@st.composite
def four_centroids_strategy(draw):
    """
    Strategy: 4 random centroids of shape (4, 4) with values in [-0.1, 0.1].
    Represents [log_returns, volatility, rsi_relative, volume_impact] centroids.
    """
    data = draw(
        st.lists(
            st.lists(
                st.floats(min_value=-0.1, max_value=0.1, allow_nan=False, allow_infinity=False),
                min_size=4,
                max_size=4,
            ),
            min_size=4,
            max_size=4,
        )
    )
    return np.array(data, dtype=float)


def _make_df_with_rows(n_rows: int) -> pd.DataFrame:
    """Build a minimal DataFrame with n_rows rows and a DatetimeIndex."""
    index = pd.date_range("2023-01-01", periods=n_rows, freq="B")
    return pd.DataFrame(
        {
            "Close":  [1000.0] * n_rows,
            "Volume": [1_000_000.0] * n_rows,
        },
        index=index,
    )


# ---------------------------------------------------------------------------
# Property 4: _map_enhanced_centroids_to_labels assigns all 4 labels exactly once
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(four_centroids_strategy())
def test_property4_enhanced_centroids_assigns_all_labels_exactly_once(centers):
    """
    **Validates: Requirements 2.1**

    Property: _map_enhanced_centroids_to_labels() with 4 centroids:
      - Returns a dict with exactly 4 entries.
      - Keys are {0, 1, 2, 3}.
      - Values are exactly {"Beli Saat Turun", "Momentum", "High Risk", "Konsolidasi"}.
    """
    label_map = _map_enhanced_centroids_to_labels(centers)

    # Assert 1: exactly 4 entries
    assert len(label_map) == 4, (
        f"Expected 4 entries in label_map, got {len(label_map)}: {label_map}"
    )

    # Assert 2: keys are {0, 1, 2, 3}
    assert set(label_map.keys()) == {0, 1, 2, 3}, (
        f"Expected keys {{0, 1, 2, 3}}, got {set(label_map.keys())}"
    )

    # Assert 3: values are exactly the 4 expected labels
    assert set(label_map.values()) == _EXPECTED_LABELS, (
        f"Expected labels {_EXPECTED_LABELS}, got {set(label_map.values())}"
    )


# ---------------------------------------------------------------------------
# Property 5: TrainingWindowManager.validate_window() returns True iff len(df) >= 60
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.integers(min_value=10, max_value=200))
def test_property5_validate_window_returns_true_iff_sufficient_data(trading_days):
    """
    **Validates: Requirements 2.2**

    Property: TrainingWindowManager.validate_window(df) returns True
    if and only if len(df) >= 60.
    """
    manager = TrainingWindowManager(window_months=3, min_trading_days=60)
    df = _make_df_with_rows(trading_days)

    result = manager.validate_window(df)

    if trading_days >= 60:
        assert result is True, (
            f"validate_window should return True for {trading_days} rows (>= 60), "
            f"but returned {result}"
        )
    else:
        assert result is False, (
            f"validate_window should return False for {trading_days} rows (< 60), "
            f"but returned {result}"
        )
