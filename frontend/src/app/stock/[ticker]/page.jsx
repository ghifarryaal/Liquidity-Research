import StockDetailClient from './StockDetailClient';

// Required by @cloudflare/next-on-pages — all dynamic routes must use edge runtime
export const runtime = 'edge';

// Disable static generation for this dynamic route
export const dynamic = 'force-dynamic';

export default async function StockDetailPage(props) {
  // In Next.js 15+, params is a Promise
  const params = await props.params;
  const ticker = params?.ticker?.toUpperCase() || '';
  
  return <StockDetailClient ticker={ticker} />;
}
