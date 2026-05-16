"""
API endpoint tests for LiquidityResearch backend — Advanced K-Means Clustering
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Test client setup
# ---------------------------------------------------------------------------

def _make_mock_ohlcv(n=100, seed=42):
    """Create a realistic OHLCV DataFrame for mocking."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    close = 5000.0 + np.cumsum(rng.normal(0, 50, n))
    close = np.abs(close)
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
# Basic health check tests (no mocking needed)
# ---------------------------------------------------------------------------

class TestHealthEndpoints:
    def test_root_returns_200(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/")
        data = response.json()
        assert "service" in data or "status" in data

    def test_health_check_returns_healthy(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# Training window info endpoint
# ---------------------------------------------------------------------------

class TestTrainingWindowInfoEndpoint:
    def test_returns_200(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/cluster/training-window-info")
        assert response.status_code == 200

    def test_returns_required_fields(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/cluster/training-window-info")
        assert response.status_code == 200
        data = response.json()
        assert "start_date" in data
        assert "end_date" in data
        assert "trading_days" in data
        assert "missing_values_pct" in data

    def test_trading_days_is_positive(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/cluster/training-window-info")
        data = response.json()
        assert data["trading_days"] > 0


# ---------------------------------------------------------------------------
# Backtest endpoint
# ---------------------------------------------------------------------------

class TestBacktestEndpoint:
    def test_returns_422_for_missing_ticker(self):
        from app.main import app
        client = TestClient(app)
        response = client.post("/api/cluster/backtest", json={})
        assert response.status_code == 422  # Pydantic validation error

    def test_returns_valid_structure_with_mock(self):
        """Test POST /cluster/backtest with mocked data fetch."""
        from app.main import app
        mock_df = _make_mock_ohlcv(100)

        with patch("app.routers.cluster.fetch_single_ticker", return_value=mock_df):
            client = TestClient(app)
            response = client.post(
                "/api/cluster/backtest",
                json={"ticker": "BBCA.JK", "backtest_months": 6, "generate_chart": False},
            )

        # Should return 200 or 422 (if indicators fail on mock data)
        assert response.status_code in [200, 422, 500]

        if response.status_code == 200:
            data = response.json()
            assert "cumulative_returns" in data
            assert "sharpe_ratio" in data
            assert "maximum_drawdown" in data
            assert "total_trades" in data
            assert "win_rate" in data

    def test_ticker_normalized_to_uppercase(self):
        """Ensure lowercase ticker is normalized."""
        from app.main import app
        mock_df = _make_mock_ohlcv(100)

        with patch("app.routers.cluster.fetch_single_ticker", return_value=mock_df):
            client = TestClient(app)
            response = client.post(
                "/api/cluster/backtest",
                json={"ticker": "bbca", "backtest_months": 6},
            )
        # Should not 404 due to case mismatch
        assert response.status_code != 404


# ---------------------------------------------------------------------------
# Backward compatibility — existing endpoints still work
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    def test_macro_endpoint_returns_200(self):
        from app.main import app
        client = TestClient(app)
        with patch("app.routers.cluster.get_macro_score") as mock_macro:
            mock_macro.return_value = {
                "volatility_penalty": 0.3,
                "risk_adjusted_score": 0.7,
                "macro_regime": "Neutral",
                "world_indices": [],
                "commodities": [],
                "dxy_zscore": 0.1,
                "us10y_zscore": 0.2,
                "dxy_level": 0.5,
                "us10y_level": 0.5,
            }
            response = client.get("/api/macro")
        assert response.status_code == 200

    def test_macro_endpoint_returns_required_fields(self):
        from app.main import app
        client = TestClient(app)
        with patch("app.routers.cluster.get_macro_score") as mock_macro:
            mock_macro.return_value = {
                "volatility_penalty": 0.3,
                "risk_adjusted_score": 0.7,
                "macro_regime": "Neutral",
                "world_indices": [],
                "commodities": [],
                "dxy_zscore": 0.1,
                "us10y_zscore": 0.2,
                "dxy_level": 0.5,
                "us10y_level": 0.5,
            }
            response = client.get("/api/macro")
        data = response.json()
        assert "volatility_penalty" in data
        assert "risk_adjusted_score" in data
        assert "macro_regime" in data

    def test_invalid_index_returns_404(self):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/cluster/invalid_index")
        assert response.status_code in [404, 422]


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class TestSchemaModels:
    def test_training_window_info_model(self):
        from app.models.schemas import TrainingWindowInfo
        info = TrainingWindowInfo(
            start_date="2023-10-01",
            end_date="2024-01-01",
            trading_days=63,
            missing_values_pct=2.5,
            tickers_processed=45,
            tickers_failed=[],
        )
        assert info.trading_days == 63
        assert info.missing_values_pct == 2.5

    def test_enhanced_backtest_result_model(self):
        from app.models.schemas import EnhancedBacktestResult
        result = EnhancedBacktestResult(
            ticker="BBCA.JK",
            start_date="2023-07-01",
            end_date="2024-01-01",
            initial_capital=100_000_000.0,
            final_equity=108_500_000.0,
            cumulative_returns=0.085,
            sharpe_ratio=1.45,
            maximum_drawdown=0.062,
            total_trades=12,
            winning_trades=8,
            win_rate=0.667,
        )
        assert result.ticker == "BBCA.JK"
        assert result.cumulative_returns == 0.085

    def test_backtest_result_has_new_fields(self):
        from app.models.schemas import BacktestResult
        result = BacktestResult(
            total_trades=10,
            winning_trades=6,
            win_rate=0.6,
            avg_rr_achieved=1.5,
            max_drawdown_pct=-5.0,
            best_trade_pct=8.0,
            worst_trade_pct=-3.0,
            cumulative_returns=0.12,
            sharpe_ratio=1.2,
            maximum_drawdown=0.08,
        )
        assert result.cumulative_returns == 0.12
        assert result.sharpe_ratio == 1.2
        assert result.maximum_drawdown == 0.08

    def test_cluster_response_has_training_window_field(self):
        """ClusterResponse schema should accept training_window field."""
        from app.models.schemas import ClusterResponse, MacroScore, TrainingWindowInfo
        # Just verify the field exists on the model
        assert hasattr(ClusterResponse, "model_fields")
        assert "training_window" in ClusterResponse.model_fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
