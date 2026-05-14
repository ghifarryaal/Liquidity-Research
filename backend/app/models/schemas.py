"""
Pydantic response models for the LiquidityResearch API.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Technical Indicator snapshot
# ---------------------------------------------------------------------------


class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = Field(None, description="RSI(14)")
    macd: Optional[float] = Field(None, description="MACD line")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    macd_hist: Optional[float] = Field(None, description="MACD histogram")
    ema_20: Optional[float] = Field(None, description="EMA(20)")
    ema_50: Optional[float] = Field(None, description="EMA(50)")
    bb_upper: Optional[float] = Field(None, description="Bollinger Band upper")
    bb_middle: Optional[float] = Field(None, description="Bollinger Band middle / SMA20")
    bb_lower: Optional[float] = Field(None, description="Bollinger Band lower")
    bb_width: Optional[float] = Field(None, description="Bollinger Band width %")
    atr: Optional[float] = Field(None, description="Average True Range (14)")
    volume_ratio: Optional[float] = Field(
        None, description="Current volume / 20-day avg volume"
    )


# ---------------------------------------------------------------------------
# Macro / risk scoring
# ---------------------------------------------------------------------------


class GlobalMarketItem(BaseModel):
    symbol: str
    name: str
    price: float
    change: float


class MacroScore(BaseModel):
    volatility_penalty: float = Field(
        ...,
        description=(
            "Score 0-1. Higher = more macro risk. "
            "Derived from VIX proxy and bond spread proxies."
        ),
    )
    risk_adjusted_score: float = Field(
        ...,
        description="Net risk score after applying macro penalty.",
    )
    macro_regime: str = Field(
        ...,
        description="One of: 'Risk-On', 'Neutral', 'Risk-Off'",
    )
    world_indices: list[GlobalMarketItem] = Field(default_factory=list)
    commodities: list[GlobalMarketItem] = Field(default_factory=list)
    # Macro feature signals (for display and supervised model)
    dxy_zscore: Optional[float] = Field(None, description="DXY z-score vs 30-day mean")
    us10y_zscore: Optional[float] = Field(None, description="US10Y z-score vs 30-day mean")
    dxy_level: Optional[float] = Field(None, description="DXY normalized level (0-1)")
    us10y_level: Optional[float] = Field(None, description="US10Y normalized level (0-1)")


# ---------------------------------------------------------------------------
# Macro Sentiment Detail (for frontend card)
# ---------------------------------------------------------------------------


class MacroSentimentDetail(BaseModel):
    dxy_zscore: float = Field(0.0, description="DXY z-score: positive = strong USD")
    us10y_zscore: float = Field(0.0, description="US10Y z-score: positive = rising yields")
    dxy_level: float = Field(0.0, description="DXY normalized level")
    us10y_level: float = Field(0.0, description="US10Y normalized level")
    dxy_trend: str = Field("Neutral", description="'Strengthening' | 'Weakening' | 'Neutral'")
    us10y_trend: str = Field("Neutral", description="'Rising' | 'Falling' | 'Neutral'")
    impact_on_idx: str = Field("", description="AI explanation of impact on IDX in Indonesian")


# ---------------------------------------------------------------------------
# Supervised Model Validation
# ---------------------------------------------------------------------------


class SupervisedValidation(BaseModel):
    total_predictions: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0
    high_conviction_precision: float = 0.0
    avg_confidence: float = 0.0


# ---------------------------------------------------------------------------
# Trade Plan
# ---------------------------------------------------------------------------


class TradePlan(BaseModel):
    entry_range: str
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    rr_ratio: str
    status: str  # Strong Buy, Speculative, High Risk
    lot_recommendation: int
    scaling_strategy: str
    is_confirmed: bool
    logic_explanation: str


# ---------------------------------------------------------------------------
# Backtest Scorecard
# ---------------------------------------------------------------------------


class BacktestResult(BaseModel):
    total_trades: int = Field(0, description="Number of signals simulated")
    winning_trades: int = Field(0, description="Number of winning trades")
    win_rate: float = Field(0.0, description="Win rate 0-1")
    avg_rr_achieved: float = Field(0.0, description="Average risk/reward achieved")
    max_drawdown_pct: float = Field(0.0, description="Worst single trade %")
    best_trade_pct: float = Field(0.0, description="Best single trade %")
    worst_trade_pct: float = Field(0.0, description="Worst single trade %")


# ---------------------------------------------------------------------------
# Panic Meter
# ---------------------------------------------------------------------------


class PanicMeter(BaseModel):
    score: float = Field(..., description="Panic level 0-100 (100 = extreme fear)")
    label: str = Field(..., description="Calm | Waspada | Panik | Extreme Fear")
    vix_level: Optional[float] = None
    dxy_level: Optional[float] = None
    breadth_bullish_pct: float = Field(0.0, description="% stocks in bullish cluster")
    description: str = Field("", description="Plain-language Indonesian explanation")


# ---------------------------------------------------------------------------
# Per-stock cluster result
# ---------------------------------------------------------------------------


class StockClusterResult(BaseModel):
    ticker: str
    name: str = Field("", description="Company name")
    sector: str = Field("", description="GICS sector")

    # Price data
    current_price: float
    price_change_pct: float = Field(..., description="1-day % change")
    week_change_pct: float = Field(0.0, description="5-day % change")
    month_change_pct: float = Field(0.0, description="1-month % change")
    volume: int = Field(0, description="Latest volume")
    market_cap: Optional[float] = None

    # Cluster output
    cluster_id: int
    cluster_label: str = Field(
        ...,
        description=(
            "Human-readable cluster label: "
            "'Buy the Dip' | 'Trending / Momentum' | 'Hold / Sideways' | 'High Risk / Avoid'"
        ),
    )
    cluster_color: str = Field(
        ..., description="Hex color for the cluster badge"
    )

    # Recommendation
    strategy: str = Field(
        ..., description="Short actionable strategy in Indonesian"
    )
    reasoning: str = Field(
        ..., description="Plain-language reasoning in Indonesian (for educational UI)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Cluster confidence score 0-1"
    )

    # ── Supervised ML Output ─────────────────────────────────────────────
    confidence_score: float = Field(
        0.5, ge=0.0, le=1.0,
        description="XGBoost/RF probability of +5% gain within 5 days (0-1)"
    )
    is_high_conviction: bool = Field(
        False,
        description="True if confidence_score > 0.75 — 'High Conviction Setup'"
    )

    # Risk Management & Style
    take_profit: Optional[float] = Field(None, description="Recommended TP price")
    stop_loss: Optional[float] = Field(None, description="Recommended SL price")
    trading_style: str = Field("Swing Trade", description="Day Trade | Swing Trade | Investasi")

    # Dynamic Trade Plan
    trade_plan: Optional[TradePlan] = None

    # Backtest Scorecard
    backtest: Optional[BacktestResult] = None

    # Technical snapshot
    indicators: TechnicalIndicators
    macro: MacroScore


# ---------------------------------------------------------------------------
# Index-level cluster response
# ---------------------------------------------------------------------------


class ClusterResponse(BaseModel):
    index_name: str
    generated_at: str = Field(..., description="ISO-8601 UTC timestamp")
    period_days: int = Field(180, description="Days of historical data used")
    total_stocks: int
    cluster_summary: dict[str, int] = Field(
        ..., description="Cluster label -> count"
    )
    macro: MacroScore
    macro_sentiment: Optional[MacroSentimentDetail] = None
    supervised_validation: Optional[SupervisedValidation] = None
    panic_meter: Optional[PanicMeter] = None
    stocks: list[StockClusterResult]


# ---------------------------------------------------------------------------
# Stock detail (OHLCV for charting)
# ---------------------------------------------------------------------------


class OHLCVBar(BaseModel):
    time: str  # ISO date string "YYYY-MM-DD"
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockDetailResponse(BaseModel):
    ticker: str
    name: str
    sector: str = ""
    ohlcv: list[OHLCVBar]
    ema_20_series: list[dict] = Field(default_factory=list)
    ema_50_series: list[dict] = Field(default_factory=list)
    bb_upper_series: list[dict] = Field(default_factory=list)
    bb_middle_series: list[dict] = Field(default_factory=list)
    bb_lower_series: list[dict] = Field(default_factory=list)
    
    # Pricing & Performance
    current_price: float
    price_change_pct: float
    week_change_pct: float
    month_change_pct: float
    volume: int

    # Cluster Analysis
    cluster_label: str
    cluster_color: str
    strategy: str
    reasoning: str
    confidence: float
    
    # Risk Management
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trading_style: str = "Swing Trade"

    # Trade Plan & Backtest
    trade_plan: Optional[TradePlan] = None
    backtest: Optional[BacktestResult] = None
    
    # Supervised ML Output
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    is_high_conviction: bool = False
    
    indicators: TechnicalIndicators
