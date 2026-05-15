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
