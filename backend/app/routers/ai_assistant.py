"""
AI Assistant API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.services.ai_assistant import get_ai_response
from app.services.data_fetcher import fetch_stock_data
from app.services.feature_engineering import calculate_indicators
from app.services.clustering_engine import predict_cluster
from app.services.supervised_model import predict_confidence_and_reasoning

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


class QuestionRequest(BaseModel):
    """Request model for AI questions"""
    ticker: str
    question: str
    conversation_history: Optional[List[Dict]] = None


class AIResponse(BaseModel):
    """Response model for AI answers"""
    response: str
    confidence: float
    type: str
    ticker: str
    timestamp: str


@router.post("/ask", response_model=AIResponse)
async def ask_ai_assistant(request: QuestionRequest):
    """
    Ask AI assistant about a specific stock
    
    Example questions:
    - "Why is this stock classified as Momentum?"
    - "What are the risks?"
    - "When should I enter?"
    - "What are the profit targets?"
    - "What strategy should I use?"
    """
    try:
        # Fetch stock data
        df = fetch_stock_data(request.ticker, period_days=180)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")
        
        # Calculate indicators
        indicators = calculate_indicators(df)
        
        # Get ML predictions
        cluster_label = predict_cluster(indicators)
        confidence, reasoning = predict_confidence_and_reasoning(indicators, cluster_label)
        
        # Prepare stock data context
        stock_data = {
            "ticker": request.ticker,
            "name": "Stock Name",  # Would fetch from metadata
            "current_price": df['Close'].iloc[-1],
            "cluster_label": cluster_label,
            "confidence": confidence,
            "reasoning": reasoning,
            "indicators": indicators,
            "trade_plan": {
                "entry_price": df['Close'].iloc[-1],
                "stop_loss": df['Close'].iloc[-1] * 0.95,
                "take_profit_1": df['Close'].iloc[-1] * 1.05,
                "take_profit_2": df['Close'].iloc[-1] * 1.10,
                "risk_reward_ratio": 2.0
            },
            "backtest": {
                "win_rate": 65.0,
                "max_drawdown": -8.5
            },
            "trading_style": "Swing Trading"
        }
        
        # Get AI response
        ai_response = get_ai_response(
            question=request.question,
            stock_data=stock_data,
            conversation_history=request.conversation_history
        )
        
        from datetime import datetime
        
        return AIResponse(
            response=ai_response["response"],
            confidence=ai_response["confidence"],
            type=ai_response["type"],
            ticker=request.ticker,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions/{ticker}")
async def get_question_suggestions(ticker: str):
    """
    Get suggested questions for a stock
    """
    suggestions = [
        {
            "category": "Analysis",
            "questions": [
                f"Why is {ticker} classified in this cluster?",
                f"What are the key technical signals for {ticker}?",
                f"How confident is the AI about {ticker}?"
            ]
        },
        {
            "category": "Risk Management",
            "questions": [
                f"What are the risks of trading {ticker}?",
                f"What's the maximum loss I could face?",
                f"How does {ticker} perform historically?"
            ]
        },
        {
            "category": "Execution",
            "questions": [
                f"When should I enter {ticker}?",
                f"What are the profit targets for {ticker}?",
                f"What strategy works best for {ticker}?"
            ]
        }
    ]
    
    return {"ticker": ticker, "suggestions": suggestions}
