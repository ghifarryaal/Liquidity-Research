"""
Service layer tests for LiquidityResearch — Advanced K-Means Clustering
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n=100, start_price=1000.0, seed=42):
    """Create a realistic OHLCV DataFrame for testing."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    close = start_price + np.cumsum(rng.normal(0, 10, n))
    close = np.abs(close)  # ensure positive
    return pd.DataFrame(
        {
            "Open":   close * rng.uniform(0.99, 1.01, n),
            "High":   close * rng.uniform(1.00, 1.02, n),
            "Low":    close * rng.uniform(0.98, 1.00, n),
            "Close":  close,
            "Volume": rng.uniform(1e6, 5e6, n),
        },
        index=dates,
    )


# ---------------------------------------------------------------------------
# compute_enhanced_features tests
# ---------------------------------------------------------------------------

class TestComputeEnhancedFeatures:
    def test_returns_4d_feature_vector(self):
        from app.services.feature_engineering import compute_enhanced_features
        df = _make_ohlcv(80)
        result = compute_enhanced_features(df)
        assert "feature_vector" in result
        assert len(result["feature_vector"]) == 4

    def test_no_nan_inf_in_feature_vector(self):
        from app.services.feature_engineering import compute_enhanced_features
        df = _make_ohlcv(80)
        result = compute_enhanced_features(df)
        fv = result["feature_vector"]
        assert all(not np.isnan(v) and not np.isinf(v) for v in fv)

    def test_rsi_relative_in_0_1(self):
        from app.services.feature_engineering import compute_enhanced_features
        df = _make_ohlcv(80)
        result = compute_enhanced_features(df)
        assert 0.0 <= result["rsi_relative"] <= 1.0

    def test_insufficient_data_returns_neutral(self):
        from app.services.feature_engineering import compute_enhanced_features
        df = _make_ohlcv(10)  # too few rows
        result = compute_enhanced_features(df)
        # Should return neutral values, not raise
        assert result["feature_vector"] == [0.0, 0.0, 0.5, 1.0]

    def test_handles_missing_values_via_ffill(self):
        from app.services.feature_engineering import compute_enhanced_features
        df = _make_ohlcv(80)
        # Inject 10% NaN
        nan_idx = list(range(5, 15))
        df.loc[df.index[nan_idx], "Close"] = np.nan
        result = compute_enhanced_features(df)
        fv = result["feature_vector"]
        assert len(fv) == 4
        assert all(not np.isnan(v) for v in fv)

    def test_batch_processing(self):
        from app.services.feature_engineering import compute_enhanced_features_batch
        ohlcv_map = {
            "BBCA.JK": _make_ohlcv(80, seed=1),
            "BBRI.JK": _make_ohlcv(80, seed=2),
            "TLKM.JK": _make_ohlcv(80, seed=3),
        }
        results = compute_enhanced_features_batch(ohlcv_map)
        assert len(results) == 3
        for ticker, feat in results.items():
            assert len(feat["feature_vector"]) == 4

    def test_build_enhanced_feature_matrix_shape(self):
        from app.services.feature_engineering import (
            compute_enhanced_features_batch,
            build_enhanced_feature_matrix,
        )
        ohlcv_map = {f"TICK{i}.JK": _make_ohlcv(80, seed=i) for i in range(5)}
        batch = compute_enhanced_features_batch(ohlcv_map)
        tickers, matrix = build_enhanced_feature_matrix(batch)
        assert len(tickers) == 5
        assert matrix.shape == (5, 4)


# ---------------------------------------------------------------------------
# TrainingWindowManager tests
# ---------------------------------------------------------------------------

