"""
API endpoint tests for LiquidityResearch backend
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "LiquidityResearch API" in response.json()["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_market_overview_lq45():
    """Test market overview endpoint for LQ45"""
    response = client.get("/api/market-overview?index=lq45")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
    assert "macro_sentiment" in data
    assert "panic_meter" in data
    assert len(data["stocks"]) > 0


def test_market_overview_kompas100():
    """Test market overview endpoint for KOMPAS100"""
    response = client.get("/api/market-overview?index=kompas100")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
    assert len(data["stocks"]) > 0


def test_stock_detail():
    """Test stock detail endpoint"""
    response = client.get("/api/stock/BBCA.JK?period_days=180")
    assert response.status_code == 200
    data = response.json()
    assert "ticker" in data
    assert "current_price" in data
    assert "indicators" in data
    assert "cluster_label" in data
    assert "reasoning" in data
    assert "trade_plan" in data
    assert "backtest" in data


def test_stock_detail_invalid_ticker():
    """Test stock detail with invalid ticker"""
    response = client.get("/api/stock/INVALID.JK")
    assert response.status_code in [404, 500]  # Should handle gracefully


def test_clusters_endpoint():
    """Test clusters endpoint"""
    response = client.get("/api/clusters?index=lq45")
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
    assert len(data["clusters"]) > 0
    
    # Check cluster structure
    first_cluster = data["clusters"][0]
    assert "label" in first_cluster
    assert "stocks" in first_cluster
    assert "count" in first_cluster


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.get("/api/market-overview?index=lq45")
    assert "access-control-allow-origin" in response.headers


def test_api_response_time():
    """Test API response time is reasonable"""
    import time
    start = time.time()
    response = client.get("/api/market-overview?index=lq45")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 5.0  # Should respond within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
