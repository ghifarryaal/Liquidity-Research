"""
cluster.py — FastAPI router for clustering endpoints.

Endpoints:
  GET /api/cluster/{index_name}   → Full index cluster analysis
  GET /api/stock/{ticker}         → Single stock OHLCV + indicators for charting
  GET /api/macro                  → Current macro risk score
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import numpy as np
from fastapi import APIRouter, HTTPException, Path, Query

from app.constants.lq45_tickers import LQ45_TICKER_SYMBOLS, LQ45_TICKER_META
from app.constants.kompas100_tickers import KOMPAS100_TICKER_SYMBOLS, KOMPAS100_TICKER_META
from app.constants.dbx_tickers import DBX_TICKER_SYMBOLS, DBX_TICKER_META
from app.models.schemas import (
    BacktestResult,
    ClusterResponse,
    MacroScore,
    OHLCVBar,
    PanicMeter,
    StockClusterResult,
    StockDetailResponse,
    TechnicalIndicators,
    TradePlan,
)
from app.services.clustering_engine import (
    CLUSTER_CONFIG,
    generate_reasoning,
    run_clustering,
)
from app.services.data_fetcher import fetch_index_ohlcv, fetch_single_ticker, get_latest_price_info
from app.services.feature_engineering import (
    build_feature_matrix,
    compute_all_indicators,
    compute_indicators,
)
from app.services.macro_weighting import apply_macro_penalty, get_macro_score, get_macro_features
from app.services.supervised_model import (
    train_predictor,
    predict_confidence,
    validate_30day,
    FEATURE_NAMES,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Index lookup table
# ---------------------------------------------------------------------------

INDEX_MAP: dict[str, tuple[list[str], dict]] = {
    "lq45": (LQ45_TICKER_SYMBOLS, LQ45_TICKER_META),
    "kompas100": (KOMPAS100_TICKER_SYMBOLS, KOMPAS100_TICKER_META),
    "dbx": (DBX_TICKER_SYMBOLS, DBX_TICKER_META),
}


# ---------------------------------------------------------------------------
# GET /api/cluster/{index_name}
# ---------------------------------------------------------------------------


@router.get(
    "/cluster/{index_name}",
    response_model=ClusterResponse,
    summary="Run ML clustering on an index",
    description=(
        "Fetches 6 months of OHLCV data for all stocks in the specified index, "
        "computes technical indicators, applies K-Means clustering, and returns "
        "cluster labels with actionable insights in Indonesian."
    ),
)
async def get_cluster_analysis(
    index_name: str = Path(
        ...,
        description="Index to analyse: 'lq45', 'kompas100', or 'dbx'",
        pattern="^(lq45|kompas100|dbx)$",
    ),
    period_days: int = Query(180, ge=30, le=365, description="Days of historical data"),
):
    index_name = index_name.lower()
    if index_name not in INDEX_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Index '{index_name}' not found. Use 'lq45' or 'kompas100'.",
        )

    tickers, meta = INDEX_MAP[index_name]

    # 1. Fetch OHLCV
    logger.info("[%s] Fetching OHLCV for %d tickers", index_name, len(tickers))
    try:
        ohlcv_map = await fetch_index_ohlcv(tickers, period_days)
    except Exception as exc:
        logger.error("OHLCV fetch failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Data fetch failed: {exc}")

    if not ohlcv_map:
        raise HTTPException(status_code=503, detail="No data returned from yfinance.")

    # 2. Feature engineering
    indicator_map = compute_all_indicators(ohlcv_map)
    valid_tickers, feature_matrix = build_feature_matrix(indicator_map)

    if len(valid_tickers) < 4:
        raise HTTPException(
            status_code=422,
            detail="Insufficient data for clustering (need ≥ 4 stocks with valid indicators).",
        )

    # 3. Clustering
    cluster_map = run_clustering(valid_tickers, feature_matrix)

    # 4. Macro score
    macro_raw = await get_macro_score()
    macro = MacroScore(
        volatility_penalty=macro_raw["volatility_penalty"],
        risk_adjusted_score=macro_raw["risk_adjusted_score"],
        macro_regime=macro_raw["macro_regime"],
        world_indices=macro_raw.get("world_indices", []),
        commodities=macro_raw.get("commodities", []),
        dxy_zscore=macro_raw.get("dxy_zscore"),
        us10y_zscore=macro_raw.get("us10y_zscore"),
        dxy_level=macro_raw.get("dxy_level"),
        us10y_level=macro_raw.get("us10y_level"),
    )

    # 5. Assemble stock results
    stocks: list[StockClusterResult] = []
    cluster_summary: dict[str, int] = {k: 0 for k in CLUSTER_CONFIG}

    from app.models.schemas import MacroSentimentDetail, SupervisedValidation
    from app.services.clustering_engine import calculate_risk_management
    from app.services.trade_plan_engine import calculate_trade_plan
    from app.services.backtest_engine import run_backtest

    # 3b. Macro features (DXY/US10Y) for supervised model
    macro_feats = await get_macro_features()
    dxy_zscore   = macro_feats.get("dxy_zscore",   0.0)
    us10y_zscore = macro_feats.get("us10y_zscore", 0.0)

    # 3c. Train supervised model on all OHLCV data
    logger.info("[%s] Training supervised predictor...", index_name)
    predictor = train_predictor(ohlcv_map, dxy_zscore=dxy_zscore, us10y_zscore=us10y_zscore)

    # 3d. Predict confidence score for each valid ticker
    confidence_scores = predict_confidence(
        predictor, indicator_map, dxy_zscore=dxy_zscore, us10y_zscore=us10y_zscore
    )

    # 3e. 30-day validation
    validation_raw = validate_30day(
        predictor, ohlcv_map, dxy_zscore=dxy_zscore, us10y_zscore=us10y_zscore
    )
    supervised_val = SupervisedValidation(
        total_predictions=validation_raw["total_predictions"],
        correct_predictions=validation_raw["correct_predictions"],
        accuracy=validation_raw["accuracy"],
        high_conviction_precision=validation_raw["high_conviction_precision"],
        avg_confidence=validation_raw["avg_confidence"],
    )

    for ticker in valid_tickers:
        cluster_info = cluster_map.get(ticker, {})
        ind = indicator_map.get(ticker, {})
        df = ohlcv_map.get(ticker)
        price_info = get_latest_price_info(df)
        stock_meta = meta.get(ticker, {"name": ticker, "sector": "Unknown"})

        raw_label = cluster_info.get("cluster_label", "Hold / Sideways")
        adjusted_label, confidence, macro_suffix = apply_macro_penalty(raw_label, macro_raw)
        # Override confidence with cluster confidence if better
        confidence = max(confidence, cluster_info.get("confidence", 0.65))

        strategy, reasoning = generate_reasoning(adjusted_label, ind, macro_suffix)
        
        # Risk Management
        risk = calculate_risk_management(
            adjusted_label, 
            price_info.get("current_price", 0.0), 
            ind.get("atr")
        )
        
        # Dynamic Trade Plan — wrap dict into TradePlan Pydantic model
        plan_raw = calculate_trade_plan(df, ind, adjusted_label, index_name=index_name)
        trade_plan_obj = TradePlan(**plan_raw) if plan_raw else None

        # Backtest Scorecard
        bt_raw = run_backtest(df)
        bt_obj = BacktestResult(**bt_raw) if bt_raw else None

        # ── Supervised ML: Confidence Score ──────────────────────────────
        raw_conf_score = confidence_scores.get(ticker, 0.5)
        is_high_conviction = raw_conf_score > 0.75

        indicators = TechnicalIndicators(
            rsi=ind.get("rsi"),
            macd=ind.get("macd"),
            macd_signal=ind.get("macd_signal"),
            macd_hist=ind.get("macd_hist"),
            ema_20=ind.get("ema_20"),
            ema_50=ind.get("ema_50"),
            bb_upper=ind.get("bb_upper"),
            bb_middle=ind.get("bb_middle"),
            bb_lower=ind.get("bb_lower"),
            bb_width=ind.get("bb_width"),
            atr=ind.get("atr"),
            volume_ratio=ind.get("volume_ratio"),
        )

        stocks.append(
            StockClusterResult(
                ticker=ticker,
                name=stock_meta.get("name", ticker),
                sector=stock_meta.get("sector", "Unknown"),
                current_price=price_info.get("current_price", 0.0),
                price_change_pct=price_info.get("price_change_pct", 0.0),
                week_change_pct=price_info.get("week_change_pct", 0.0),
                month_change_pct=price_info.get("month_change_pct", 0.0),
                volume=price_info.get("volume", 0),
                cluster_id=cluster_info.get("cluster_id", 0),
                cluster_label=adjusted_label,
                cluster_color=CLUSTER_CONFIG[adjusted_label]["color"],
                strategy=strategy,
                reasoning=reasoning,
                confidence=round(confidence, 3),
                confidence_score=raw_conf_score,
                is_high_conviction=is_high_conviction,
                take_profit=risk["take_profit"],
                stop_loss=risk["stop_loss"],
                trading_style=risk["trading_style"],
                trade_plan=trade_plan_obj,
                backtest=bt_obj,
                indicators=indicators,
                macro=macro,
            )
        )

        cluster_summary[adjusted_label] = cluster_summary.get(adjusted_label, 0) + 1

    # Sort by cluster label priority then confidence desc
    label_order = ["Buy the Dip", "Trending / Momentum", "Hold / Sideways", "High Risk / Avoid"]
    stocks.sort(key=lambda s: (label_order.index(s.cluster_label), -s.confidence))

    # Build Panic Meter from macro + market breadth
    bullish_count = cluster_summary.get("Buy the Dip", 0) + cluster_summary.get("Trending / Momentum", 0)
    breadth_bullish_pct = bullish_count / len(stocks) * 100 if stocks else 0.0
    panic_score = _compute_panic_score(macro_raw, breadth_bullish_pct)
    panic_meter = PanicMeter(
        score=panic_score["score"],
        label=panic_score["label"],
        vix_level=macro_raw.get("components", {}).get("^VIX"),
        dxy_level=macro_raw.get("components", {}).get("DX-Y.NYB"),
        breadth_bullish_pct=round(breadth_bullish_pct, 1),
        description=panic_score["description"],
    )

    # Build Macro Sentiment Detail (DXY + US10Y)
    macro_sentiment = _build_macro_sentiment(macro_raw)

    return ClusterResponse(
        index_name=index_name.upper(),
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        period_days=period_days,
        total_stocks=len(stocks),
        cluster_summary=cluster_summary,
        macro=macro,
        macro_sentiment=macro_sentiment,
        supervised_validation=supervised_val,
        panic_meter=panic_meter,
        stocks=stocks,
    )


# ---------------------------------------------------------------------------
# GET /api/stock/{ticker}
# ---------------------------------------------------------------------------


@router.get(
    "/stock/{ticker}",
    response_model=StockDetailResponse,
    summary="Get full OHLCV + indicator series for a single stock (for charting)",
)
async def get_stock_detail(
    ticker: str = Path(..., description="Yahoo Finance ticker, e.g. BBCA.JK"),
    period_days: int = Query(180, ge=30, le=365),
):
    ticker = ticker.upper()
    if not ticker.endswith(".JK"):
        ticker = f"{ticker}.JK"

    try:
        # 1. Fetch data
        df = await fetch_single_ticker(ticker, period_days)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        # 2. Compute indicators and features
        ind = compute_indicators(df)
        if not ind:
            raise HTTPException(status_code=422, detail=f"Could not compute indicators for {ticker}")

        # 3. Build OHLCV bars for charting
        ohlcv_bars = [
            OHLCVBar(
                time=str(row.name.date()),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
                volume=int(row["Volume"]),
            )
            for _, row in df.iterrows()
        ]

        series = ind.get("series", {})
        from app.services.data_fetcher import get_latest_price_info
        price_info = get_latest_price_info(df)

        # 4. Simplified Cluster Label for single stock (rule-based)
        # Aligned with clustering_engine.py logic for consistency
        rsi = ind.get("rsi", 50)
        macd = ind.get("macd")
        macd_sig = ind.get("macd_signal")
        ema20_gap = ind.get("ema20_gap_pct", 0)
        ema50_gap = ind.get("ema50_gap_pct", 0)
        bb_pos = ind.get("bb_position", 0.5)
        bb_width = ind.get("bb_width", 0)
        atr_pct = ind.get("atr_pct", 0)
        vol_ratio = ind.get("volume_ratio", 1.0)
        
        # Calculate momentum score (same as clustering_engine._map_centroids_to_labels)
        momentum = 0.0
        
        # RSI scoring
        if rsi > 60:
            momentum += 1.5
        elif rsi > 50:
            momentum += 0.5
        elif rsi < 35:
            momentum -= 1.5
        else:
            momentum -= 0.3
        
        # MACD scoring
        if macd is not None and macd_sig is not None:
            macd_str = macd - macd_sig
            momentum += float(np.clip(macd_str * 3, -1.5, 1.5))
        
        # EMA gap scoring (BOTH ema20 and ema50)
        momentum += float(np.clip(ema20_gap / 5.0, -1.0, 1.0))
        momentum += float(np.clip(ema50_gap / 8.0, -0.8, 0.8))
        
        # Bollinger Band position scoring
        momentum += (bb_pos - 0.5) * 1.5
        
        # Risk flags
        is_high_risk = (bb_width > 10.0) or (atr_pct > 4.0) or (vol_ratio > 3.0)
        is_dip = (rsi < 42) and (bb_pos < 0.35) and (ema20_gap < -1.0)
        
        # Determine label based on momentum and risk flags
        if momentum > 1.0:
            label = "Trending / Momentum"
        elif momentum < -1.0:
            # Low momentum: check if it's a safe dip or risky
            if is_high_risk:
                # High risk takes priority over dip signal
                label = "High Risk / Avoid"
            elif is_dip or rsi < 42:
                # Safe dip: low RSI + near lower BB + below EMA
                label = "Buy the Dip"
            else:
                # Low momentum but no clear dip signal
                label = "Buy the Dip"
        else:
            # Middle range momentum
            if is_high_risk:
                label = "High Risk / Avoid"
            else:
                label = "Hold / Sideways"

        from app.services.clustering_engine import CLUSTER_CONFIG, generate_reasoning, calculate_risk_management
        from app.services.trade_plan_engine import calculate_trade_plan
        from app.services.backtest_engine import run_backtest
        
        # Apply macro penalty to adjust label based on macro regime
        macro_raw = await get_macro_score()
        adjusted_label, macro_confidence, macro_suffix = apply_macro_penalty(label, macro_raw)
        
        strategy, reasoning = generate_reasoning(adjusted_label, ind, macro_suffix)
        risk = calculate_risk_management(adjusted_label, price_info.get("current_price", 0.0), ind.get("atr"))
        plan_raw = calculate_trade_plan(df, ind, adjusted_label, index_name="lq45")
        bt_raw = run_backtest(df)

        all_meta = {**LQ45_TICKER_META, **KOMPAS100_TICKER_META, **DBX_TICKER_META}
        meta = all_meta.get(ticker, {"name": ticker, "sector": "Unknown"})

        current_price = price_info.get("current_price") or 0.0
        price_change = price_info.get("price_change_pct") or 0.0
        week_change = price_info.get("week_change_pct") or 0.0
        month_change = price_info.get("month_change_pct") or 0.0
        vol = price_info.get("volume") or 0
        
        # Construct indicators safely (only non-null values)
        ind_data = {k: v for k, v in ind.items() if v is not None}
        indicators_obj = TechnicalIndicators(**ind_data)

        # ── XGBoost Prediction: Train on single ticker + get real confidence ──
        macro_feats = await get_macro_features()
        dxy_zscore   = macro_feats.get("dxy_zscore",   0.0)
        us10y_zscore = macro_feats.get("us10y_zscore", 0.0)

        # Train on this single ticker's data
        predictor = train_predictor(
            {ticker: df},
            dxy_zscore=dxy_zscore,
            us10y_zscore=us10y_zscore
        )

        # Get real XGBoost confidence score
        raw_conf_score = 0.5  # default fallback
        if predictor:
            conf_dict = predict_confidence(
                predictor,
                {ticker: ind},
                dxy_zscore=dxy_zscore,
                us10y_zscore=us10y_zscore
            )
            raw_conf_score = conf_dict.get(ticker, 0.5)

        is_high_conviction = raw_conf_score > 0.75

        return StockDetailResponse(
            ticker=ticker,
            name=meta.get("name", ticker),
            sector=meta.get("sector", "Unknown"),
            ohlcv=ohlcv_bars,
            ema_20_series=series.get("ema_20", []),
            ema_50_series=series.get("ema_50", []),
            bb_upper_series=series.get("bb_upper", []),
            bb_middle_series=series.get("bb_middle", []),
            bb_lower_series=series.get("bb_lower", []),
            current_price=current_price,
            price_change_pct=price_change,
            week_change_pct=week_change,
            month_change_pct=month_change,
            volume=vol,
            cluster_label=adjusted_label,
            cluster_color=CLUSTER_CONFIG.get(adjusted_label, {}).get("color", "#FFFFFF"),
            strategy=strategy,
            reasoning=reasoning,
            confidence=macro_confidence,
            take_profit=risk.get("take_profit"),
            stop_loss=risk.get("stop_loss"),
            trading_style=risk.get("trading_style", "Swing Trade"),
            trade_plan=TradePlan(**plan_raw) if plan_raw else None,
            backtest=BacktestResult(**bt_raw) if bt_raw else None,
            confidence_score=raw_conf_score,
            is_high_conviction=is_high_conviction,
            indicators=indicators_obj
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        err_detail = f"Error in get_stock_detail: {str(e)}\n{traceback.format_exc()}"
        logger.error(err_detail)
        raise HTTPException(status_code=500, detail=err_detail)


# ---------------------------------------------------------------------------
# GET /api/macro
# ---------------------------------------------------------------------------


@router.get(
    "/macro",
    response_model=MacroScore,
    summary="Get current global macro risk score",
)
async def get_macro():
    macro_raw = await get_macro_score()
    return MacroScore(
        volatility_penalty=macro_raw["volatility_penalty"],
        risk_adjusted_score=macro_raw["risk_adjusted_score"],
        macro_regime=macro_raw["macro_regime"],
        world_indices=macro_raw.get("world_indices", []),
        commodities=macro_raw.get("commodities", []),
        dxy_zscore=macro_raw.get("dxy_zscore"),
        us10y_zscore=macro_raw.get("us10y_zscore"),
        dxy_level=macro_raw.get("dxy_level"),
        us10y_level=macro_raw.get("us10y_level"),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _compute_panic_score(macro_raw: dict, breadth_bullish_pct: float) -> dict:
    """
    Combine macro penalty + market breadth into a 0-100 Panic Score.
    High score = high fear / hold-cash territory.
    """
    penalty = macro_raw.get("volatility_penalty", 0.5)

    # Breadth: fewer bullish stocks = more fear
    breadth_fear = max(0.0, (50.0 - breadth_bullish_pct) / 50.0)

    # Weighted average: 60% macro, 40% breadth
    raw = (penalty * 0.6) + (breadth_fear * 0.4)
    score = round(raw * 100, 1)

    if score < 25:
        label = "Tenang"
        desc  = "Kondisi pasar stabil. Pelaku pasar optimis. Peluang entry masih terbuka."
    elif score < 50:
        label = "Waspada"
        desc  = "Mulai ada tekanan. Pertimbangkan untuk mengurangi ukuran posisi dan pasang Stop Loss ketat."
    elif score < 75:
        label = "Panik"
        desc  = "Ketidakpastian tinggi. Disarankan menahan kas dan menunggu konfirmasi arah pasar."
    else:
        label = "Extreme Fear"
        desc  = "Pasar dalam kondisi sangat tertekan. Hindari buka posisi baru. Cash is King."

    return {"score": score, "label": label, "description": desc}


def _build_macro_sentiment(macro_raw: dict):
    """
    Build a MacroSentimentDetail object from the raw macro score dict.
    Generates trend labels and an Indonesian-language IDX impact explanation.
    """
    from app.models.schemas import MacroSentimentDetail

    dxy_zscore   = macro_raw.get("dxy_zscore",   0.0)
    us10y_zscore = macro_raw.get("us10y_zscore", 0.0)
    dxy_level    = macro_raw.get("dxy_level",    0.5)
    us10y_level  = macro_raw.get("us10y_level",  0.5)

    # ── Trend labels ──────────────────────────────────────────────────────
    if dxy_zscore > 0.5:
        dxy_trend = "Strengthening"
    elif dxy_zscore < -0.5:
        dxy_trend = "Weakening"
    else:
        dxy_trend = "Neutral"

    if us10y_zscore > 0.5:
        us10y_trend = "Rising"
    elif us10y_zscore < -0.5:
        us10y_trend = "Falling"
    else:
        us10y_trend = "Neutral"

    # ── IDX Impact explanation (Indonesian) ───────────────────────────────
    parts: list[str] = []

    # DXY impact
    if dxy_trend == "Strengthening":
        parts.append(
            "Dolar AS sedang menguat (DXY naik). Hal ini cenderung menekan mata uang Rupiah "
            "dan membebani saham-saham yang bergantung pada impor bahan baku."
        )
    elif dxy_trend == "Weakening":
        parts.append(
            "Dolar AS sedang melemah (DXY turun). Ini berpotensi positif bagi Rupiah "
            "dan memberikan ruang bagi Bank Indonesia untuk menjaga suku bunga stabil."
        )
    else:
        parts.append("Dolar AS bergerak sideways — tekanan valas terhadap IDX relatif netral.")

    # US10Y impact
    if us10y_trend == "Rising":
        parts.append(
            "Yield obligasi AS 10 tahun sedang naik. Kondisi ini biasanya mendorong capital outflow "
            "dari emerging market termasuk Indonesia, yang dapat menekan IHSG dalam jangka pendek."
        )
    elif us10y_trend == "Falling":
        parts.append(
            "Yield obligasi AS 10 tahun sedang turun. Ini mengurangi daya tarik aset safe-haven AS "
            "dan berpotensi mendorong aliran modal masuk ke pasar saham emerging market seperti IDX."
        )
    else:
        parts.append("Yield obligasi AS 10 tahun stabil — dampak terhadap aliran modal ke IDX masih netral.")

    impact_on_idx = " ".join(parts)

    return MacroSentimentDetail(
        dxy_zscore=round(dxy_zscore, 4),
        us10y_zscore=round(us10y_zscore, 4),
        dxy_level=round(dxy_level, 4),
        us10y_level=round(us10y_level, 4),
        dxy_trend=dxy_trend,
        us10y_trend=us10y_trend,
        impact_on_idx=impact_on_idx,
    )

