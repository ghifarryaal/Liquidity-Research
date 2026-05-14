import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function middleware(request) {
  const { pathname, searchParams } = request.nextUrl;

  // Intercept JSON API requests to /stock/{ticker}
  // These come from old cached JS bundles that call the wrong URL
  const acceptHeader = request.headers.get('accept') || '';
  const isApiCall = !acceptHeader.includes('text/html');

  if (pathname.startsWith('/stock/') && isApiCall) {
    // Extract ticker from path e.g. /stock/MEDC => MEDC
    const ticker = pathname.split('/stock/')[1]?.split('?')[0];
    if (!ticker) return NextResponse.next();

    // Normalize: add .JK suffix if missing
    const normalizedTicker = ticker.toUpperCase().endsWith('.JK')
      ? ticker.toUpperCase()
      : `${ticker.toUpperCase()}.JK`;

    const periodDays = searchParams.get('period_days') || '180';
    const backendUrl = `${BACKEND_URL}/api/stock/${normalizedTicker}?period_days=${periodDays}`;

    try {
      const resp = await fetch(backendUrl, {
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await resp.json();
      return NextResponse.json(data, { status: resp.status });
    } catch (err) {
      return NextResponse.json({ detail: `Proxy error: ${err.message}` }, { status: 502 });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/stock/:path*'],
};
