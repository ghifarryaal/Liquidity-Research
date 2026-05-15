import StockDetailClient from './StockDetailClient';

// REQUIRED by @cloudflare/next-on-pages
export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export default function StockDetailPage() {
  return <StockDetailClient />;
}
