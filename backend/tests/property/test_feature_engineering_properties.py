"""
Property-Based Tests for Feature Engineering Module.

**Validates: Requirements 1.1, 1.2, 1.3**

Properties tested:
  1. Forward fill preserves time series integrity
  2. RobustScaler produces median ≈ 0 for each feature
  3. compute_enhanced_features() returns valid 4D vector
"""

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st, assume
from sklearn.preprocessing import RobustScaler

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from app.services.feature_engineering import compute_enhanced_features


# ---------------------------------------------------------------------------
# Helpers / Strategies
# ---------------------------------------------------------------------------

def _make_ohlcv_df(close_prices, volumes, index=None):
    """Build a minimal OHLCV DataFrame from close prices and volumes."""
    n = len(close_prices)
    if index is None:
        index = pd.date_range("2023-01-01", periods=n, freq="B")
    df = pd.DataFrame(
        {
            "Open":   close_prices,
            "High":   [p * 1.01 for p in close_prices],
            "Low":    [p * 0.99 for p in close_prices],
            "Close":  close_prices,
            "Volume": volumes,
        },
        index=index,
    )
    return df


@st.composite
def ohlcv_with_nans(draw):
    """
    Strategy: DataFrame with ~10% NaN values injected into Close column.
    Returns (df_with_nans, original_non_nan_values).
    """
    n = draw(st.integers(min_value=30, max_value=80))
    close_prices = draw(
        st.lists(
            st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    volumes = draw(
        st.lists(
            st.floats(min_value=1e6, max_value=1e9, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    df = _make_ohlcv_df(close_prices, volumes)

    # Inject ~10% NaN values (but not the first row, so ffill can work)
    nan_count = max(1, int(n * 0.10))
    nan_indices = draw(
        st.lists(
            st.integers(min_value=1, max_value=n - 1),
            min_size=nan_count,
            max_size=nan_count,
            unique=True,
        )
    )
    original_non_nan = {i: df["Close"].iloc[i] for i in range(n) if i not in nan_indices}
    df.loc[df.index[nan_indices], "Close"] = np.nan

    return df, original_non_nan


@st.composite
def feature_matrix_strategy(draw):
    """
    Strategy: random feature matrix with n_samples in [10, 50] and n_features=4.
    """
    n_samples = draw(st.integers(min_value=10, max_value=50))
    data = draw(
        st.lists(
            st.lists(
                st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
                min_size=4,
                max_size=4,
            ),
            min_size=n_samples,
            max_size=n_samples,
        )
    )
    return np.array(data, dtype=float)


@st.composite
def valid_ohlcv_df(draw):
    """
    Strategy: valid OHLCV DataFrame with at least 60 rows.
    Close prices in [100, 10000], volumes in [1e6, 1e9].
    """
    n = draw(st.integers(min_value=60, max_value=120))
    close_prices = draw(
        st.lists(
            st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    # Ensure no zero prices (would break log returns)
    assume(all(p > 0 for p in close_prices))

    volumes = draw(
        st.lists(
            st.floats(min_value=1e6, max_value=1e9, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    return _make_ohlcv_df(close_prices, volumes)


# ---------------------------------------------------------------------------
# Property 1: Forward fill preserves time series integrity
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(ohlcv_with_nans())
def test_property1_ffill_preserves_time_series_integrity(data):
    """
    **Validates: Requirements 1.1**

    Property: After applying ffill().dropna() to a series with ~10% NaN values:
      - No NaN values remain in the result.
      - Non-missing values that were present before ffill are preserved unchanged.
    """
    df, original_non_nan = data

    close_series = df["Close"].astype(float)
    filled = close_series.ffill().dropna()

    # Assert 1: No NaN values remain after ffill + dropna
    assert not filled.isna().any(), "NaN values remain after ffill().dropna()"

    # Assert 2: Non-missing values are preserved (values that were not NaN remain unchanged)
    for idx, original_value in original_non_nan.items():
        # The index in filled may shift due to dropna, so use positional lookup
        # We check that the original non-NaN value still appears in the filled series
        # at the same datetime index position
        dt_index = df.index[idx]
        if dt_index in filled.index:
            assert abs(filled[dt_index] - original_value) < 1e-9, (
                f"Non-missing value at position {idx} was altered: "
                f"expected {original_value}, got {filled[dt_index]}"
            )


# ---------------------------------------------------------------------------
# Property 2: RobustScaler produces median ≈ 0 for each feature
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(feature_matrix_strategy())
def test_property2_robust_scaler_median_near_zero(matrix):
    """
    **Validates: Requirements 1.2**

    Property: After applying RobustScaler to a feature matrix,
    the median of each column is approximately 0 (abs < 0.1).
    """
    # RobustScaler needs at least 2 samples to compute IQR
    assume(matrix.shape[0] >= 2)

    # Skip degenerate columns where all values are identical (IQR = 0)
    for col_idx in range(matrix.shape[1]):
        col = matrix[:, col_idx]
        assume(np.std(col) > 1e-10)

    scaler = RobustScaler()
    scaled = scaler.fit_transform(matrix)

    for col_idx in range(scaled.shape[1]):
        col_median = float(np.median(scaled[:, col_idx]))
        assert abs(col_median) < 0.1, (
            f"Column {col_idx} median after RobustScaler is {col_median:.4f}, "
            f"expected abs < 0.1"
        )


# ---------------------------------------------------------------------------
# Property 3: compute_enhanced_features() returns valid 4D vector
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(valid_ohlcv_df())
def test_property3_enhanced_features_valid_4d_vector(df):
    """
    **Validates: Requirements 1.3**

    Property: compute_enhanced_features() on valid OHLCV data (>=60 rows):
      - feature_vector has exactly 4 elements.
      - No NaN or Inf in feature_vector.
      - rsi_relative is in [0, 1].
    """
    result = compute_enhanced_features(df)

    # Assert 1: feature_vector has exactly 4 elements
    fv = result.get("feature_vector")
    assert fv is not None, "feature_vector key missing from result"
    assert len(fv) == 4, f"Expected 4 elements in feature_vector, got {len(fv)}"

    # Assert 2: No NaN or Inf in feature_vector
    for i, val in enumerate(fv):
        assert not np.isnan(val), f"NaN found at feature_vector[{i}] = {val}"
        assert not np.isinf(val), f"Inf found at feature_vector[{i}] = {val}"

    # Assert 3: rsi_relative is in [0, 1]
    rsi_relative = result.get("rsi_relative")
    assert rsi_relative is not None, "rsi_relative key missing from result"
    assert 0.0 <= rsi_relative <= 1.0, (
        f"rsi_relative = {rsi_relative} is outside [0, 1]"
    )
