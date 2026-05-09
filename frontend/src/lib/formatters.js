/** Format price in IDR (Rupiah) */
export function formatPrice(value) {
  if (value == null || isNaN(value)) return '—';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/** Format percentage change with sign */
export function formatPct(value, decimals = 2) {
  if (value == null || isNaN(value)) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

/** Format large number to compact (1.2M, 5.3B) */
export function formatVolume(value) {
  if (value == null || isNaN(value)) return '—';
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
  return value.toString();
}

/** Format a float indicator value to N decimals */
export function formatIndicator(value, decimals = 2) {
  if (value == null || isNaN(value)) return '—';
  return Number(value).toFixed(decimals);
}

/** Return CSS class for positive/negative/neutral */
export function changeClass(value) {
  if (value == null || isNaN(value)) return 'neutral';
  if (value > 0) return 'positive';
  if (value < 0) return 'negative';
  return 'neutral';
}

/** Format RSI with zone label */
export function rsiLabel(rsi) {
  if (rsi == null) return { text: '—', zone: 'neutral' };
  if (rsi < 30) return { text: `${rsi.toFixed(1)} (Oversold)`, zone: 'positive' };
  if (rsi > 70) return { text: `${rsi.toFixed(1)} (Overbought)`, zone: 'negative' };
  return { text: rsi.toFixed(1), zone: 'neutral' };
}

/** Human-readable date */
export function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleDateString('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'Asia/Jakarta',
  });
}

/** Confidence → percentage string */
export function formatConfidence(value) {
  if (value == null) return '—';
  return `${Math.round(value * 100)}%`;
}
