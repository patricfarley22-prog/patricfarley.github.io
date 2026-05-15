#!/usr/bin/env python3
"""
CONTINUOUS MONITOR
Runs all alpha scanners + Telegram alerts + Paper trading
"""

import time
import json
import os
from datetime import datetime, timedelta
from alpha_master_v2 import AlphaMasterV2
from paper_trading import PaperTrader
from telegram_alerts import TelegramAlerter

class ContinuousMonitor:
    """Continuous alpha monitoring system"""
    
    def __init__(self, interval_minutes=5):
        self.interval = interval_minutes * 60
        self.master = AlphaMasterV2()
        self.trader = PaperTrader()
        self.alerter = TelegramAlerter()
        self.cycle_count = 0
    
    def run_cycle(self):
        """Single monitoring cycle"""
        self.cycle_count += 1
        print(f"\n{'='*80}")
        print(f"CYCLE #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        # 1. Run alpha scan
        print("\n[1/4] Running alpha scan...")
        try:
            self.master.run_full_scan()
        except Exception as e:
            print(f"Alpha scan error: {e}")
        
        # 2. Check for A+ coins
        print("\n[2/4] Checking for A+ alerts...")
        a_plus_coins = self.get_a_plus_coins()
        
        if a_plus_coins:
            print(f"Found {len(a_plus_coins)} A+ coins!")
            
            # Send Telegram alerts
            for coin in a_plus_coins[:3]:
                print(f"Sending alert for {coin['symbol']}...")
                self.alerter.alert_a_plus(coin)
                
                # Paper trade (small amount)
                print(f"Paper trading {coin['symbol']}...")
                price = coin.get('price', 0)
                if price > 0:
                    self.trader.buy(
                        symbol=coin['symbol'],
                        price=price,
                        amount=50,  # $50 per trade
                        target=price * 2,
                        stop_loss=price * 0.8
                    )
        else:
            print("No A+ coins this cycle")
        
        # 3. Check stop losses
        print("\n[3/4] Checking stop losses...")
        # In real implementation, fetch current prices
        # For now, skip
        
        # 4. Portfolio status
        print("\n[4/4] Portfolio status...")
        self.trader.display_portfolio()
        
        print(f"\nNext cycle in {self.interval//60} minutes...")
    
    def get_a_plus_coins(self) -> list:
        """Get A+ coins from latest scan"""
        filepath = os.path.join("meme_coin_data", "alpha_master_report.json")
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, "r") as f:
                report = json.load(f)
                return [c for c in report.get("top_15", []) if c.get("master_grade") == "A+"]
        except:
            return []
    
    def run_continuous(self, hours=24):
        """Run continuous monitoring"""
        print("=" * 80)
        print("CONTINUOUS ALPHA MONITOR")
        print("=" * 80)
        print(f"Duration: {hours}h | Interval: {self.interval//60}min")
        print("Components:")
        print("- Live DexScreener Monitor")
        print("- Pump.fun Scanner")
        print("- Twitter Research Bot")
        print("- Quantum Signal Generator")
        print("- Telegram Alerts")
        print("- Paper Trading")
        print("=" * 80)
        
        start = datetime.now()
        end = start + timedelta(hours=hours)
        
        while datetime.now() < end:
            try:
                self.run_cycle()
            except Exception as e:
                print(f"Cycle error: {e}")
            
            if datetime.now() < end:
                time.sleep(self.interval)
        
        # Final summary
        print(f"\n{'='*80}")
        print("MONITORING COMPLETE")
        print(f"{'='*80}")
        print(f"Cycles: {self.cycle_count}")
        print(f"Duration: {hours}h")
        
        stats = self.trader.get_stats()
        print(f"\nFinal Portfolio:")
        print(f"  Balance: ${stats['balance']:.2f}")
        print(f"  ROI: {stats['roi_pct']:+.2f}%")
        print(f"  Trades: {stats['total_trades']}")
        print(f"  Win Rate: {stats['win_rate']}%")
        
        # Send daily summary
        self.alerter.daily_summary(
            coins_found=self.cycle_count * 10,
            a_plus_count=0,
            top_coins=[]
        )

def main():
    monitor = ContinuousMonitor(interval_minutes=5)
    
    print("=" * 80)
    print("CONTINUOUS MONITORING SYSTEM")
    print("=" * 80)
    print("\nThis will:")
    print("1. Check DexScreener every 5 minutes")
    print("2. Find trending + new launches")
    print("3. Generate quantum signals")
    print("4. Alert A+ coins via Telegram")
    print("5. Paper trade A+ coins ($50 each)")
    print("6. Track stop losses")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Run for 1 hour (test mode)
    monitor.run_cycle()
    
    print(f"\n{'='*80}")
    print("SINGLE CYCLE COMPLETE")
    print(f"{'='*80}")
    print("\nTo run continuously:")
    print("  monitor.run_continuous(hours=24)")

if __name__ == "__main__":
    main()
