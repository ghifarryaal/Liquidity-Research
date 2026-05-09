"""
data_fetcher.py — Direct Yahoo Finance v8 API fetcher (bypasses yfinance rate-limiting).

Fetches real-time OHLCV data using direct HTTP calls to the Yahoo Finance chart API.
Falls back to GBM mock data only if the API is completely unreachable.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import concurrent.futures

import httpx
import pandas as pd
import numpy as np
from cachetools import TTLCache

from app.services.mock_data import generate_mock_batch

logger = logging.getLogger(__name__)

# TTL cache: 15 minutes for stock data (fresh enough for intraday research)
_cache: TTLCache = TTLCache(maxsize=20, ttl=900)

BATCH_SIZE = 50  # concurrent requests per batch
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def fetch_index_ohlcv(
    tickers: list[str],
    period_days: int = 180,
) -> dict[str, pd.DataFrame]:
    """
    Download OHLCV data for a list of tickers via direct Yahoo Finance v8 API.

    Returns:
        dict mapping ticker -> DataFrame[Open, High, Low, Close, Volume]
    """
    cache_key = (tuple(sorted(tickers)), period_days)
    if cache_key in _cache:
        logger.info("Cache hit for %d tickers", len(tickers))
        return _cache[cache_key]

    end_ts = int(datetime.now(tz=timezone.utc).timestamp())
    start_ts = int((datetime.now(tz=timezone.utc) - timedelta(days=period_days)).timestamp())

    logger.info("Fetching %d tickers via YF v8 API [%s days]", len(tickers), period_days)

    result: dict[str, pd.DataFrame] = {}

    # Batched async fetch
    batches = [tickers[i:i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]

    async with httpx.AsyncClient(headers=_HEADERS, timeout=30.0, follow_redirects=True) as client:
        for batch in batches:
            tasks = [_fetch_ticker(client, ticker, start_ts, end_ts) for ticker in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for ticker, res in zip(batch, batch_results):
                if isinstance(res, Exception):
                    logger.warning("Failed %s: %s", ticker, res)
                elif res is not None:
                    result[ticker] = res

    logger.info("Loaded %d / %d tickers from YF v8 API", len(result), len(tickers))

    # Fallback to mock data only if ALL requests failed
    if not result:
        logger.warning(
            "Yahoo Finance v8 returned 0 tickers — falling back to synthetic GBM data."
        )
        result = generate_mock_batch(tickers, period_days)
        logger.info("Mock data generated for %d tickers", len(result))

    _cache[cache_key] = result
    return result


async def fetch_single_ticker(
    ticker: str,
    period_days: int = 180,
) -> Optional[pd.DataFrame]:
    """Fetch OHLCV for a single ticker."""
    data = await fetch_index_ohlcv([ticker], period_days)
    return data.get(ticker)


# ---------------------------------------------------------------------------
# Internal async fetcher
# ---------------------------------------------------------------------------


async def _fetch_ticker(
    client: httpx.AsyncClient,
    ticker: str,
    start_ts: int,
    end_ts: int,
) -> Optional[pd.DataFrame]:
    """Fetch a single ticker from Yahoo Finance v8 chart API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {
        "period1": start_ts,
        "period2": end_ts,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }

    try:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            logger.warning("YF v8 %s status %d", ticker, r.status_code)
            return None

        data = r.json()
        chart = data.get("chart", {})
        error = chart.get("error")
        if error:
            logger.warning("YF v8 error for %s: %s", ticker, error)
            return None

        results = chart.get("result")
        if not results:
            return None

        result = results[0]
        timestamps = result.get("timestamp")
        if not timestamps:
            return None

        quote = result["indicators"]["quote"][0]

        # Prefer adjusted close, fall back to regular close
        adj = result["indicators"].get("adjclose")
        close_arr = adj[0]["adjclose"] if adj else quote["close"]

        df = pd.DataFrame(
            {
                "Open":   quote["open"],
                "High":   quote["high"],
                "Low":    quote["low"],
                "Close":  close_arr,
                "Volume": quote["volume"],
            },
            index=pd.to_datetime(timestamps, unit="s", utc=True).tz_convert("Asia/Jakarta"),
        )
        df.index.name = "Date"

        # Clean up
        df = df.dropna(subset=["Close"])
        df["Volume"] = df["Volume"].fillna(0).astype(np.int64)

        if len(df) < 30:
            logger.warning("Too few bars for %s: %d", ticker, len(df))
            return None

        return df

    except Exception as exc:
        logger.warning("Fetch failed %s: %s", ticker, exc)
        return None


# ---------------------------------------------------------------------------
# Price helpers
# ---------------------------------------------------------------------------


def get_latest_price_info(df: pd.DataFrame) -> dict:
    """Extract latest price and change % from an OHLCV DataFrame."""
    if df is None or df.empty:
        return {
            "current_price": 0.0,
            "price_change_pct": 0.0,
            "week_change_pct": 0.0,
            "month_change_pct": 0.0,
            "volume": 0,
        }

    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) >= 2 else latest

    current_price = float(latest["Close"])
    prev_close    = float(prev["Close"])
    change_pct    = ((current_price - prev_close) / prev_close * 100) if prev_close else 0.0

    week_bar  = df.iloc[-6]  if len(df) >= 6  else df.iloc[0]
    month_bar = df.iloc[-22] if len(df) >= 22 else df.iloc[0]

    week_change  = (current_price - float(week_bar["Close"]))  / float(week_bar["Close"])  * 100
    month_change = (current_price - float(month_bar["Close"])) / float(month_bar["Close"]) * 100

    return {
        "current_price":    round(current_price, 2),
        "price_change_pct": round(change_pct, 2),
        "week_change_pct":  round(week_change, 2),
        "month_change_pct": round(month_change, 2),
        "volume":           int(latest["Volume"]),
    }
