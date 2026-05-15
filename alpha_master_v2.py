#!/usr/bin/env python3
"""
ALPHA MASTER SYSTEM V2
Integrates 4 components:
1. Live DexScreener Monitor
2. Pump.fun Scanner
3. Twitter Research Bot
4. Quantum Signal Generator
"""

import os
import json
from datetime import datetime
from live_dexscreener_monitor import LiveDexMonitor
from pump_fun_scanner import PumpFunScanner
from twitter_research_bot import TwitterResearchBot

DATA_DIR = "meme_coin_data"

class AlphaMasterV2:
    """Master integration of all alpha tools"""
    
    def __init__(self):
        self.dex_monitor = LiveDexMonitor()
        self.pump_scanner = PumpFunScanner()
        self.twitter_bot = TwitterResearchBot()
    
    def run_full_scan(self):
        """Run all 3 scanners"""
        print("=" * 80)
        print("ALPHA MASTER V2 - FULL SYSTEM SCAN")
        print("=" * 80)
        
        # 1. DexScreener Monitor
        print("\n[1/3] LIVE DEXSCREENER MONITOR")
        print("-" * 80)
        dex_coins = self.dex_monitor.check_once()
        
        # 2. Pump.fun Scanner
        print("\n[2/3] PUMP.FUN LAUNCH SCANNER")
        print("-" * 80)
        pump_coins = self.pump_scanner.scan_once()
        
        # 3. Twitter Research (on discovered coins)
        print("\n[3/3] TWITTER RESEARCH BOT")
        print("-" * 80)
        
        # Get symbols from discovered coins
        symbols = []
        for c in dex_coins[:5]:
            symbols.append(c["symbol"])
        for c in pump_coins[:5]:
            if c["symbol"] not in symbols:
                symbols.append(c["symbol"])
        
        # Add known trending
        trending = ["BONK", "WIF", "PEPE", "FLOKI", "TROLL", "DOGE", "SHIB"]
        for t in trending:
            if t not in symbols:
                symbols.append(t)
        
        twitter_results = self.twitter_bot.research_multiple(symbols[:10])
        
        # Combine and rank
        self.combine_and_rank(dex_coins, pump_coins, twitter_results)
    
    def combine_and_rank(self, dex_coins, pump_coins, twitter_results):
        """Combine all results and create master ranking"""
        print("\n" + "=" * 80)
        print("MASTER ALPHA RANKING")
        print("=" * 80)
        
        all_coins = {}
        
        # Add DexScreener coins
        for c in dex_coins:
            symbol = c["symbol"]
            all_coins[symbol] = {
                "source": "dexscreener",
                **c
            }
        
        # Add Pump.fun coins
        for c in pump_coins:
            symbol = c["symbol"]
            if symbol in all_coins:
                all_coins[symbol]["pump_score"] = c["launch_score"]
                all_coins[symbol]["source"] += "+pump"
            else:
                all_coins[symbol] = {
                    "source": "pump",
                    **c
                }
        
        # Add Twitter data
        for c in twitter_results:
            symbol = c["symbol"]
            if symbol in all_coins:
                all_coins[symbol]["social_score"] = c["social_score"]
                all_coins[symbol]["twitter_signals"] = c["social_signals"]
            else:
                all_coins[symbol] = {
                    "source": "twitter",
                    **c
                }
        
        # Calculate master score
        ranked = []
        for symbol, data in all_coins.items():
            master_score = 0
            
            # DexScreener component (0-50 points)
            if "alpha_score" in data:
                master_score += data["alpha_score"] * 0.5
            
            # Pump.fun component (0-30 points)
            if "pump_score" in data:
                master_score += data["pump_score"] * 0.3
            
            # Twitter component (0-20 points)
            if "social_score" in data:
                master_score += data["social_score"] * 0.2
            
            # Quantum bonus
            if data.get("quantum_signal") == "BUY":
                master_score *= 1.2
            elif data.get("quantum_signal") == "SELL":
                master_score *= 0.8
            
            data["master_score"] = round(master_score, 1)
            
            # Grade
            if master_score >= 80:
                data["master_grade"] = "A+"
            elif master_score >= 70:
                data["master_grade"] = "A"
            elif master_score >= 60:
                data["master_grade"] = "B+"
            elif master_score >= 50:
                data["master_grade"] = "B"
            elif master_score >= 40:
                data["master_grade"] = "C+"
            else:
                data["master_grade"] = "C"
            
            ranked.append(data)
        
        # Sort
        ranked.sort(key=lambda x: x["master_score"], reverse=True)
        
        # Display top 15
        print(f"\n{'#':<4} {'Symbol':<10} {'Source':<15} {'Grade':<6} {'Score':<8} {'Price':<14} {'MCap':<10} {'Quantum':<15}")
        print("-" * 80)
        
        for i, c in enumerate(ranked[:15], 1):
            source = c.get("source", "unknown")[:14]
            print(f"{i:<4} {c['symbol']:<10} {source:<15} {c['master_grade']:<6} {c['master_score']:<7.1f} ${c.get('price', 0):<13.8f} ${c.get('market_cap', 0)/1_000_000:<9.2f}M {c.get('quantum_signal', 'N/A'):<15}")
        
        # A+ Master alerts
        a_plus = [c for c in ranked if c["master_grade"] == "A+"]
        if a_plus:
            print(f"\n{'='*80}")
            print(f"MASTER A+ ALERTS: {len(a_plus)} COINS")
            print(f"{'='*80}")
            
            for c in a_plus:
                print(f"\n  {c['symbol']} - {c.get('name', 'Unknown')}")
                print(f"  Sources: {c['source']}")
                print(f"  Master Score: {c['master_score']}/100")
                print(f"  Price: ${c.get('price', 0):.8f}")
                print(f"  MCap: ${c.get('market_cap', 0)/1_000_000:.2f}M")
                print(f"  Quantum: {c.get('quantum_signal', 'N/A')} ({c.get('quantum_confidence', 0)*100:.0f}%)")
                
                if "alpha_signals" in c:
                    print(f"  Dex Signals: {', '.join(c['alpha_signals'][:3])}")
                if "launch_signals" in c:
                    print(f"  Pump Signals: {', '.join(c['launch_signals'][:3])}")
                if "twitter_signals" in c:
                    print(f"  Social Signals: {', '.join(c['twitter_signals'][:3])}")
        
        # Save master report
        self.save_master_report(ranked)
    
    def save_master_report(self, ranked):
        """Save comprehensive report"""
        filepath = os.path.join(DATA_DIR, "alpha_master_report.json")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "system": "Alpha Master V2",
            "components": [
                "DexScreener Monitor",
                "Pump.fun Scanner",
                "Twitter Research Bot",
                "Quantum Signal Generator"
            ],
            "total_coins": len(ranked),
            "a_plus_count": len([c for c in ranked if c["master_grade"] == "A+"]),
            "top_15": ranked[:15]
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nMaster report saved: {filepath}")
    
    def run_continuous(self, hours=24):
        """Run all monitors continuously"""
        print("=" * 80)
        print("ALPHA MASTER V2 - CONTINUOUS MODE")
        print(f"Duration: {hours}h")
        print("=" * 80)
        
        import time
        from datetime import timedelta
        
        start = datetime.now()
        end = start + timedelta(hours=hours)
        cycle = 0
        
        while datetime.now() < end:
            cycle += 1
            print(f"\n\n[MASTER CYCLE #{cycle}]")
            self.run_full_scan()
            
            if datetime.now() < end:
                print(f"\nNext cycle in 5 minutes...")
                time.sleep(300)
        
        print(f"\n{'='*80}")
        print("CONTINUOUS MODE COMPLETE")
        print(f"Cycles: {cycle}")
        print(f"{'='*80}")

def main():
    master = AlphaMasterV2()
    
    print("=" * 80)
    print("ALPHA MASTER SYSTEM V2")
    print("=" * 80)
    print("\nIntegrated Components:")
    print("1. Live DexScreener Monitor (trending + new pairs)")
    print("2. Pump.fun Launch Scanner (fresh launches)")
    print("3. Twitter Research Bot (social sentiment)")
    print("4. Quantum Signal Generator (BUY/SELL/HOLD)")
    print("\nStarting master scan...")
    print("=" * 80)
    
    master.run_full_scan()
    
    print(f"\n{'='*80}")
    print("SCAN COMPLETE")
    print(f"{'='*80}")
    print("\nTo run continuous:")
    print("  master.run_continuous(hours=24)")
    print("\nTo run single component:")
    print("  master.dex_monitor.check_once()")
    print("  master.pump_scanner.scan_once()")
    print("  master.twitter_bot.research_coin('SYMBOL')")

if __name__ == "__main__":
    main()
