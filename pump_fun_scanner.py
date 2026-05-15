#!/usr/bin/env python3
"""
PUMP.FUN SCANNER
Monitors new meme coin launches and filters for potential
Integrates with quantum scanner
"""

import requests
import json
import os
import time
import math
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

class PumpFunScanner:
    """Scanner for Pump.fun launches"""
    
    def __init__(self):
        self.session = requests.Session()
        self.seen_launches = set()
        self.load_seen()
    
    def load_seen(self):
        filepath = os.path.join(DATA_DIR, "pump_seen.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.seen_launches = set(data.get("launches", []))
    
    def save_seen(self):
        filepath = os.path.join(DATA_DIR, "pump_seen.json")
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "count": len(self.seen_launches),
                "launches": list(self.seen_launches)
            }, f, indent=2)
    
    def fetch_recent_launches(self) -> List[Dict]:
        """Fetch recent launches from Pump.fun API"""
        # Pump.fun API endpoint (unofficial)
        url = "https://frontend-api.pump.fun/coins/for-you"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json() if isinstance(response.json(), list) else []
        except:
            pass
        
        # Fallback: use DexScreener Solana new pairs
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Filter for very small market caps (likely Pump.fun)
                launches = []
                for item in data if isinstance(data, list) else []:
                    mcap = float(item.get("marketCap", 0) or 0)
                    if 0 < mcap < 1_000_000:  # Under $1M = likely fresh launch
                        launches.append(item)
                return launches
        except:
            pass
        
        return []
    
    def calculate_quantum_signal(self, mcap: float, volume: float, age_hours: float) -> Dict:
        """Quantum signal for new launches"""
        # For new launches, different factors matter
        mcap_size = 1 - math.tanh(mcap / 100_000)  # Smaller = more potential
        vol_signal = math.tanh(volume / 10_000)    # Volume = interest
        age_factor = math.tanh(age_hours / 6)      # 6h = half-life
        
        superposition = (mcap_size * 0.4 + vol_signal * 0.4 + (1 - age_factor) * 0.2)
        
        if superposition > 0.5:
            signal = "EARLY BUY"
            confidence = min(0.7, superposition)
        elif superposition < 0.2:
            signal = "SKIP"
            confidence = 0.5
        else:
            signal = "WATCH"
            confidence = 0.4
        
        return {"signal": signal, "confidence": round(confidence, 3)}
    
    def analyze_launch(self, launch: Dict) -> Optional[Dict]:
        """Analyze a new launch"""
        mint = launch.get("mint", "") or launch.get("tokenAddress", "")
        symbol = launch.get("symbol", "UNKNOWN")
        
        if mint in self.seen_launches:
            return None
        
        # Extract data
        mcap = float(launch.get("marketCap", 0) or 0)
        price = float(launch.get("price", launch.get("priceUsd", 0)) or 0)
        volume = float(launch.get("volume", {}).get("h24", 0) or 0)
        
        # Skip if too big or no data
        if mcap > 5_000_000 or mcap <= 0:
            return None
        
        # Age estimate (from created_timestamp if available)
        created = launch.get("created_timestamp", 0)
        if created:
            age_hours = (datetime.now().timestamp() - created) / 3600
        else:
            age_hours = 1  # Assume fresh
        
        # Quantum signal
        quantum = self.calculate_quantum_signal(mcap, volume, age_hours)
        
        # Launch score
        score = 0
        signals = []
        
        # Market cap (smaller = more upside)
        if mcap < 100_000:
            score += 30
            signals.append("Ultra micro ($100K)")
        elif mcap < 500_000:
            score += 25
            signals.append("Micro cap ($500K)")
        elif mcap < 1_000_000:
            score += 15
            signals.append("Small cap ($1M)")
        
        # Volume (early volume = interest)
        vol_ratio = volume / mcap if mcap > 0 else 0
        if vol_ratio > 1.0:
            score += 30
            signals.append("High early volume")
        elif vol_ratio > 0.5:
            score += 20
            signals.append("Good volume")
        elif vol_ratio > 0.1:
            score += 10
            signals.append("Some volume")
        
        # Age (very new = higher risk but higher reward)
        if age_hours < 1:
            score += 15
            signals.append("Just launched (<1h)")
        elif age_hours < 6:
            score += 10
            signals.append("Very new (<6h)")
        elif age_hours < 24:
            score += 5
            signals.append("New (<24h)")
        
        # Social signal (if available)
        replies = int(launch.get("reply_count", 0))
        if replies > 100:
            score += 15
            signals.append("Active replies (100+)")
        elif replies > 50:
            score += 10
            signals.append("Growing replies (50+)")
        
        grade = "A+" if score >= 80 else "A" if score >= 70 else "B+" if score >= 60 else "B" if score >= 50 else "C"
        
        self.seen_launches.add(mint)
        
        return {
            "symbol": symbol,
            "name": launch.get("name", "Unknown"),
            "mint": mint,
            "price": price,
            "market_cap": mcap,
            "volume_24h": volume,
            "age_hours": round(age_hours, 1),
            "replies": replies,
            "quantum_signal": quantum["signal"],
            "quantum_confidence": quantum["confidence"],
            "launch_score": score,
            "launch_grade": grade,
            "launch_signals": signals,
            "chain": "solana",
            "discovered_at": datetime.now().isoformat()
        }
    
    def scan_once(self) -> List[Dict]:
        """Single scan"""
        print(f"\n{'='*80}")
        print(f"PUMP.FUN SCANNER - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        launches = self.fetch_recent_launches()
        print(f"Fetched {len(launches)} potential launches")
        
        analyzed = []
        for launch in launches:
            result = self.analyze_launch(launch)
            if result:
                analyzed.append(result)
        
        analyzed.sort(key=lambda x: x["launch_score"], reverse=True)
        
        if analyzed:
            print(f"\nNEW LAUNCHES: {len(analyzed)} coins")
            print(f"\n{'#':<4} {'Symbol':<10} {'Grade':<6} {'Score':<7} {'Age':<10} {'MCap':<10} {'Quantum':<15}")
            print("-" * 80)
            
            for i, c in enumerate(analyzed[:10], 1):
                age_str = f"{c['age_hours']:.1f}h"
                print(f"{i:<4} {c['symbol'][:11]:<10} {c['launch_grade']:<6} {c['launch_score']:<6.0f} {age_str:<10} ${c['market_cap']/1000:<9.1f}K {c['quantum_signal']:<15}")
            
            # A+ alerts
            a_plus = [c for c in analyzed if c["launch_grade"] == "A+"]
            if a_plus:
                print(f"\n{'='*80}")
                print(f"A+ LAUNCH ALERTS: {len(a_plus)} coins!")
                print(f"{'='*80}")
                for c in a_plus:
                    print(f"\n  {c['symbol']} - {c['name']}")
                    print(f"  Age: {c['age_hours']:.1f}h | MCap: ${c['market_cap']/1000:.1f}K")
                    print(f"  Price: ${c['price']:.8f}")
                    print(f"  Quantum: {c['quantum_signal']} ({c['quantum_confidence']*100:.0f}%)")
                    print(f"  Signals: {', '.join(c['launch_signals'])}")
        else:
            print("\nNo new launches this cycle")
        
        self.save_seen()
        self.save_results(analyzed)
        return analyzed
    
    def save_results(self, launches: List[Dict]):
        filepath = os.path.join(DATA_DIR, "pump_launches.json")
        existing = []
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                existing = json.load(f).get("launches", [])
        
        with open(filepath, "w") as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "total": len(existing) + len(launches),
                "launches": existing + launches
            }, f, indent=2)
    
    def run_continuous(self, hours: float = 24.0):
        """Run continuous scanning"""
        print("=" * 80)
        print("PUMP.FUN SCANNER + QUANTUM")
        print(f"Duration: {hours}h | Interval: 5min")
        print("=" * 80)
        
        start = datetime.now()
        scan_num = 0
        
        while (datetime.now() - start).total_seconds() < hours * 3600:
            scan_num += 1
            print(f"\n[Scan #{scan_num}]")
            try:
                self.scan_once()
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(300)  # 5 minutes
        
        print(f"\nDone. Scans: {scan_num}")

def main():
    scanner = PumpFunScanner()
    
    print("=" * 80)
    print("PUMP.FUN LAUNCH SCANNER + QUANTUM")
    print("=" * 80)
    print("\nFinds brand new meme coin launches")
    print("Scores them for investment potential")
    print("\nStarting scan...")
    print("=" * 80)
    
    scanner.scan_once()
    
    print(f"\n{'='*80}")
    print("To run continuous: scanner.run_continuous(hours=24)")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
