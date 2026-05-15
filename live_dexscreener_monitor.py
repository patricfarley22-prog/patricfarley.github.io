#!/usr/bin/env python3
"""
LIVE DEXSCREENER MONITOR
Checks every 5 minutes for trending nano-cap coins
Integrates with quantum scanner
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

class LiveDexMonitor:
    """Live monitor for DexScreener trending"""
    
    def __init__(self, check_interval=300):  # 5 minutes
        self.check_interval = check_interval
        self.seen_coins = set()
        self.load_seen()
        self.session = requests.Session()
        
    def load_seen(self):
        filepath = os.path.join(DATA_DIR, "dex_seen_coins.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.seen_coins = set(data.get("coins", []))
    
    def save_seen(self):
        filepath = os.path.join(DATA_DIR, "dex_seen_coins.json")
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "count": len(self.seen_coins),
                "coins": list(self.seen_coins)
            }, f, indent=2)
    
    def fetch_trending(self) -> List[Dict]:
        """Fetch trending from DexScreener"""
        url = "https://api.dexscreener.com/token-boosts/top/v1"
        try:
            response = self.session.get(url, timeout=10)
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def fetch_new_pairs(self) -> List[Dict]:
        """Fetch new pairs"""
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        try:
            response = self.session.get(url, timeout=10)
            return response.json() if response.status_code == 200 else []
        except:
            return []
    
    def calculate_quantum_signal(self, change_24h: float, volume: float, mcap: float) -> Dict:
        """Quantum-like signal calculation"""
        price_change = math.tanh(change_24h / 50)
        vol_ratio = math.tanh(volume / mcap) if mcap > 0 else 0
        mcap_size = 1 - math.tanh(mcap / 5_000_000)
        
        superposition = (price_change * 0.4 + vol_ratio * 0.3 + mcap_size * 0.3)
        
        if superposition > 0.3:
            signal = "BUY"
            confidence = min(0.9, 0.5 + superposition * 0.4)
        elif superposition < -0.2:
            signal = "SELL"
            confidence = min(0.9, 0.5 + abs(superposition) * 0.4)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return {"signal": signal, "confidence": round(confidence, 3)}
    
    def analyze_coin(self, coin: Dict) -> Optional[Dict]:
        """Analyze a coin"""
        token = coin.get("tokenAddress", "") or coin.get("address", "")
        symbol = coin.get("symbol", "UNKNOWN")
        
        if token in self.seen_coins:
            return None
        
        # Extract data with fallbacks
        price = float(coin.get("priceUsd", coin.get("price", 0)) or 0)
        mcap = float(coin.get("marketCap", 0) or 0)
        volume = float(coin.get("volume", {}).get("h24", coin.get("volume24h", 0)) or 0)
        
        # Price changes
        price_change = coin.get("priceChange", {})
        change_1h = float(price_change.get("h1", 0) or 0)
        change_24h = float(price_change.get("h24", 0) or 0)
        
        # Skip if too big or no data
        if mcap > 10_000_000 or mcap <= 0 or price <= 0:
            return None
        
        # Quantum signal
        quantum = self.calculate_quantum_signal(change_24h, volume, mcap)
        
        # Alpha score
        score = 0
        signals = []
        
        if change_1h > 50: score += 25; signals.append("50%+ 1h")
        elif change_1h > 20: score += 15; signals.append("20%+ 1h")
        
        if change_24h > 100: score += 25; signals.append("100%+ 24h")
        elif change_24h > 50: score += 20; signals.append("50%+ 24h")
        elif change_24h > 20: score += 10; signals.append("20%+ 24h")
        
        vol_ratio = volume / mcap if mcap > 0 else 0
        if vol_ratio > 0.5: score += 20; signals.append("High volume")
        elif vol_ratio > 0.2: score += 10; signals.append("Good volume")
        
        if mcap < 1_000_000: score += 15; signals.append("Micro gem")
        elif mcap < 3_000_000: score += 10; signals.append("Nano cap")
        
        grade = "A+" if score >= 80 else "A" if score >= 70 else "B+" if score >= 60 else "B" if score >= 50 else "C"
        
        self.seen_coins.add(token)
        
        return {
            "symbol": symbol,
            "name": coin.get("name", "Unknown"),
            "price": price,
            "market_cap": mcap,
            "volume_24h": volume,
            "change_1h": change_1h,
            "change_24h": change_24h,
            "quantum_signal": quantum["signal"],
            "quantum_confidence": quantum["confidence"],
            "alpha_score": score,
            "alpha_grade": grade,
            "alpha_signals": signals,
            "chain": coin.get("chainId", "solana"),
            "token_address": token,
            "url": coin.get("url", ""),
            "discovered_at": datetime.now().isoformat()
        }
    
    def check_once(self) -> List[Dict]:
        """Single check cycle"""
        print(f"\n{'='*80}")
        print(f"DEXSCREENER CHECK - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        trending = self.fetch_trending()
        new_pairs = self.fetch_new_pairs()
        all_coins = trending + new_pairs
        
        print(f"Fetched: {len(trending)} trending + {len(new_pairs)} new = {len(all_coins)} total")
        
        alpha_coins = []
        for coin in all_coins:
            analyzed = self.analyze_coin(coin)
            if analyzed:
                alpha_coins.append(analyzed)
        
        alpha_coins.sort(key=lambda x: x["alpha_score"], reverse=True)
        
        if alpha_coins:
            print(f"\nNEW ALPHA: {len(alpha_coins)} coins found!")
            print(f"\n{'#':<4} {'Symbol':<10} {'Grade':<6} {'Score':<7} {'1h':<8} {'24h':<8} {'MCap':<10} {'Quantum':<15}")
            print("-" * 80)
            
            for i, c in enumerate(alpha_coins[:10], 1):
                print(f"{i:<4} {c['symbol'][:11]:<10} {c['alpha_grade']:<6} {c['alpha_score']:<6.0f} {c['change_1h']:<+7.1f}% {c['change_24h']:<+7.1f}% ${c['market_cap']/1_000_000:<9.2f}M {c['quantum_signal']:<15}")
            
            # A+ alerts
            a_plus = [c for c in alpha_coins if c["alpha_grade"] == "A+"]
            if a_plus:
                print(f"\n{'='*80}")
                print(f"A+ ALERTS: {len(a_plus)} coins!")
                print(f"{'='*80}")
                for c in a_plus:
                    print(f"\n  {c['symbol']} - {c['name']}")
                    print(f"  Price: ${c['price']:.8f} | MCap: ${c['market_cap']/1_000_000:.2f}M")
                    print(f"  1h: {c['change_1h']:+.1f}% | 24h: {c['change_24h']:+.1f}%")
                    print(f"  Quantum: {c['quantum_signal']} ({c['quantum_confidence']*100:.0f}%)")
                    print(f"  Signals: {', '.join(c['alpha_signals'])}")
                    print(f"  URL: {c['url']}")
        else:
            print("\nNo new alpha this cycle")
        
        self.save_seen()
        self.save_alpha(alpha_coins)
        return alpha_coins
    
    def save_alpha(self, coins: List[Dict]):
        filepath = os.path.join(DATA_DIR, "dex_alpha_discovered.json")
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                existing = json.load(f).get("coins", [])
        
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total": len(existing) + len(coins),
                "coins": existing + coins
            }, f, indent=2)
    
    def run_continuous(self, hours: float = 24.0):
        """Run continuous monitoring"""
        print("=" * 80)
        print("LIVE DEXSCREENER MONITOR")
        print(f"Duration: {hours}h | Interval: {self.check_interval//60}min")
        print("=" * 80)
        
        start = datetime.now()
        end = start + timedelta(hours=hours)
        check_num = 0
        
        while datetime.now() < end:
            check_num += 1
            print(f"\n[Check #{check_num}]")
            try:
                self.check_once()
            except Exception as e:
                print(f"Error: {e}")
            
            if datetime.now() < end:
                next_check = datetime.now() + timedelta(seconds=self.check_interval)
                print(f"\nNext check: {next_check.strftime('%H:%M:%S')}")
                time.sleep(self.check_interval)
        
        print(f"\n{'='*80}")
        print("MONITORING COMPLETE")
        print(f"Checks: {check_num} | Duration: {hours}h")
        print(f"Seen: {len(self.seen_coins)} coins")
        print(f"{'='*80}")

def main():
    monitor = LiveDexMonitor()
    
    print("=" * 80)
    print("LIVE DEXSCREENER MONITOR + QUANTUM SCANNER")
    print("=" * 80)
    print("\nFeatures:")
    print("- Checks DexScreener every 5 minutes")
    print("- Finds trending + new pairs")
    print("- Quantum signal generation")
    print("- Alpha scoring (A+ to C)")
    print("- A+ alerts")
    print("\nStarting now...")
    print("=" * 80)
    
    monitor.check_once()
    
    print(f"\n{'='*80}")
    print("To run continuously: monitor.run_continuous(hours=24)")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
