// Cluster label → UI configuration mapping
// Single source of truth for colors, icons, and copy
// New labels (backend v2): 'Beli Saat Turun', 'Momentum', 'Konsolidasi', 'High Risk'
// Legacy aliases kept for backward compatibility

const _DIP = {
  label:        'Beli Saat Turun',
  labelID:      'Beli Saat Turun',
  color:        '#00FFB2',
  bgClass:      'badge-dip',
  glowColor:    'rgba(0,255,178,0.35)',
  borderColor:  'rgba(0,255,178,0.4)',
  icon:         '📉',
  emoji:        '🟢',
  priority:     0,
  description:  'Saham oversold, berpotensi technical bounce',
  filterLabel:  'Beli Saat Turun',
};

const _MOMENTUM = {
  label:        'Momentum',
  labelID:      'Tren Naik / Momentum',
  color:        '#60a5fa',
  bgClass:      'badge-momentum',
  glowColor:    'rgba(59,130,246,0.35)',
  borderColor:  'rgba(59,130,246,0.4)',
  icon:         '🚀',
  emoji:        '🔵',
  priority:     1,
  description:  'Momentum bullish kuat, harga di atas EMA',
  filterLabel:  'Momentum',
};

const _HOLD = {
  label:        'Konsolidasi',
  labelID:      'Konsolidasi / Sideways',
  color:        '#fbbf24',
  bgClass:      'badge-hold',
  glowColor:    'rgba(245,158,11,0.35)',
  borderColor:  'rgba(245,158,11,0.4)',
  icon:         '⏸️',
  emoji:        '🟡',
  priority:     2,
  description:  'Pergerakan sideways, tunggu konfirmasi arah',
  filterLabel:  'Konsolidasi',
};

const _RISK = {
  label:        'High Risk',
  labelID:      'Risiko Tinggi / Hindari',
  color:        '#f87171',
  bgClass:      'badge-avoid',
  glowColor:    'rgba(239,68,68,0.35)',
  borderColor:  'rgba(239,68,68,0.4)',
  icon:         '⚠️',
  emoji:        '🔴',
  priority:     3,
  description:  'Volatilitas tinggi, sinyal teknikal bearish',
  filterLabel:  'High Risk',
};

export const CLUSTER_CONFIG = {
  // ── New labels (backend v2) ──
  'Beli Saat Turun':    _DIP,
  'Momentum':           _MOMENTUM,
  'Konsolidasi':        _HOLD,
  'High Risk':          _RISK,

  // ── Legacy aliases (backward compat) ──
  'Buy the Dip':        _DIP,
  'Trending / Momentum': _MOMENTUM,
  'Hold / Sideways':    _HOLD,
  'High Risk / Avoid':  _RISK,
};

// Canonical label list (new names only)
export const CLUSTER_LABELS = ['Beli Saat Turun', 'Momentum', 'Konsolidasi', 'High Risk'];

export const MACRO_REGIME_CONFIG = {
  'Risk-On':  { color: '#00FFB2', icon: '📈', label: 'Risk On',  desc: 'Kondisi global mendukung' },
  'Neutral':  { color: '#fbbf24', icon: '⚖️',  label: 'Netral',   desc: 'Kondisi global campuran' },
  'Risk-Off': { color: '#f87171', icon: '🛡️',  label: 'Risk Off', desc: 'Kondisi global waspada' },
};

// Educational tooltips — Indonesian
export const INDICATOR_TOOLTIPS = {
  RSI: {
    title: 'RSI (Relative Strength Index)',
    body: 'Mengukur kecepatan dan perubahan pergerakan harga. Nilai di bawah 30 = oversold (murah secara teknikal), di atas 70 = overbought (mahal secara teknikal). Rentang ideal: 40–60.',
  },
  MACD: {
    title: 'MACD (Moving Average Convergence Divergence)',
    body: 'Indikator momentum yang menunjukkan hubungan antara dua moving average. Ketika garis MACD memotong ke atas garis sinyal = sinyal bullish. Sebaliknya = sinyal bearish.',
  },
  EMA: {
    title: 'EMA (Exponential Moving Average)',
    body: 'Rata-rata harga bergerak yang memberi bobot lebih pada harga terbaru. EMA 20 = tren jangka pendek. EMA 50 = tren jangka menengah. Harga di atas EMA = uptrend.',
  },
  BB: {
    title: 'Bollinger Bands',
    body: 'Tiga garis yang membentuk "pita" di sekitar harga. Pita menyempit = volatilitas rendah (breakout akan datang). Harga di bawah garis bawah = area oversold potensial.',
  },
  Clustering: {
    title: 'Machine Learning Clustering',
    body: 'AI menggunakan K-Means Clustering untuk mengelompokkan saham berdasarkan pola teknikal serupa. Setiap cluster memiliki karakteristik RSI, MACD, dan Bollinger Bands yang khas.',
  },
  ATR: {
    title: 'ATR (Average True Range)',
    body: 'Mengukur volatilitas harga. ATR tinggi = pergerakan harga besar. Gunakan untuk menentukan jarak stop-loss: stop-loss = 1.5–2x ATR dari harga entry.',
  },
  VOL: {
    title: 'Volume Ratio',
    body: 'Rasio volume hari ini dibanding rata-rata 20 hari. Nilai > 1.5 = volume tinggi, mengkonfirmasi pergerakan harga. Volume rendah saat harga naik = sinyal lemah.',
  },
};
