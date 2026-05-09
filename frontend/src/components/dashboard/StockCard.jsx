'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ClusterBadge from './ClusterBadge';
import ReasoningBox from '@/components/education/ReasoningBox';
import CandlestickChart from '@/components/charts/CandlestickChart';
import { LabelWithTooltip } from '@/components/education/Tooltip';
import { useStockDetail } from '@/hooks/useStockDetail';
import { formatPrice, formatPct, formatIndicator, formatVolume, changeClass, rsiLabel } from '@/lib/formatters';
import { CLUSTER_CONFIG } from '@/constants/clusterConfig';

export default function StockCard({ stock, index }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = CLUSTER_CONFIG[stock.cluster_label] ?? CLUSTER_CONFIG['Hold / Sideways'];

  // Fetch chart data only when expanded
  const { ohlcv, ema20, ema50, bbUpper, bbMiddle, bbLower, isLoading: chartLoading } =
    useStockDetail(expanded ? stock.ticker : null);

  const rsi = rsiLabel(stock.indicators?.rsi);
  const macdBull = stock.indicators?.macd != null &&
    stock.indicators?.macd_signal != null &&
    stock.indicators.macd > stock.indicators.macd_signal;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.4, ease: 'easeOut' }}
      className={`glass-card group cursor-pointer overflow-hidden ${expanded ? 'col-span-1 sm:col-span-2 xl:col-span-3' : ''}`}
      style={{
        borderColor: expanded ? cfg.borderColor : 'rgba(255,255,255,0.07)',
        boxShadow: expanded
          ? `0 0 40px ${cfg.glowColor}, 0 4px 30px rgba(0,0,0,0.5)`
          : undefined,
      }}
      onClick={() => !expanded && setExpanded(true)}
      role="button"
      aria-expanded={expanded}
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && setExpanded(v => !v)}
    >
      {/* Top glow accent on hover */}
      <div
        className="absolute top-0 left-0 right-0 h-px transition-opacity duration-500"
        style={{
          background: `linear-gradient(90deg, transparent, ${cfg.color}, transparent)`,
          opacity: expanded ? 1 : 0,
        }}
      />

      <div className="p-5">
        {/* ── Header row ──────────────────────────────────────── */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-white font-mono tracking-tight">
                {stock.ticker.replace('.JK', '')}
              </span>
              <span className="text-xs text-slate-500 hidden sm:inline truncate max-w-[140px]">
                {stock.name}
              </span>
            </div>
            <span className="text-xs text-slate-600 mt-0.5 block">
              {stock.sector}
            </span>
          </div>
          <div className="flex-shrink-0">
            <ClusterBadge label={stock.cluster_label} />
          </div>
        </div>

        {/* ── Price row ────────────────────────────────────────── */}
        <div className="flex items-end gap-3 mb-4">
          <span className="text-2xl font-bold text-white font-mono tabular-nums">
            {formatPrice(stock.current_price)}
          </span>
          <div className="flex flex-col items-start pb-0.5">
            <span className={`text-sm font-semibold font-mono ${changeClass(stock.price_change_pct)}`}>
              {formatPct(stock.price_change_pct)}
            </span>
            <span className="text-xs text-slate-600">1D</span>
          </div>

          {/* 5D & 1M */}
          <div className="ml-auto flex gap-3 text-xs">
            <div className="flex flex-col items-end">
              <span className={`font-mono font-medium ${changeClass(stock.week_change_pct)}`}>
                {formatPct(stock.week_change_pct)}
              </span>
              <span className="text-slate-600">5D</span>
            </div>
            <div className="flex flex-col items-end">
              <span className={`font-mono font-medium ${changeClass(stock.month_change_pct)}`}>
                {formatPct(stock.month_change_pct)}
              </span>
              <span className="text-slate-600">1M</span>
            </div>
          </div>
        </div>

        {/* ── Indicator pills ──────────────────────────────────── */}
        <div className="flex flex-wrap gap-2 mb-4">
          {/* RSI */}
          <span className="indicator-pill">
            <LabelWithTooltip label="RSI" indicator="RSI" className="text-slate-500" />
            <span
              className="font-semibold"
              style={{ color: rsi.zone === 'positive' ? '#00FFB2' : rsi.zone === 'negative' ? '#f87171' : '#94a3b8' }}
            >
              {formatIndicator(stock.indicators?.rsi, 1)}
            </span>
          </span>

          {/* MACD signal */}
          <span className="indicator-pill">
            <LabelWithTooltip label="MACD" indicator="MACD" className="text-slate-500" />
            <span className={macdBull ? 'text-emerald-400 font-semibold' : 'text-red-400 font-semibold'}>
              {macdBull ? '▲ Bull' : '▼ Bear'}
            </span>
          </span>

          {/* Volume */}
          <span className="indicator-pill">
            <LabelWithTooltip label="Vol" indicator="VOL" className="text-slate-500" />
            <span className="font-mono">{formatVolume(stock.volume)}</span>
          </span>

          {/* BB position */}
          {stock.indicators?.bb_lower != null && (
            <span className="indicator-pill">
              <LabelWithTooltip label="BB" indicator="BB" className="text-slate-500" />
              <span className="font-mono text-amber-400">
                {formatIndicator(stock.indicators?.bb_width, 1)}%
              </span>
            </span>
          )}
        </div>

        {/* ── Strategy preview ─────────────────────────────────── */}
        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-500 truncate max-w-[200px] sm:max-w-[260px]">
            {stock.strategy}
          </p>
          <button
            className="flex items-center gap-1 text-xs font-semibold transition-colors duration-200"
            style={{ color: expanded ? cfg.color : '#64748b' }}
            onClick={(e) => { e.stopPropagation(); setExpanded(v => !v); }}
          >
            {expanded ? 'Tutup' : 'Analisis'}
            <svg
              className={`w-3.5 h-3.5 transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* ── Expanded panel ───────────────────────────────────────── */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            key="expanded"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: 'easeInOut' }}
            className="overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            <div
              className="px-5 pb-6 pt-2 border-t"
              style={{ borderColor: 'rgba(255,255,255,0.05)' }}
            >
              {/* Chart */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                    📊 Candlestick Chart
                    <span className="text-xs font-normal text-slate-600">180 hari terakhir</span>
                  </h3>
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    EMA 20 · EMA 50 · Bollinger Bands
                  </div>
                </div>

                {chartLoading ? (
                  <div className="flex items-center justify-center h-[340px] rounded-xl bg-navy-800">
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-8 h-8 rounded-full border-2 border-navy-500 border-t-cyan-400 animate-spin" />
                      <span className="text-xs text-slate-500">Mengunduh data historis...</span>
                    </div>
                  </div>
                ) : (
                  <CandlestickChart
                    ohlcv={ohlcv}
                    ema20={ema20}
                    ema50={ema50}
                    bbUpper={bbUpper}
                    bbMiddle={bbMiddle}
                    bbLower={bbLower}
                  />
                )}
              </div>

              {/* Indicators detail */}
              <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
                <IndicatorDetail
                  label="RSI (14)"
                  value={formatIndicator(stock.indicators?.rsi, 1)}
                  note={stock.indicators?.rsi < 30 ? 'Oversold' : stock.indicators?.rsi > 70 ? 'Overbought' : 'Normal'}
                  noteColor={stock.indicators?.rsi < 30 ? '#00FFB2' : stock.indicators?.rsi > 70 ? '#f87171' : '#64748b'}
                  tooltip="RSI"
                />
                <IndicatorDetail
                  label="EMA 20"
                  value={formatPrice(stock.indicators?.ema_20)}
                  note={stock.current_price > stock.indicators?.ema_20 ? 'Harga di atas' : 'Harga di bawah'}
                  noteColor={stock.current_price > stock.indicators?.ema_20 ? '#00FFB2' : '#f87171'}
                  tooltip="EMA"
                />
                <IndicatorDetail
                  label="EMA 50"
                  value={formatPrice(stock.indicators?.ema_50)}
                  note={stock.current_price > stock.indicators?.ema_50 ? 'Harga di atas' : 'Harga di bawah'}
                  noteColor={stock.current_price > stock.indicators?.ema_50 ? '#00FFB2' : '#f87171'}
                  tooltip="EMA"
                />
                <IndicatorDetail
                  label="ATR (14)"
                  value={formatPrice(stock.indicators?.atr)}
                  note="Volatilitas harian"
                  noteColor="#94a3b8"
                  tooltip="ATR"
                />
              </div>

              {/* BB row */}
              <div className="mt-3 grid grid-cols-3 gap-3">
                <IndicatorDetail label="BB Upper" value={formatPrice(stock.indicators?.bb_upper)} note="" noteColor="" tooltip="BB" />
                <IndicatorDetail label="BB Middle" value={formatPrice(stock.indicators?.bb_middle)} note="SMA 20" noteColor="#94a3b8" tooltip="BB" />
                <IndicatorDetail label="BB Lower" value={formatPrice(stock.indicators?.bb_lower)} note="" noteColor="" tooltip="BB" />
              </div>

              {/* Reasoning */}
              <ReasoningBox stock={stock} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function IndicatorDetail({ label, value, note, noteColor, tooltip }) {
  return (
    <div
      className="rounded-xl px-3 py-3"
      style={{
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.05)',
      }}
    >
      <div className="text-xs text-slate-500 mb-1 flex items-center gap-1">
        <LabelWithTooltip label={label} indicator={tooltip} />
      </div>
      <div className="text-sm font-mono font-semibold text-slate-200">{value ?? '—'}</div>
      {note && (
        <div className="text-xs mt-0.5 font-medium" style={{ color: noteColor }}>
          {note}
        </div>
      )}
    </div>
  );
}
