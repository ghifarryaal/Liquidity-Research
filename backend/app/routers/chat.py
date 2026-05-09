"""
LiquidityResearch — AI Mentor Chat Router
POST /api/chat  →  Streaming SSE via Gemini 1.5 Flash
"""

import os
import json
import time
import logging
import hashlib
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import google.generativeai as genai
from pydantic import BaseModel
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter()

# ---------------------------------------------------------------------------
# In-Memory Caches
# ---------------------------------------------------------------------------

# Definition cache: key = sha256(question), value = full AI response string
# TTL = 24 h, max 512 entries (common educational questions)
_DEFINITION_CACHE: TTLCache = TTLCache(maxsize=512, ttl=86_400)

# Rate-limit tracker: key = session_id, value = list[float] (timestamps)
_RATE_TRACKER: TTLCache = TTLCache(maxsize=10_000, ttl=60)

RATE_LIMIT = 10          # max requests per 60-second window
CACHE_KEYWORDS = {       # lowercase fragments that trigger definition caching
    "apa itu", "jelaskan", "definisi", "pengertian", "apa yang dimaksud",
    "bagaimana cara kerja", "tolong jelaskan",
}

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str   # 'user' | 'model'
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: dict = {}          # Page context (ticker, cluster_label, indicators…)
    session_id: str = "anonymous"

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
Identitas:
Kamu adalah "Liquidity Mentor" — seorang edukator keuangan berpengalaman yang berfokus pada Bursa Efek Indonesia (BEI/IDX). Kamu adalah bagian dari platform LiquidityResearch, sebuah alat analisis berbasis Machine Learning untuk saham LQ45 dan KOMPAS 100.

Ekosistem LiquidityResearch yang HARUS kamu pahami:
1. **Clustering ML** — Saham dikelompokkan menjadi 4 klaster:
   - "Buy the Dip": Saham oversold dengan potensi reversal (RSI rendah, BB lower band).
   - "Trending": Saham dalam uptrend kuat (MACD bullish, EMA20 > EMA50, volume tinggi).
   - "Sideways / Accumulation": Pergerakan terbatas, cocok untuk akumulasi bertahap.
   - "High Risk / Avoid": Volatilitas sangat tinggi, sinyal bearish dominan.
2. **Stop Loss (SL) berbasis ATR** — SL dihitung: Harga Entry − (1.5 × ATR14). ATR digunakan karena mencerminkan "keramaian pasar" (volatilitas aktual), bukan sekadar persentase tetap.
3. **Take Profit (TP) berbasis Fibonacci** — TP dihitung menggunakan Fibonacci extension dari swing low/high terakhir, dengan target utama di level 1.272× dan 1.618×, atau Risk/Reward minimal 1:2.
4. **Indikator Kunci**: RSI (14), MACD, Bollinger Bands, EMA20/EMA50, Volume Ratio, ATR (14).

Gaya Bahasa & Analogi:
- Gunakan Bahasa Indonesia yang profesional namun mudah dipahami pemula.
- Gunakan analogi pasar IDX:
  * "Market maker" → "bandar pasar"
  * "Volatility" → "keramaian pasar" atau "gejolak harga"
  * "Oversold" → "sudah banyak dijual, jenuh jual"
  * "Uptrend" → "tren naik"
  * "Blue chip" → "saham papan utama"
  * "Liquidity" → "likuiditas" atau "kemudahan jual beli"
- Saat menjelaskan konsep matematis, selalu sertakan contoh numerik sederhana.
- Gunakan format Markdown: **bold** untuk istilah penting, bullet list untuk poin-poin, dan tabel kecil bila relevan.

Batasan Keras (WAJIB dipatuhi):
1. ❌ DILARANG memberikan saran langsung Beli/Jual/Tahan (Buy/Sell/Hold) untuk saham tertentu.
2. ❌ DILARANG memprediksi harga di masa depan secara spesifik.
3. ✅ SELALU jelaskan LOGIKA dan KONSEP di balik angka.
4. ✅ SELALU sertakan disclaimer singkat jika relevan.

Context Awareness:
Kamu akan menerima konteks halaman saat ini (ticker, klaster, indikator). Gunakan informasi ini untuk membuat penjelasan lebih relevan dan spesifik.

