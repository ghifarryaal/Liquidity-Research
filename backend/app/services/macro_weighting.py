"""
macro_weighting.py — Global macro risk scoring via direct Yahoo Finance v8 API.

Proxies used (all via direct HTTP, no paid API needed):
- ^VIX          : CBOE Volatility Index
- ^TNX          : US 10-Year Treasury Yield
- DX-Y.NYB      : US Dollar Index
- GC=F          : Gold Futures
- ^JKSE         : IDX Composite
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
import numpy as np
import pandas as pd
from cachetools import TTLCache

logger = logging.getLogger(__name__)

_macro_cache: TTLCache = TTLCache(maxsize=5, ttl=1800)
_macro_feat_cache: TTLCache = TTLCache(maxsize=2, ttl=1800)

# Proxy symbol -> weight (positive = risk-on factor, negative = risk-off factor)
MACRO_PROXIES: dict[str, float] = {
    "^VIX":     0.35,   # High VIX = more risk
    "^TNX":     0.25,   # High yields = risk pressure
    "DX-Y.NYB": 0.20,   # Strong USD = EM risk-off
    "GC=F":    -0.10,   # Gold rise = safe-haven demand (risk-off)
    "^JKSE":   -0.10,   # IHSG falling = domestic risk-off
}

GLOBAL_INDICES: dict[str, str] = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "^DJI":  "Dow Jones",
    "^N225": "Nikkei 225",
    "^HSI":  "Hang Seng",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX",
    "^FCHI": "CAC 40",
    "^STI": "STI Index",
    "^AXJO": "ASX 200",
}

COMMODITIES: dict[str, str] = {
    "CL=F":  "Crude Oil",
    "GC=F":  "Gold",
    "SI=F":  "Silver",
    "BZ=F":  "Brent Oil",
    "HG=F":  "Copper",
    "NI=F":  "Nickel",
    "NG=F":  "Nat Gas",
    "ZC=F":  "Corn",
    "CC=F":  "Cocoa",
    "KC=F":  "Coffee",
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


async def get_macro_score() -> dict:
    """Compute the current macro risk score (cached 30 min)."""
    if "macro_score" in _macro_cache:
        return _macro_cache["macro_score"]
    result = await _compute_macro_score()
    _macro_cache["macro_score"] = result
    return result


async def _compute_macro_score() -> dict:
    end_ts   = int(datetime.now(tz=timezone.utc).timestamp())
    start_ts = int((datetime.now(tz=timezone.utc) - timedelta(days=60)).timestamp())

    components: dict[str, float] = {}
    weighted_sum = 0.0
    total_weight = 0.0

    async with httpx.AsyncClient(headers=_HEADERS, timeout=20.0) as client:
        # Fetching Macro Proxies (for scoring)
        macro_tasks = {
            proxy: _fetch_macro_series(client, proxy, start_ts, end_ts)
            for proxy in MACRO_PROXIES
        }
        
        # Fetching World Indices
        index_tasks = {
            symbol: _fetch_macro_series(client, symbol, start_ts, end_ts)
            for symbol in GLOBAL_INDICES
        }
        
        # Fetching Commodities
        comm_tasks = {
            symbol: _fetch_macro_series(client, symbol, start_ts, end_ts)
            for symbol in COMMODITIES
        }

        all_results = await asyncio.gather(
            *[asyncio.gather(*macro_tasks.values(), return_exceptions=True),
              asyncio.gather(*index_tasks.values(), return_exceptions=True),
              asyncio.gather(*comm_tasks.values(), return_exceptions=True)]
        )
    
    macro_results, index_results, comm_results = all_results

    # 1. Process Macro Proxies for Score
    for proxy, series_or_exc in zip(macro_tasks.keys(), macro_results):
        weight = MACRO_PROXIES[proxy]
        if isinstance(series_or_exc, (Exception, type(None))): continue
        series = series_or_exc
        if len(series) < 10: continue
        try:
            roll_mean = series.rolling(30, min_periods=5).mean().iloc[-1]
            roll_std  = series.rolling(30, min_periods=5).std().iloc[-1]
            latest    = series.iloc[-1]
            z = (latest - roll_mean) / roll_std if roll_std > 0 else 0.0
            z_norm = float((np.clip(z, -3, 3) + 3) / 6.0)
            components[proxy] = round(z_norm, 4)
            weighted_sum  += weight * z_norm
            total_weight  += abs(weight)
        except: continue

    # 2. Process World Indices
    world_indices = []
    for symbol, series_or_exc in zip(index_tasks.keys(), index_results):
        if isinstance(series_or_exc, (Exception, type(None))): continue
        series = series_or_exc
        if len(series) < 2: continue
        world_indices.append({
            "symbol": symbol,
            "name": GLOBAL_INDICES[symbol],
            "price": float(round(series.iloc[-1], 2)),
            "change": float(round((series.iloc[-1] / series.iloc[-2] - 1) * 100, 2)) if series.iloc[-2] else 0.0
        })

    # 3. Process Commodities
    commodities = []
    for symbol, series_or_exc in zip(comm_tasks.keys(), comm_results):
        if isinstance(series_or_exc, (Exception, type(None))): continue
        series = series_or_exc
        if len(series) < 2: continue
        commodities.append({
            "symbol": symbol,
            "name": COMMODITIES[symbol],
            "price": float(round(series.iloc[-1], 2)),
            "change": float(round((series.iloc[-1] / series.iloc[-2] - 1) * 100, 2)) if series.iloc[-2] else 0.0
        })

    penalty = 0.5
    if total_weight > 0:
        penalty = float(np.clip((weighted_sum / total_weight + 1) / 2, 0.0, 1.0))

    # Extract DXY and US10Y z-scores for supervised model
    dxy_zscore   = float(components.get("DX-Y.NYB", 0.5) * 6 - 3)  # back to z-score range
    us10y_zscore = float(components.get("^TNX",     0.5) * 6 - 3)

    return {
        "volatility_penalty":  round(penalty, 4),
        "risk_adjusted_score": round(penalty, 4),
        "macro_regime":        _map_regime(penalty),
        "components":          components,
        "world_indices":       world_indices,
        "commodities":         commodities,
        # Raw macro feature signals for supervised model
        "dxy_zscore":          round(dxy_zscore, 4),
        "us10y_zscore":        round(us10y_zscore, 4),
        "dxy_level":           round(float(components.get("DX-Y.NYB", 0.5)), 4),
        "us10y_level":         round(float(components.get("^TNX",     0.5)), 4),
    }


async def get_macro_features() -> dict:
    """
    Return DXY and US10Y z-scores for use as supervised model features.
    Cached alongside the main macro score.
    """
    score = await get_macro_score()
    return {
        "dxy_zscore":   score.get("dxy_zscore",   0.0),
        "us10y_zscore": score.get("us10y_zscore", 0.0),
        "dxy_level":    score.get("dxy_level",    0.0),
        "us10y_level":  score.get("us10y_level",  0.0),
    }


async def _fetch_macro_series(
    client: httpx.AsyncClient,
    symbol: str,
    start_ts: int,
    end_ts: int,
) -> pd.Series | None:
    """Fetch Close prices for a macro proxy via Yahoo Finance v8 API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": start_ts,
        "period2": end_ts,
        "interval": "1d",
        "events": "history",
    }
    try:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            return None
        data   = r.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return None
        ts    = result[0].get("timestamp", [])
        close = result[0]["indicators"]["quote"][0].get("close", [])
        if not ts or not close:
            return None
        s = pd.Series(
            [float(v) if v is not None else float("nan") for v in close],
            index=pd.to_datetime(ts, unit="s", utc=True),
            name=symbol,
        ).dropna()
        return s if len(s) > 0 else None
    except Exception as exc:
        logger.warning("Fetch macro %s error: %s", symbol, exc)
        return None


