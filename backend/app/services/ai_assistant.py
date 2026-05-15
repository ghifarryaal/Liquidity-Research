"""
AI-Powered Stock Analysis Assistant using Google Gemini
Provides intelligent, context-aware responses about stock analysis
"""
import os
import logging
from typing import Dict, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# System Prompt for Stock Analysis Assistant
# ---------------------------------------------------------------------------

STOCK_ANALYSIS_PROMPT = """
Kamu adalah "Liquidity Analyst" — AI analyst saham Indonesia dari platform LiquidityResearch.
Kamu menganalisis saham LQ45 dan KOMPAS100 menggunakan data Machine Learning dan indikator teknikal.

KONTEKS PLATFORM:
- Platform menggunakan K-Means clustering untuk mengelompokkan saham
- Cluster: "Buy the Dip", "Momentum", "Breakout", "Reversal", "Consolidation", "Avoid"
- Confidence score dari Random Forest classifier (0-100%)
- Indikator: RSI(14), MACD, Bollinger Bands, EMA20/50, ATR(14), Volume Ratio
- Trade plan: Entry, Stop Loss (ATR-based), Take Profit (Fibonacci-based)
- Backtest: Win rate, Profit factor, Max drawdown

GAYA RESPONS:
- Bahasa Indonesia yang profesional dan mudah dipahami
- Gunakan data spesifik dari konteks yang diberikan
- Format dengan Markdown (bold, bullet points)
- Berikan insight yang actionable dan edukatif
- Maksimal 3-4 paragraf atau bullet points

BATASAN:
- Jangan rekomendasikan beli/jual secara langsung
- Selalu jelaskan logika di balik analisis
- Sertakan disclaimer singkat jika membahas strategi

Jawab pertanyaan user berdasarkan data saham yang diberikan dalam konteks.
"""


def build_stock_context(stock_data: Dict) -> str:
    """Build a rich context string from stock data for Gemini"""
    ticker = stock_data.get("ticker", "").replace(".JK", "")
    name = stock_data.get("name", "")
    cluster = stock_data.get("cluster_label", "")
    confidence = stock_data.get("confidence", 0)
    reasoning = stock_data.get("reasoning", "")
    current_price = stock_data.get("current_price", 0)
    price_change = stock_data.get("price_change_pct", 0)
    trading_style = stock_data.get("trading_style", "")

    indicators = stock_data.get("indicators", {})
    trade_plan = stock_data.get("trade_plan", {})
    backtest = stock_data.get("backtest", {})

    ctx = f"""
=== DATA SAHAM: {ticker} ({name}) ===

KLASIFIKASI ML:
- Cluster: {cluster}
- Confidence: {confidence * 100:.0f}%
- Trading Style: {trading_style}
- AI Reasoning: {reasoning}

HARGA:
- Harga Saat Ini: Rp {current_price:,.0f}
- Perubahan: {price_change:+.2f}%

INDIKATOR TEKNIKAL:
- RSI (14): {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}
- MACD Signal: {indicators.get('macd_signal', 'N/A')}
- Volume Ratio: {indicators.get('volume_ratio', 'N/A')}x
- ATR (14): Rp {indicators.get('atr', 'N/A'):,.0f} (jika numerik)
- EMA 20: Rp {indicators.get('ema_20', 'N/A'):,.0f} (jika numerik)
- EMA 50: Rp {indicators.get('ema_50', 'N/A'):,.0f} (jika numerik)
- BB Upper: Rp {indicators.get('bb_upper', 'N/A'):,.0f} (jika numerik)
- BB Lower: Rp {indicators.get('bb_lower', 'N/A'):,.0f} (jika numerik)

TRADE PLAN:
- Entry: Rp {trade_plan.get('entry_price', 'N/A'):,.0f} (jika numerik)
- Stop Loss: Rp {trade_plan.get('stop_loss', 'N/A'):,.0f} (jika numerik)
- Take Profit 1: Rp {trade_plan.get('take_profit_1', 'N/A'):,.0f} (jika numerik)
- Take Profit 2: Rp {trade_plan.get('take_profit_2', 'N/A'):,.0f} (jika numerik)
- Risk/Reward: 1:{trade_plan.get('risk_reward_ratio', 'N/A')}

BACKTEST (180 hari):
- Win Rate: {backtest.get('win_rate', 'N/A')}%
- Profit Factor: {backtest.get('profit_factor', 'N/A')}
- Max Drawdown: {backtest.get('max_drawdown', 'N/A')}%
- Total Return: {backtest.get('total_return', 'N/A')}%
"""
    return ctx


def get_ai_response(
    question: str,
    stock_data: Dict,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Get AI response using Google Gemini with full stock context

    Args:
        question: User's question
        stock_data: Complete stock analysis data from ML pipeline
        conversation_history: Previous messages for multi-turn conversation

    Returns:
        Dict with response, confidence, and type
    """
    if not GEMINI_API_KEY:
        return {
            "response": "⚠️ AI Assistant tidak tersedia. API Key belum dikonfigurasi.",
            "confidence": 0,
            "type": "error"
        }

    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=STOCK_ANALYSIS_PROMPT,
        )

        # Build conversation history
        history = []
        if conversation_history:
            for msg in conversation_history:
                history.append({
                    "role": "user" if msg.get("role") == "user" else "model",
                    "parts": [msg.get("content", "")],
                })

        chat = model.start_chat(history=history)

        # Build full prompt with stock context
        stock_context = build_stock_context(stock_data)
        full_prompt = f"{stock_context}\n\n=== PERTANYAAN USER ===\n{question}"

        response = chat.send_message(full_prompt)
        response_text = response.text

        # Determine response type from question
        question_lower = question.lower()
        if any(w in question_lower for w in ["why", "kenapa", "mengapa", "alasan"]):
            resp_type = "reasoning"
        elif any(w in question_lower for w in ["risk", "risiko", "bahaya", "rugi"]):
            resp_type = "risk_analysis"
        elif any(w in question_lower for w in ["when", "kapan", "entry", "masuk"]):
            resp_type = "entry_timing"
        elif any(w in question_lower for w in ["target", "profit", "tp", "untung"]):
            resp_type = "profit_targets"
        elif any(w in question_lower for w in ["strategy", "strategi", "cara"]):
            resp_type = "strategy"
        else:
            resp_type = "general"

        return {
            "response": response_text,
            "confidence": stock_data.get("confidence", 0.8),
            "type": resp_type
        }

    except Exception as e:
        logger.error("Gemini AI assistant error: %s", e)
        return {
            "response": f"⚠️ Terjadi kesalahan saat menghubungi AI: {str(e)}",
            "confidence": 0,
            "type": "error"
        }
