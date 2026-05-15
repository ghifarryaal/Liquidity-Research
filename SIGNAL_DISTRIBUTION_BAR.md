# Signal Distribution Bar - Dashboard Feature

## Overview

Section bar baru di dashboard yang menampilkan distribusi signal BUY, HOLD, dan SELL secara visual dengan progress bar dan statistik lengkap.

## Features

### 1. **Visual Progress Bar**
- 🟢 **BUY** - Hijau gradient (#00FFB2)
- 🟡 **HOLD** - Kuning/Orange gradient (#f59e0b)
- 🔴 **SELL** - Merah gradient (#ef4444)
- Animated bar dengan smooth transition
- Hover tooltip menampilkan jumlah emiten per kategori

### 2. **Market Sentiment Indicator**
Otomatis mendeteksi sentimen pasar berdasarkan distribusi:
- **Bullish** 📈 - Jika BUY > 50%
- **Bearish** 📉 - Jika SELL > 50%
- **Neutral** ➡️ - Jika HOLD > 60%
- **Mixed** 🔀 - Jika tidak ada dominasi jelas

### 3. **Statistics Cards**
Tiga card menampilkan:
- Jumlah emiten per kategori
- Persentase dari total
- Color-coded untuk visual clarity

### 4. **Contextual Insight**
Text insight otomatis berdasarkan distribusi:
- **Mayoritas Bullish:** Saran untuk akumulasi dengan risk management
- **Mayoritas Bearish:** Saran untuk reduce exposure atau tunggu reversal
- **Mayoritas Hold:** Saran untuk tunggu konfirmasi arah
- **Mixed:** Saran untuk fokus stock picking individual

## Component Structure

```
SignalDistribution.jsx
├── Header (Sentiment + Total Stocks)
├── Progress Bar (Animated, with tooltips)
├── Legend Cards (BUY, HOLD, SELL statistics)
└── Insight Text (Contextual recommendation)
```

## Logic

### Signal Categorization
```javascript
stocks.forEach(stock => {
  const signal = stock.signal || 'HOLD';
  if (signal.includes('BUY')) {
    counts.buy++;  // Includes "BUY" and "STRONG BUY"
  } else if (signal.includes('SELL')) {
    counts.sell++;  // Includes "SELL" and "STRONG SELL"
  } else {
    counts.hold++;  // Default for "HOLD" or null
  }
});
```

### Percentage Calculation
```javascript
percentages = {
  buy: (distribution.buy / distribution.total) * 100,
  hold: (distribution.hold / distribution.total) * 100,
  sell: (distribution.sell / distribution.total) * 100,
}
```

### Sentiment Detection
```javascript
if (percentages.buy > 50) → Bullish
else if (percentages.sell > 50) → Bearish
else if (percentages.hold > 60) → Neutral
else → Mixed
```

## Responsive Design

### Desktop (md+)
- Full width bar dengan padding 6
- Text size: base/lg
- Icon size: 3xl
- Card padding: 3

### Mobile
- Compact bar dengan padding 4
- Text size: xs/sm
- Icon size: 2xl
- Card padding: 2
- Grid layout tetap 3 columns untuk symmetry

## Animation

- **Initial:** Fade in from top (y: -10)
- **Progress Bar:** Width animation dengan stagger delay
  - BUY: 0s delay
  - HOLD: 0.1s delay
  - SELL: 0.2s delay
- **Duration:** 0.8s dengan easeOut easing
- **Hover:** Tooltip fade in/out

## Integration

### Location
Ditampilkan di **InsightFeed** component, sebelum header "Penyaring Saham Taktis"

### Props
```jsx
<SignalDistribution 
  stocks={stocks}      // Array of stock objects with signal field
  isLoading={isLoading} // Boolean for loading state
/>
```

### Data Requirements
Setiap stock object harus memiliki field:
- `signal`: string ("BUY", "STRONG BUY", "HOLD", "SELL", "STRONG SELL")

## Example Output

### Scenario 1: Bullish Market
```
📈 Distribusi Sinyal Pasar
Sentimen: Bullish

[████████████████████░░░░░░░░] 65% BUY | 25% HOLD | 10% SELL

BUY: 26 (65%)
HOLD: 10 (25%)
SELL: 4 (10%)

💡 Mayoritas sinyal bullish. Pasar menunjukkan peluang entry yang menarik.
```

### Scenario 2: Bearish Market
```
📉 Distribusi Sinyal Pasar
Sentimen: Bearish

[░░░░░░░░████████████████████] 15% BUY | 25% HOLD | 60% SELL

BUY: 6 (15%)
HOLD: 10 (25%)
SELL: 24 (60%)

💡 Mayoritas sinyal bearish. Pasar menunjukkan tekanan jual.
```

### Scenario 3: Neutral Market
```
➡️ Distribusi Sinyal Pasar
Sentimen: Neutral

[░░░░░░░░████████████░░░░░░░░] 20% BUY | 65% HOLD | 15% SELL

BUY: 8 (20%)
HOLD: 26 (65%)
SELL: 6 (15%)

💡 Mayoritas sinyal hold. Pasar dalam fase konsolidasi.
```

## Files Created/Modified

### New Files:
- ✅ `frontend/src/components/dashboard/SignalDistribution.jsx`

### Modified Files:
- ✅ `frontend/src/components/dashboard/InsightFeed.jsx`
  - Import SignalDistribution
  - Add component before header

## Deployment

- ✅ Committed to GitHub (commit `d7aaeca`)
- ✅ Vercel will auto-deploy in 2-3 minutes
- ⚠️ Requires VPS backend update to show real signal data

## Verification Steps

1. **Wait for Vercel deployment** (~2-3 minutes)
2. **Open dashboard:** https://indonesiastockanalyst.my.id
3. **Clear cache:** `Cmd + Shift + R` or `Ctrl + Shift + R`
4. **Check for Signal Distribution bar** above the table
5. **Verify:**
   - Progress bar shows colored sections
   - Hover tooltips work
   - Statistics cards show numbers
   - Sentiment indicator displays correctly
   - Insight text is contextual

## Notes

- Component gracefully handles loading state with skeleton
- Falls back to HOLD if signal is null/undefined
- Minimum width 2% for each section to ensure visibility
- Percentage labels only show if section > 8% width
- Tooltips appear on hover for detailed breakdown

## Future Enhancements

Potential improvements:
- [ ] Click on bar section to filter table by signal type
- [ ] Historical trend chart (signal distribution over time)
- [ ] Export signal distribution as image/PDF
- [ ] Add animation when data updates
- [ ] Show signal strength breakdown (STRONG vs MODERATE vs WEAK)

## Commit

```
d7aaeca - Add Signal Distribution bar to dashboard showing BUY/HOLD/SELL breakdown
```
