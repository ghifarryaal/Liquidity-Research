'use client';

import { motion } from 'framer-motion';

const GAUGE_COLORS = [
  { threshold: 25,  color: '#00FFB2', bg: 'rgba(0,255,178,0.1)',  ring: 'rgba(0,255,178,0.3)'  },
  { threshold: 50,  color: '#fbbf24', bg: 'rgba(251,191,36,0.1)', ring: 'rgba(251,191,36,0.3)' },
  { threshold: 75,  color: '#f97316', bg: 'rgba(249,115,22,0.1)', ring: 'rgba(249,115,22,0.3)' },
  { threshold: 100, color: '#ef4444', bg: 'rgba(239,68,68,0.1)',  ring: 'rgba(239,68,68,0.3)'  },
];

function getStyle(score) {
  return GAUGE_COLORS.find(c => score < c.threshold) ?? GAUGE_COLORS[3];
}

export default function PanicMeterWidget({ panicMeter }) {
  if (!panicMeter) return null;

  const { score, label, breadth_bullish_pct, description, vix_level, dxy_level } = panicMeter;
  const style = getStyle(score);
  const isBullish = breadth_bullish_pct >= 50; // Keep icon trend separately

  // SVG arc gauge parameters - Optimized to avoid overlap
  const R = 62;
  const cx = 80;
  const cy = 64; // Moved up significantly
  const circumference = Math.PI * R; // half-circle
  const fillArc = (score / 100) * circumference;

  return (
    <div
      className="col-span-1 md:col-span-4 rounded-2xl border p-4 md:p-5 flex flex-col gap-3 md:gap-4 transition-all duration-500 h-[240px] sm:h-[260px] relative overflow-hidden"
      style={{ background: style.bg, borderColor: style.ring }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[22px]" style={{ color: style.color }}>
            {isBullish ? 'trending_up' : 'trending_down'}
          </span>
          <span className="text-[13px] font-black uppercase tracking-[0.25em] text-white">
            Market Pulse
          </span>
        </div>
        <div
          className="text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest text-black shadow-lg"
          style={{ background: style.color }}
        >
          {label}
        </div>
      </div>

      {/* Wrap everything in a content div for better layout control */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        {/* Main Content Area: Gauge + Stats */}
        <div className="flex items-center justify-between gap-4">
          {/* Speedometer Left */}
          <div className="relative w-[130px] h-[75px] flex-shrink-0">
            <svg viewBox="0 0 160 90" className="w-full h-full overflow-visible">
              <path
                d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
                fill="none"
                stroke="rgba(255,255,255,0.08)"
                strokeWidth="18"
                strokeLinecap="round"
              />
              <motion.path
                d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
                fill="none"
                stroke={style.color}
                strokeWidth="18"
                strokeLinecap="round"
                strokeDasharray={`${circumference}`}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: circumference - fillArc }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
              />
            </svg>
            <div className="absolute bottom-[-10px] left-0 right-0 text-center flex flex-col items-center">
              <span className="text-3xl font-black font-mono text-white leading-none tracking-tighter">
                {score.toFixed(1)}
              </span>
              <span className="text-[9px] text-white/40 font-black uppercase tracking-widest mt-1">Fear Score</span>
            </div>
          </div>

          {/* Indicators Right */}
          <div className="grid grid-cols-2 gap-x-4 gap-y-3 flex-1">
            <SubStat label="VIX" value={vix_level != null ? vix_level.toFixed(1) : '—'} note="FEAR" />
            <SubStat label="DXY" value={dxy_level != null ? dxy_level.toFixed(1) : '—'} note="USD" />
            <SubStat
              label="BREADTH"
              value={`${breadth_bullish_pct}%`}
              note="BULL"
              positive={breadth_bullish_pct >= 50}
            />
            <SubStat
              label="SENTIMENT"
              value={breadth_bullish_pct >= 50 ? 'BULL' : 'BEAR'}
              note="BIAS"
              positive={breadth_bullish_pct >= 50}
            />
          </div>
        </div>

        {/* Description Box */}
        <div className="bg-black/40 backdrop-blur-md rounded-xl border border-white/5 p-3 flex-shrink-0">
          <p className="text-[10px] leading-relaxed font-bold text-white/90 italic line-clamp-2">
            "{description}"
          </p>
        </div>
      </div>

      {/* Bottom Legend - Fixed Alignment */}
      <div className="pt-2 border-t border-white/5">
        <div className="flex gap-1 h-1.5 rounded-full overflow-hidden mb-1">
          <div className="flex-1 bg-[#00FFB2]" />
          <div className="flex-1 bg-[#fbbf24]" />
          <div className="flex-1 bg-[#f97316]" />
          <div className="flex-1 bg-[#ef4444]" />
        </div>
        <div className="grid grid-cols-4 w-full text-[8px] text-white/40 font-black uppercase tracking-widest text-center">
          <span>Tenang</span>
          <span>Waspada</span>
          <span>Panik</span>
          <span>Extreme</span>
        </div>
      </div>
    </div>
  );
}

function SubStat({ label, value, note, positive }) {
  return (
    <div className="flex flex-col">
      <span className="text-[8px] text-white/50 font-black uppercase tracking-tighter mb-0.5">{label}</span>
      <span
        className="text-[16px] font-black font-mono leading-none"
        style={{ color: positive === undefined ? '#ffffff' : positive ? '#00FFB2' : '#ef4444' }}
      >
        {value}
      </span>
      <span className="text-[8px] text-white/30 font-bold uppercase">{note}</span>
    </div>
  );
}
