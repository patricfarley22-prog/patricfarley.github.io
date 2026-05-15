#!/usr/bin/env python3
"""
ULTIMATE ALPHA SYSTEM
Live DexScreener monitor + Quantum Scanner + Community Analyzer
Checks every 5 minutes for trending nano-cap meme coins
"""

import requests
import json
import os
import time
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

class AlphaMonitor:
    """Live monitor for nano-cap alpha"""
    
    def __init__(self, check_interval=300):  # 5 minutes
        self.check_interval = check_interval
        self.seen_coins = set()
        self.load_seen_coins()
        
    def load_seen_coins(self):
        """Load previously seen coins"""
        filepath = os.path.join(DATA_DIR, "alpha_seen_coins.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.seen_coins = set(data.get("coins", []))
    
    def save_seen_coins(self):
        """Save seen coins"""
        filepath = os.path.join(DATA_DIR, "alpha_seen_coins.json")
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "count": len(self.seen_coins),
                "coins": list(self.seen_coins)
            }, f, indent=2)
    
    def fetch_trending(self, chain="solana") -> List[Dict]:
        """Fetch trending coins from DexScreener"""
        url = f"https://api.dexscreener.com/token-boosts/top/v1"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching trending: {e}")
            return []
    
    def fetch_new_pairs(self, chain="solana") -> List[Dict]:
        """Fetch new pairs from DexScreener"""
        url = f"https://api.dexscreener.com/token-profiles/latest/v1"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching new pairs: {e}")
            return []
    
    def analyze_coin(self, coin_data: Dict) -> Optional[Dict]:
        """Analyze a coin for alpha potential"""
        symbol = coin_data.get("tokenAddress", "") or coin_data.get("symbol", "UNKNOWN")
        
        # Skip if already seen
        if symbol in self.seen_coins:
            return None
        
        # Extract data
        price = float(coin_data.get("price", 0))
        mcap = float(coin_data.get("marketCap", 0))
        volume = float(coin_data.get("volume", 0))
        change_1h = float(coin_data.get("priceChange1h", 0))
        change_24h = float(coin_data.get("priceChange24h", 0))
        
        # Skip if too big (over $10M) or no data
        if mcap > 10_000_000 or mcap <= 0:
            return None
        
        # Calculate quantum signal
        quantum = self.calculate_quantum_signal(change_24h, volume, mcap)
        
        # Calculate alpha score
        alpha = self.calculate_alpha_score(change_1h, change_24h, volume, mcap)
        
        # Mark as seen
        self.seen_coins.add(symbol)
        
        return {
            "symbol": symbol,
            "name": coin_data.get("name", "Unknown"),
            "price": price,
            "market_cap": mcap,
            "volume_24h": volume,
            "change_1h": change_1h,
            "change_24h": change_24h,
            "quantum_signal": quantum["signal"],
            "quantum_confidence": quantum["confidence"],
            "alpha_score": alpha["score"],
            "alpha_grade": alpha["grade"],
            "alpha_signals": alpha["signals"],
            "chain": coin_data.get("chainId", "unknown"),
            "token_address": coin_data.get("tokenAddress", ""),
            "url": coin_data.get("url", ""),
            "discovered_at": datetime.now().isoformat()
        }
    
    def calculate_quantum_signal(self, change_24h, volume, mcap):
        """Calculate quantum-like signal"""
        # Normalize features
        price_change = math.tanh(change_24h / 50)
        vol_ratio = math.tanh(volume / mcap) if mcap > 0 else 0
        mcap_size = 1 - math.tanh(mcap / 5_000_000)
        
        # Superposition
        superposition = (price_change * 0.4 + vol_ratio * 0.3 + mcap_size * 0.3)
        
        # Signal
        if superposition > 0.3:
            signal = "QUANTUM BUY"
            confidence = min(0.9, 0.5 + superposition * 0.4)
        elif superposition < -0.2:
            signal = "QUANTUM SELL"
            confidence = min(0.9, 0.5 + abs(superposition) * 0.4)
        else:
            signal = "QUANTUM HOLD"
            confidence = 0.5
        
        return {"signal": signal, "confidence": round(confidence, 3)}
    
    def calculate_alpha_score(self, change_1h, change_24h, volume, mcap):
        """Calculate alpha score"""
        score = 0
        signals = []
        
        # Momentum (1h)
        if change_1h > 100:
            score += 30
            signals.append("100%+ in 1h (parabolic)")
        elif change_1h > 50:
            score += 25
            signals.append("50%+ in 1h (strong pump)")
        elif change_1h > 20:
            score += 15
            signals.append("20%+ in 1h (early pump)")
        
        # Momentum (24h)
        if change_24h > 200:
            score += 25
            signals.append("200%+ in 24h (mooning)")
        elif change_24h > 100:
            score += 20
            signals.append("100%+ in 24h (trending)")
        elif change_24h > 50:
            score += 10
            signals.append("50%+ in 24h (moving)")
        
        # Volume
        vol_ratio = volume / mcap if mcap > 0 else 0
        if vol_ratio > 0.5:
            score += 20
            signals.append("High volume (50%+ of mcap)")
        elif vol_ratio > 0.2:
            score += 10
            signals.append("Decent volume (20%+ of mcap)")
        
        # Market cap size (smaller = more upside)
        if mcap < 1_000_000:
            score += 15
            signals.append("Under $1M (micro gem)")
        elif mcap < 3_000_000:
            score += 10
            signals.append("Under $3M (nano cap)")
        elif mcap < 5_000_000:
            score += 5
            signals.append("Under $5M (low cap)")
        
        # Grade
        if score >= 80:
            grade = "A+"
        elif score >= 70:
            grade = "A"
        elif score >= 60:
            grade = "B+"
        elif score >= 50:
            grade = "B"
        elif score >= 40:
            grade = "C+"
        else:
            grade = "C"
        
        return {"score": score, "grade": grade, "signals": signals}
    
    def check_for_alpha(self):
        """Main check loop"""
        print(f"\n{'='*80}")
        print(f"ALPHA CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Fetch trending and new pairs
        trending = self.fetch_trending()
        new_pairs = self.fetch_new_pairs()
        
        all_coins = trending + new_pairs
        
        print(f"Fetched {len(trending)} trending + {len(new_pairs)} new = {len(all_coins)} total")
        
        # Analyze each
        alpha_coins = []
        for coin in all_coins:
            analyzed = self.analyze_coin(coin)
            if analyzed:
                alpha_coins.append(analyzed)
        
        # Sort by alpha score
        alpha_coins.sort(key=lambda x: x["alpha_score"], reverse=True)
        
        # Display
        if alpha_coins:
            print(f"\nALERT NEW ALPHA FOUND: {len(alpha_coins)} coins")
            print(f"\n{'#':<4} {'Symbol':<12} {'Grade':<6} {'Score':<7} {'1h':<8} {'24h':<8} {'MCap':<10} {'Signal':<15}")
            print("-" * 80)
            
            for i, coin in enumerate(alpha_coins[:10], 1):
                print(
                    f"{i:<4} "
                    f"{coin['symbol'][:11]:<12} "
                    f"{coin['alpha_grade']:<6} "
                    f"{coin['alpha_score']:<6.0f} "
                    f"{coin['change_1h']:<+7.1f}% "
                    f"{coin['change_24h']:<+7.1f}% "
                    f"${coin['market_cap']/1_000_000:<9.2f}M "
                    f"{coin['quantum_signal']:<15}"
                )
            
            # Save alpha coins
            self.save_alpha_coins(alpha_coins)
            
            # Alert for A+ coins
            a_plus = [c for c in alpha_coins if c["alpha_grade"] == "A+"]
            if a_plus:
                print(f"\nHOT A+ ALPHA ALERTS: {len(a_plus)} coins")
                for coin in a_plus:
                    print(f"\n  ALERT {coin['symbol']}")
                    print(f"     Grade: {coin['alpha_grade']} ({coin['alpha_score']}/100)")
                    print(f"     Price: ${coin['price']:.8f}")
                    print(f"     MCap: ${coin['market_cap']/1_000_000:.2f}M")
                    print(f"     1h: {coin['change_1h']:+.1f}% | 24h: {coin['change_24h']:+.1f}%")
                    print(f"     Quantum: {coin['quantum_signal']} ({coin['quantum_confidence']*100:.0f}%)")
                    print(f"     Signals:")
                    for signal in coin["alpha_signals"]:
                        print(f"       - {signal}")
        else:
            print("\nDATA No new alpha found this cycle")
        
        self.save_seen_coins()
        
        return alpha_coins
    
    def save_alpha_coins(self, coins: List[Dict]):
        """Save alpha coins"""
        filepath = os.path.join(DATA_DIR, "alpha_discovered.json")
        
        # Load existing
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                existing = data.get("coins", [])
        
        # Add new
        all_coins = existing + coins
        
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total_discovered": len(all_coins),
                "coins": all_coins
            }, f, indent=2)
    
    def run_continuous(self, duration_hours=24):
        """Run continuous monitoring"""
        print("=" * 80)
        print("ULTIMATE ALPHA MONITOR")
        print("Checking every 5 minutes for nano-cap gems")
        print("=" * 80)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        check_count = 0
        
        while datetime.now() < end_time:
            check_count += 1
            print(f"\n\n[Check #{check_count}]")
            
            try:
                self.check_for_alpha()
            except Exception as e:
                print(f"Error in check: {e}")
            
            # Wait for next check
            next_check = datetime.now() + timedelta(seconds=self.check_interval)
            print(f"\nWAIT Next check at {next_check.strftime('%H:%M:%S')}")
            time.sleep(self.check_interval)
        
        print(f"\n{'='*80}")
        print("MONITORING COMPLETE")
        print(f"{'='*80}")
        print(f"Total checks: {check_count}")
        print(f"Duration: {duration_hours} hours")
        print(f"Seen coins: {len(self.seen_coins)}")
        print(f"Data saved to: {DATA_DIR}/alpha_discovered.json")

def main():
    monitor = AlphaMonitor(check_interval=300)  # 5 minutes
    
    print("=" * 80)
    print("ULTIMATE ALPHA SYSTEM")
    print("=" * 80)
    print("\nComponents:")
    print("OK DexScreener trending monitor")
    print("OK Quantum signal generator")
    print("OK Alpha scoring (0-100)")
    print("OK A+ alerts")
    print("OK Continuous monitoring")
    print("\nStarting single check now...")
    print("=" * 80)
    
    # Single check
    monitor.check_for_alpha()
    
    print(f"\n{'='*80}")
    print("OPTIONS:")
    print(f"{'='*80}")
    print("1. Run continuous monitoring (24 hours)")
    print("2. Run single check")
    print("3. View discovered coins")
    print(f"\nTo run continuous: monitor.run_continuous(duration_hours=24)")

if __name__ == "__main__":
    main()
