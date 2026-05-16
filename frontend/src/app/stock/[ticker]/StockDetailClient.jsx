'use client';

import { useStockDetail } from '@/hooks/useStockDetail';
import CandlestickChart from '@/components/charts/CandlestickChart';
import { formatPrice, formatPct, rsiLabel } from '@/lib/formatters';
import TradePlanTable from '@/components/dashboard/TradePlanTable';
import BacktestScorecard from '@/components/dashboard/BacktestScorecard';
import SignalExplanation from '@/components/dashboard/SignalExplanation';
import { useParams, useRouter } from 'next/navigation';
import Disclaimer from '@/components/layout/Disclaimer';
import { motion } from 'framer-motion';

export default function StockDetailClient() {
  const router = useRouter();
  const params = useParams();
  const tickerParam = params?.ticker || '';
  const ticker = tickerParam.toUpperCase();
  const fullTicker = ticker.endsWith('.JK') ? ticker : `${ticker}.JK`;
  
  const { detail, ohlcv, ema20, ema50, bbUpper, bbMiddle, bbLower, isLoading, isError, error } =
    useStockDetail(fullTicker);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <p className="text-on-surface-variant font-data-mono">Menganalisis {ticker}...</p>
        </div>
      </div>
    );
  }

  if (isError || !detail) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-surface-container rounded-lg border border-error/30 p-8 text-center">
          <span className="material-symbols-outlined text-error text-5xl mb-4">warning</span>
          <h1 className="text-display-sm text-on-surface mb-2">Terjadi Kesalahan</h1>
          <p className="text-on-surface-variant mb-6 text-sm italic whitespace-pre-wrap text-left max-h-[300px] overflow-auto bg-black/20 p-4 rounded">
            {error?.message || "Maaf, emiten ini tidak dapat ditemukan atau sedang mengalami gangguan data."}
          </p>
          <button onClick={() => router.push('/')} className="px-6 py-2 bg-primary text-on-primary rounded font-bold uppercase tracking-widest text-xs">
            Kembali ke Dashboard
          </button>
        </div>
      </div>
    );
  }

  const stock = detail || {};
  const indicators = stock.indicators || {};
  const rsi = rsiLabel(indicators?.rsi);
  const macdBull = indicators?.macd != null &&
    indicators?.macd_signal != null &&
    indicators.macd > indicators.macd_signal;
    
  const volRatio = indicators?.volume_ratio || 0;
  const tickerDisplay = (stock.ticker || ticker || '').replace('.JK', '') || ticker;

  // Debug logging
  if (typeof window !== 'undefined') {
    console.log('[StockDetailClient] Stock data:', {
      ticker: stock.ticker,
      signal: stock.signal,
      signal_strength: stock.signal_strength,
      signal_recommendation: stock.signal_recommendation,
      confidence_score: stock.confidence_score,
    });
  }

  return (
    <div className="min-h-screen bg-background text-on-background p-4 md:p-6 lg:p-8 pt-[88px] md:pt-[104px]">
      <Disclaimer />
      <div className="max-w-7xl mx-auto flex flex-col gap-6 md:gap-8 stagger-children">
        {/* 0. Back Navigation */}
        <motion.button 
          onClick={() => router.push('/')}
          whileHover={{ x: -4 }}
          whileTap={{ scale: 0.97 }}
          className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors group w-fit focus-ring"
        >
          <span className="material-symbols-outlined text-lg md:text-xl">arrow_back</span>
          <span className="text-xs md:text-sm font-bold uppercase tracking-widest">Kembali ke Dashboard</span>
        </motion.button>

        {/* 1. Header Section (Full Width) */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 shadow-lg gap-4 md:gap-0">
          <div className="flex flex-col gap-1 w-full md:w-auto">
            <div className="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-3">
              <h1 className="font-ticker-lg text-3xl sm:text-4xl lg:text-5xl text-primary uppercase tracking-tight">{tickerDisplay}</h1>
              <span className="text-lg sm:text-xl lg:text-2xl text-on-surface-variant font-medium">{stock.name || '—'}</span>
            </div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-2 sm:mt-3">
              <span className="text-xs uppercase font-bold px-2 sm:px-3 py-1 bg-surface-variant text-on-surface-variant rounded-full border border-outline-variant">
                {stock.sector}
              </span>
              <span className="font-data-mono text-xs sm:text-sm text-on-surface-variant flex items-center gap-1">
                <span className="material-symbols-outlined text-[12px] sm:text-[14px]">location_on</span>
                IDX Jakarta
              </span>
            </div>
          </div>
          <div className="flex flex-col items-start md:items-end gap-1 w-full md:w-auto">
            <div className="flex items-baseline gap-2 sm:gap-3">
              <span className="font-display-sm text-3xl sm:text-4xl lg:text-5xl text-on-surface">{formatPrice(stock.current_price ?? 0)}</span>
              <span className={`font-data-mono text-lg sm:text-xl lg:text-2xl flex items-center ${(stock.price_change_pct ?? 0) > 0 ? 'text-semantic-bullish' : (stock.price_change_pct ?? 0) < 0 ? 'text-semantic-bearish' : 'text-on-surface-variant'}`}>
                {(stock.price_change_pct ?? 0) > 0 ? '▲' : (stock.price_change_pct ?? 0) < 0 ? '▼' : ''}
                {formatPct(stock.price_change_pct ?? 0)}
              </span>
            </div>
            <span className="text-[10px] sm:text-xs text-on-surface-variant uppercase font-data-mono tracking-[0.2em]">Live Price Update (1D)</span>
          </div>
        </header>

        {/* 2. Interactive Chart Section (Full Width) */}
        <section className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 flex flex-col gap-4 md:gap-6 shadow-md">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
            <h3 className="font-heading-table text-on-surface-variant uppercase tracking-[0.15em] flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
              <span className="material-symbols-outlined text-primary text-lg sm:text-xl">leaderboard</span>
              Price Action & Technical Layers
            </h3>
            <div className="flex flex-wrap gap-2 sm:gap-4 font-data-mono text-[10px] sm:text-[11px] text-on-surface-variant">
              <span className="flex items-center gap-1 sm:gap-2"><div className="w-2 sm:w-3 h-0.5 bg-[#06b6d4]"></div> EMA 20</span>
              <span className="flex items-center gap-1 sm:gap-2"><div className="w-2 sm:w-3 h-0.5 bg-[#a855f7]"></div> EMA 50</span>
              <span className="flex items-center gap-1 sm:gap-2"><div className="w-2 sm:w-3 h-2 sm:h-3 bg-orange-400/20 border border-orange-400/40 rounded-sm"></div> BB Bands</span>
            </div>
          </div>

          <div className="w-full h-[300px] sm:h-[400px] lg:h-[500px] bg-[#020817] rounded-xl border border-outline-variant/30 relative overflow-hidden flex items-center justify-center">
            <CandlestickChart
              ohlcv={ohlcv}
              ema20={ema20}
              ema50={ema50}
              bbUpper={bbUpper}
              bbMiddle={bbMiddle}
              bbLower={bbLower}
            />
          </div>
        </section>

        {/* 3. Technical Snapshot (Full Width Grid) */}
        <section className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 shadow-md">
          <h3 className="text-xs font-bold text-on-surface-variant uppercase tracking-[0.2em] mb-4 md:mb-6 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[18px] sm:text-[20px]">analytics</span>
            Technical Snapshot
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            {[
              { label: 'RSI (14)', value: stock.indicators?.rsi?.toFixed(1), meta: rsi.zone.toUpperCase(), color: rsi.zone === 'positive' ? 'text-semantic-bullish' : rsi.zone === 'negative' ? 'text-semantic-bearish' : 'text-on-surface-variant' },
              { label: 'MACD', value: stock.indicators?.macd?.toFixed(1), meta: macdBull ? 'BULLISH' : 'BEARISH', color: macdBull ? 'text-semantic-bullish' : 'text-semantic-bearish' },
              { label: 'Vol Ratio', value: `${volRatio.toFixed(1)}x`, meta: volRatio > 1.5 ? 'ELEVATED' : 'NORMAL', color: volRatio > 1.5 ? 'text-tertiary' : 'text-on-surface-variant' },
              { label: 'ATR (14)', value: stock.indicators?.atr ? Math.round(stock.indicators.atr) : '—', meta: 'VOLATILITY', color: 'text-on-surface-variant' }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                whileHover={{ y: -2, scale: 1.02 }}
                transition={{ duration: 0.15 }}
                className="flex flex-col gap-1 p-3 sm:p-4 lg:p-5 bg-background/40 rounded-xl border border-outline-variant/50 cursor-default"
              >
                <span className="text-[9px] sm:text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">{item.label}</span>
                <span className="font-data-mono text-xl sm:text-2xl font-bold text-on-surface">{item.value}</span>
                <span className={`text-[9px] sm:text-[10px] font-bold ${item.color}`}>{item.meta}</span>
              </motion.div>
            ))}
          </div>
        </section>

        {/* 4. Analyst Desk Briefing (Full Width) */}
        <section className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 flex flex-col gap-4 md:gap-6 shadow-md">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center border-b border-outline-variant pb-4 md:pb-6 gap-4">
            <div className="flex items-center gap-3 md:gap-4">
              <span className="material-symbols-outlined text-primary text-3xl md:text-4xl">psychology</span>
              <div>
                <h2 className="text-xl md:text-2xl font-bold text-on-surface uppercase tracking-tight">Analyst Desk Briefing</h2>
                <span className="text-[10px] sm:text-xs text-on-surface-variant font-data-mono">AI-Generated Strategy Reasoning</span>
              </div>
            </div>
            <div className="flex flex-col items-start lg:items-end gap-2">
              <div className="px-4 md:px-6 py-2 bg-primary/10 border border-primary text-primary font-bold rounded-lg text-xs sm:text-sm uppercase tracking-widest">
                {stock.cluster_label || '—'}
              </div>
              <div className="flex flex-col items-start lg:items-end gap-1">
                <div className="flex items-center gap-2 md:gap-3">
                  <span className="text-[9px] sm:text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Clustering Confidence</span>
                  <span className="font-data-mono text-xs sm:text-sm text-primary font-bold">{Math.round((stock.confidence ?? 0) * 100)}%</span>
                </div>
                <span className="text-[8px] sm:text-[9px] text-on-surface-variant/70 font-data-mono italic">K-Means cluster distance</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 md:gap-8">
            <div className="lg:col-span-3">
              <h4 className="text-xs uppercase font-bold text-on-surface-variant mb-3 md:mb-4 tracking-widest">Rationale & Analysis</h4>
              <div className="text-on-surface text-sm sm:text-base lg:text-lg leading-relaxed bg-background p-4 sm:p-6 lg:p-8 rounded-2xl border border-outline-variant/40 shadow-inner italic">
                "{stock.reasoning}"
              </div>
            </div>
            <div className="flex flex-col gap-4 md:gap-6">
              <div className="p-4 md:p-5 bg-background/50 rounded-xl border border-outline-variant/30">
                <h4 className="text-[9px] sm:text-[10px] uppercase font-bold text-on-surface-variant mb-2 md:mb-3 tracking-widest">Trading Style</h4>
                <div className="flex items-center gap-2 md:gap-3 text-base md:text-lg text-on-surface font-semibold">
                  <span className="material-symbols-outlined text-primary text-xl md:text-2xl">timer</span>
                  {stock.trading_style}
                </div>
              </div>
              <div className="p-4 md:p-5 bg-background/50 rounded-xl border border-outline-variant/30">
                <h4 className="text-[9px] sm:text-[10px] uppercase font-bold text-on-surface-variant mb-2 md:mb-3 tracking-widest">Data Horizon</h4>
                <div className="flex items-center gap-2 md:gap-3 text-base md:text-lg text-on-surface font-semibold">
                  <span className="material-symbols-outlined text-primary text-xl md:text-2xl">history</span>
                  180 Trading Days
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 5. Execution Strategy / Trade Plan (Full Width) */}
        <section className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 flex flex-col gap-4 md:gap-6 shadow-md">
           <h3 className="text-xs sm:text-sm font-bold text-on-surface-variant uppercase tracking-[0.2em] flex items-center gap-2 md:gap-3">
             <span className="material-symbols-outlined text-primary text-lg sm:text-xl">assignment</span>
             Execution Strategy (Action Plan)
           </h3>
           <div className="bg-background/40 rounded-xl border border-outline-variant/30 overflow-x-auto">
             {stock.trade_plan ? (
               <TradePlanTable 
                 plan={stock.trade_plan} 
                 ticker={stock.ticker} 
                 confidenceScore={stock.confidence_score}
                 isHighConviction={stock.is_high_conviction}
               />
             ) : (
               <div className="py-8 md:py-12 text-center text-on-surface-variant italic text-sm">
                 Trade plan sedang disiapkan...
               </div>
             )}
           </div>
        </section>

        {/* 5b. Signal Explanation (Full Width) */}
        <SignalExplanation
          signal={stock.signal}
          signalStrength={stock.signal_strength}
          signalRecommendation={stock.signal_recommendation}
          confidenceScore={stock.confidence_score}
        />

        {/* 6. Backtest Scorecard (Full Width) */}
        <section className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 shadow-md">
          <h3 className="text-xs sm:text-sm font-bold text-on-surface-variant uppercase tracking-[0.2em] mb-4 md:mb-6 flex items-center gap-2 md:gap-3">
            <span className="material-symbols-outlined text-primary text-lg sm:text-xl">fact_check</span>
            Historical Performance (Backtest)
          </h3>
          <BacktestScorecard backtest={stock.backtest} ticker={stock.ticker} />
        </section>

        {/* Footer Disclaimer */}
        <footer className="text-center py-6 md:py-8 text-[10px] sm:text-[11px] text-on-surface-variant uppercase tracking-[0.2em] opacity-60">
          LiquidityResearch Engine · Quantitative Analysis · v1.0
        </footer>
      </div>
    </div>
  );
}
