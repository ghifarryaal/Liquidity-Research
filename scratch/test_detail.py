
import asyncio
import pandas as pd
from app.services.data_fetcher import fetch_single_ticker
from app.services.feature_engineering import compute_indicators
from app.services.trade_plan_engine import calculate_trade_plan
from app.services.backtest_engine import run_backtest
from app.services.clustering_engine import generate_reasoning, calculate_risk_management
from app.models.schemas import TradePlan, BacktestResult, StockDetailResponse, TechnicalIndicators

async def test_stock_detail(ticker):
    print(f"Testing detail for {ticker}...")
    df = await fetch_single_ticker(ticker, 180)
    if df is None or df.empty:
        print("Empty DF")
        return
        
    price_info = {
        "current_price":    float(df["Close"].iloc[-1]),
        "price_change_pct": float(((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100),
        "volume":           int(df["Volume"].iloc[-1]),
        "week_change_pct":  0.0,
        "month_change_pct": 0.0,
    }
    
    ind = compute_indicators(df)
    label = "Hold / Sideways"
    
    strategy, reasoning = generate_reasoning(label, ind)
    
    # Correct call
    risk = calculate_risk_management(label, price_info["current_price"], ind.get("atr"))
    print(f"Risk management: {risk}")
    
    plan_raw = calculate_trade_plan(df, ind, label, index_name="lq45")
    bt_raw = run_backtest(df)
    
    resp = StockDetailResponse(
        ticker=ticker,
        name="Test",
        sector="Test",
        ohlcv=[],
        ema_20_series=[],
        ema_50_series=[],
        bb_upper_series=[],
        bb_middle_series=[],
        bb_lower_series=[],
        current_price=price_info["current_price"],
        price_change_pct=price_info["price_change_pct"],
        week_change_pct=price_info["week_change_pct"],
        month_change_pct=price_info["month_change_pct"],
        volume=price_info["volume"],
        cluster_label=label,
        cluster_color="#FFFFFF",
        strategy=strategy,
        reasoning=reasoning,
        confidence=0.85,
        take_profit=risk["take_profit"],
        stop_loss=risk["stop_loss"],
        trading_style=risk["trading_style"],
        trade_plan=TradePlan(**plan_raw) if plan_raw else None,
        backtest=BacktestResult(**bt_raw) if bt_raw else None,
        confidence_score=0.78,
        is_high_conviction=True,
        indicators=TechnicalIndicators(**ind)
    )
    print("Full StockDetailResponse validation SUCCESS")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    asyncio.run(test_stock_detail("BBCA.JK"))
