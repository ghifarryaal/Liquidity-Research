# Signal Filter Buttons - Dashboard Feature

## Overview

Tombol filter baru di dashboard toolbar yang memungkinkan user untuk melihat saham berdasarkan signal trading (BUY, HOLD, SELL), mirip dengan filter klaster AI yang sudah ada.

## Features

### 1. **Filter Buttons**
Empat tombol filter signal:
- **🔍 Semua Sinyal** - Tampilkan semua saham (default)
- **🟢 Buy** - Tampilkan hanya saham dengan signal BUY atau STRONG BUY
- **🟡 Hold** - Tampilkan hanya saham dengan signal HOLD
- **🔴 Sell** - Tampilkan hanya saham dengan signal SELL atau STRONG SELL

### 2. **Visual Design**
- **Active state:** Border tebal (2px) dengan warna signal, background transparan
- **Inactive state:** Border tipis abu-abu, hover effect
- **Color-coded:**
  - BUY: Hijau (#00FFB2)
  - HOLD: Kuning/Orange (#f59e0b)
  - SELL: Merah (#ef4444)
  - Semua: Abu-abu (#94a3b8)
- **Emoji indicators:** 🟢 🟡 🔴 untuk visual clarity

### 3. **Filter Logic**
```javascript
// Kombinasi dengan filter cluster
if (activeFilter !== 'all') {
  list = list.filter(s => s.cluster_label === activeFilter);
}

// Filter by signal
if (activeSignalFilter !== 'all') {
  list = list.filter(s => {
    const signal = s.signal || 'HOLD';
    return signal.includes(activeSignalFilter);
  });
}
```

**Logic:**
- `signal.includes('BUY')` → Matches "BUY" dan "STRONG BUY"
- `signal.includes('SELL')` → Matches "SELL" dan "STRONG SELL"
- Default fallback → "HOLD" jika signal null/undefined

### 4. **Combined Filtering**
User dapat menggunakan **multiple filters** secara bersamaan:
- ✅ Filter Klaster AI + Filter Signal
- ✅ Filter Signal + Search
- ✅ Filter Klaster + Filter Signal + Search

**Example:**
- Filter: "Buy the Dip" + Signal: "BUY" → Hanya saham Buy the Dip dengan signal BUY
- Filter: "Trending / Momentum" + Signal: "STRONG BUY" → Hanya saham momentum dengan strong buy signal

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 Search: [Cari emiten, nama, atau sektor...]         │
│                                                         │
│ Filter Klaster AI                                       │
│ [Semua] [Beli Saat Turun] [Momentum] [Konsolidasi]    │
│ [Risiko Tinggi]                                        │
│                                                         │
│ Filter Sinyal Trading                                   │
│ [🔍 Semua Sinyal] [🟢 Buy] [🟡 Hold] [🔴 Sell]        │
└─────────────────────────────────────────────────────────┘
```

## Button States

### Active State (Selected)
```jsx
style={{
  background: `${opt.color}15`,  // 15% opacity
  borderColor: opt.color,         // Solid color border
  color: opt.color                // Text color matches signal
}}
className="border-2"              // Thicker border
```

### Inactive State
```jsx
style={{
  color: 'var(--md-sys-color-on-surface-variant)'
}}
className="bg-surface border border-outline-variant hover:border-outline"
```

## Responsive Design

### Desktop (md+)
- Full width buttons dengan padding 3
- Text size: 11px
- Icon/Emoji size: normal
- Flex wrap untuk multiple rows jika perlu

### Mobile
- Compact buttons dengan padding 1.5
- Text size: 11px (sama)
- Flex wrap untuk multiple rows
- Touch-friendly spacing (gap-2)

## Integration

### Location
Di dalam **Toolbar** section, setelah "Filter Klaster AI"

### State Management
```javascript
const [activeSignalFilter, setActiveSignalFilter] = useState('all');
```

### Reset Filter
Tombol "Reset filter" akan reset semua filter:
```javascript
onClick={() => {
  setSearch('');
  setActiveFilter('all');
  setActiveSignalFilter('all');  // ← Reset signal filter
}}
```

## Filter Options Configuration

```javascript
const SIGNAL_FILTER_OPTIONS = [
  { 
    value: 'all', 
    label: 'Semua Sinyal', 
    icon: 'filter_list', 
    color: '#94a3b8' 
  },
  { 
    value: 'BUY', 
    label: 'Buy', 
    icon: 'arrow_upward', 
    color: '#00FFB2', 
    emoji: '🟢' 
  },
  { 
    value: 'HOLD', 
    label: 'Hold', 
    icon: 'pause', 
    color: '#f59e0b', 
    emoji: '🟡' 
  },
  { 
    value: 'SELL', 
    label: 'Sell', 
    icon: 'arrow_downward', 
    color: '#ef4444', 
    emoji: '🔴' 
  },
];
```

## Use Cases

### Use Case 1: Cari Peluang Buy
**Action:** Klik tombol "🟢 Buy"
**Result:** Tabel hanya menampilkan saham dengan signal BUY atau STRONG BUY
**Benefit:** Fokus pada peluang entry yang direkomendasikan

### Use Case 2: Review Posisi Hold
**Action:** Klik tombol "🟡 Hold"
**Result:** Tabel hanya menampilkan saham dengan signal HOLD
**Benefit:** Review saham yang perlu monitoring lebih lanjut

### Use Case 3: Identifikasi Risk
**Action:** Klik tombol "🔴 Sell"
**Result:** Tabel hanya menampilkan saham dengan signal SELL atau STRONG SELL
**Benefit:** Identifikasi saham yang perlu di-exit atau dihindari

### Use Case 4: Kombinasi Filter
**Action:** 
1. Klik "Buy the Dip" (cluster filter)
2. Klik "🟢 Buy" (signal filter)

**Result:** Hanya saham Buy the Dip dengan signal BUY
**Benefit:** Temukan saham oversold dengan konfirmasi signal buy

## Example Scenarios

### Scenario 1: Bullish Market
```
Filter: 🟢 Buy
Result: 26 saham (65% dari total)
Insight: Mayoritas pasar bullish, banyak peluang entry
```

### Scenario 2: Bearish Market
```
Filter: 🔴 Sell
Result: 24 saham (60% dari total)
Insight: Mayoritas pasar bearish, banyak saham perlu di-exit
```

### Scenario 3: Neutral Market
```
Filter: 🟡 Hold
Result: 26 saham (65% dari total)
Insight: Pasar konsolidasi, tunggu konfirmasi arah
```

### Scenario 4: Selective Trading
```
Filter Cluster: "Trending / Momentum"
Filter Signal: 🟢 Buy
Result: 8 saham
Insight: Saham momentum dengan signal buy - high probability setup
```

## Data Requirements

Setiap stock object harus memiliki field:
- `signal`: string ("BUY", "STRONG BUY", "HOLD", "SELL", "STRONG SELL")
- Jika `signal` null/undefined → Default ke "HOLD"

## Files Modified

- ✅ `frontend/src/components/dashboard/InsightFeed.jsx`
  - Added `SIGNAL_FILTER_OPTIONS` constant
  - Added `activeSignalFilter` state
  - Added signal filter logic in `filtered` useMemo
  - Added signal filter buttons UI
  - Updated reset filter to include signal filter

## Deployment

- ✅ Committed to GitHub (commit `0b22400`)
- ✅ Vercel will auto-deploy in 2-3 minutes
- ⚠️ Requires VPS backend update to show real signal data

## Verification Steps

1. **Wait for Vercel deployment** (~2-3 minutes)
2. **Open dashboard:** https://indonesiastockanalyst.my.id
3. **Clear cache:** `Cmd + Shift + R` or `Ctrl + Shift + R`
4. **Check for signal filter buttons** below cluster filter
5. **Test filtering:**
   - Click "🟢 Buy" → Table shows only BUY signals
   - Click "🟡 Hold" → Table shows only HOLD signals
   - Click "🔴 Sell" → Table shows only SELL signals
   - Click "Semua Sinyal" → Table shows all stocks
6. **Test combined filtering:**
   - Select cluster filter + signal filter
   - Verify table shows correct combination
7. **Test reset:**
   - Apply multiple filters
   - Click "Reset filter" in empty state
   - Verify all filters reset to "all"

## Interaction with Other Features

### Signal Distribution Bar
- Signal filter buttons work in tandem with distribution bar
- Clicking filter updates table, distribution bar shows overall stats
- Distribution bar is NOT filtered (always shows all stocks)

### Cluster Filter
- Can be used together with signal filter
- Filters are applied sequentially (cluster → signal → search)
- Independent toggle behavior

### Search
- Search applies after all filters
- Can search within filtered results
- Reset button clears all filters + search

### Sort
- Sort applies after filtering
- Maintains sort order when changing filters
- Options: Confidence, Change %, Ticker

## Future Enhancements

Potential improvements:
- [ ] Show count badge on each filter button (e.g., "Buy (26)")
- [ ] Add "STRONG" filter to separate STRONG BUY/SELL from regular
- [ ] Click on Signal Distribution bar section to auto-filter
- [ ] Keyboard shortcuts (B for Buy, H for Hold, S for Sell)
- [ ] Save filter preferences to localStorage
- [ ] URL query params for shareable filtered views

## Notes

- Filter buttons use emoji for better visual recognition
- Active state uses 15% opacity background for subtle highlight
- Border-2 on active state makes selection clear
- Hover effect on inactive buttons for better UX
- Touch-friendly spacing for mobile users
- Gracefully handles null/undefined signal values

## Commit

```
0b22400 - Add signal filter buttons (BUY/HOLD/SELL) to dashboard toolbar
```
