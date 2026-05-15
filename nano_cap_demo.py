#!/usr/bin/env python3
"""
NANO-CAP MEME COIN DEMO
Shows example output for coins under $10M market cap
"""

import json
import os
from datetime import datetime

# Create sample nano-cap data based on what the scanner would find
SAMPLE_NANO_CAPS = [
    {
        "id": "aura-on-sol",
        "symbol": "AURA",
        "name": "aura",
        "current_price": 0.0198786,
        "market_cap": 9_141_078,
        "total_volume": 3_120_016,
        "price_change_24h": -0.005626460294938785,
        "price_change_percentage_24h": -22.06017,
        "price_change_percentage_7d_in_currency": 111.76800459036038,
        "price_change_percentage_30d_in_currency": 124.29423833083571,
        "ath": 0.239828,
        "ath_change_percentage": -91.81034,
        "ath_date": "2025-07-22T22:59:58.891Z",
    },
    {
        "id": "harrypotterobamasonic10in",
        "symbol": "BITCOIN",
        "name": "HarryPotterObamaSonic10Inu",
        "current_price": 0.01914628,
        "market_cap": 9_139_975,
        "total_volume": 2_744_137,
        "price_change_24h": -0.00071189354414955,
        "price_change_percentage_24h": -3.58489,
        "price_change_percentage_7d_in_currency": -9.052737416164366,
        "price_change_percentage_30d_in_currency": 6.434554919110506,
        "ath": 0.373421,
        "ath_change_percentage": -94.87383,
        "ath_date": "2024-10-13T05:00:06.998Z",
    },
    {
        "id": "moolah",
        "symbol": "MOOLAH",
        "name": "Moolah",
        "current_price": 0.0185099,
        "market_cap": 8_509_901,
        "total_volume": 261571,
        "price_change_24h": -5.9012417565153e-05,
        "price_change_percentage_24h": -0.3178,
        "price_change_percentage_7d_in_currency": -3.264875557365893,
        "price_change_percentage_30d_in_currency": 28.5418697715969,
        "ath": 0.03169501,
        "ath_change_percentage": -41.63313,
        "ath_date": "2026-05-09T15:20:29.007Z",
    },
    # Simulated smaller coins (typical for nano-caps)
    {
        "id": "nano-doge",
        "symbol": "NANODOGE",
        "name": "Nano Doge",
        "current_price": 0.00000123,
        "market_cap": 5_200_000,
        "total_volume": 450_000,
        "price_change_24h": 0.00000005,
        "price_change_percentage_24h": 25.5,
        "price_change_percentage_7d_in_currency": 150.0,
        "price_change_percentage_30d_in_currency": 400.0,
        "ath": 0.00000500,
        "ath_change_percentage": -75.4,
        "ath_date": "2026-04-01T00:00:00.000Z",
    },
    {
        "id": "micro-pepe",
        "symbol": "MICROPEPE",
        "name": "Micro Pepe",
        "current_price": 0.00004567,
        "market_cap": 3_800_000,
        "total_volume": 120_000,
        "price_change_24h": -0.00000200,
        "price_change_percentage_24h": -4.2,
        "price_change_percentage_7d_in_currency": -25.0,
        "price_change_percentage_30d_in_currency": -60.0,
        "ath": 0.00020000,
        "ath_change_percentage": -77.2,
        "ath_date": "2026-02-15T00:00:00.000Z",
    },
    {
        "id": "tiny-shib",
        "symbol": "TINYSHIB",
        "name": "Tiny Shib",
        "current_price": 0.00000089,
        "market_cap": 2_100_000,
        "total_volume": 85_000,
        "price_change_24h": 0.00000003,
        "price_change_percentage_24h": 15.0,
        "price_change_percentage_7d_in_currency": 45.0,
        "price_change_percentage_30d_in_currency": 120.0,
        "ath": 0.00000500,
        "ath_change_percentage": -82.2,
        "ath_date": "2026-03-20T00:00:00.000Z",
    },
    {
        "id": "mini-floki",
        "symbol": "MINIFLOKI",
        "name": "Mini Floki",
        "current_price": 0.00001234,
        "market_cap": 1_500_000,
        "total_volume": 65_000,
        "price_change_24h": -0.00000100,
        "price_change_percentage_24h": -7.5,
        "price_change_percentage_7d_in_currency": -15.0,
        "price_change_percentage_30d_in_currency": -40.0,
        "ath": 0.00008000,
        "ath_change_percentage": -84.6,
        "ath_date": "2026-01-10T00:00:00.000Z",
    },
    {
        "id": "pico-bonk",
        "symbol": "PICOBONK",
        "name": "Pico Bonk",
        "current_price": 0.00000045,
        "market_cap": 890_000,
        "total_volume": 32_000,
        "price_change_24h": 0.00000002,
        "price_change_percentage_24h": 20.0,
        "price_change_percentage_7d_in_currency": 80.0,
        "price_change_percentage_30d_in_currency": 250.0,
        "ath": 0.00000200,
        "ath_change_percentage": -77.5,
        "ath_date": "2026-04-10T00:00:00.000Z",
    },
]


