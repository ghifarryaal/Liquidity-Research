// This is a pure client-side app (use client + SWR).
// BASE_URL is resolved in the browser using the NEXT_PUBLIC_ env var.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';


async function fetchJSON(url) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  /** GET /api/cluster/{lq45|kompas100} */
  getClusterData: (indexName, periodDays = 180) =>
    fetchJSON(`${BASE_URL}/api/cluster/${indexName}?period_days=${periodDays}`),

  /** GET /api/stock/{ticker} */
  getStockDetail: (ticker, periodDays = 180) =>
    fetchJSON(`${BASE_URL}/api/stock/${ticker}?period_days=${periodDays}`),

  /** GET /api/macro */
  getMacro: () =>
    fetchJSON(`${BASE_URL}/api/macro`),

  /** GET / */
  health: () =>
    fetchJSON(`${BASE_URL}/`),
};
