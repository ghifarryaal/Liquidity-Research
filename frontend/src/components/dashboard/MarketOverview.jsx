'use client';

import PanicMeterWidget from './PanicMeterWidget';
import MacroSentimentCard from './MacroSentimentCard';
import { motion } from 'framer-motion';

function GlobalTickerBox({ title, icon, items, isLoading }) {
  const avgChange = items?.length > 0 
    ? items.reduce((acc, curr) => acc + curr.change, 0) / items.length 
    : 0;
  
  const isUp = avgChange >= 0;
  const color = isUp ? '#00FFB2' : '#ef4444';
  const bg = isUp ? 'rgba(0,255,178,0.1)' : 'rgba(239,68,68,0.1)';
  const ring = isUp ? 'rgba(0,255,178,0.3)' : 'rgba(239,68,68,0.3)';

  return (
    <div 
      className="md:col-span-4 rounded-2xl border p-5 flex flex-col h-[260px] transition-all duration-500 hover:shadow-2xl hover:shadow-black/40"
      style={{ background: bg, borderColor: ring }}
    >
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[22px]" style={{ color }}>{icon}</span>
          <span className="text-[12px] font-black uppercase tracking-[0.2em] text-white/90">{title}</span>
        </div>
        <span className="text-[10px] font-black px-2 py-0.5 rounded border uppercase tracking-widest shadow-sm" style={{ borderColor: ring, color }}>
          {isUp ? 'Bullish' : 'Bearish'}
        </span>
      </div>
      
      <div className="flex-1 overflow-hidden relative">
        <div className="absolute inset-0 overflow-y-auto no-scrollbar scroll-smooth">
          <div className="flex flex-col gap-1.5 pb-4">
            {isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => <div key={i} className="h-10 bg-white/5 animate-pulse rounded-lg" />)}
              </div>
            ) : items?.length > 0 ? (
              items.map((item) => (
                <div key={item.symbol} className="flex justify-between items-center bg-black/30 p-2 rounded-xl border border-white/5 hover:border-white/20 transition-all group">
                  <div className="flex flex-col min-w-0">
                    <span className="text-[11px] font-black text-white truncate group-hover:text-primary transition-colors">{item.name}</span>
                    <span className="text-[9px] text-white/40 font-bold font-mono tracking-tighter uppercase">{item.symbol}</span>
                  </div>
                  <div className="flex flex-col items-end flex-shrink-0">
                    <span className="text-[11px] font-black font-mono text-white/90">{item.price.toLocaleString()}</span>
                    <span className={`text-[10px] font-black font-mono ${item.change >= 0 ? 'text-semantic-bullish' : 'text-semantic-bearish'}`}>
                      {item.change >= 0 ? '+' : ''}{item.change}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-[10px] text-white/30 text-center py-12 font-bold uppercase tracking-widest">Sinkronisasi data...</div>
            )}
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-10 bg-gradient-to-t from-black/40 to-transparent pointer-events-none" />
      </div>
      
      <div className="mt-3 pt-3 border-t border-white/5 flex justify-between items-center">
        <div className="flex flex-col">
          <span className="text-[8px] text-white/40 font-black uppercase tracking-widest">Index Alpha</span>
          <span className="text-sm font-black font-mono" style={{ color }}>
            {avgChange >= 0 ? '+' : ''}{avgChange.toFixed(2)}%
          </span>
        </div>
        <div className="flex items-center gap-2">
           <span className="text-[9px] font-black text-white/30 uppercase tracking-widest">Live</span>
           <div className={`w-2 h-2 rounded-full ${isUp ? 'bg-semantic-bullish shadow-[0_0_8px_#00FFB2]' : 'bg-semantic-bearish shadow-[0_0_8px_#ef4444]'} animate-pulse`} />
        </div>
      </div>
    </div>
  );
}

