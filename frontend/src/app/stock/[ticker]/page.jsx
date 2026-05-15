import StockDetailClient from './StockDetailClient';

// REQUIRED by @cloudflare/next-on-pages for dynamic routes
export const runtime = 'edge';

export default function StockDetailPage() {
  return <StockDetailClient />;
}
