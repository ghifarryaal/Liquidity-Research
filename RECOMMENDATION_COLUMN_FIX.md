# Fix: Kolom Rekomendasi Tidak Muncul

## Masalah

Kolom "REKOMENDASI" di tabel dashboard ada di header tapi tidak ada data yang ditampilkan.

## Root Cause

Di file `frontend/src/components/dashboard/InsightFeed.jsx`:
- Header tabel memiliki 9 kolom (termasuk "Rekomendasi")
- Body tabel hanya memiliki 8 `<td>` (kolom rekomendasi tidak ada)
- Loading skeleton dan empty state menggunakan `colSpan={8}` (seharusnya 9)

## Solusi

### 1. Tambah kolom rekomendasi di body tabel

```jsx
<td className="py-2.5 px-4">
  <span className="text-[10px] text-on-surface-variant max-w-[200px] line-clamp-2">
    {stock.signal_recommendation || stock.strategy || '—'}
  </span>
</td>
```

**Logic:**
- Prioritas 1: `signal_recommendation` (dari API signal generation)
- Prioritas 2: `strategy` (dari cluster reasoning)
- Fallback: `—` (dash jika tidak ada data)

### 2. Update loading skeleton

```jsx
Array.from({ length: 9 }).map((_, j) => (  // Changed from 8 to 9
  <td key={j} className="py-3 px-4">
    <div className="h-3.5 bg-surface-container-high rounded animate-pulse" 
         style={{ width: j === 8 ? '150px' : ... }} />  // Width for recommendation column
  </td>
))
```

### 3. Update empty state colspan

```jsx
<td colSpan={9} className="py-16 text-center">  // Changed from 8 to 9
```

## Expected Output

Setelah fix ini dan VPS ter-update, kolom "REKOMENDASI" akan menampilkan:

**Contoh 1 (dengan signal_recommendation):**
```
🟢 BUY - Confidence 72% | Pertimbangkan entry bertahap dengan manajemen risiko ketat
```

**Contoh 2 (fallback ke strategy):**
```
Pertimbangkan akumulasi bertahap di area support.
```

**Contoh 3 (no data):**
```
—
```

## Deployment

- ✅ Frontend: Auto-deploy ke Vercel (commit `2b650c1`)
- ⚠️ Backend: Perlu update VPS agar `signal_recommendation` tersedia di API

## Verifikasi

1. **Tunggu Vercel deployment selesai** (~2-3 menit)
2. **Buka dashboard:** https://indonesiastockanalyst.my.id
3. **Clear cache:** `Cmd + Shift + R` atau `Ctrl + Shift + R`
4. **Cek kolom "REKOMENDASI":**
   - Jika VPS sudah ter-update: akan muncul text rekomendasi lengkap
   - Jika VPS belum ter-update: akan muncul strategy text (fallback)

## Related Files

- `frontend/src/components/dashboard/InsightFeed.jsx` - Main fix
- `backend/app/routers/cluster.py` - API yang return `signal_recommendation`
- `backend/app/services/clustering_engine.py` - Function `get_buy_hold_sell_signal()`

## Commit

```
2b650c1 - Add recommendation column to InsightFeed table
```
