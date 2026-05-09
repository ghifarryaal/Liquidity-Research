"""
mock_data.py — Realistic mock OHLCV data generator for when yfinance is unavailable.

Generates synthetic but realistic-looking price series using geometric Brownian motion,
preserving real-world IDR price ranges for each ticker.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Known approximate price ranges for LQ45/KOMPAS100 stocks (IDR)
PRICE_SEEDS = {
    "BBCA.JK": 9800, "BBRI.JK": 4800, "BMRI.JK": 6200, "BBNI.JK": 5400,
    "TLKM.JK": 3200, "ASII.JK": 5000, "UNVR.JK": 2700, "KLBF.JK": 1600,
    "GOTO.JK": 70,   "BUKA.JK": 100,  "ICBP.JK": 11000,"INDF.JK": 7500,
    "GGRM.JK": 22000,"HMSP.JK": 1000, "SMGR.JK": 5500, "INTP.JK": 6000,
    "PTBA.JK": 3600, "ITMG.JK": 27000,"MEDC.JK": 1400, "HRUM.JK": 1800,
    "MIKA.JK": 2800, "SIDO.JK": 650,  "UNTR.JK": 27000,"TBIG.JK": 2600,
    "TOWR.JK": 1000, "PGAS.JK": 1700, "EXCL.JK": 2200, "MNCN.JK": 900,
    "SCMA.JK": 750,  "PWON.JK": 480,  "BSDE.JK": 1100, "CTRA.JK": 1200,
    "MAPI.JK": 1600, "MDKA.JK": 2200, "INCO.JK": 4500, "AMMN.JK": 8500,
    "MBMA.JK": 800,  "ADRO.JK": 3800, "CPIN.JK": 4700, "JPFA.JK": 1550,
    "INKP.JK": 8500, "TKIM.JK": 6500, "BRPT.JK": 1050, "AKRA.JK": 1500,
    "AMRT.JK": 2800, "ISAT.JK": 2400, "JSMR.JK": 4200, "BNGA.JK": 1400,
    "BJBR.JK": 1100, "LPKR.JK": 210,  "SMRA.JK": 680,  "WIKA.JK": 550,
    "WSKT.JK": 180,  "PTPP.JK": 620,  "ESSA.JK": 640,  "LSIP.JK": 1250,
    "SSMS.JK": 1050, "MYOR.JK": 2700, "ULTJ.JK": 1680, "SRTG.JK": 2600,
    "TINS.JK": 1050, "PGEO.JK": 1300, "PANI.JK": 8000, "NCKL.JK": 1150,
    "HEAL.JK": 1600, "BFIN.JK": 1400, "DOID.JK": 580,  "INDY.JK": 1450,
    "RAJA.JK": 1900, "TPIA.JK": 9400, "LINK.JK": 3100, "POWR.JK": 1550,
    "BTPS.JK": 1350, "ERAA.JK": 670,  "WIFI.JK": 580,  "DMAS.JK": 270,
    "KRAS.JK": 390,  "KAEF.JK": 920,  "ELSA.JK": 480,  "DSNG.JK": 740,
    "MIDI.JK": 680,  "PTRO.JK": 2000, "RALS.JK": 640,  "ACES.JK": 800,
    "MPPA.JK": 420,  "PJAA.JK": 680,  "BKSL.JK": 102,  "EMTK.JK": 340,
    "SSIA.JK": 650,  "TOTL.JK": 550,  "AUTO.JK": 2150, "ARNA.JK": 700,
    "BMTR.JK": 185,  "MAHA.JK": 980,  "AGRO.JK": 1250, "BELI.JK": 128,
    "HRTA.JK": 1850, "NISP.JK": 1250, "BNII.JK": 480,  "WSBP.JK": 92,
}

DEFAULT_PRICE = 2000


def generate_mock_ohlcv(ticker: str, n_days: int = 180) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data using Geometric Brownian Motion.
    Seed is derived from ticker name for reproducibility.
    """
    seed = int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16) % (2**31)
    rng = np.random.default_rng(seed)

    base_price = PRICE_SEEDS.get(ticker, DEFAULT_PRICE)

    # GBM parameters
    mu = rng.uniform(-0.001, 0.002)   # drift
    sigma = rng.uniform(0.015, 0.03)  # volatility

    # Generate trading day dates
    end_date = datetime.now(tz=timezone.utc)
    dates = []
    cur = end_date - timedelta(days=int(n_days * 1.5))
    while len(dates) < n_days:
        if cur.weekday() < 5:  # Mon-Fri
            dates.append(cur.date())
        cur += timedelta(days=1)
    dates = dates[:n_days]

    # Geometric Brownian Motion
    dt = 1 / 252
    returns = rng.normal(mu * dt, sigma * np.sqrt(dt), n_days)

    # Add regime changes for realism
    regime_start = rng.integers(40, 100)
    regime_len   = rng.integers(20, 50)
    returns[regime_start:regime_start + regime_len] += rng.uniform(-0.003, 0.003)

    prices = base_price * np.exp(np.cumsum(returns))

    # Build OHLCV
    opens   = prices * (1 + rng.uniform(-0.005, 0.005, n_days))
    intraday_range = np.abs(rng.normal(0, sigma * 0.6, n_days))
    highs   = np.maximum(prices, opens) * (1 + intraday_range)
    lows    = np.minimum(prices, opens) * (1 - intraday_range)
    closes  = prices

    # Volume: correlated with volatility
    avg_vol = rng.integers(5_000_000, 100_000_000)
    vols    = avg_vol * (1 + rng.exponential(0.5, n_days))
    vols    = vols * (1 + 3 * np.abs(returns) / sigma)  # spike on big moves

    df = pd.DataFrame({
        "Open":   opens.round(0),
        "High":   highs.round(0),
        "Low":    lows.round(0),
        "Close":  closes.round(0),
        "Volume": vols.astype(int),
    }, index=pd.DatetimeIndex(
        [datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc) for d in dates]
    ))

    return df


def generate_mock_batch(tickers: list[str], n_days: int = 180) -> dict[str, pd.DataFrame]:
    """Generate mock OHLCV for a batch of tickers."""
    return {ticker: generate_mock_ohlcv(ticker, n_days) for ticker in tickers}
