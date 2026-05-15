import StockDetailClient from './StockDetailClient';

// Required by @cloudflare/next-on-pages — all dynamic routes must use edge runtime
export const runtime = 'edge';

export default function StockDetailPage({ params }) {
  const ticker = params?.ticker?.toUpperCase() || '';
  
  return <StockDetailClient ticker={ticker} />;
}
