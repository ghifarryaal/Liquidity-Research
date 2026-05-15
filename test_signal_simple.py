#!/usr/bin/env python3
"""Test signal generation locally"""

# Add backend to path
import sys
sys.path.insert(0, 'backend')

from app.services.clustering_engine import get_buy_hold_sell_signal

# Test
label = "Buy the Dip"
confidence = 0.8

print(f"Testing: label='{label}', confidence={confidence}")
result = get_buy_hold_sell_signal(label, confidence)
print(f"Result: {result}")
print(f"\nSignal: {result['signal']}")
print(f"Strength: {result['strength']}")
print(f"Recommendation: {result['recommendation']}")
