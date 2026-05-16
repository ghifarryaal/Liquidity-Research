'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import Navbar from '@/components/layout/Navbar';
import { useClusterData } from '@/hooks/useClusterData';
import Disclaimer from '@/components/layout/Disclaimer';

const MarketOverview = dynamic(() => import('@/components/dashboard/MarketOverview'), { ssr: false });
const InsightFeed = dynamic(() => import('@/components/dashboard/InsightFeed'), { ssr: false });

export default function DashboardPage() {
  const [activeIndex, setActiveIndex] = useState('lq45');

  const {
    data, stocks, macro, macroSentiment, supervisedValidation,
    clusterSummary, generatedAt, totalStocks,
    isLoading, isError, refresh,
  } = useClusterData(activeIndex);

  const panicMeter = data?.panic_meter ?? null;

  const handleIndexChange = (newIndex) => {
    setActiveIndex(newIndex);
  };

  return (
    <div className="bg-background text-on-background min-h-screen">
      <Navbar
        activeIndex={activeIndex}
        onIndexChange={handleIndexChange}
        generatedAt={generatedAt}
        onRefresh={refresh}
      />

      <main className="pt-[72px] md:pt-[88px] pb-8 md:pb-12 lg:pb-16">
        <Disclaimer />

        {/* Hero Banner */}
        <div className="px-4 md:px-6 lg:px-8 max-w-[1440px] mx-auto mb-4 md:mb-6">
          <div className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-r from-primary/5 via-surface-container to-surface-container p-5 md:p-7">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
            <div className="relative z-10 flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary bg-primary/10 border border-primary/30 px-2 py-0.5 rounded-full">
                    AI · ML · Real-Time
                  </span>
                  <span className="text-[10px] font-black uppercase tracking-[0.2em] text-on-surface-variant bg-surface-variant/50 border border-outline-variant px-2 py-0.5 rounded-full">
                    LQ45 · Kompas100 · DBX
                  </span>
                </div>
                <h1 className="text-xl md:text-2xl lg:text-3xl font-black text-on-surface leading-tight mb-1">
                  Analisis Saham Indonesia<br className="hidden sm:block" />
                  <span className="text-primary"> Berbasis Machine Learning</span>
                </h1>
                <p className="text-xs md:text-sm text-on-surface-variant max-w-xl">
                  K-Means clustering 4D · XGBoost confidence scoring · Backtest engine dengan stop loss & trailing stop · AI Mentor Gemini · Tanpa login.
                </p>
              </div>
              <div className="flex flex-wrap gap-3 sm:flex-col sm:items-end shrink-0">
                <div className="flex items-center gap-2 text-[11px] font-bold text-semantic-bullish">
                  <div className="w-2 h-2 rounded-full bg-semantic-bullish animate-pulse" />
                  Data Real-Time
                </div>
                <div className="flex items-center gap-2 text-[11px] font-bold text-primary">
                  <span className="material-symbols-outlined text-[14px]">psychology</span>
                  Gemini AI Mentor
                </div>
                <div className="flex items-center gap-2 text-[11px] font-bold text-on-surface-variant">
                  <span className="material-symbols-outlined text-[14px]">lock_open</span>
                  Gratis · Open Source
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 md:px-6 lg:px-8 max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
        <MarketOverview
          stocks={stocks}
          clusterSummary={clusterSummary}
          macro={macro}
          macroSentiment={macroSentiment}
          supervisedValidation={supervisedValidation}
          panicMeter={panicMeter}
          totalStocks={totalStocks}
          generatedAt={generatedAt}
          indexName={activeIndex}
          isLoading={isLoading}
        />
        
        <InsightFeed
          stocks={stocks}
          isLoading={isLoading}
          isError={isError}
        />
      </div>
    </main>
    </div>
  );
}
