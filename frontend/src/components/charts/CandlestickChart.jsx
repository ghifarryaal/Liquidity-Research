'use client';

import dynamic from 'next/dynamic';
import Spinner from '@/components/ui/Spinner';

// Dynamic import with SSR disabled — lightweight-charts requires browser globals
const CandlestickChartInner = dynamic(
  () => import('./CandlestickChartInner'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-[340px]">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="md" color="cyan" />
          <span className="text-xs text-slate-500">Memuat chart...</span>
        </div>
      </div>
    ),
  }
);

export default function CandlestickChart(props) {
  return <CandlestickChartInner {...props} />;
}
