'use client';

import { motion } from 'framer-motion';

const SIGNAL_DETAILS = {
  'STRONG BUY': {
    emoji: '🟢',
    color: '#00FFB2',
    bgColor: 'rgba(0,255,178,0.1)',
    borderColor: 'rgba(0,255,178,0.3)',
    title: 'STRONG BUY',
    subtitle: 'Sinyal Beli Kuat',
    description: 'Kondisi pasar menunjukkan peluang entry yang sangat menarik dengan tingkat keyakinan tinggi (>75%). Momentum bullish kuat dengan dukungan teknikal yang solid.',
    action: '✓ Pertimbangkan akumulasi dengan posisi penuh',
    riskLevel: 'Rendah-Sedang',
    riskColor: '#00FFB2',
    timeframe: 'Swing Trade / Investasi',
    confidence: 'Tinggi (>75%)',
  },
  'BUY': {
    emoji: '🟢',
    color: '#00FFB2',
    bgColor: 'rgba(0,255,178,0.15)',
    borderColor: 'rgba(0,255,178,0.25)',
    title: 'BUY',
    subtitle: 'Sinyal Beli',
    description: 'Peluang entry yang baik dengan keyakinan sedang (60-75%). Teknikal menunjukkan potensi kenaikan dengan risiko yang terukur.',
    action: '✓ Pertimbangkan entry bertahap dengan manajemen risiko ketat',
    riskLevel: 'Sedang',
    riskColor: '#60a5fa',
    timeframe: 'Swing Trade',
    confidence: 'Sedang (60-75%)',
  },
  'HOLD': {
    emoji: '🟡',
    color: '#f59e0b',
    bgColor: 'rgba(245,158,11,0.1)',
    borderColor: 'rgba(245,158,11,0.3)',
    title: 'HOLD',
    subtitle: 'Tahan Posisi',
    description: 'Kondisi pasar masih belum jelas atau keyakinan rendah (<60%). Disarankan untuk menunggu konfirmasi arah yang lebih jelas sebelum mengambil keputusan.',
    action: '⏸ Tunggu konfirmasi atau cari entry point yang lebih baik',
    riskLevel: 'Sedang-Tinggi',
    riskColor: '#f59e0b',
    timeframe: 'Wait & See',
    confidence: 'Rendah (<60%)',
  },
  'SELL': {
    emoji: '🔴',
    color: '#ef4444',
    bgColor: 'rgba(239,68,68,0.1)',
    borderColor: 'rgba(239,68,68,0.3)',
    title: 'SELL',
    subtitle: 'Sinyal Jual',
    description: 'Kondisi pasar menunjukkan risiko yang meningkat dengan keyakinan sedang (60-75%). Disarankan untuk mengurangi eksposur atau menghindari entry baru.',
    action: '✗ Pertimbangkan exit atau reduce posisi',
    riskLevel: 'Tinggi',
    riskColor: '#ef4444',
    timeframe: 'Scalping / Exit',
    confidence: 'Sedang (60-75%)',
  },
  'STRONG SELL': {
    emoji: '🔴',
    color: '#dc2626',
    bgColor: 'rgba(220,38,38,0.1)',
    borderColor: 'rgba(220,38,38,0.3)',
    title: 'STRONG SELL',
    subtitle: 'Sinyal Jual Kuat',
    description: 'Kondisi pasar sangat risiko dengan tingkat keyakinan tinggi (>75%). Momentum bearish kuat dengan teknikal yang menunjukkan potensi penurunan signifikan.',
    action: '✗ Exit posisi atau hindari entry baru',
    riskLevel: 'Sangat Tinggi',
    riskColor: '#dc2626',
    timeframe: 'Exit / Avoid',
    confidence: 'Tinggi (>75%)',
  },
};

