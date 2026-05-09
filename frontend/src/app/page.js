'use client';

import { useState } from 'react';
import Navbar from '@/components/layout/Navbar';
import MarketOverview from '@/components/dashboard/MarketOverview';
import InsightFeed from '@/components/dashboard/InsightFeed';
import { useClusterData } from '@/hooks/useClusterData';
import Disclaimer from '@/components/layout/Disclaimer';

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

      <main className="pt-[88px] pb-section-margin">
        <Disclaimer />
        <div className="px-container-padding max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-gutter">
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