Disclaimer standar (sisipkan saat membahas strategi/level harga):
> ⚠️ *Analisis ini bersifat edukatif dan bukan ajakan jual/beli. Trading saham mengandung risiko kehilangan modal.*
"""

# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

def _check_rate_limit(session_id: str) -> bool:
    """Returns True if request is allowed, False if rate-limited."""
    now = time.time()
    timestamps: list = _RATE_TRACKER.get(session_id, [])
    # Keep only timestamps within the last 60 seconds
    timestamps = [t for t in timestamps if now - t < 60]
    if len(timestamps) >= RATE_LIMIT:
        return False
    timestamps.append(now)
    _RATE_TRACKER[session_id] = timestamps
    return True

# ---------------------------------------------------------------------------
# Cache Key
# ---------------------------------------------------------------------------

def _is_cacheable(question: str) -> bool:
    """Heuristic: cache pure definition/explanation questions."""
    q = question.lower().strip()
    return any(q.startswith(kw) for kw in CACHE_KEYWORDS)

def _cache_key(question: str) -> str:
    return hashlib.sha256(question.strip().lower().encode()).hexdigest()

# ---------------------------------------------------------------------------
# Gemini Streaming Generator
# ---------------------------------------------------------------------------

async def _stream_from_gemini(
    messages: list[ChatMessage], context: dict
) -> AsyncGenerator[str, None]:
    """Yields SSE-formatted chunks from Gemini 1.5 Flash."""
    if not GEMINI_API_KEY:
        yield _sse("⚠️ API Key Gemini belum dikonfigurasi. Hubungi administrator platform.")
        yield _sse("[DONE]")
        return

    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction=SYSTEM_PROMPT,
        )

        # Build history (all messages except the last)
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content],
            })

        chat_session = model.start_chat(history=history)

        # Enrich last user message with page context
        last_content = messages[-1].content
        if context:
            ctx_lines = ["[KONTEKS HALAMAN SAAT INI]"]
            if "ticker" in context:
                ctx_lines.append(f"- Ticker: {context['ticker']}")
            if "cluster_label" in context:
                ctx_lines.append(f"- Klaster ML: {context['cluster_label']}")
            if "indicators" in context:
                ind = context["indicators"]
                if "rsi" in ind:
                    ctx_lines.append(f"- RSI (14): {round(ind['rsi'], 1)}")
                if "atr" in ind:
                    ctx_lines.append(f"- ATR (14): {round(ind['atr'], 0)} IDR")
                if "macd" in ind:
                    ctx_lines.append(f"- MACD: {round(ind['macd'], 2)}")
            if "trade_plan" in context:
                tp = context["trade_plan"]
                if "stop_loss" in tp:
                    ctx_lines.append(f"- Stop Loss: {tp['stop_loss']}")
                if "take_profit_1" in tp:
                    ctx_lines.append(f"- Take Profit 1: {tp['take_profit_1']}")
            full_prompt = "\n".join(ctx_lines) + "\n\n" + last_content
        else:
            full_prompt = last_content

        response = chat_session.send_message(full_prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield _sse(chunk.text)

        yield _sse("[DONE]")

    except Exception as exc:
        logger.error("Gemini stream error: %s", exc)
        yield _sse(f"\n\n⚠️ **Mentor mengalami gangguan koneksi.** Silakan coba lagi. `({exc})`")
        yield _sse("[DONE]")

# ---------------------------------------------------------------------------
# SSE Helpers
# ---------------------------------------------------------------------------

def _sse(data: str) -> str:
    """Wrap text as a proper SSE data event."""
    return f"data: {json.dumps(data)}\n\n"

async def _stream_cached(text: str) -> AsyncGenerator[str, None]:
    """Replay a cached response word-by-word for a consistent UX."""
    words = text.split(" ")
    for i, word in enumerate(words):
        chunk = word if i == 0 else " " + word
        yield _sse(chunk)
    yield _sse("[DONE]")

# ---------------------------------------------------------------------------
# Endpoint: POST /api/chat
# ---------------------------------------------------------------------------

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Streaming SSE chat endpoint for Liquidity Mentor.

    - Enforces 10 req/min per session_id.
    - Caches responses for common definition questions (24-hour TTL).
    - Streams tokens as Server-Sent Events.
    """
    # 1. Rate limit check
    if not _check_rate_limit(req.session_id):
        raise HTTPException(
            status_code=429,
            detail="Terlalu banyak permintaan. Silakan tunggu sebentar sebelum bertanya lagi. (Limit: 10/menit)",
        )

    if not req.messages:
        raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong.")

    last_question = req.messages[-1].content

    # 2. Definition cache check (only for context-free, definition queries)
    if _is_cacheable(last_question) and not req.context:
        key = _cache_key(last_question)
        if key in _DEFINITION_CACHE:
            logger.info("Cache HIT for definition: %s…", last_question[:40])
            return StreamingResponse(
                _stream_cached(_DEFINITION_CACHE[key]),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "X-Cache": "HIT",
                },
            )

        # Cache MISS: stream from Gemini, collect full response for caching
        async def _stream_and_cache() -> AsyncGenerator[str, None]:
            collected = []
            async for chunk in _stream_from_gemini(req.messages, req.context):
                data = json.loads(chunk.split("data: ", 1)[1])
                if data != "[DONE]":
                    collected.append(data)
                yield chunk
            _DEFINITION_CACHE[key] = "".join(collected)
            logger.info("Cache SET for definition: %s…", last_question[:40])

        return StreamingResponse(
            _stream_and_cache(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # 3. Regular streaming (context-aware queries)
    return StreamingResponse(
        _stream_from_gemini(req.messages, req.context),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Endpoint: GET /api/chat/status
# ---------------------------------------------------------------------------

@router.get("/chat/status")
async def chat_status():
    """Returns cache and rate-limit diagnostics."""
    return {
        "definition_cache_entries": len(_DEFINITION_CACHE),
        "active_sessions_tracked": len(_RATE_TRACKER),
        "rate_limit_per_minute": RATE_LIMIT,
        "gemini_configured": bool(GEMINI_API_KEY),
    }
