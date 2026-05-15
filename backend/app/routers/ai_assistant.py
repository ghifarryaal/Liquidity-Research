"""
AI Assistant API endpoints - powered by Google Gemini
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from app.services.ai_assistant import get_ai_response
from app.services.data_fetcher import fetch_single_ticker, get_latest_price_info
from app.services.feature_engineering import compute_indicators
from app.services.clustering_engine import CLUSTER_CONFIG, generate_reasoning, calculate_risk_management
from app.services.trade_plan_engine import calculate_trade_plan
from app.services.backtest_engine import run_backtest
from app.constants.lq45_tickers import LQ45_TICKER_META
from app.constants.kompas100_tickers import KOMPAS100_TICKER_META
from app.constants.dbx_tickers import DBX_TICKER_META

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


class QuestionRequest(BaseModel):
    ticker: str
    question: str
    conversation_history: Optional[List[Dict]] = None


class AIResponse(BaseModel):
    response: str
    confidence: float
    type: str
    ticker: str
    timestamp: str


@router.post("/ask", response_model=AIResponse)
async def ask_ai_assistant(request: QuestionRequest):
    """
    Ask AI assistant (powered by Google Gemini) about a specific stock.

    Example questions:
    - "Kenapa saham ini masuk cluster Momentum?"
    - "Apa risikonya kalau saya beli sekarang?"
    - "Kapan waktu yang tepat untuk entry?"
    - "Berapa target profit yang realistis?"
    - "Strategi apa yang cocok untuk saham ini?"
    """
    ticker = request.ticker.upper()
    if not ticker.endswith(".JK"):
        ticker = f"{ticker}.JK"

    try:
        # Fetch real stock data
        df = await fetch_single_ticker(ticker, period_days=180)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Data tidak ditemukan untuk {ticker}")

        # Compute indicators
        ind = compute_indicators(df)
        if not ind:
            raise HTTPException(status_code=422, detail=f"Tidak dapat menghitung indikator untuk {ticker}")

        # Determine cluster label
        rsi = ind.get("rsi", 50)
        bb_pos = ind.get("bb_position", 0.5)
        if rsi > 60 and bb_pos > 0.6:
            label = "Trending / Momentum"
        elif rsi < 40 and bb_pos < 0.4:
            label = "Buy the Dip"
        elif rsi > 75 or ind.get("bb_width", 0) > 15:
            label = "High Risk / Avoid"
        else:
            label = "Hold / Sideways"

        # Get price info
        price_info = get_latest_price_info(df)
        current_price = price_info.get("current_price", 0.0)

        # Generate reasoning and trade plan
        strategy, reasoning = generate_reasoning(label, ind)
        risk = calculate_risk_management(label, current_price, ind.get("atr"))
        plan_raw = calculate_trade_plan(df, ind, label, index_name="lq45")
        bt_raw = run_backtest(df)

        # Get stock metadata
        all_meta = {**LQ45_TICKER_META, **KOMPAS100_TICKER_META, **DBX_TICKER_META}
        meta = all_meta.get(ticker, {"name": ticker, "sector": "Unknown"})

        # Build stock data context for Gemini
        stock_data = {
            "ticker": ticker,
            "name": meta.get("name", ticker),
            "sector": meta.get("sector", "Unknown"),
            "current_price": current_price,
            "price_change_pct": price_info.get("price_change_pct", 0.0),
            "cluster_label": label,
            "confidence": 0.85,
            "reasoning": reasoning,
            "trading_style": risk.get("trading_style", "Swing Trade"),
            "indicators": {
                "rsi": ind.get("rsi"),
                "macd": ind.get("macd"),
                "macd_signal": ind.get("macd_signal"),
                "volume_ratio": ind.get("volume_ratio"),
                "atr": ind.get("atr"),
                "ema_20": ind.get("ema_20"),
                "ema_50": ind.get("ema_50"),
                "bb_upper": ind.get("bb_upper"),
                "bb_lower": ind.get("bb_lower"),
            },
            "trade_plan": plan_raw or {
                "entry_price": current_price,
                "stop_loss": risk.get("stop_loss"),
                "take_profit_1": risk.get("take_profit"),
                "take_profit_2": risk.get("take_profit", current_price) * 1.05 if risk.get("take_profit") else None,
                "risk_reward_ratio": 2.0,
            },
            "backtest": bt_raw or {
                "win_rate": 0,
                "profit_factor": 0,
                "max_drawdown": 0,
                "total_return": 0,
            },
        }

        # Get Gemini AI response
        ai_result = get_ai_response(
            question=request.question,
            stock_data=stock_data,
            conversation_history=request.conversation_history,
        )

        return AIResponse(
            response=ai_result["response"],
            confidence=ai_result["confidence"],
            type=ai_result["type"],
            ticker=ticker,
            timestamp=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions/{ticker}")
async def get_question_suggestions(ticker: str):
    """Get suggested questions for a stock"""
    ticker_display = ticker.upper().replace(".JK", "")
    return {
        "ticker": ticker_display,
        "suggestions": [
            {
                "category": "Analisis",
                "questions": [
                    f"Kenapa {ticker_display} masuk cluster ini?",
                    f"Apa sinyal teknikal utama untuk {ticker_display}?",
                    f"Seberapa kuat tren {ticker_display} saat ini?",
                ]
            },
            {
                "category": "Risiko",
                "questions": [
                    f"Apa risiko utama trading {ticker_display}?",
                    f"Berapa potensi kerugian maksimal?",
                    f"Bagaimana performa historis {ticker_display}?",
                ]
            },
            {
                "category": "Eksekusi",
                "questions": [
                    f"Kapan waktu terbaik untuk entry {ticker_display}?",
                    f"Berapa target profit yang realistis?",
                    f"Strategi apa yang cocok untuk {ticker_display}?",
                ]
            }
        ]
    }