def display_nano_caps(coins):
    """Display nano-cap coins"""
    print("=" * 80)
    print("NANO-CAP MEME COINS (Under $10M Market Cap)")
    print("=" * 80)
    print(f"Found: {len(coins)} coins")
    print("=" * 80)
    
    print(f"\n{'#':<4} {'Symbol':<12} {'Name':<20} {'Price':<14} {'MCap':<10} {'24h':<8} {'7d':<8} {'30d':<8}")
    print("-" * 80)
    
    for i, coin in enumerate(coins, 1):
        print(
            f"{i:<4} "
            f"{coin['symbol']:<12} "
            f"{coin['name'][:19]:<20} "
            f"${coin['current_price']:<13.8f} "
            f"${coin['market_cap']/1_000_000:<9.2f}M "
            f"{coin['price_change_percentage_24h']:<+7.1f}% "
            f"{coin['price_change_percentage_7d_in_currency']:<+7.1f}% "
            f"{coin['price_change_percentage_30d_in_currency']:<+7.1f}%"
        )
    
    # Summary
    avg_mcap = sum(c["market_cap"] for c in coins) / len(coins)
    avg_24h = sum(c["price_change_percentage_24h"] for c in coins) / len(coins)
    avg_7d = sum(c["price_change_percentage_7d_in_currency"] for c in coins) / len(coins)
    avg_30d = sum(c["price_change_percentage_30d_in_currency"] for c in coins) / len(coins)
    
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Average Market Cap: ${avg_mcap/1_000_000:.2f}M")
    print(f"Average 24h Change: {avg_24h:+.2f}%")
    print(f"Average 7d Change: {avg_7d:+.2f}%")
    print(f"Average 30d Change: {avg_30d:+.2f}%")
    print(f"Total Coins: {len(coins)}")
    
    # Ranges
    print(f"\nSmallest MCap: ${min(c['market_cap'] for c in coins)/1_000:.0f}K")
    print(f"Largest MCap: ${max(c['market_cap'] for c in coins)/1_000_000:.2f}M")
    
    # Top performers
    top_24h = max(coins, key=lambda x: x["price_change_percentage_24h"])
    worst_24h = min(coins, key=lambda x: x["price_change_percentage_24h"])
    top_30d = max(coins, key=lambda x: x["price_change_percentage_30d_in_currency"])
    worst_30d = min(coins, key=lambda x: x["price_change_percentage_30d_in_currency"])
    
    print(f"\nTop 24h Gainer: {top_24h['symbol']} ({top_24h['price_change_percentage_24h']:+.1f}%)")
    print(f"Worst 24h Drop: {worst_24h['symbol']} ({worst_24h['price_change_percentage_24h']:+.1f}%)")
    print(f"Top 30d Gainer: {top_30d['symbol']} ({top_30d['price_change_percentage_30d_in_currency']:+.1f}%)")
    print(f"Worst 30d Drop: {worst_30d['symbol']} ({worst_30d['price_change_percentage_30d_in_currency']:+.1f}%)")
    
    # ATH analysis
    print(f"\n{'='*80}")
    print("ALL-TIME HIGH ANALYSIS")
    print(f"{'='*80}")
    
    avg_ath_drop = sum(c["ath_change_percentage"] for c in coins) / len(coins)
    print(f"Average ATH Drop: {avg_ath_drop:.1f}%")
    
    closest_to_ath = min(coins, key=lambda x: abs(x["ath_change_percentage"]))
    print(f"Closest to ATH: {closest_to_ath['symbol']} ({closest_to_ath['ath_change_percentage']:.1f}%)")
    
    furthest_from_ath = min(coins, key=lambda x: x["ath_change_percentage"])
    print(f"Furthest from ATH: {furthest_from_ath['symbol']} ({furthest_from_ath['ath_change_percentage']:.1f}%)")


def main():
    print("=" * 80)
    print("NANO-CAP MEME COIN DEMO")
    print("Showing what the scanner would find under $10M market cap")
    print("=" * 80)
    
    display_nano_caps(SAMPLE_NANO_CAPS)
    
    # Save
    DATA_DIR = "meme_coin_data"
    os.makedirs(DATA_DIR, exist_ok=True)
    
    filepath = os.path.join(DATA_DIR, "nano_cap_meme_coins.json")
    with open(filepath, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "max_market_cap": 10_000_000,
            "count": len(SAMPLE_NANO_CAPS),
            "note": "Sample data - run nano_cap_meme_scout.py for real-time data",
            "coins": SAMPLE_NANO_CAPS
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print("FILES CREATED")
    print(f"{'='*80}")
    print(f"1. nano_cap_meme_scout.py - Real-time scanner (uses CoinGecko API)")
    print(f"2. nano_cap_demo.py - This demo with sample data")
    print(f"3. meme_coin_data/nano_cap_meme_coins.json - Saved coin list")
    print(f"\nTo get REAL data, run: python nano_cap_meme_scout.py")
    print(f"(Requires CoinGecko API - free tier, rate limited)")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
