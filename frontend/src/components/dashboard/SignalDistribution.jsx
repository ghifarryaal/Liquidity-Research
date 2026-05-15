'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';

export default function SignalDistribution({ stocks, isLoading }) {
  const distribution = useMemo(() => {
    if (!stocks || stocks.length === 0) {
      return { buy: 0, hold: 0, sell: 0, total: 0 };
    }

    const counts = {
      buy: 0,
      hold: 0,
      sell: 0,
    };

    stocks.forEach(stock => {
      const signal = stock.signal || 'HOLD';
      if (signal.includes('BUY')) {
        counts.buy++;
      } else if (signal.includes('SELL')) {
        counts.sell++;
      } else {
        counts.hold++;
      }
    });

    return {
      ...counts,
      total: stocks.length,
    };
  }, [stocks]);

  const percentages = useMemo(() => {
    if (distribution.total === 0) {
      return { buy: 0, hold: 0, sell: 0 };
    }
    return {
      buy: (distribution.buy / distribution.total) * 100,
      hold: (distribution.hold / distribution.total) * 100,
      sell: (distribution.sell / distribution.total) * 100,
    };
  }, [distribution]);

  // Market sentiment based on distribution
  const sentiment = useMemo(() => {
    if (percentages.buy > 50) {
      return { label: 'Bullish', color: '#00FFB2', icon: '📈' };
    } else if (percentages.sell > 50) {
      return { label: 'Bearish', color: '#ef4444', icon: '📉' };
    } else if (percentages.hold > 60) {
      return { label: 'Neutral', color: '#f59e0b', icon: '➡️' };
    } else {
      return { label: 'Mixed', color: '#94a3b8', icon: '🔀' };
    }
  }, [percentages]);

  if (isLoading) {
    return (
      <div className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 mb-4 md:mb-6">
        <div className="h-6 bg-surface-container-high rounded animate-pulse mb-4" />
        <div className="h-8 bg-surface-container-high rounded animate-pulse" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-surface-container rounded-xl border border-outline-variant p-4 md:p-6 mb-4 md:mb-6 shadow-sm"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4 md:mb-5">
        <div className="flex items-center gap-2 md:gap-3">
          <span className="text-2xl md:text-3xl">{sentiment.icon}</span>
          <div>
            <h3 className="text-sm md:text-base font-bold text-on-surface">Distribusi Sinyal Pasar</h3>
            <p className="text-[10px] md:text-xs text-on-surface-variant">
              Sentimen: <span className="font-bold" style={{ color: sentiment.color }}>{sentiment.label}</span>
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xl md:text-2xl font-bold text-on-surface">{distribution.total}</div>
          <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider">Emiten</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative h-8 md:h-10 bg-surface-container-highest rounded-full overflow-hidden mb-3 md:mb-4 border border-outline-variant/30">
        <div className="absolute inset-0 flex">
          {/* BUY Section */}
          {percentages.buy > 0 && (
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentages.buy}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-[#00FFB2] to-[#00cc8e] relative group cursor-pointer"
              style={{ minWidth: percentages.buy > 0 ? '2%' : '0' }}
            >
              {percentages.buy > 8 && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[10px] md:text-xs font-bold text-white drop-shadow-md">
                    {Math.round(percentages.buy)}%
                  </span>
                </div>
              )}
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                <div className="bg-[#00FFB2] text-white text-[10px] md:text-xs font-bold px-2 md:px-3 py-1 md:py-1.5 rounded-lg shadow-lg whitespace-nowrap">
                  🟢 BUY: {distribution.buy} emiten
                </div>
              </div>
            </motion.div>
          )}

          {/* HOLD Section */}
          {percentages.hold > 0 && (
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentages.hold}%` }}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
              className="h-full bg-gradient-to-r from-[#f59e0b] to-[#d97706] relative group cursor-pointer"
              style={{ minWidth: percentages.hold > 0 ? '2%' : '0' }}
            >
              {percentages.hold > 8 && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[10px] md:text-xs font-bold text-white drop-shadow-md">
                    {Math.round(percentages.hold)}%
                  </span>
                </div>
              )}
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                <div className="bg-[#f59e0b] text-white text-[10px] md:text-xs font-bold px-2 md:px-3 py-1 md:py-1.5 rounded-lg shadow-lg whitespace-nowrap">
                  🟡 HOLD: {distribution.hold} emiten
                </div>
              </div>
            </motion.div>
          )}

          {/* SELL Section */}
          {percentages.sell > 0 && (
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${percentages.sell}%` }}
              transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
              className="h-full bg-gradient-to-r from-[#ef4444] to-[#dc2626] relative group cursor-pointer"
              style={{ minWidth: percentages.sell > 0 ? '2%' : '0' }}
            >
              {percentages.sell > 8 && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[10px] md:text-xs font-bold text-white drop-shadow-md">
                    {Math.round(percentages.sell)}%
                  </span>
                </div>
              )}
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                <div className="bg-[#ef4444] text-white text-[10px] md:text-xs font-bold px-2 md:px-3 py-1 md:py-1.5 rounded-lg shadow-lg whitespace-nowrap">
                  🔴 SELL: {distribution.sell} emiten
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-3 gap-2 md:gap-3">
        {/* BUY */}
        <div className="flex items-center gap-1.5 md:gap-2 p-2 md:p-3 bg-[#00FFB2]/10 rounded-lg border border-[#00FFB2]/30">
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-[#00FFB2]" />
          <div className="flex-1 min-w-0">
            <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Buy</div>
            <div className="flex items-baseline gap-1">
              <span className="text-sm md:text-lg font-bold text-[#00FFB2]">{distribution.buy}</span>
              <span className="text-[9px] md:text-[10px] text-on-surface-variant">({Math.round(percentages.buy)}%)</span>
            </div>
          </div>
        </div>

        {/* HOLD */}
        <div className="flex items-center gap-1.5 md:gap-2 p-2 md:p-3 bg-[#f59e0b]/10 rounded-lg border border-[#f59e0b]/30">
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-[#f59e0b]" />
          <div className="flex-1 min-w-0">
            <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Hold</div>
            <div className="flex items-baseline gap-1">
              <span className="text-sm md:text-lg font-bold text-[#f59e0b]">{distribution.hold}</span>
              <span className="text-[9px] md:text-[10px] text-on-surface-variant">({Math.round(percentages.hold)}%)</span>
            </div>
          </div>
        </div>

        {/* SELL */}
        <div className="flex items-center gap-1.5 md:gap-2 p-2 md:p-3 bg-[#ef4444]/10 rounded-lg border border-[#ef4444]/30">
          <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-[#ef4444]" />
          <div className="flex-1 min-w-0">
            <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Sell</div>
            <div className="flex items-baseline gap-1">
              <span className="text-sm md:text-lg font-bold text-[#ef4444]">{distribution.sell}</span>
              <span className="text-[9px] md:text-[10px] text-on-surface-variant">({Math.round(percentages.sell)}%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Insight Text */}
      <div className="mt-3 md:mt-4 p-2 md:p-3 bg-background/40 rounded-lg border border-outline-variant/30">
        <p className="text-[10px] md:text-xs text-on-surface-variant leading-relaxed">
          {percentages.buy > 50 && (
            <>
              <span className="font-bold text-[#00FFB2]">Mayoritas sinyal bullish.</span> Pasar menunjukkan peluang entry yang menarik. Pertimbangkan akumulasi dengan manajemen risiko yang ketat.
            </>
          )}
          {percentages.sell > 50 && (
            <>
              <span className="font-bold text-[#ef4444]">Mayoritas sinyal bearish.</span> Pasar menunjukkan tekanan jual. Disarankan untuk mengurangi eksposur atau menunggu konfirmasi reversal.
            </>
          )}
          {percentages.hold > 60 && (
            <>
              <span className="font-bold text-[#f59e0b]">Mayoritas sinyal hold.</span> Pasar dalam fase konsolidasi. Tunggu konfirmasi arah yang lebih jelas sebelum mengambil posisi besar.
            </>
          )}
          {percentages.buy <= 50 && percentages.sell <= 50 && percentages.hold <= 60 && (
            <>
              <span className="font-bold text-[#94a3b8]">Sinyal pasar mixed.</span> Tidak ada dominasi jelas. Fokus pada stock picking individual dengan analisis mendalam.
            </>
          )}
        </p>
      </div>
    </motion.div>
  );
}
