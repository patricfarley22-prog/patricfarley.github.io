#!/usr/bin/env python3
import json
from datetime import datetime

COINS = [
    {"symbol": "TROLL", "name": "Troll", "market_cap": 116950000, "price": 0.116525, "change_24h": -11.5, "change_7d": -20.0},
    {"symbol": "MELANIA", "name": "Melania Meme", "market_cap": 96410000, "price": 0.101189, "change_24h": -4.7, "change_7d": 0.0},
    {"symbol": "TURBO", "name": "Turbo", "market_cap": 84880000, "price": 0.00123, "change_24h": -8.9, "change_7d": 0.0},
    {"symbol": "BRETT", "name": "Brett", "market_cap": 83530000, "price": 0.008421, "change_24h": -8.2, "change_7d": 0.0},
    {"symbol": "BABYDOGE", "name": "Baby Doge Coin", "market_cap": 78990000, "price": 0.000000, "change_24h": -4.1, "change_7d": 0.0},
    {"symbol": "PONKE", "name": "Ponke", "market_cap": 65000000, "price": 0.065, "change_24h": -12.0, "change_7d": 0.0},
    {"symbol": "MOG", "name": "Mog Coin", "market_cap": 59240000, "price": 0.000001, "change_24h": -7.8, "change_7d": 0.0},
    {"symbol": "POPCAT", "name": "Popcat", "market_cap": 58950000, "price": 0.06016, "change_24h": -5.5, "change_7d": 0.0},
    {"symbol": "UPUMP", "name": "Unit Pump", "market_cap": 57210000, "price": 0.001794, "change_24h": -4.8, "change_7d": 0.0},
    {"symbol": "MEW", "name": "cat in a dogs world", "market_cap": 51590000, "price": 0.00058, "change_24h": -7.5, "change_7d": 0.0},
    {"symbol": "GIGA", "name": "Gigachad", "market_cap": 42870000, "price": 0.004469, "change_24h": -7.7, "change_7d": 0.0},
    {"symbol": "WKC", "name": "Wiki Cat", "market_cap": 42970000, "price": 0.000000, "change_24h": -1.5, "change_7d": 0.0},
    {"symbol": "BOME", "name": "BOOK OF MEME", "market_cap": 40700000, "price": 0.00059, "change_24h": -6.0, "change_7d": 0.0},
    {"symbol": "PM", "name": "PumpMeme", "market_cap": 40380000, "price": 1.26, "change_24h": -2.7, "change_7d": 0.0},
    {"symbol": "ELON", "name": "Dogelon Mars", "market_cap": 39330000, "price": 0.000000, "change_24h": -4.8, "change_7d": 0.0},
    {"symbol": "ROSA", "name": "Rosa Inu", "market_cap": 37850000, "price": 0.000373, "change_24h": 0.4, "change_7d": 0.0},
    {"symbol": "ZEREBRO", "name": "zerebro", "market_cap": 28471555, "price": 0.02821, "change_24h": -2.0, "change_7d": 0.0},
    {"symbol": "House", "name": "Housecoin", "market_cap": 3338250, "price": 0.003346, "change_24h": -14.57, "change_7d": 0.0},
    {"symbol": "DOWGE", "name": "Dowge", "market_cap": 3200000, "price": 0.003144, "change_24h": -5.34, "change_7d": -8.0},
    {"symbol": "TOKABU", "name": "Tokabu", "market_cap": 2410000, "price": 0.00241, "change_24h": -15.49, "change_7d": -20.0},
    {"symbol": "BITTY", "name": "The Bitcoin Mascot", "market_cap": 933910, "price": 0.00092, "change_24h": -2.03, "change_7d": 0.0},
    {"symbol": "WOBBLES", "name": "Wobbles", "market_cap": 910000, "price": 0.000914, "change_24h": -19.49, "change_7d": -25.0},
    {"symbol": "PENGO", "name": "Pengo", "market_cap": 590000, "price": 0.000592, "change_24h": -2.38, "change_7d": -5.0},
    {"symbol": "OMEGAX", "name": "OmegaX", "market_cap": 360000, "price": 0.000365, "change_24h": -1.73, "change_7d": 0.0},
    {"symbol": "HACHI", "name": "Hachi", "market_cap": 22000, "price": 0.000000, "change_24h": -2.90, "change_7d": -5.0}
]

def main():
    coins = sorted(COINS, key=lambda x: x['market_cap'], reverse=True)
    
    print("=" * 80)
    print("TOP 25 MEME COINS UNDER $200M")
    print("=" * 80)
    
    print("\n{:<4} {:<10} {:<22} {:<12} {:<12} {:<8} {:<8}".format("#", "Symbol", "Name", "MCap", "Price", "24h", "7d"))
    print("-" * 80)
    
    for i, c in enumerate(coins, 1):
        mcap = c['market_cap'] / 1_000_000
        print("{:<4} {:<10} {:<22} ${:<11.2f}M ${:<11.8f} {:<+7.1f}% {:<+7.1f}%".format(
            i, c['symbol'], c['name'][:20], mcap, c['price'], c['change_24h'], c['change_7d']))
    
    nano = [c for c in coins if c['market_cap'] < 1_000_000]
    micro = [c for c in coins if 1_000_000 <= c['market_cap'] < 10_000_000]
    small = [c for c in coins if 10_000_000 <= c['market_cap'] < 50_000_000]
    mid = [c for c in coins if 50_000_000 <= c['market_cap'] < 200_000_000]
    
    print("\n" + "="*80)
    print("BREAKDOWN:")
    print("  Nano (<$1M): {}".format(len(nano)))
    print("  Micro ($1-10M): {}".format(len(micro)))
    print("  Small ($10-50M): {}".format(len(small)))
    print("  Mid ($50-200M): {}".format(len(mid)))
    
    best = sorted([c for c in coins if c['change_24h']], key=lambda x: x['change_24h'], reverse=True)[:5]
    worst = sorted([c for c in coins if c['change_24h']], key=lambda x: x['change_24h'])[:5]
    
    print("\n" + "="*80)
    print("TOP PICKS:")
    print("\n  Best 24h:")
    for c in best:
        print("    {}: {:+.1f}%".format(c['symbol'], c['change_24h']))
    print("\n  Worst 24h (dip buys):")
    for c in worst:
        print("    {}: {:+.1f}%".format(c['symbol'], c['change_24h']))
    
    with open('meme_coin_data/top25_under200m.json', 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'count': len(coins), 'coins': coins}, f, indent=2)
    
    print("\n" + "="*80)
    print("Saved: meme_coin_data/top25_under200m.json")
    print("="*80)

if __name__ == "__main__":
    main()
