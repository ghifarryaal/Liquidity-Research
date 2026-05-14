/**
 * Next.js Edge API Route - Proxy for stock detail requests.
 *
 * This route handler intercepts GET requests to /stock/{ticker}
 * (the old URL format used by cached frontend builds) and proxies
 * them to the correct backend API endpoint.
 *
 * This allows old cached Cloudflare Pages builds to continue working
 * while we migrate to the new /api/stock/{ticker} URL format.
 */
export const runtime = 'edge';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function GET(request, { params }) {
  const { ticker } = await params;
  
  // Normalize ticker: ensure it has .JK suffix
  const normalizedTicker = ticker.toUpperCase().endsWith('.JK')
    ? ticker.toUpperCase()
    : `${ticker.toUpperCase()}.JK`;

  // Get period_days from query string, default to 180
  const { searchParams } = new URL(request.url);
  const periodDays = searchParams.get('period_days') || '180';

  const backendUrl = `${BACKEND_URL}/api/stock/${normalizedTicker}?period_days=${periodDays}`;

  try {
    const response = await fetch(backendUrl, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    const data = await response.json();

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ detail: `Proxy error: ${err.message}` }),
      {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
