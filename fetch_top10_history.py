#!/usr/bin/env python3
"""
FETCH TOP 10 MOVER HISTORY
Pulls 365-day historical data for the top performing meme coins
"""

import json
import os
from datetime import datetime
from meme_coin_scout import MemeCoinScout

def main():
    # Top 10 movers by 30-day return
    top10 = [
        "kishu-inu",      # KISHU: +896.5%
        "wojak",          # WOJAK: +422.4%
        "utya",           # UTYA: +313.7%
        "meme-horse",     # MHORSE: +257.5%
        "zerebro",        # ZEREBRO: +193.4%
        "aura-on-sol",    # AURA: +124.3%
        "gigachad-2",     # GIGA: +130.4%
        "dogs",           # DOGS: +94.3%
        "ponke",          # PONKE: +47.7%
        "degen-base"      # DEGEN: +39.1%
    ]
    
    scout = MemeCoinScout(max_mcap=100_000_000)
    
    print("=" * 80)
    print("FETCHING TOP 10 MOVER HISTORIES")
    print("=" * 80)
    print("Coins: KISHU, WOJAK, UTYA, MHORSE, ZEREBRO, AURA, GIGA, DOGS, PONKE, DEGEN")
    print("Data: 365 days daily OHLCV")
    print("Rate limit: 2s between requests")
    print("=" * 80)
    
    results = []
    
    for i, coin_id in enumerate(top10, 1):
        print(f"\n[{i}/10] Fetching {coin_id.upper()}...")
        
        history = scout.fetch_historical_data(coin_id, days=365)
        
        if history:
            scout.save_history(coin_id, history)
            results.append({
                "id": coin_id,
                "days": history["days"],
                "metrics": history["metrics"]
            })
            print(f"  SUCCESS: {history['days']} days")
            print(f"  Return: {history['metrics']['total_return_pct']:+.2f}%")
            print(f"  Volatility: {history['metrics']['volatility_annualized_pct']:.2f}%")
        else:
            print(f"  FAILED")
    
    # Save summary
    summary_path = os.path.join("meme_coin_data", "top10_movers_summary.json")
    with open(summary_path, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "count": len(results),
            "coins": results
        }, f, indent=2)
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print(f"Fetched: {len(results)}/10 coins")
    print(f"Summary: {summary_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
