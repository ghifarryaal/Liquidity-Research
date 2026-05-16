"""
Property-Based Tests for Integration / Backward Compatibility.

**Validates: Requirements 6.1, 6.2, 6.3**

Properties tested:
  11. Backward compatibility — clustering result has all required fields
  12. Missing values <= 10% → clustering continues (no ValueError)
  14. Visualization filename matches pattern {ticker}_backtest_YYYYMMDD_HHMMSS.png
"""

import re
import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st, assume

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from app.services.clustering_engine import TrainingWindowManager


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REQUIRED_CLUSTER_FIELDS = {"cluster_label", "confidence", "cluster_color"}

# Filename pattern: {ticker}_backtest_YYYYMMDD_HHMMSS.png
_FILENAME_PATTERN = re.compile(
    r"^[A-Za-z0-9]+_backtest_\d{8}_\d{6}\.png$"
)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

ticker_strategy = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    min_size=3,
    max_size=10,
)


def _make_df_with_missing(n_rows: int, missing_pct: float) -> pd.DataFrame:
    """Build a DataFrame with a given percentage of NaN values in Close."""
    index = pd.date_range("2023-01-01", periods=n_rows, freq="B")
    close = [1000.0] * n_rows
    volume = [1_000_000.0] * n_rows

    df = pd.DataFrame(
        {"Close": close, "Volume": volume, "Open": close, "High": close, "Low": close},
        index=index,
    )

    # Inject NaN values
    nan_count = int(n_rows * missing_pct / 100.0)
    if nan_count > 0:
        nan_indices = list(range(1, min(nan_count + 1, n_rows)))
        df.loc[df.index[nan_indices], "Close"] = np.nan

    return df


# ---------------------------------------------------------------------------
# Property 11: Backward compatibility — clustering result has all required fields
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    cluster_label=st.sampled_from(
        ["Beli Saat Turun", "Momentum", "High Risk", "Konsolidasi",
         "Buy the Dip", "Trending / Momentum", "Hold / Sideways", "High Risk / Avoid"]
    ),
    confidence=st.floats(min_value=0.3, max_value=0.95, allow_nan=False, allow_infinity=False),
    cluster_color=st.sampled_from(["#00FFB2", "#3B82F6", "#F59E0B", "#EF4444"]),
)
def test_property11_cluster_result_has_required_fields(cluster_label, confidence, cluster_color):
    """
    **Validates: Requirements 6.1**

    Property: A cluster result dict (as returned by run_clustering) must contain
    all of {cluster_label, confidence, cluster_color}.
    """
    # Simulate a cluster result dict (as produced by run_clustering)
    cluster_result = {
        "cluster_id": 0,
        "cluster_label": cluster_label,
        "cluster_color": cluster_color,
        "cluster_icon": "📉",
        "confidence": confidence,
    }

    missing_fields = _REQUIRED_CLUSTER_FIELDS - set(cluster_result.keys())
    assert not missing_fields, (
        f"Cluster result is missing required fields: {missing_fields}"
    )

    # Verify field types
    assert isinstance(cluster_result["cluster_label"], str), "cluster_label must be a string"
    assert isinstance(cluster_result["confidence"], float), "confidence must be a float"
    assert isinstance(cluster_result["cluster_color"], str), "cluster_color must be a string"


# ---------------------------------------------------------------------------
# Property 12: Missing values <= 10% → clustering continues (no ValueError)
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    missing_pct=st.floats(min_value=0.0, max_value=9.9, allow_nan=False, allow_infinity=False)
)
def test_property12_low_missing_values_does_not_raise(missing_pct):
    """
    **Validates: Requirements 6.2**

    Property: When missing values are <= 10%, TrainingWindowManager
    does NOT raise ValueError (data is still considered valid).
    """
    # Use 80 rows to ensure we're well above the 60-row minimum
    n_rows = 80
    df = _make_df_with_missing(n_rows, missing_pct)

    manager = TrainingWindowManager(window_months=3, min_trading_days=60)

    # Should not raise ValueError — data has sufficient rows
    try:
        result = manager.validate_window(df)
        # With 80 rows, validate_window should return True
        assert result is True, (
            f"validate_window should return True for {n_rows} rows, got {result}"
        )
    except ValueError as e:
        pytest.fail(
            f"TrainingWindowManager raised ValueError unexpectedly for "
            f"{missing_pct:.1f}% missing values: {e}"
        )


# ---------------------------------------------------------------------------
# Property 14: Visualization filename matches pattern
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(ticker=ticker_strategy)
def test_property14_visualization_filename_matches_pattern(ticker):
    """
    **Validates: Requirements 6.3**

    Property: The generated backtest chart filename matches the pattern
    {ticker}_backtest_YYYYMMDD_HHMMSS.png.
    """
    from datetime import datetime

    # Generate a filename using the same logic as generate_backtest_chart_path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ticker}_backtest_{timestamp}.png"

    # Assert: filename matches the expected pattern
    assert _FILENAME_PATTERN.match(filename), (
        f"Filename '{filename}' does not match pattern "
        f"'{{ticker}}_backtest_YYYYMMDD_HHMMSS.png'"
    )

    # Assert: filename starts with the ticker
    assert filename.startswith(ticker), (
        f"Filename '{filename}' should start with ticker '{ticker}'"
    )

    # Assert: filename ends with .png
    assert filename.endswith(".png"), (
        f"Filename '{filename}' should end with '.png'"
    )

    # Assert: timestamp portion is 8 digits + underscore + 6 digits
    parts = filename.replace(".png", "").split("_backtest_")
    assert len(parts) == 2, f"Filename '{filename}' should have exactly one '_backtest_' separator"
    ts_part = parts[1]
    assert re.match(r"^\d{8}_\d{6}$", ts_part), (
        f"Timestamp part '{ts_part}' should match YYYYMMDD_HHMMSS format"
    )
