#!/usr/bin/env python3
"""
TELEGRAM ALERTS
Sends alerts to your phone via Telegram bot
Uses requests library (no external dependencies)
"""

import requests
import json
import os
from datetime import datetime

# Get bot token from environment or TOOLS.md
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = "6643728142"  # Patric's Telegram ID

class TelegramAlerter:
    """Send Telegram alerts for alpha signals"""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or BOT_TOKEN
        self.chat_id = chat_id or CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str) -> bool:
        """Send text message"""
        if self.bot_token == "YOUR_BOT_TOKEN_HERE":
            print(f"[TELEGRAM WOULD SEND]\n{text}\n")
            return True
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def alert_a_plus(self, coin: dict):
        """Alert for A+ coin"""
        text = f"""🚨 *A+ ALPHA ALERT*

💎 *{coin['symbol']}* - {coin.get('name', '')}
📊 Grade: *{coin['alpha_grade']}* ({coin['alpha_score']}/100)
💰 Price: ${coin.get('price', 0):.8f}
🏦 MCap: ${coin.get('market_cap', 0)/1_000_000:.2f}M
📈 1h: {coin.get('change_1h', 0):+.1f}%
📈 24h: {coin.get('change_24h', 0):+.1f}%
🔮 Quantum: *{coin.get('quantum_signal', 'N/A')}* ({coin.get('quantum_confidence', 0)*100:.0f}%)

Signals:
"""
        for signal in coin.get('alpha_signals', [])[:3]:
            text += f"• {signal}\n"
        
        text += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_message(text)
    
    def alert_new_launch(self, coin: dict):
        """Alert for new launch"""
        text = f"""🚀 *NEW LAUNCH ALERT*

💎 *{coin['symbol']}* - {coin.get('name', '')}
📊 Grade: *{coin['launch_grade']}* ({coin['launch_score']}/100)
💰 Price: ${coin.get('price', 0):.8f}
🏦 MCap: ${coin.get('market_cap', 0)/1000:.1f}K
🆕 Age: {coin.get('age_hours', 0):.1f}h
🔮 Quantum: *{coin.get('quantum_signal', 'N/A')}*

Signals:
"""
        for signal in coin.get('launch_signals', [])[:3]:
            text += f"• {signal}\n"
        
        text += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_message(text)
    
    def alert_quantum_flip(self, symbol: str, old_signal: str, new_signal: str, confidence: float):
        """Alert when quantum signal changes"""
        text = f"""🔄 *QUANTUM FLIP*

💎 *{symbol}*
Before: {old_signal}
After: *{new_signal}* ({confidence*100:.0f}%)

Check DexScreener for entry!"
"""
        return self.send_message(text)
    
    def daily_summary(self, coins_found: int, a_plus_count: int, top_coins: list):
        """Daily summary alert"""
        text = f"""📊 *DAILY ALPHA SUMMARY*

Found: {coins_found} coins
A+ Alerts: {a_plus_count}

Top Picks:
"""
        for i, coin in enumerate(top_coins[:5], 1):
            text += f"{i}. {coin['symbol']} ({coin.get('alpha_grade', 'N/A')})\n"
        
        text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self.send_message(text)

def main():
    alerter = TelegramAlerter()
    
    # Test alerts
    print("=" * 80)
    print("TELEGRAM ALERT SYSTEM")
    print("=" * 80)
    
    test_coin = {
        "symbol": "TEST",
        "name": "Test Coin",
        "price": 0.0001,
        "market_cap": 500000,
        "change_1h": 25.0,
        "change_24h": 150.0,
        "alpha_score": 85,
        "alpha_grade": "A+",
        "quantum_signal": "BUY",
        "quantum_confidence": 0.75,
        "alpha_signals": ["100%+ 1h", "High volume", "Micro gem"]
    }
    
    print("\nSending test A+ alert...")
    alerter.alert_a_plus(test_coin)
    
    print("\n✅ Telegram alert system ready!")
    print(f"\nTo use:")
    print("  alerter = TelegramAlerter()")
    print("  alerter.alert_a_plus(coin)")
    print("  alerter.alert_new_launch(coin)")
    print("  alerter.daily_summary(count, a_plus, coins)")

if __name__ == "__main__":
    main()
