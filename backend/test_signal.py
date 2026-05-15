#!/usr/bin/env python3
"""
Quick test script to verify signal generation works
"""
import sys
sys.path.insert(0, '/root/prediksi-saham-LQ45/backend')

from app.services.clustering_engine import get_buy_hold_sell_signal

# Test cases
test_cases = [
    ("Buy the Dip", 0.8),
    ("Buy the Dip", 0.5),
    ("Trending / Momentum", 0.85),
    ("Hold / Sideways", 0.55),
    ("High Risk / Avoid", 0.7),
]

print("Testing get_buy_hold_sell_signal()...\n")

for label, conf in test_cases:
    try:
        result = get_buy_hold_sell_signal(label, conf)
        print(f"✓ Label: {label:25} | Conf: {conf} | Signal: {result['signal']:15} | Rec: {result['recommendation'][:50]}")
    except Exception as e:
        print(f"✗ Label: {label:25} | Conf: {conf} | ERROR: {e}")

print("\nDone!")
