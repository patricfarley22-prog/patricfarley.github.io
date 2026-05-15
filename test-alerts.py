#!/usr/bin/env python3
"""
TEST ALERT SYSTEM
Simple alert system for meme coins
"""

import json
import os
import time
from datetime import datetime

class AlertSystem:
    def __init__(self):
        self.data_dir = 'meme_coin_data'
        self.alert_file = f'{self.data_dir}/alerts.json'
        self.load_alerts()
    
    def load_alerts(self):
        if os.path.exists(self.alert_file):
            with open(self.alert_file, 'r') as f:
                self.alerts = json.load(f)
        else:
            self.alerts = []
    
    def save_alerts(self):
        with open(self.alert_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def check_price_alert(self, symbol, current_price, threshold=0.05):
        """Check if price moved more than threshold"""
        # Load previous price
        history_file = f'{self.data_dir}/{symbol}_history.json'
        if not os.path.exists(history_file):
            return None
        
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        history = data.get('history', [])
        if len(history) < 2:
            return None
        
        prev_price = history[-2]['price']
        if prev_price <= 0:
            return None
        
        change = (current_price - prev_price) / prev_price
        
        if abs(change) >= threshold:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'type': 'PRICE',
                'severity': 'HIGH' if abs(change) > 0.1 else 'MEDIUM',
                'message': f"Price {'UP' if change > 0 else 'DOWN'} {abs(change)*100:.1f}%",
                'old_price': prev_price,
                'new_price': current_price,
                'change_pct': change * 100
            }
            
            self.alerts.append(alert)
            self.save_alerts()
            
            return alert
        
        return None
    
    def check_all_coins(self):
        """Check all saved coins for alerts"""
        print("Checking all coins for alerts...")
        
        alerts_triggered = []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('_history.json'):
                symbol = filename.replace('_history.json', '')
                
                with open(f'{self.data_dir}/{filename}', 'r') as f:
                    data = json.load(f)
                
                history = data.get('history', [])
                if not history:
                    continue
                
                latest = history[-1]
                current_price = latest.get('price', 0)
                
                alert = self.check_price_alert(symbol, current_price)
                if alert:
                    alerts_triggered.append(alert)
                    print(f"ALERT: {alert['symbol']} - {alert['message']}")
        
        return alerts_triggered
    
    def display_alerts(self, limit=10):
        """Display recent alerts"""
        if not self.alerts:
            print("No alerts yet")
            return
        
        print("\n" + "=" * 80)
        print("RECENT ALERTS")
        print("=" * 80)
        
        recent = self.alerts[-limit:]
        for alert in reversed(recent):
            print(f"\n[{alert['timestamp'][:19]}]")
            print(f"  {alert['symbol']}: {alert['type']} - {alert['message']}")
            if 'old_price' in alert:
                print(f"  Price: ${alert['old_price']:.8f} -> ${alert['new_price']:.8f}")


def main():
    print("=" * 80)
    print("MEME COIN ALERT SYSTEM TEST")
    print("=" * 80)
    
    alerts = AlertSystem()
    
    # Check all coins
    triggered = alerts.check_all_coins()
    
    if triggered:
        print(f"\n{len(triggered)} alerts triggered!")
        alerts.display_alerts()
    else:
        print("\nNo alerts triggered")
        print("Alerts trigger on 5%+ price moves")
    
    # Display all alerts
    alerts.display_alerts(limit=5)
    
    print("\n" + "=" * 80)
    print("Alert system test complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
