'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { CLUSTER_CONFIG } from '@/constants/clusterConfig';
import { formatPrice, formatPct, changeClass } from '@/lib/formatters';

const FILTER_OPTIONS = [
  { value: 'all', label: 'Semua' },
  { value: 'Buy the Dip', label: 'Beli Saat Turun' },
  { value: 'Trending / Momentum', label: 'Momentum' },
  { value: 'Hold / Sideways', label: 'Konsolidasi Netral' },
  { value: 'High Risk / Avoid', label: 'Risiko Tinggi' },
];

export default function InsightFeed({ stocks, isLoading, isError }) {
  const router = useRouter();
  const [activeFilter, setActiveFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('confidence');

  const filtered = useMemo(() => {
    let list = [...(stocks || [])];

    if (activeFilter !== 'all') {
      list = list.filter(s => s.cluster_label === activeFilter);
    }

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        s =>
          s.ticker.toLowerCase().includes(q) ||
          s.name.toLowerCase().includes(q) ||
          s.sector?.toLowerCase().includes(q)
      );
    }

    if (sortBy === 'confidence') {
      list.sort((a, b) => b.confidence - a.confidence);
    } else if (sortBy === 'change') {
      list.sort((a, b) => b.price_change_pct - a.price_change_pct);
    } else if (sortBy === 'ticker') {
      list.sort((a, b) => a.ticker.localeCompare(b.ticker));
    }

    return list;
  }, [stocks, activeFilter, search, sortBy]);

  if (isError) {
    return (
      <div className="lg:col-span-12 flex flex-col items-center justify-center py-24 gap-4 bg-surface-container rounded-xl border border-outline-variant">
        <span className="material-symbols-outlined text-4xl text-error">warning</span>
        <h3 className="text-lg font-semibold text-on-surface">Gagal memuat data</h3>
      </div>
    );
  }

  const formatPrice = (val) => new Intl.NumberFormat('id-ID').format(val || 0);
  const formatPct = (val) => `${val > 0 ? '+' : ''}${(val || 0).toFixed(2)}%`;

  return (
    <div className="lg:col-span-12 bg-surface-container-lowest flex flex-col pt-2">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-6 gap-4">
        <div>
          <h1 className="font-display-sm text-display-sm text-on-surface mb-1">Penyaring Saham Taktis</h1>
          <p className="text-on-surface-variant text-body-standard font-body-standard">Sinyal kuantitatif waktu nyata berdasarkan klasterisasi AI.</p>
        </div>
      </div>

      {/* Toolbar: Search & Filters */}
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 mb-4 p-3 bg-surface-container rounded-lg border border-outline-variant">
        <div className="relative w-full xl:w-[320px]">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">search</span>
          <input
            type="text"
            placeholder="Cari emiten, sektor, atau indeks..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-surface border border-outline-variant rounded pl-9 pr-3 py-1.5 text-on-surface focus:border-primary focus:ring-1 focus:ring-primary transition-all text-[13px] outline-none placeholder:text-on-surface-variant"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[12px] text-on-surface-variant mr-2">Filter Klaster:</span>
          {FILTER_OPTIONS.map(opt => {
            const isActive = activeFilter === opt.value;
            return (
              <button
                key={opt.value}
                onClick={() => setActiveFilter(opt.value)}
                className={`px-3 py-1 rounded-full text-[12px] flex items-center space-x-1 transition-colors ${
                  isActive 
                    ? 'bg-surface border border-primary text-primary' 
                    : 'bg-surface border border-outline-variant text-on-surface-variant hover:border-outline hover:text-on-surface'
                }`}
              >
                <span>{opt.label}</span>
                {isActive && activeFilter !== 'all' && (
                  <span className="material-symbols-outlined text-[14px]">close</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Terminal Data Grid */}
      <div className="border border-outline-variant rounded-lg bg-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left whitespace-nowrap">
            <thead>
              <tr className="border-b border-outline-variant">
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-left">
                  Emiten
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-left">
                  Harga
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-right cursor-pointer hover:text-on-surface transition-colors" onClick={() => setSortBy('change')}>
                  <div className="flex items-center justify-end space-x-1">
                    <span>1H %</span>
                    <span className={`material-symbols-outlined text-[14px] ${sortBy === 'change' ? 'opacity-100 text-primary' : 'opacity-0'}`}>arrow_downward</span>
                  </div>
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-right">
                  5H %
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-right">
                  30H %
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase text-left">
                  Klaster AI
                </th>
                <th className="py-2 px-4 font-heading-table text-heading-table text-on-surface-variant uppercase cursor-pointer hover:text-on-surface transition-colors" onClick={() => setSortBy('confidence')}>
                  <div className="flex items-center space-x-1">
                    <span>Keyakinan</span>
                    <span className={`material-symbols-outlined text-[14px] ${sortBy === 'confidence' ? 'opacity-100 text-primary' : 'opacity-0'}`}>arrow_downward</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant relative">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-on-surface-variant">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                      Memuat data...
                    </div>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-on-surface-variant">Tidak ada emiten yang sesuai.</td>
                </tr>
              ) : (
                filtered.map((stock) => (
                  <tr 
                    key={stock.ticker} 
                    className="hover:bg-surface-container-low transition-colors cursor-pointer group"
                    onClick={() => router.push(`/stock/${stock.ticker.replace('.JK', '')}`)}
                  >
                    <td className="py-2 px-4">
                      <div className="flex flex-col">
                        <span className="font-ticker text-on-surface group-hover:text-primary transition-colors">{stock.ticker.replace('.JK', '')}</span>
                        <span className="text-[10px] text-on-surface-variant truncate max-w-[120px]">{stock.name}</span>
                        <span className="text-[9px] text-slate-500 font-medium uppercase tracking-tighter">{stock.sector}</span>
                      </div>
                    </td>
                    <td className="py-2 px-4 font-data-mono text-on-surface">
                      {formatPrice(stock.current_price)}
                    </td>
                    <td className={`py-2 px-4 text-right font-data-mono font-bold ${changeClass(stock.price_change_pct)}`}>
                      <div className="flex items-center justify-end gap-0.5">
                        {stock.price_change_pct > 0 ? '▲' : stock.price_change_pct < 0 ? '▼' : ''}
                        {formatPct(stock.price_change_pct)}
                      </div>
                    </td>
                    <td className={`py-2 px-4 text-right font-data-mono font-bold ${changeClass(stock.week_change_pct)}`}>
                      <div className="flex items-center justify-end gap-0.5">
                        {stock.week_change_pct > 0 ? '▲' : stock.week_change_pct < 0 ? '▼' : ''}
                        {formatPct(stock.week_change_pct)}
                      </div>
                    </td>
                    <td className={`py-2 px-4 text-right font-data-mono font-bold ${changeClass(stock.month_change_pct)}`}>
                      <div className="flex items-center justify-end gap-0.5">
                        {stock.month_change_pct > 0 ? '▲' : stock.month_change_pct < 0 ? '▼' : ''}
                        {formatPct(stock.month_change_pct)}
                      </div>
                    </td>
                    <td className="py-2 px-4">
                      <div className="flex flex-col gap-1">
                        <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-surface-container-highest text-on-surface border border-outline-variant w-fit">
                          {CLUSTER_CONFIG[stock.cluster_label]?.label || stock.cluster_label}
                        </span>
                        {stock.trade_plan && (
                          <span className="text-[9px] text-primary font-bold uppercase flex items-center gap-0.5">
                            <span className="material-symbols-outlined text-[12px]">verified</span>
                            Plan Ready
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-2 px-4">
                      <div className="flex flex-col">
                        <span className="font-data-mono text-[12px] font-bold text-primary">
                          {Math.round(stock.confidence * 100)}%
                        </span>
                        <div className="w-16 h-1 bg-surface-container-highest rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary" 
                            style={{ width: `${stock.confidence * 100}%` }}
                          />
                        </div>
                        <span className="font-data-mono text-[11px] text-on-surface-variant">
                          {Math.round(stock.confidence * 100)}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
