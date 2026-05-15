import StockDetailClient from './StockDetailClient';

// Use Node.js runtime instead of edge to avoid SES restrictions
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export default function StockDetailPage() {
  return <StockDetailClient />;
}