export default function SignalExplanation({ signal, signalStrength, signalRecommendation, confidenceScore }) {
  if (!signal) return null;

  const details = SIGNAL_DETAILS[signal] || SIGNAL_DETAILS['HOLD'];
  const confidencePct = Math.round((confidenceScore ?? 0.5) * 100);

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 lg:p-8 shadow-md"
      style={{
        borderColor: details.borderColor,
        background: `linear-gradient(135deg, ${details.bgColor} 0%, rgba(255,255,255,0.02) 100%)`,
      }}
    >
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4 md:gap-6 mb-6 md:mb-8 pb-6 md:pb-8 border-b border-outline-variant">
        <div className="flex items-start gap-3 md:gap-4">
          <div className="text-4xl md:text-5xl">{details.emoji}</div>
          <div className="flex-1">
            <h2 className="text-2xl md:text-3xl font-bold text-on-surface uppercase tracking-tight mb-1">
              {details.title}
            </h2>
            <p className="text-sm md:text-base text-on-surface-variant font-medium">{details.subtitle}</p>
          </div>
        </div>

        {/* Signal Strength Badge */}
        <div className="flex flex-col items-start lg:items-end gap-2">
          <div
            className="px-4 md:px-6 py-2 rounded-lg font-bold text-xs md:text-sm uppercase tracking-widest border"
            style={{
              background: details.bgColor,
              borderColor: details.borderColor,
              color: details.color,
            }}
          >
            {signalStrength || 'MODERATE'} CONVICTION
          </div>
          <div className="flex items-center gap-2 md:gap-3">
            <span className="text-[10px] md:text-xs text-on-surface-variant uppercase tracking-widest font-bold">
              Confidence Score
            </span>
            <span className="font-data-mono text-sm md:text-base font-bold" style={{ color: details.color }}>
              {confidencePct}%
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 md:gap-8 mb-6 md:mb-8">
        {/* Description */}
        <div className="lg:col-span-2">
          <h3 className="text-xs md:text-sm font-bold text-on-surface-variant uppercase tracking-widest mb-3 md:mb-4">
            Penjelasan Sinyal
          </h3>
          <p className="text-sm md:text-base text-on-surface leading-relaxed bg-background/40 p-4 md:p-6 rounded-xl border border-outline-variant/30">
            {details.description}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="flex flex-col gap-3 md:gap-4">
          <div className="p-4 md:p-5 bg-background/50 rounded-xl border border-outline-variant/30">
            <h4 className="text-[9px] md:text-[10px] uppercase font-bold text-on-surface-variant mb-2 md:mb-3 tracking-widest">
              Risk Level
            </h4>
            <div className="flex items-center gap-2 md:gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ background: details.riskColor }}
              />
              <span className="text-sm md:text-base font-bold text-on-surface">
                {details.riskLevel}
              </span>
            </div>
          </div>

          <div className="p-4 md:p-5 bg-background/50 rounded-xl border border-outline-variant/30">
            <h4 className="text-[9px] md:text-[10px] uppercase font-bold text-on-surface-variant mb-2 md:mb-3 tracking-widest">
              Timeframe
            </h4>
            <div className="flex items-center gap-2 md:gap-3 text-sm md:text-base font-bold text-on-surface">
              <span className="material-symbols-outlined text-lg md:text-xl" style={{ color: details.color }}>
                schedule
              </span>
              {details.timeframe}
            </div>
          </div>

          <div className="p-4 md:p-5 bg-background/50 rounded-xl border border-outline-variant/30">
            <h4 className="text-[9px] md:text-[10px] uppercase font-bold text-on-surface-variant mb-2 md:mb-3 tracking-widest">
              Conviction
            </h4>
            <div className="flex items-center gap-2 md:gap-3 text-sm md:text-base font-bold text-on-surface">
              <span className="material-symbols-outlined text-lg md:text-xl" style={{ color: details.color }}>
                verified
              </span>
              {details.confidence}
            </div>
          </div>
        </div>
      </div>

      {/* Action Recommendation */}
      <div className="bg-background/60 rounded-xl border border-outline-variant/40 p-4 md:p-6 mb-6 md:mb-8">
        <h3 className="text-xs md:text-sm font-bold text-on-surface-variant uppercase tracking-widest mb-3 md:mb-4">
          Rekomendasi Aksi
        </h3>
        <p
          className="text-sm md:text-base font-semibold leading-relaxed"
          style={{ color: details.color }}
        >
          {details.action}
        </p>
      </div>

      {/* Signal Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <div className="p-4 md:p-5 bg-background/40 rounded-xl border border-outline-variant/30">
          <h4 className="text-[10px] md:text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-3 md:mb-4">
            Faktor Pendukung
          </h4>
          <ul className="space-y-2 text-xs md:text-sm text-on-surface">
            {signal.includes('BUY') && (
              <>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-0.5">✓</span>
                  <span>Momentum teknikal positif</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-0.5">✓</span>
                  <span>Harga mendekati support level</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary mt-0.5">✓</span>
                  <span>Volume perdagangan meningkat</span>
                </li>
              </>
            )}
            {signal.includes('SELL') && (
              <>
                <li className="flex items-start gap-2">
                  <span className="text-semantic-bearish mt-0.5">✗</span>
                  <span>Momentum teknikal negatif</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-semantic-bearish mt-0.5">✗</span>
                  <span>Harga mendekati resistance level</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-semantic-bearish mt-0.5">✗</span>
                  <span>Volatilitas meningkat signifikan</span>
                </li>
              </>
            )}
            {signal.includes('HOLD') && (
              <>
                <li className="flex items-start gap-2">
                  <span className="text-on-surface-variant mt-0.5">—</span>
                  <span>Sinyal teknikal masih ambigu</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-on-surface-variant mt-0.5">—</span>
                  <span>Keyakinan model masih rendah</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-on-surface-variant mt-0.5">—</span>
                  <span>Tunggu konfirmasi lebih lanjut</span>
                </li>
              </>
            )}
          </ul>
        </div>

        <div className="p-4 md:p-5 bg-background/40 rounded-xl border border-outline-variant/30">
          <h4 className="text-[10px] md:text-xs font-bold text-on-surface-variant uppercase tracking-widest mb-3 md:mb-4">
            Manajemen Risiko
          </h4>
          <ul className="space-y-2 text-xs md:text-sm text-on-surface">
            <li className="flex items-start gap-2">
              <span className="material-symbols-outlined text-[14px] text-primary mt-0.5">shield</span>
              <span>Pasang stop-loss di bawah support terdekat</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="material-symbols-outlined text-[14px] text-primary mt-0.5">trending_up</span>
              <span>Target profit sesuai risk/reward 1:2</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="material-symbols-outlined text-[14px] text-primary mt-0.5">scale</span>
              <span>Ukuran posisi sesuai risk tolerance</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Full Recommendation Text */}
      {signalRecommendation && (
        <div className="mt-6 md:mt-8 pt-6 md:pt-8 border-t border-outline-variant">
          <h4 className="text-xs md:text-sm font-bold text-on-surface-variant uppercase tracking-widest mb-3 md:mb-4">
            Rekomendasi Lengkap
          </h4>
          <p className="text-sm md:text-base text-on-surface leading-relaxed italic bg-background/30 p-4 md:p-6 rounded-xl border border-outline-variant/20">
            {signalRecommendation}
          </p>
        </div>
      )}
    </motion.section>
  );
}
