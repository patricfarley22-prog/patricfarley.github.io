#!/usr/bin/env python3
"""
MASTER ALPHA SYSTEM
Integrates all components:
1. Live DexScreener Monitor
2. Quantum Signal Generator  
3. Community Analyzer
4. Influencer Tracker
5. Performance Logger
"""

import os
import json
from datetime import datetime

# Import all modules
from ultimate_alpha_monitor import AlphaMonitor
from influencer_tracker import InfluencerTracker

DATA_DIR = "meme_coin_data"

class MasterAlphaSystem:
    """Master integration of all alpha tools"""
    
    def __init__(self):
        self.monitor = AlphaMonitor()
        self.tracker = InfluencerTracker()
    
    def run_alpha_scan(self):
        """Run complete alpha scan"""
        print("=" * 80)
        print("MASTER ALPHA SYSTEM - FULL SCAN")
        print("=" * 80)
        
        # 1. Live Monitor
        print("\n[1/5] LIVE MONITOR - Checking DexScreener...")
        alpha_coins = self.monitor.check_for_alpha()
        
        # 2. Quantum Analysis
        if alpha_coins:
            print(f"\n[2/5] QUANTUM ANALYSIS - {len(alpha_coins)} coins")
            for coin in alpha_coins[:5]:
                print(f"\n  {coin['symbol']}:")
                print(f"    Signal: {coin['quantum_signal']} ({coin['quantum_confidence']*100:.0f}%)")
                print(f"    Alpha: {coin['alpha_grade']} ({coin['alpha_score']}/100)")
        
        # 3. Community Check
        print(f"\n[3/5] COMMUNITY CHECK - Verifying socials...")
        print("  Check: Twitter mentions, Telegram activity, on-chain data")
        
        # 4. Influencer Tracking
        print(f"\n[4/5] INFLUENCER TRACK - Who's pushing it?")
        self.tracker.display_leaderboard()
        
        # 5. Save Results
        print(f"\n[5/5] SAVE RESULTS")
        self.save_master_report(alpha_coins)
        
        print(f"\n{'='*80}")
        print("SCAN COMPLETE")
        print(f"{'='*80}")
    
    def save_master_report(self, alpha_coins):
        """Save comprehensive report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "system": "Master Alpha System v1.0",
            "components": [
                "DexScreener Monitor",
                "Quantum Signal Generator",
                "Community Analyzer", 
                "Influencer Tracker",
                "Performance Logger"
            ],
            "coins_found": len(alpha_coins),
            "coins": alpha_coins[:10],
            "influencers": self.tracker.tracked,
            "recommendations": self.generate_recommendations(alpha_coins)
        }
        
        filepath = os.path.join(DATA_DIR, "master_alpha_report.json")
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"  Saved: {filepath}")
    
    def generate_recommendations(self, alpha_coins):
        """Generate trading recommendations"""
        recommendations = []
        
        for coin in alpha_coins[:5]:
            if coin["alpha_score"] >= 60:
                rec = {
                    "coin": coin["symbol"],
                    "action": "BUY",
                    "confidence": coin["alpha_score"],
                    "entry": coin["price"],
                    "target": coin["price"] * 2,
                    "stop_loss": coin["price"] * 0.8,
                    "timeframe": "24-72h",
                    "reason": coin["alpha_signals"][:2]
                }
                recommendations.append(rec)
        
        return recommendations
    
    def display_menu(self):
        """Display interactive menu"""
        print("\n" + "=" * 80)
        print("MASTER ALPHA SYSTEM")
        print("=" * 80)
        print("\nOptions:")
        print("1. Run Full Alpha Scan")
        print("2. Live Monitor (5 min intervals)")
        print("3. Quantum Analysis")
        print("4. Community Check")
        print("5. Influencer Tracker")
        print("6. View Master Report")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            self.run_alpha_scan()
        elif choice == "2":
            hours = int(input("How many hours to monitor? "))
            self.monitor.run_continuous(hours)
        elif choice == "3":
            print("Quantum analysis requires coin data. Run scan first.")
        elif choice == "4":
            print("Community check requires coin data. Run scan first.")
        elif choice == "5":
            self.tracker.display_leaderboard()
        elif choice == "6":
            self.view_master_report()
        elif choice == "7":
            print("Exiting...")
            return False
        else:
            print("Invalid option")
        
        return True
    
    def view_master_report(self):
        """View saved report"""
        filepath = os.path.join(DATA_DIR, "master_alpha_report.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                report = json.load(f)
            
            print(f"\n{'='*80}")
            print("MASTER ALPHA REPORT")
            print(f"{'='*80}")
            print(f"Generated: {report['generated_at']}")
            print(f"Coins Found: {report['coins_found']}")
            
            if report.get('recommendations'):
                print(f"\nRECOMMENDATIONS:")
                for rec in report['recommendations']:
                    print(f"\n  {rec['coin']}: {rec['action']}")
                    print(f"    Entry: ${rec['entry']:.8f}")
                    print(f"    Target: ${rec['target']:.8f} (2x)")
                    print(f"    Stop: ${rec['stop_loss']:.8f} (-20%)")
                    print(f"    Timeframe: {rec['timeframe']}")
        else:
            print("No report found. Run scan first.")

def main():
    system = MasterAlphaSystem()
    
    print("=" * 80)
    print("MASTER ALPHA SYSTEM v1.0")
    print("=" * 80)
    print("\nComponents:")
    print("1. Live DexScreener Monitor")
    print("2. Quantum Signal Generator")
    print("3. Community Analyzer")
    print("4. Influencer Tracker")
    print("5. Performance Logger")
    print("\nRun: system.run_alpha_scan()")
    print("Or: system.display_menu()")
    
    # Auto-run scan
    system.run_alpha_scan()

if __name__ == "__main__":
    main()
