# 🚀 Quick Fix: Update VPS untuk Signal

## Copy-Paste Command Ini ke VPS:

```bash
cd /root/prediksi-saham-LQ45 && \
git pull origin main && \
git log --oneline -1 && \
docker-compose down && \
docker-compose up -d --build backend && \
echo "⏳ Waiting 15 seconds for backend to start..." && \
sleep 15 && \
echo "✅ Testing API..." && \
curl -s "https://api-quant.indonesiastockanalyst.my.id/api/stock/BBCA.JK" | python3 -c "import sys, json; data = json.load(sys.stdin); signal = data.get('signal'); print('✓ Signal:', signal if signal else '❌ STILL NONE - CHECK LOGS!'); print('✓ Strength:', data.get('signal_strength')); print('✓ Recommendation:', data.get('signal_recommendation')[:80] if data.get('signal_recommendation') else 'None')"
```

## Expected Output:

```
✓ Signal: BUY (atau STRONG BUY, HOLD, SELL, STRONG SELL)
✓ Strength: MODERATE (atau STRONG, WEAK)
✓ Recommendation: 🟢 BUY - Confidence 72% | Pertimbangkan entry bertahap...
```

## Jika Signal Masih None:

```bash
# Force rebuild dengan no-cache
cd /root/prediksi-saham-LQ45 && \
docker-compose down && \
docker-compose build --no-cache backend && \
docker-compose up -d backend && \
sleep 15 && \
docker-compose logs backend --tail=50 | grep -i "error\|signal"
```

## Verifikasi Frontend:

1. Buka: https://indonesiastockanalyst.my.id
2. Clear cache: `Cmd + Shift + R` (Mac) atau `Ctrl + Shift + R` (Windows)
3. Cek kolom "SINYAL" → harus ada badge 🟢 BUY, 🟡 HOLD, atau 🔴 SELL
4. Klik detail saham → harus ada card "Signal Explanation"

## Troubleshooting Lengkap:

Lihat file: `UPDATE_VPS_SIGNAL.md`