def apply_macro_penalty(cluster_label: str, macro_score: dict) -> tuple[str, float, str]:
    """Adjust cluster confidence/label based on macro regime."""
    penalty = macro_score.get("volatility_penalty", 0.5)
    regime  = macro_score.get("macro_regime", "Neutral")

    if regime == "Risk-Off" and penalty > 0.65:
        if cluster_label == "Buy the Dip":
            return (
                cluster_label, 0.55,
                " Namun, kondisi makro global sedang Risk-Off — pertimbangkan menunggu konfirmasi."
            )
        elif cluster_label == "Trending / Momentum":
            return (
                "Hold / Sideways", 0.50,
                " Tren positif mungkin tertekan oleh kondisi pasar global yang volatile."
            )

    if regime == "Risk-On" and penalty < 0.35:
        if cluster_label == "Hold / Sideways":
            return (
                cluster_label, 0.70,
                " Kondisi makro mendukung — pantau untuk potensi breakout."
            )

    return (cluster_label, 0.65, "")


def _map_regime(penalty: float) -> str:
    if penalty < 0.35:
        return "Risk-On"
    elif penalty < 0.65:
        return "Neutral"
    return "Risk-Off"


def _neutral_score() -> dict:
    return {
        "volatility_penalty":  0.50,
        "risk_adjusted_score": 0.50,
        "macro_regime":        "Neutral",
        "components":          {},
        "world_indices":       [],
        "commodities":         [],
    }
