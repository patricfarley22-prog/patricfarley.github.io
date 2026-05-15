#!/usr/bin/env python3
"""
MASTER CONTROL SYSTEM
Complete alpha trading system with all features
"""

import os
import json
import time
from datetime import datetime

class MasterControl:
    """Master control for all alpha systems"""
    
    def __init__(self):
        self.systems = {
            "alpha_scanner": "alpha_master_v2.py",
            "dex_monitor": "live_dexscreener_monitor.py",
            "pump_scanner": "pump_fun_scanner.py",
            "twitter_bot": "twitter_research_bot.py",
            "quantum_scanner": "quantum_meme_signals.py",
            "influencer_tracker": "influencer_tracker.py",
            "paper_trading": "paper_trading.py",
            "telegram_alerts": "telegram_alerts.py",
            "continuous_monitor": "continuous_monitor.py"
        }
    
    def show_menu(self):
        """Show main menu"""
        print("\n" + "=" * 80)
        print("MASTER CONTROL - ALPHA TRADING SYSTEM")
        print("=" * 80)
        print("\n1. Run Full Alpha Scan (all components)")
        print("2. Start Continuous Monitor (24h)")
        print("3. Run DexScreener Monitor Only")
        print("4. Run Pump.fun Scanner Only")
        print("5. Run Twitter Research Only")
        print("6. View Quantum Signals")
        print("7. View Influencer Tracker")
        print("8. Paper Trading Dashboard")
        print("9. Send Test Telegram Alert")
        print("10. View All Reports")
        print("0. Exit")
        print("=" * 80)
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def run_full_scan(self):
        """Run complete scan"""
        print("\nRunning full alpha scan...")
        os.system("python alpha_master_v2.py")
    
    def run_continuous(self):
        """Run continuous monitor"""
        hours = input("How many hours? (default 24): ").strip()
        hours = int(hours) if hours else 24
        print(f"\nStarting {hours}h continuous monitor...")
        os.system(f"python continuous_monitor.py")
    
    def run_dex_only(self):
        """Run DexScreener only"""
        print("\nRunning DexScreener monitor...")
        os.system("python live_dexscreener_monitor.py")
    
    def run_pump_only(self):
        """Run Pump.fun only"""
        print("\nRunning Pump.fun scanner...")
        os.system("python pump_fun_scanner.py")
    
    def run_twitter_only(self):
        """Run Twitter only"""
        print("\nRunning Twitter research...")
        os.system("python twitter_research_bot.py")
    
    def view_quantum(self):
        """View quantum signals"""
        print("\nViewing quantum signals...")
        os.system("python quantum_meme_signals.py")
    
    def view_influencers(self):
        """View influencer tracker"""
        print("\nViewing influencer tracker...")
        os.system("python influencer_tracker.py")
    
    def paper_dashboard(self):
        """Paper trading dashboard"""
        print("\nPaper Trading Dashboard...")
        os.system("python paper_trading.py")
    
    def test_telegram(self):
        """Test Telegram alerts"""
        print("\nSending test alert...")
        os.system("python telegram_alerts.py")
    
    def view_reports(self):
        """View all generated reports"""
        print("\n" + "=" * 80)
        print("REPORTS")
        print("=" * 80)
        
        reports = {
            "alpha_master_report.json": "Master Alpha Report",
            "alpha_discovered.json": "DexScreener Discoveries",
            "alpha_seen_coins.json": "Seen Coins",
            "pump_launches.json": "Pump.fun Launches",
            "twitter_research.json": "Twitter Research",
            "quantum_meme_signals.json": "Quantum Signals",
            "meme_coin_rankings.json": "Coin Rankings",
            "low_cap_meme_coins.json": "Low Cap Coins ($100M)",
            "nano_cap_meme_coins.json": "Nano Cap Coins ($10M)",
            "best_nano_caps.json": "Best Nano Caps",
            "paper_trading_state.json": "Paper Trading State",
            "influencer_calls.json": "Influencer Calls"
        }
        
        for filename, description in reports.items():
            filepath = os.path.join("meme_coin_data", filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"  [OK] {description:35s} ({filename}) - {size} bytes")
            else:
                print(f"  [MISSING] {description:35s} ({filename})")
        
        print("\nView any report:")
        print("  import json")
        print("  with open('meme_coin_data/FILE.json') as f:")
        print("      data = json.load(f)")
    
    def run(self):
        """Main loop"""
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.run_full_scan()
            elif choice == "2":
                self.run_continuous()
            elif choice == "3":
                self.run_dex_only()
            elif choice == "4":
                self.run_pump_only()
            elif choice == "5":
                self.run_twitter_only()
            elif choice == "6":
                self.view_quantum()
            elif choice == "7":
                self.view_influencers()
            elif choice == "8":
                self.paper_dashboard()
            elif choice == "9":
                self.test_telegram()
            elif choice == "10":
                self.view_reports()
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("\nInvalid option")
            
            input("\nPress Enter to continue...")

def main():
    print("=" * 80)
    print("MASTER CONTROL SYSTEM")
    print("=" * 80)
    print("\nIntegrated Systems:")
    print("- Live DexScreener Monitor")
    print("- Pump.fun Launch Scanner")
    print("- Twitter Research Bot")
    print("- Quantum Signal Generator")
    print("- Influencer Tracker")
    print("- Telegram Alerts")
    print("- Paper Trading")
    print("- Continuous Monitor")
    print("\nAll systems ready!")
    print("=" * 80)
    
    control = MasterControl()
    control.run()

if __name__ == "__main__":
    main()
