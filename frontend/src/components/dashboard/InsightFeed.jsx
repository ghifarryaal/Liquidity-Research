'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { CLUSTER_CONFIG } from '@/constants/clusterConfig';
import { changeClass } from '@/lib/formatters';
import SignalDistribution from './SignalDistribution';

const FILTER_OPTIONS = [
  { value: 'all', label: 'Semua', icon: 'grid_view' },
  { value: 'Buy the Dip', label: 'Beli Saat Turun', icon: 'trending_down' },
  { value: 'Trending / Momentum', label: 'Momentum', icon: 'trending_up' },
  { value: 'Hold / Sideways', label: 'Konsolidasi', icon: 'trending_flat' },
  { value: 'High Risk / Avoid', label: 'Risiko Tinggi', icon: 'warning' },
];

const SIGNAL_FILTER_OPTIONS = [
  { value: 'all', label: 'Semua Sinyal', icon: 'filter_list', color: '#94a3b8' },
  { value: 'BUY', label: 'Buy', icon: 'arrow_upward', color: '#00FFB2', emoji: '🟢' },
  { value: 'HOLD', label: 'Hold', icon: 'pause', color: '#f59e0b', emoji: '🟡' },
  { value: 'SELL', label: 'Sell', icon: 'arrow_downward', color: '#ef4444', emoji: '🔴' },
];

const SORT_OPTIONS = [
  { value: 'confidence', label: 'Keyakinan' },
  { value: 'change', label: 'Perubahan' },
  { value: 'ticker', label: 'Ticker' },
];

const CLUSTER_COLORS = {
  'Buy the Dip':          { bg: 'rgba(0,255,178,0.1)',   border: 'rgba(0,255,178,0.3)',   text: '#00FFB2' },
  'Trending / Momentum':  { bg: 'rgba(59,130,246,0.1)',  border: 'rgba(59,130,246,0.3)',  text: '#60a5fa' },
  'Hold / Sideways':      { bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.3)', text: '#94a3b8' },
  'High Risk / Avoid':    { bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)',   text: '#f87171' },
};

function ClusterChip({ label }) {
  const cfg = CLUSTER_CONFIG[label];
  const c = CLUSTER_COLORS[label] || { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)', text: '#94a3b8' };
  return (
    <span
      className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold border whitespace-nowrap"
      style={{ background: c.bg, borderColor: c.border, color: c.text }}
    >
      {cfg?.label || label}
    </span>
  );
}

function ConfidenceMini({ score }) {
  const pct = Math.round((score ?? 0) * 100);
  const color = pct >= 75 ? '#00FFB2' : pct >= 50 ? '#60a5fa' : '#f59e0b';
  return (
    <div className="flex items-center gap-2">
      <div className="w-12 md:w-16 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="font-data-mono text-[11px] font-bold" style={{ color }}>{pct}%</span>
    </div>
  );
}

function SignalBadge({ signal }) {
  if (!signal) return <span className="text-[10px] text-on-surface-variant">—</span>;
  
  let bgColor, textColor, icon;
  
  if (signal.includes('STRONG BUY')) {
    bgColor = 'rgba(0,255,178,0.2)';
    textColor = '#00FFB2';
    icon = '🟢';
  } else if (signal.includes('BUY')) {
    bgColor = 'rgba(0,255,178,0.15)';
    textColor = '#00FFB2';
    icon = '🟢';
  } else if (signal.includes('HOLD')) {
    bgColor = 'rgba(245,158,11,0.15)';
    textColor = '#f59e0b';
    icon = '🟡';
  } else if (signal.includes('SELL')) {
    bgColor = 'rgba(239,68,68,0.15)';
    textColor = '#ef4444';
    icon = '🔴';
  } else {
    bgColor = 'rgba(148,163,184,0.1)';
    textColor = '#94a3b8';
    icon = '⚪';
  }
  
  return (
    <span
      className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold border whitespace-nowrap"
      style={{ background: bgColor, borderColor: textColor, color: textColor }}
    >
      {icon} {signal.replace('STRONG ', '')}
    </span>
  );
}

