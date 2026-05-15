"""
Service layer tests for LiquidityResearch
"""
import pytest
import pandas as pd
import numpy as np
from app.services.feature_engineering import calculate_indicators
from app.services.clustering_engine import cluster_stocks
from app.services.backtest_engine import backtest_strategy


def test_calculate_indicators():
    """Test technical indicator calculation"""
    # Create sample OHLCV data
    dates = pd.date_range('2024-01-01', periods=100)
    df = pd.DataFrame({
        'Open': np.random.uniform(100, 110, 100),
        'High': np.random.uniform(110, 120, 100),
        'Low': np.random.uniform(90, 100, 100),
        'Close': np.random.uniform(100, 110, 100),
        'Volume': np.random.uniform(1000000, 2000000, 100)
    }, index=dates)
    
    indicators = calculate_indicators(df)
    
    # Check all required indicators are present
    assert 'rsi' in indicators
    assert 'macd' in indicators
    assert 'macd_signal' in indicators
    assert 'bb_upper' in indicators
    assert 'bb_middle' in indicators
    assert 'bb_lower' in indicators
    assert 'ema_20' in indicators
    assert 'ema_50' in indicators
    assert 'atr' in indicators
    assert 'volume_ratio' in indicators
    
    # Check RSI is in valid range
    assert 0 <= indicators['rsi'] <= 100
    
    # Check ATR is positive
    assert indicators['atr'] > 0


def test_cluster_stocks():
    """Test stock clustering"""
    # Create sample feature data
    features = pd.DataFrame({
        'rsi': np.random.uniform(30, 70, 50),
        'macd': np.random.uniform(-1, 1, 50),
        'volume_ratio': np.random.uniform(0.5, 2.0, 50),
        'price_change_pct': np.random.uniform(-5, 5, 50),
        'volatility': np.random.uniform(0.01, 0.05, 50)
    })
    
    clusters = cluster_stocks(features, n_clusters=6)
    
    # Check cluster assignments
    assert len(clusters) == 50
    assert all(0 <= c < 6 for c in clusters)
    
    # Check we have multiple clusters
    assert len(set(clusters)) > 1


def test_backtest_strategy():
    """Test backtesting engine"""
    # Create sample price data
    dates = pd.date_range('2024-01-01', periods=100)
    prices = pd.Series(
        np.random.uniform(100, 110, 100),
        index=dates
    )
    
    # Simple strategy: buy at 100, sell at 110
    entry_price = 100
    stop_loss = 95
    take_profit = 110
    
    result = backtest_strategy(
        prices=prices,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit
    )
    
    # Check backtest result structure
    assert 'total_trades' in result
    assert 'win_rate' in result
    assert 'profit_factor' in result
    assert 'max_drawdown' in result
    assert 'total_return' in result
    
    # Check values are reasonable
    assert 0 <= result['win_rate'] <= 100
    assert result['profit_factor'] >= 0
    assert result['max_drawdown'] <= 0


def test_feature_engineering_edge_cases():
    """Test feature engineering with edge cases"""
    # Test with minimal data
    dates = pd.date_range('2024-01-01', periods=20)
    df = pd.DataFrame({
        'Open': [100] * 20,
        'High': [105] * 20,
        'Low': [95] * 20,
        'Close': [100] * 20,
        'Volume': [1000000] * 20
    }, index=dates)
    
    indicators = calculate_indicators(df)
    
    # Should handle flat prices gracefully
    assert indicators is not None
    assert 'rsi' in indicators


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