class TestTrainingWindowManager:
    def test_validate_window_true_for_60_rows(self):
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        df = _make_ohlcv(60)
        assert manager.validate_window(df) is True

    def test_validate_window_false_for_59_rows(self):
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        df = _make_ohlcv(59)
        assert manager.validate_window(df) is False

    def test_validate_window_true_for_100_rows(self):
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        df = _make_ohlcv(100)
        assert manager.validate_window(df) is True

    def test_get_training_metadata_raises_for_insufficient_data(self):
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        df = _make_ohlcv(30)
        with pytest.raises(ValueError, match="Insufficient training data"):
            manager.get_training_metadata(df)

    def test_get_training_metadata_returns_correct_keys(self):
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        df = _make_ohlcv(80)
        meta = manager.get_training_metadata(df)
        assert "start_date" in meta
        assert "end_date" in meta
        assert "trading_days" in meta
        assert "missing_values_pct" in meta
        assert meta["trading_days"] == 80

    def test_get_training_metadata_warns_on_high_missing(self, caplog):
        """Verify warning is logged when missing values exceed 10%."""
        import logging
        from app.services.clustering_engine import TrainingWindowManager
        manager = TrainingWindowManager()
        # Build a DataFrame where >10% of ALL cells are NaN
        df = _make_ohlcv(80)
        # Inject NaN into multiple columns to exceed 10% of total cells
        nan_idx = list(range(1, 20))  # 19 rows out of 80 = ~24% of rows
        for col in ["Close", "Open", "High", "Low", "Volume"]:
            df.loc[df.index[nan_idx], col] = np.nan
        with caplog.at_level(logging.WARNING, logger="app.services.clustering_engine"):
            manager.get_training_metadata(df)
        assert any("missing" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# TradingSimulator tests
# ---------------------------------------------------------------------------

class TestTradingSimulator:
    def test_execute_buy_sets_stop_loss_at_3pct(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        entry_price = 5000.0
        sim._execute_buy("2023-01-01", entry_price, "Beli Saat Turun")
        assert sim.position is not None
        assert abs(sim.position["stop_loss"] - entry_price * 0.97) < 1e-6

    def test_stop_loss_triggers_forced_sell(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim._execute_buy("2023-01-01", 5000.0, "Beli Saat Turun")
        # Price drops below stop loss
        sim.process_day("2023-01-02", 4800.0, "Beli Saat Turun")
        assert sim.position is None
        assert len(sim.trades) == 1
        assert sim.trades[0]["stop_loss_triggered"] is True

    def test_trailing_stop_activates_after_5pct_profit(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim._execute_buy("2023-01-01", 5000.0, "Momentum")
        # Price rises 6% — trailing stop should activate
        sim._update_trailing_stop(5300.0)
        assert sim.position["trailing_stop"] is not None
        assert abs(sim.position["trailing_stop"] - 5300.0 * 0.95) < 1e-6

    def test_trailing_stop_not_active_below_5pct(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim._execute_buy("2023-01-01", 5000.0, "Momentum")
        # Price rises only 3% — trailing stop should NOT activate
        sim._update_trailing_stop(5150.0)
        assert sim.position["trailing_stop"] is None

    def test_sell_signal_closes_position(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim._execute_buy("2023-01-01", 5000.0, "Beli Saat Turun")
        sim.process_day("2023-06-01", 5500.0, "High Risk")
        assert sim.position is None
        assert len(sim.trades) == 1
        assert sim.trades[0]["exit_reason"] == "signal"

    def test_no_double_buy(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim.process_day("2023-01-01", 5000.0, "Beli Saat Turun")
        initial_shares = sim.position["shares"] if sim.position else 0
        sim.process_day("2023-01-02", 5000.0, "Beli Saat Turun")
        # Shares should not change — no double buy
        if sim.position:
            assert sim.position["shares"] == initial_shares

    def test_trade_record_has_all_required_fields(self):
        from app.services.backtest_engine import TradingSimulator
        sim = TradingSimulator(initial_capital=10_000_000.0)
        sim._execute_buy("2023-01-01", 5000.0, "Beli Saat Turun")
        sim._execute_sell("2023-06-01", 5500.0, "signal")
        trade = sim.trades[0]
        required = {
            "entry_date", "entry_price", "entry_label",
            "exit_date", "exit_price", "exit_label",
            "shares", "pnl", "pnl_pct", "holding_days",
            "exit_reason", "stop_loss_triggered", "trailing_stop_triggered",
        }
        assert required.issubset(set(trade.keys()))


# ---------------------------------------------------------------------------
# run_enhanced_backtest tests
# ---------------------------------------------------------------------------

class TestRunEnhancedBacktest:
    def test_returns_empty_for_small_df(self):
        from app.services.backtest_engine import run_enhanced_backtest
        df = _make_ohlcv(20)
        result = run_enhanced_backtest(df, {})
        assert result["total_trades"] == 0
        assert result["cumulative_returns"] == 0.0

    def test_returns_all_required_keys(self):
        from app.services.backtest_engine import run_enhanced_backtest
        df = _make_ohlcv(100)
        # Build a simple timeline: alternate buy/sell labels
        timeline = {}
        for i, ts in enumerate(df.index):
            date_str = str(ts.date())
            timeline[date_str] = "Beli Saat Turun" if i % 10 < 5 else "High Risk"
        result = run_enhanced_backtest(df, timeline)
        required_keys = {
            "ticker", "start_date", "end_date", "initial_capital", "final_equity",
            "cumulative_returns", "sharpe_ratio", "maximum_drawdown",
            "total_trades", "winning_trades", "win_rate", "trades", "equity_curve",
        }
        assert required_keys.issubset(set(result.keys()))

    def test_equity_curve_length_matches_df(self):
        from app.services.backtest_engine import run_enhanced_backtest
        df = _make_ohlcv(100)
        timeline = {str(ts.date()): "Konsolidasi" for ts in df.index}
        result = run_enhanced_backtest(df, timeline)
        assert len(result["equity_curve"]) == len(df)

    def test_maximum_drawdown_non_negative(self):
        from app.services.backtest_engine import run_enhanced_backtest
        df = _make_ohlcv(100)
        timeline = {str(ts.date()): "Beli Saat Turun" for ts in df.index}
        result = run_enhanced_backtest(df, timeline)
        assert result["maximum_drawdown"] >= 0.0


# ---------------------------------------------------------------------------
# Backward compatibility tests
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    def test_cluster_config_has_original_labels(self):
        from app.services.clustering_engine import CLUSTER_CONFIG
        original_labels = {"Buy the Dip", "Trending / Momentum", "Hold / Sideways", "High Risk / Avoid"}
        for label in original_labels:
            assert label in CLUSTER_CONFIG, f"Original label '{label}' missing from CLUSTER_CONFIG"

    def test_cluster_config_has_new_labels(self):
        from app.services.clustering_engine import CLUSTER_CONFIG
        new_labels = {"Beli Saat Turun", "Momentum", "Konsolidasi", "High Risk"}
        for label in new_labels:
            assert label in CLUSTER_CONFIG, f"New label '{label}' missing from CLUSTER_CONFIG"

    def test_generate_reasoning_handles_all_labels(self):
        from app.services.clustering_engine import generate_reasoning
        all_labels = [
            "Buy the Dip", "Trending / Momentum", "Hold / Sideways", "High Risk / Avoid",
            "Beli Saat Turun", "Momentum", "Konsolidasi", "High Risk",
        ]
        ind = {"rsi": 45.0, "macd": 0.1, "macd_signal": 0.05, "volume_ratio": 1.2}
        for label in all_labels:
            strategy, reasoning = generate_reasoning(label, ind)
            assert isinstance(strategy, str) and len(strategy) > 0
            assert isinstance(reasoning, str) and len(reasoning) > 0

    def test_get_buy_hold_sell_signal_handles_all_labels(self):
        from app.services.clustering_engine import get_buy_hold_sell_signal
        buy_labels = ["Buy the Dip", "Trending / Momentum", "Beli Saat Turun", "Momentum"]
        hold_labels = ["Hold / Sideways", "Konsolidasi"]
        sell_labels = ["High Risk / Avoid", "High Risk"]

        for label in buy_labels:
            result = get_buy_hold_sell_signal(label, 0.8)
            assert result["base_signal"] == "BUY", f"Expected BUY for '{label}'"

        for label in hold_labels:
            result = get_buy_hold_sell_signal(label, 0.8)
            assert result["base_signal"] == "HOLD", f"Expected HOLD for '{label}'"

        for label in sell_labels:
            result = get_buy_hold_sell_signal(label, 0.8)
            assert result["base_signal"] == "SELL", f"Expected SELL for '{label}'"

    def test_run_clustering_accepts_training_period_days(self):
        """Ensure run_clustering still works with the new optional parameter."""
        from app.services.clustering_engine import run_clustering
        import numpy as np
        # 5 tickers, 8-feature vectors (existing format)
        tickers = [f"TICK{i}.JK" for i in range(5)]
        matrix = np.random.rand(5, 8)
        # Should not raise
        result = run_clustering(tickers, matrix, training_period_days=90)
        assert len(result) == 5
        for ticker, info in result.items():
            assert "cluster_label" in info
            assert "confidence" in info
            assert "cluster_color" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
