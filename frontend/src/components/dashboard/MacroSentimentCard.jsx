'use client';

import { motion } from 'framer-motion';

/**
 * MacroSentimentCard — Displays current DXY and US10Y trends with
 * an AI-generated explanation of their impact on the Indonesian IDX.
 *
 * Props:
 *   macroSentiment  : object from API { dxy_zscore, us10y_zscore, dxy_trend, us10y_trend, impact_on_idx }
 *   isLoading       : boolean
 */

function TrendBadge({ label }) {
  const config = {
    Strengthening: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', icon: '↑' },
    Weakening:     { color: '#00FFB2', bg: 'rgba(0,255,178,0.10)', icon: '↓' },
    Rising:        { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', icon: '↑' },
    Falling:       { color: '#00FFB2', bg: 'rgba(0,255,178,0.10)', icon: '↓' },
    Neutral:       { color: '#94a3b8', bg: 'rgba(148,163,184,0.10)', icon: '→' },
  };
  const cfg = config[label] ?? config.Neutral;
  return (
    <span
      className="inline-flex items-center gap-1 text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded"
      style={{ background: cfg.bg, color: cfg.color }}
    >
      <span>{cfg.icon}</span> {label}
    </span>
  );
}

function ZScoreBar({ zscore, label }) {
  // zscore is approx -3 to +3; map to 0–100%
  const pct = Math.round(((zscore + 3) / 6) * 100);
  const clamped = Math.max(0, Math.min(100, pct));

  const barColor = zscore > 0.5
    ? '#ef4444'    // bearish pressure (strong USD / high yields)
    : zscore < -0.5
    ? '#00FFB2'    // bullish (weak USD / low yields)
    : '#fbbf24';   // neutral

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-[9px] font-black text-white/50 uppercase tracking-widest">{label}</span>
        <span className="text-[10px] font-mono font-black" style={{ color: barColor }}>
          z={zscore > 0 ? '+' : ''}{zscore.toFixed(2)}
        </span>
      </div>
      <div className="w-full h-1.5 bg-white/10 rounded-full relative overflow-hidden">
        {/* Center marker */}
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/20" />
        {/* Z-score fill */}
        <motion.div
          className="absolute top-0 h-full rounded-full"
          style={{
            background: barColor,
            left: zscore >= 0 ? '50%' : `${clamped}%`,
            width: `${Math.abs(clamped - 50)}%`,
            boxShadow: `0 0 6px ${barColor}80`,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.abs(clamped - 50)}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <div className="flex justify-between text-[8px] text-white/20 font-mono">
        <span>Weak</span>
        <span>Strong</span>
      </div>
    </div>
  );
}

export default function MacroSentimentCard({ macroSentiment, isLoading }) {
  if (isLoading) {
    return (
      <div className="md:col-span-12 h-[180px] bg-surface-container rounded-xl animate-pulse" />
    );
  }

  if (!macroSentiment) return null;

  const {
    dxy_zscore   = 0,
    us10y_zscore = 0,
    dxy_trend    = 'Neutral',
    us10y_trend  = 'Neutral',
    impact_on_idx = '',
  } = macroSentiment;

  // Overall risk tone: both rising → risk-off; both falling → risk-on
  const isRiskOff = dxy_trend === 'Strengthening' || us10y_trend === 'Rising';
  const isRiskOn  = dxy_trend === 'Weakening'     && us10y_trend === 'Falling';
  const accentColor = isRiskOn ? '#00FFB2' : isRiskOff ? '#ef4444' : '#fbbf24';

  return (
    <motion.div
      className="md:col-span-12 rounded-2xl border p-5 relative overflow-hidden"
      style={{
        background: `rgba(${isRiskOn ? '0,255,178' : isRiskOff ? '239,68,68' : '251,191,36'},0.05)`,
        borderColor: `${accentColor}40`,
      }}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Background glow */}
      <div
        className="absolute top-0 right-0 w-40 h-40 blur-[90px] opacity-10 pointer-events-none"
        style={{ background: accentColor }}
      />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px]" style={{ color: accentColor }}>
              public
            </span>
            <span className="text-[11px] font-black uppercase tracking-[0.2em] text-white/90">
              Sentimen Makro Global → Dampak ke IDX
            </span>
          </div>
          <span
            className="text-[9px] font-black px-2 py-0.5 rounded border uppercase tracking-widest"
            style={{ borderColor: `${accentColor}60`, color: accentColor }}
          >
            {isRiskOn ? 'Risk-On' : isRiskOff ? 'Risk-Off' : 'Neutral'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* DXY Panel */}
          <div className="flex flex-col gap-3 bg-black/20 rounded-xl p-4 border border-white/5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black text-white/60 uppercase tracking-widest">
                DXY — U.S. Dollar Index
              </span>
              <TrendBadge label={dxy_trend} />
            </div>
            <ZScoreBar zscore={dxy_zscore} label="DXY Strength" />
            <p className="text-[10px] text-white/40 leading-relaxed">
              {dxy_trend === 'Strengthening'
                ? 'USD menguat → tekanan pada Rupiah & outflow dari EM'
                : dxy_trend === 'Weakening'
                ? 'USD melemah → potensi inflow ke saham EM & Rupiah stabil'
                : 'USD sideways → dampak netral terhadap Rupiah'}
            </p>
          </div>

          {/* US10Y Panel */}
          <div className="flex flex-col gap-3 bg-black/20 rounded-xl p-4 border border-white/5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black text-white/60 uppercase tracking-widest">
                US10Y — Treasury Yield
              </span>
              <TrendBadge label={us10y_trend} />
            </div>
            <ZScoreBar zscore={us10y_zscore} label="Yield Pressure" />
            <p className="text-[10px] text-white/40 leading-relaxed">
              {us10y_trend === 'Rising'
                ? 'Yield naik → capital outflow dari EM ke obligasi AS'
                : us10y_trend === 'Falling'
                ? 'Yield turun → daya tarik EM meningkat, potensi inflow ke IDX'
                : 'Yield stabil → aliran modal ke IDX relatif tidak terganggu'}
            </p>
          </div>

          {/* AI Explanation */}
          <div className="flex flex-col gap-2 bg-black/20 rounded-xl p-4 border border-white/5">
            <div className="flex items-center gap-1.5 mb-1">
              <span className="material-symbols-outlined text-[14px]" style={{ color: accentColor }}>
                psychology
              </span>
              <span className="text-[9px] font-black uppercase tracking-widest text-white/50">
                Analisis AI — Dampak pada IDX
              </span>
            </div>
            <p className="text-[11px] text-white/70 leading-relaxed">
              {impact_on_idx || 'Menganalisis kondisi makro global...'}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