export default function MarketOverview({ stocks, clusterSummary, macro, macroSentiment, supervisedValidation, panicMeter, totalStocks, generatedAt, indexName, isLoading }) {
  if (isLoading) {
    return <div className="lg:col-span-12 h-[540px] bg-surface-container rounded-xl animate-pulse" />;
  }

  // Derive macro percentages
  const isRiskOn = macro?.macro_regime === 'Risk-On';
  const isBearish = macro?.macro_regime === 'Risk-Off';
  let fillPct = 50;
  if (isRiskOn) fillPct = 80;
  if (isBearish) fillPct = 20;

  return (
    <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-12 gap-gutter mb-gutter">
      
      {/* 1. Macro Sentiment Gauge */}
      <div className="md:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-6 flex flex-col h-[260px] relative overflow-hidden">
        {/* Background Accent */}
        <div 
          className="absolute top-0 right-0 w-32 h-32 blur-[80px] opacity-20 pointer-events-none"
          style={{ background: isRiskOn ? '#00FFB2' : isBearish ? '#ef4444' : '#fbbf24' }}
        />

        <div className="flex justify-between items-start mb-4 relative z-10">
          <h2 className="text-[11px] font-black text-white uppercase tracking-[0.2em]">Sentimen Makro</h2>
          <span className="material-symbols-outlined text-primary text-[20px] animate-pulse">public</span>
        </div>
        
        <div className="flex-1 flex flex-col justify-center items-center relative z-10">
          <span className="text-[10px] text-white/50 uppercase font-black tracking-widest mb-1">Regime Status</span>
          <span className={`text-3xl font-black font-mono tracking-tighter ${isRiskOn ? 'text-semantic-bullish' : isBearish ? 'text-semantic-bearish' : 'text-amber-400'}`}>
            {macro?.macro_regime || 'NEUTRAL'}
          </span>
          
          <div className="w-full max-w-[200px] h-1.5 bg-white/10 rounded-full relative overflow-hidden mt-6 mb-2">
            <div 
              className={`absolute left-0 top-0 h-full transition-all duration-1000 ${isBearish ? 'bg-semantic-bearish' : isRiskOn ? 'bg-semantic-bullish' : 'bg-amber-400'}`} 
              style={{ width: `${fillPct}%` }}
            ></div>
          </div>
        </div>
        
        <div className="flex flex-col items-center pt-4 border-t border-white/10 relative z-10">
          <span className="text-[10px] text-white/50 uppercase font-black tracking-[0.2em] mb-1">Risk Adjusted Score</span>
          <span className="font-data-mono text-2xl font-black text-white leading-none">
            {macro ? Math.round(macro.risk_adjusted_score * 100) : '—'}
          </span>
        </div>
      </div>

      {/* 2. Index Performance */}
      <div className="md:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-4 flex flex-col justify-between h-[260px] hover:bg-surface-variant/50 transition-colors">
        <div className="flex justify-between items-center mb-1">
          <h3 className="font-ticker-lg text-ticker-lg text-primary">{indexName.toUpperCase()}</h3>
          <span className="bg-surface-variant text-on-surface-variant px-1.5 py-0.5 rounded text-[9px] font-data-mono uppercase tracking-wider">Active</span>
        </div>
        <div className="flex-1 flex flex-col justify-center">
          <div className="flex items-baseline">
            <span className="text-4xl font-bold text-on-surface">{totalStocks}</span>
            <span className="ml-2 text-xs text-on-surface-variant uppercase tracking-widest font-medium">Emiten</span>
          </div>
          <p className="text-[11px] text-on-surface-variant mt-2">Data historis 6 bulan terakhir dianalisis secara real-time.</p>
        </div>
        <div className="mt-3 pt-2 border-t border-outline-variant flex justify-between font-data-mono text-[10px] text-on-surface-variant">
          <span>AI ANALYZED</span>
          <span>{generatedAt ? new Date(generatedAt).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) : '—'}</span>
        </div>
      </div>

      {/* 3. Market Momentum */}
      <div className="md:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-4 flex flex-col justify-between h-[260px] hover:bg-surface-variant/50 transition-colors">
        <div className="flex justify-between items-center mb-1">
          <h3 className="font-ticker-lg text-[15px] font-semibold text-primary">Market Momentum</h3>
          <span className="material-symbols-outlined text-[20px] text-on-surface-variant">rocket_launch</span>
        </div>
        
        <div className="flex-1 grid grid-cols-2 gap-4 items-center">
          {/* Bullish */}
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-semantic-bullish">
              {clusterSummary?.['Trending / Momentum'] || 0}
            </span>
            <span className="text-[9px] text-semantic-bullish font-bold uppercase tracking-wider">Bullish Trend</span>
          </div>
          
          {/* Bearish */}
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-semantic-bearish">
              {clusterSummary?.['High Risk / Avoid'] || 0}
            </span>
            <span className="text-[9px] text-semantic-bearish font-bold uppercase tracking-wider">Bearish / Risk</span>
          </div>
          
          {/* Buy the Dip */}
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-cyan-400">
              {clusterSummary?.['Buy the Dip'] || 0}
            </span>
            <span className="text-[9px] text-cyan-400 font-bold uppercase tracking-wider">Buy the Dip</span>
          </div>
          
          {/* Sideways */}
          <div className="flex flex-col">
            <span className="text-3xl font-bold text-slate-400">
              {clusterSummary?.['Hold / Sideways'] || 0}
            </span>
            <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Sideways / Hold</span>
          </div>
        </div>
        
        <div className="mt-3 pt-2 border-t border-outline-variant flex justify-between font-data-mono text-[9px] text-on-surface-variant uppercase tracking-widest">
          <span>Clustering Analysis</span>
          <span>4 Categories</span>
        </div>
      </div>

      {/* 4. Panic Meter */}
      <PanicMeterWidget panicMeter={panicMeter} />

      {/* 5. World Indices */}
      <GlobalTickerBox 
        title="Indeks Saham Dunia" 
        icon="language" 
        items={macro?.world_indices} 
        isLoading={isLoading} 
      />

      {/* 6. World Commodities */}
      <GlobalTickerBox 
        title="Komoditas Dunia" 
        icon="database" 
        items={macro?.commodities} 
        isLoading={isLoading} 
      />

      {/* 7. Supervised Model Validation */}
      {supervisedValidation && supervisedValidation.total_predictions > 0 && (
        <motion.div
          className="md:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-5 flex flex-col gap-3 h-[260px]"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-primary">model_training</span>
            <span className="text-[11px] font-black uppercase tracking-[0.15em] text-white/90">XGBoost Validation</span>
          </div>
          <div className="grid grid-cols-2 gap-3 flex-1">
            <div className="flex flex-col justify-center">
              <span className="text-[9px] text-white/40 font-black uppercase tracking-widest mb-1">30-Day Accuracy</span>
              <span className="text-3xl font-black font-mono text-primary">
                {Math.round((supervisedValidation.accuracy ?? 0) * 100)}%
              </span>
            </div>
            <div className="flex flex-col justify-center">
              <span className="text-[9px] text-white/40 font-black uppercase tracking-widest mb-1">High Conviction Precision</span>
              <span className="text-3xl font-black font-mono text-semantic-bullish">
                {Math.round((supervisedValidation.high_conviction_precision ?? 0) * 100)}%
              </span>
            </div>
            <div className="flex flex-col justify-center">
              <span className="text-[9px] text-white/40 font-black uppercase tracking-widest mb-1">Total Predictions</span>
              <span className="text-2xl font-black font-mono text-white/80">
                {supervisedValidation.total_predictions}
              </span>
            </div>
            <div className="flex flex-col justify-center">
              <span className="text-[9px] text-white/40 font-black uppercase tracking-widest mb-1">Avg Confidence</span>
              <span className="text-2xl font-black font-mono text-amber-400">
                {Math.round((supervisedValidation.avg_confidence ?? 0.5) * 100)}%
              </span>
            </div>
          </div>
          <div className="pt-3 border-t border-white/5 text-[8px] text-white/20 font-black uppercase tracking-widest">
            XGBoost / RandomForest Predictor
          </div>
        </motion.div>
      )}

      {/* 8. Market Breadth (Advance/Decline) */}
      {!isLoading && (
        <motion.div
          className="md:col-span-4 bg-surface-container border border-outline-variant rounded-xl p-5 flex flex-col gap-3 h-[260px]"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-semantic-bullish">equalizer</span>
            <span className="text-[11px] font-black uppercase tracking-[0.15em] text-white/90">Market Breadth</span>
          </div>
          
          {(() => {
            const up = stocks.filter(s => (s.price_change_pct || 0) > 0).length;
            const down = stocks.filter(s => (s.price_change_pct || 0) < 0).length;
            const flat = totalStocks - up - down;
            const upPct = Math.round((up / totalStocks) * 100);
            return (
              <div className="flex-1 flex flex-col justify-center gap-4">
                <div className="flex justify-between items-end">
                  <div className="flex flex-col">
                    <span className="text-3xl font-black font-mono text-semantic-bullish">{up}</span>
                    <span className="text-[9px] text-white/40 font-black uppercase tracking-widest">Advances</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-3xl font-black font-mono text-semantic-bearish">{down}</span>
                    <span className="text-[9px] text-white/40 font-black uppercase tracking-widest">Declines</span>
                  </div>
                </div>
                
                <div className="w-full h-3 bg-white/5 rounded-full overflow-hidden flex">
                  <div className="h-full bg-semantic-bullish" style={{ width: `${upPct}%` }} />
                  <div className="h-full bg-white/10" style={{ width: `${Math.round((flat / totalStocks) * 100)}%` }} />
                  <div className="h-full bg-semantic-bearish" style={{ width: `${100 - upPct - Math.round((flat / totalStocks) * 100)}%` }} />
                </div>
                
                <div className="flex justify-between text-[10px] font-bold">
                  <span className="text-semantic-bullish">{upPct}% Bullish</span>
                  <span className="text-white/40">{flat} Unchanged</span>
                </div>
              </div>
            );
          })()}

          <div className="pt-3 border-t border-white/5 text-[8px] text-white/20 font-black uppercase tracking-widest">
            Index Internal Strength
          </div>
        </motion.div>
      )}

      {/* 9. Sector Leadership (Styled as GlobalTickerBox) */}
      {!isLoading && (() => {
        const sectors = {};
        stocks.forEach(s => {
          if (!sectors[s.sector]) sectors[s.sector] = { sum: 0, count: 0 };
          sectors[s.sector].sum += (s.price_change_pct || 0);
          sectors[s.sector].count += 1;
        });
        const sectorAvg = Object.entries(sectors).map(([name, data]) => ({
          name,
          avg: data.sum / data.count
        })).sort((a, b) => b.avg - a.avg);
        
        const avgIdxChange = sectorAvg.length > 0 ? sectorAvg.reduce((a, b) => a + b.avg, 0) / sectorAvg.length : 0;
        const isUp = avgIdxChange >= 0;
        const color = isUp ? '#00FFB2' : '#ef4444';
        const bg = isUp ? 'rgba(0,255,178,0.1)' : 'rgba(239,68,68,0.1)';
        const ring = isUp ? 'rgba(0,255,178,0.3)' : 'rgba(239,68,68,0.3)';

        return (
          <motion.div 
            className="md:col-span-4 rounded-2xl border p-5 flex flex-col h-[260px] transition-all duration-500 hover:shadow-2xl hover:shadow-black/40"
            style={{ background: bg, borderColor: ring }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[22px]" style={{ color }}>leaderboard</span>
                <span className="text-[12px] font-black uppercase tracking-[0.2em] text-white/90">Sector Momentum</span>
              </div>
              <span className="text-[10px] font-black px-2 py-0.5 rounded border uppercase tracking-widest shadow-sm" style={{ borderColor: ring, color }}>
                {isUp ? 'Strong' : 'Weak'}
              </span>
            </div>
            
            <div className="flex-1 overflow-hidden relative">
              <div className="absolute inset-0 overflow-y-auto no-scrollbar scroll-smooth pr-1">
                <div className="flex flex-col gap-1.5 pb-4">
                  {sectorAvg.map((s, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-black/30 p-2.5 rounded-xl border border-white/5 hover:border-white/20 transition-all group shrink-0">
                      <span className="text-[11px] font-black text-white/90 truncate group-hover:text-primary transition-colors pr-2">
                        {s.name}
                      </span>
                      <span className={`text-[10px] font-black font-mono shrink-0 ${s.avg >= 0 ? 'text-semantic-bullish' : 'text-semantic-bearish'}`}>
                        {s.avg > 0 ? '+' : ''}{s.avg.toFixed(2)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-10 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />
            </div>

            <div className="mt-3 pt-3 border-t border-white/5 flex justify-between items-center">
              <div className="flex flex-col">
                <span className="text-[8px] text-white/40 font-black uppercase tracking-widest">Avg Performance</span>
                <span className="text-sm font-black font-mono" style={{ color }}>
                  {avgIdxChange >= 0 ? '+' : ''}{avgIdxChange.toFixed(2)}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                 <span className="text-[9px] font-black text-white/30 uppercase tracking-widest">Calculated</span>
                 <div className={`w-2 h-2 rounded-full ${isUp ? 'bg-semantic-bullish shadow-[0_0_8px_#00FFB2]' : 'bg-semantic-bearish shadow-[0_0_8px_#ef4444]'} animate-pulse`} />
              </div>
            </div>
          </motion.div>
        );
      })()}

      {/* 10. Macro Sentiment Card (DXY + US10Y) */}
      <MacroSentimentCard macroSentiment={macroSentiment} isLoading={isLoading} />
    </div>
  );
}
