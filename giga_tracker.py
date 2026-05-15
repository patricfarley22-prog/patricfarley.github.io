#!/usr/bin/env python3
"""
GIGACHAD (GIGA) TRACKER
Continuous monitoring for 63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9
Added to tracked coins list
"""

import json
import os
from datetime import datetime

DATA_DIR = "meme_coin_data"

# GIGA coin data
GIGA = {
    "symbol": "GIGA",
    "name": "GIGACHAD",
    "token": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9",
    "chain": "solana",
    "ca": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9",
    "website": "https://gigachadsolana.com/",
    "twitter": "https://x.com/gigachad",
    "telegram": "https://t.me/gigachadsol",
    "dex": "raydium",
    "added": "2026-05-15",
    "tracker": "patric"
}

def add_to_tracked():
    """Add GIGA to tracked coins"""
    filepath = f"{DATA_DIR}/tracked_coins.json"
    
    coins = []
    if os.path.exists(filepath):
        with open(filepath) as f:
            coins = json.load(f)
    
    # Check if already tracked
    existing = [c for c in coins if c.get('symbol') == 'GIGA']
    if existing:
        print("GIGA already tracked")
        return
    
    coins.append(GIGA)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(coins, f, indent=2)
    
    print(f"GIGA added to tracked coins")
    print(f"Total tracked: {len(coins)}")
    print(f"Saved: {filepath}")

def display_tracked():
    """Show all tracked coins"""
    filepath = f"{DATA_DIR}/tracked_coins.json"
    
    if not os.path.exists(filepath):
        print("No tracked coins yet")
        return
    
    with open(filepath) as f:
        coins = json.load(f)
    
    print("=" * 80)
    print("TRACKED COINS")
    print("=" * 80)
    print(f"\n{'#':<4} {'Symbol':<10} {'Name':<20} {'Chain':<8} {'Added':<12} {'By':<10}")
    print("-" * 70)
    
    for i, c in enumerate(coins, 1):
        print(f"{i:<4} {c['symbol']:<10} {c['name'][:18]:<20} {c['chain']:<8} {c.get('added', 'N/A'):<12} {c.get('tracker', 'N/A'):<10}")
    
    print(f"\nTotal: {len(coins)} coins")

if __name__ == "__main__":
    print("GIGACHAD Tracker Setup")
    print("=" * 60)
    
    add_to_tracked()
    display_tracked()
    
    print("\n" + "=" * 60)
    print("To monitor GIGA:")
    print("  python giga_monitor.py")
    print("Or use:")
    print("  python nano_cap_fast.py --include giga")
    print("=" * 60)
