#!/usr/bin/env python3
"""
GIGACHAD (GIGA) LIVE MONITOR
Real-time tracking for 63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9
Checks every 5 minutes via DexScreener
"""

import json
import time
import math
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests

DATA_DIR = "meme_coin_data"
TOKEN = "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9"

def fetch_giga() -> Optional[Dict]:
    """Fetch GIGA data from DexScreener"""
    try:
        url = f"https://api.dexscreener.com/tokens/v1/solana/{TOKEN}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                return data[0]
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_giga(data: Dict) -> Dict:
    """Analyze GIGA data"""
    if not data:
        return {}
    
    # Extract metrics
    price = float(data.get('priceUsd', 0))
    mcap = float(data.get('marketCap', data.get('fdv', 0)))
    vol_24h = float(data.get('volume', {}).get('h24', 0))
    chg_24h = float(data.get('priceChange', {}).get('h24', 0))
    chg_1h = float(data.get('priceChange', {}).get('h1', 0))
    chg_5m = float(data.get('priceChange', {}).get('m5', 0))
    liq = float(data.get('liquidity', {}).get('usd', 0))
    buys_24h = int(data.get('txns', {}).get('h24', {}).get('buys', 0))
    sells_24h = int(data.get('txns', {}).get('h24', {}).get('sells', 0))
    
    # Ratios
    vol_mcap = vol_24h / mcap if mcap > 0 else 0
    buy_sell = buys_24h / max(sells_24h, 1)
    
    # Quantum-ish signal
    momentum = math.tanh(chg_24h / 50)
    volume_sig = math.tanh(vol_24h / mcap)
    volatility = math.exp(-abs(chg_24h) / 30)
    
    combined = momentum * 0.3 + volume_sig * 0.25 + volatility * 0.25
    
    if combined > 0.3 and chg_1h > 0:
        signal = "BUY"
        confidence = min(0.9, 0.5 + combined * 0.4)
    elif combined < -0.3 and chg_1h < 0:
        signal = "SELL"
        confidence = min(0.9, 0.5 + abs(combined) * 0.4)
    else:
        signal = "HOLD"
        confidence = 0.5
    
    return {
        'symbol': 'GIGA',
        'price': price,
        'mcap': mcap,
        'vol_24h': vol_24h,
        'chg_24h': chg_24h,
        'chg_1h': chg_1h,
        'chg_5m': chg_5m,
        'liquidity': liq,
        'vol_mcap_ratio': vol_mcap,
        'buy_sell_ratio': buy_sell,
        'buys_24h': buys_24h,
        'sells_24h': sells_24h,
        'signal': signal,
        'confidence': confidence,
        'quantum_score': combined,
        'timestamp': datetime.now().isoformat()
    }

def display_giga(analysis: Dict):
    """Display GIGA analysis"""
    if not analysis:
        print("No data available")
        return
    
    print("\n" + "=" * 80)
    print("GIGACHAD (GIGA) LIVE DATA")
    print("=" * 80)
    print(f"Time: {analysis['timestamp'][:19]}")
    print(f"\n[PRICE]")
    print(f"  Price: ${analysis['price']:.6f}")
    print(f"  Market Cap: ${analysis['mcap']/1_000_000:.2f}M")
    print(f"  Liquidity: ${analysis['liquidity']:,.0f}")
    
    print(f"\n[PERFORMANCE]")
    print(f"  24h: {analysis['chg_24h']:+.2f}%")
    print(f"  1h:  {analysis['chg_1h']:+.2f}%")
    print(f"  5m:  {analysis['chg_5m']:+.2f}%")
    
    print(f"\n[ACTIVITY]")
    print(f"  24h Volume: ${analysis['vol_24h']:,.0f}")
    print(f"  Volume/MCap: {analysis['vol_mcap_ratio']:.2%}")
    print(f"  Buys: {analysis['buys_24h']:,} | Sells: {analysis['sells_24h']:,}")
    print(f"  Buy/Sell: {analysis['buy_sell_ratio']:.2f}")
    
    print(f"\n[SIGNAL]")
    print(f"  Signal: {analysis['signal']} ({analysis['confidence']:.0%})")
    print(f"  Score: {analysis['quantum_score']:.3f}")
    
    # Alert conditions
    if analysis['chg_1h'] > 5:
        print(f"\n  ALERT: Price pumping +{analysis['chg_1h']:.1f}% in 1h")
    if analysis['chg_1h'] < -5:
        print(f"\n  ALERT: Price dumping {analysis['chg_1h']:.1f}% in 1h")
    if analysis['vol_mcap_ratio'] > 0.1:
        print(f"\n  ALERT: Volume spike {analysis['vol_mcap_ratio']:.1%} of mcap")
    
    print("=" * 80)

def save_analysis(analysis: Dict):
    """Save analysis to history"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    history_file = f"{DATA_DIR}/giga_history.json"
    history = []
    
    if os.path.exists(history_file):
        with open(history_file) as f:
            history = json.load(f)
    
    history.append(analysis)
    
    # Keep last 1000 entries
    history = history[-1000:]
    
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)
    
    return history_file

def monitor_once():
    """Single check"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking GIGA...")
    
    data = fetch_giga()
    if not data:
        print("Failed to fetch data")
        return
    
    analysis = analyze_giga(data)
    display_giga(analysis)
    
    save_analysis(analysis)
    
    return analysis

def monitor_continuous(minutes=60):
    """Continuous monitoring"""
    print("=" * 80)
    print("GIGACHAD CONTINUOUS MONITOR")
    print(f"Duration: {minutes} minutes | Interval: 5 minutes")
    print("=" * 80)
    
    cycles = 0
    end = datetime.now() + timedelta(minutes=minutes)
    
    while datetime.now() < end:
        cycles += 1
        monitor_once()
        
        if datetime.now() < end:
            print(f"\nNext check: {(datetime.now()+timedelta(minutes=5)).strftime('%H:%M:%S')}")
            time.sleep(300)  # 5 minutes
    
    print(f"\nDone. Cycles: {cycles}")

def main():
    print("GIGACHAD (GIGA) Monitor")
    print("=" * 60)
    print(f"Token: {TOKEN}")
    print("=" * 60)
    
    # Single check
    monitor_once()
    
    print("\n" + "=" * 60)
    print("To run continuous monitoring:")
    print("  python giga_monitor.py --continuous")
    print("Or:")
    print("  monitor_continuous(minutes=60)")
    print("=" * 60)

if __name__ == "__main__":
    main()