export default function InsightFeed({ stocks, isLoading, isError }) {
  const router = useRouter();
  const [activeFilter, setActiveFilter] = useState('all');
  const [activeSignalFilter, setActiveSignalFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('confidence');

  const formatPrice = (val) => new Intl.NumberFormat('id-ID').format(val || 0);
  const formatPct = (val) => `${val > 0 ? '+' : ''}${(val || 0).toFixed(2)}%`;

  const filtered = useMemo(() => {
    let list = [...(stocks || [])];
    
    // Filter by cluster label
    if (activeFilter !== 'all') {
      list = list.filter(s => s.cluster_label === activeFilter);
    }
    
    // Filter by signal
    if (activeSignalFilter !== 'all') {
      list = list.filter(s => {
        const signal = s.signal || 'HOLD';
        return signal.includes(activeSignalFilter);
      });
    }
    
    // Filter by search
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(s =>
        s.ticker.toLowerCase().includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.sector?.toLowerCase().includes(q)
      );
    }
    
    // Sort
    if (sortBy === 'confidence') list.sort((a, b) => b.confidence - a.confidence);
    else if (sortBy === 'change') list.sort((a, b) => b.price_change_pct - a.price_change_pct);
    else if (sortBy === 'ticker') list.sort((a, b) => a.ticker.localeCompare(b.ticker));
    
    return list;
  }, [stocks, activeFilter, activeSignalFilter, search, sortBy]);

  if (isError) {
    return (
      <div className="lg:col-span-12 flex flex-col items-center justify-center py-24 gap-4 bg-surface-container rounded-xl border border-outline-variant">
        <span className="material-symbols-outlined text-5xl text-semantic-bearish">cloud_off</span>
        <h3 className="text-lg font-semibold text-on-surface">Gagal memuat data</h3>
        <p className="text-sm text-on-surface-variant">Periksa koneksi internet atau coba refresh halaman</p>
      </div>
    );
  }

  return (
    <div className="lg:col-span-12 bg-surface-container-lowest flex flex-col pt-2">

      {/* Signal Distribution Bar */}
      <SignalDistribution stocks={stocks} isLoading={isLoading} />

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-4 md:mb-6 gap-3">
        <div>
          <h1 className="font-display-sm text-xl md:text-2xl text-on-surface mb-1">Penyaring Saham Taktis</h1>
          <p className="text-on-surface-variant text-xs md:text-sm">
            Sinyal kuantitatif waktu nyata ·{' '}
            {isLoading ? 'Memuat...' : `${filtered.length} dari ${stocks?.length || 0} emiten`}
          </p>
        </div>
        {/* Sort */}
        <div className="flex items-center gap-2 text-xs text-on-surface-variant">
          <span className="hidden sm:inline opacity-60">Urutkan:</span>
          <div className="flex gap-1">
            {SORT_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setSortBy(opt.value)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${
                  sortBy === opt.value
                    ? 'bg-primary/20 text-primary border border-primary/40'
                    : 'bg-surface-container border border-outline-variant text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col gap-3 mb-4 p-3 bg-surface-container rounded-xl border border-outline-variant">
        {/* Search */}
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
          <input
            type="text"
            placeholder="Cari emiten, nama, atau sektor..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-surface border border-outline-variant rounded-lg pl-9 pr-9 py-2 text-on-surface focus:border-primary focus:ring-1 focus:ring-primary transition-all text-[13px] outline-none placeholder:text-on-surface-variant"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          )}
        </div>
        
        {/* Filter chips - Cluster */}
        <div>
          <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider font-bold mb-2 px-1">
            Filter Klaster AI
          </div>
          <div className="flex flex-wrap gap-2">
            {FILTER_OPTIONS.map(opt => {
              const isActive = activeFilter === opt.value;
              return (
                <button
                  key={opt.value}
                  onClick={() => setActiveFilter(isActive && opt.value !== 'all' ? 'all' : opt.value)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-bold transition-all ${
                    isActive
                      ? 'bg-primary/15 border border-primary/50 text-primary'
                      : 'bg-surface border border-outline-variant text-on-surface-variant hover:border-outline hover:text-on-surface'
                  }`}
                >
                  <span className="material-symbols-outlined text-[13px]">{opt.icon}</span>
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Filter chips - Signal */}
        <div>
          <div className="text-[9px] md:text-[10px] text-on-surface-variant uppercase tracking-wider font-bold mb-2 px-1">
            Filter Sinyal Trading
          </div>
          <div className="flex flex-wrap gap-2">
            {SIGNAL_FILTER_OPTIONS.map(opt => {
              const isActive = activeSignalFilter === opt.value;
              return (
                <button
                  key={opt.value}
                  onClick={() => setActiveSignalFilter(isActive && opt.value !== 'all' ? 'all' : opt.value)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-bold transition-all ${
                    isActive
                      ? 'border-2'
                      : 'bg-surface border border-outline-variant hover:border-outline'
                  }`}
                  style={isActive ? {
                    background: `${opt.color}15`,
                    borderColor: opt.color,
                    color: opt.color
                  } : {
                    color: 'var(--md-sys-color-on-surface-variant)'
                  }}
                >
                  {opt.emoji && <span>{opt.emoji}</span>}
                  {!opt.emoji && <span className="material-symbols-outlined text-[13px]">{opt.icon}</span>}
                  {opt.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Desktop Table ── */}
      <div className="hidden md:block border border-outline-variant rounded-xl bg-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left whitespace-nowrap">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-high">
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Emiten</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Harga</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider text-right cursor-pointer hover:text-primary transition-colors" onClick={() => setSortBy('change')}>
                  <span className="flex items-center justify-end gap-1">
                    1H %
                    {sortBy === 'change' && <span className="material-symbols-outlined text-[13px] text-primary">arrow_downward</span>}
                  </span>
                </th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider text-right">5H %</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider text-right">30H %</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Sinyal</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Klaster AI</th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" onClick={() => setSortBy('confidence')}>
                  <span className="flex items-center gap-1">
                    Keyakinan
                    {sortBy === 'confidence' && <span className="material-symbols-outlined text-[13px] text-primary">arrow_downward</span>}
                  </span>
                </th>
                <th className="py-2.5 px-4 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">Rekomendasi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 9 }).map((_, j) => (
                      <td key={j} className="py-3 px-4">
                        <div className="h-3.5 bg-surface-container-high rounded animate-pulse" style={{ width: j === 0 ? '80px' : j === 6 ? '100px' : j === 8 ? '150px' : '56px' }} />
                      </td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-16 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">search_off</span>
                      <p className="text-on-surface-variant text-sm">Tidak ada emiten yang sesuai filter</p>
                      <button onClick={() => { setSearch(''); setActiveFilter('all'); setActiveSignalFilter('all'); }} className="text-primary text-xs font-bold hover:underline">
                        Reset filter
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((stock, idx) => (
                  <motion.tr
                    key={stock.ticker}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: Math.min(idx * 0.02, 0.4) }}
                    className="hover:bg-surface-container-low transition-colors cursor-pointer group"
                    onClick={() => router.push(`/stock/${stock.ticker.replace('.JK', '')}`)}
                  >
                    <td className="py-2.5 px-4">
                      <div className="flex flex-col">
                        <span className="font-mono font-bold text-sm text-on-surface group-hover:text-primary transition-colors">{stock.ticker.replace('.JK', '')}</span>
                        <span className="text-[10px] text-on-surface-variant truncate max-w-[140px]">{stock.name}</span>
                        <span className="text-[9px] text-on-surface-variant/50 uppercase tracking-tight">{stock.sector}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-4 font-data-mono text-sm text-on-surface">{formatPrice(stock.current_price)}</td>
                    <td className={`py-2.5 px-4 text-right font-data-mono text-sm font-bold ${changeClass(stock.price_change_pct)}`}>
                      <span className="flex items-center justify-end gap-0.5">
                        {stock.price_change_pct > 0 ? '▲' : stock.price_change_pct < 0 ? '▼' : ''}
                        {formatPct(stock.price_change_pct)}
                      </span>
                    </td>
                    <td className={`py-2.5 px-4 text-right font-data-mono text-sm font-bold ${changeClass(stock.week_change_pct)}`}>{formatPct(stock.week_change_pct)}</td>
                    <td className={`py-2.5 px-4 text-right font-data-mono text-sm font-bold ${changeClass(stock.month_change_pct)}`}>{formatPct(stock.month_change_pct)}</td>
                    <td className="py-2.5 px-4"><SignalBadge signal={stock.signal} /></td>
                    <td className="py-2.5 px-4"><ClusterChip label={stock.cluster_label} /></td>
                    <td className="py-2.5 px-4"><ConfidenceMini score={stock.confidence} /></td>
                    <td className="py-2.5 px-4">
                      <span className="text-[10px] text-on-surface-variant max-w-[200px] line-clamp-2">
                        {stock.signal_recommendation || stock.strategy || '—'}
                      </span>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Mobile Cards ── */}
      <div className="md:hidden flex flex-col gap-2">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-[72px] bg-surface-container rounded-xl animate-pulse" />
          ))
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center flex flex-col items-center gap-3">
            <span className="material-symbols-outlined text-4xl text-on-surface-variant/40">search_off</span>
            <p className="text-on-surface-variant text-sm">Tidak ada emiten yang sesuai</p>
            <button onClick={() => { setSearch(''); setActiveFilter('all'); setActiveSignalFilter('all'); }} className="text-primary text-xs font-bold hover:underline">
              Reset filter
            </button>
          </div>
        ) : (
          filtered.map((stock, idx) => (
            <motion.div
              key={stock.ticker}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.98 }}
              transition={{ delay: Math.min(idx * 0.03, 0.5) }}
              onClick={() => router.push(`/stock/${stock.ticker.replace('.JK', '')}`)}
              className="bg-surface-container border border-outline-variant rounded-xl p-3 cursor-pointer hover:border-primary/40 hover:bg-surface-container-high transition-all ripple"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="min-w-0">
                  <span className="font-mono font-bold text-sm text-on-surface">{stock.ticker.replace('.JK', '')}</span>
                  <p className="text-[10px] text-on-surface-variant truncate">{stock.name}</p>
                </div>
                <div className="flex flex-col items-end gap-0.5 shrink-0">
                  <span className={`font-data-mono text-sm font-bold ${changeClass(stock.price_change_pct)}`}>
                    {formatPct(stock.price_change_pct)}
                  </span>
                  <span className="font-data-mono text-xs text-on-surface">{formatPrice(stock.current_price)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between gap-2">
                <div className="flex flex-col gap-1 flex-1">
                  <SignalBadge signal={stock.signal} />
                  <ClusterChip label={stock.cluster_label} />
                </div>
                <ConfidenceMini score={stock.confidence} />
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Footer */}
      {!isLoading && filtered.length > 0 && (
        <p className="text-center text-[10px] text-on-surface-variant/40 mt-4 uppercase tracking-widest">
          Menampilkan {filtered.length} emiten
        </p>
      )}
    </div>
  );
}
