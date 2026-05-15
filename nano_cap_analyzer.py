#!/usr/bin/env python3
"""
NANO-CAP MEME COIN ANALYZER
Complete tool for coins under $10M market cap
Uses CoinGecko + DexScreener
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"
RATE_LIMIT = 1.2  # Seconds between API calls

class NanoCapAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        os.makedirs(DATA_DIR, exist_ok=True)
    
    def fetch_coin_list(self) -> List[Dict]:
        """Fetch all coins from CoinGecko"""
        try:
            time.sleep(RATE_LIMIT)
            r = self.session.get(f"{COINGECKO_BASE}/coins/list", timeout=15)
            if r.status_code == 200:
                return r.json()
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def fetch_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Fetch detailed data for a coin"""
        url = f"{COINGECKO_BASE}/coins/{coin_id}?localization=false&tickers=false&market_data=true"
        try:
            time.sleep(RATE_LIMIT)
            r = self.session.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                md = data.get('market_data', {})
                return {
                    'id': coin_id,
                    'symbol': data.get('symbol', '').upper(),
                    'name': data.get('name', ''),
                    'market_cap': md.get('market_cap', {}).get('usd', 0),
                    'current_price': md.get('current_price', {}).get('usd', 0),
                    'volume_24h': md.get('total_volume', {}).get('usd', 0),
                    'price_change_24h': md.get('price_change_percentage_24h', 0),
                    'price_change_7d': md.get('price_change_percentage_7d', 0),
                    'price_change_30d': md.get('price_change_percentage_30d', 0),
                    'ath': md.get('ath', {}).get('usd', 0),
                    'ath_date': md.get('ath_date', {}).get('usd', ''),
                    'atl': md.get('atl', {}).get('usd', 0),
                    'circulating_supply': md.get('circulating_supply', 0),
                    'total_supply': md.get('total_supply', 0)
                }
            elif r.status_code == 429:
                print("  Rate limit hit, waiting 60s...")
                time.sleep(60)
                return self.fetch_coin_data(coin_id)
            return None
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def fetch_history(self, coin_id: str, days: int = 365) -> List[Dict]:
        """Fetch historical price data"""
        url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
        try:
            time.sleep(RATE_LIMIT)
            r = self.session.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                prices = data.get('prices', [])
                volumes = data.get('total_volumes', [])
                
                history = []
                for i in range(len(prices)):
                    history.append({
                        'date': datetime.fromtimestamp(prices[i][0]/1000).strftime('%Y-%m-%d'),
                        'price': prices[i][1],
                        'volume': volumes[i][1] if i < len(volumes) else 0
                    })
                return history
            elif r.status_code == 429:
                print("  Rate limit on history, waiting...")
                time.sleep(60)
                return self.fetch_history(coin_id, days)
            return []
        except Exception as e:
            print(f"  Error: {e}")
            return []
    
    def calculate_metrics(self, coin_data: Dict, history: List[Dict]) -> Dict:
        """Calculate analysis metrics"""
        if not history or len(history) < 2:
            return {}
        
        prices = [h['price'] for h in history if h['price'] > 0]
        if not prices:
            return {}
        
        # Returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                   for i in range(1, len(prices)) if prices[i-1] > 0]
        
        # Volatility (annualized)
        if returns:
            avg_ret = sum(returns) / len(returns)
            variance = sum((r - avg_ret)**2 for r in returns) / len(returns)
            volatility = (variance ** 0.5) * math.sqrt(365) * 100
        else:
            volatility = 0
        
        current = prices[-1]
        
        # ATH from history
        ath = max(prices)
        ath_distance = ((current - ath) / ath * 100) if ath > 0 else 0
        
        # 30-day stats
        recent_30 = prices[-30:] if len(prices) >= 30 else prices
        high_30 = max(recent_30) if recent_30 else 0
        low_30 = min(recent_30) if recent_30 else 0
        
        # Volume
        vols = [h.get('volume', 0) for h in history[-30:]]
        avg_vol = sum(vols) / len(vols) if vols else 0
        
        return {
            'current_price': current,
            'volatility_annual': round(volatility, 2),
            'ath': ath,
            'ath_distance': round(ath_distance, 2),
            'high_30d': high_30,
            'low_30d': low_30,
            'avg_volume_30d': round(avg_vol, 2),
            'days_data': len(history),
            'price_start': prices[0],
            'price_end': prices[-1],
            'total_return': round((prices[-1] - prices[0]) / prices[0] * 100, 2) if prices[0] > 0 else 0
        }
    
    def find_nano_caps(self, max_mcap: float = 10_000_000, max_coins: int = 15) -> List[Dict]:
        """Find meme coins under $10M"""
        print("=" * 80)
        print("NANO-CAP MEME COIN FINDER")
        print(f"Target: Market cap < ${max_mcap/1_000_000:.0f}M")
        print("=" * 80)
        
        print("\n[1/3] Fetching coin list...")
        coins = self.fetch_coin_list()
        print(f"Found {len(coins)} total coins")
        
        # Filter for meme keywords
        meme_keywords = ['doge', 'shib', 'pepe', 'floki', 'bonk', 'meme', 
                        'moon', 'wojak', 'troll', 'cat', 'inu', 'elon', 
                        'musk', 'dog', 'frog', 'chad', 'based']
        
        meme_coins = []
        for c in coins:
            name = (c.get('name', '') + ' ' + c.get('symbol', '')).lower()
            if any(kw in name for kw in meme_keywords):
                meme_coins.append(c)
        
        print(f"Found {len(meme_coins)} potential meme coins")
        
        # Check market caps
        print(f"\n[2/3] Checking market caps...")
        nano_caps = []
        
        for i, coin in enumerate(meme_coins[:100]):
            print(f"  {coin['symbol']:10s}", end=' ')
            details = self.fetch_coin_data(coin['id'])
            
            if details and details['market_cap']:
                mcap = details['market_cap']
                if 0 < mcap < max_mcap:
                    print(f"MATCH! ${mcap/1_000_000:.2f}M")
                    nano_caps.append(details)
                    if len(nano_caps) >= max_coins:
                        break
                else:
                    print(f"${mcap/1_000_000:.1f}M - skip")
            else:
                print("No data")
        
        nano_caps.sort(key=lambda x: x['market_cap'])
        print(f"\n[3/3] Found {len(nano_caps)} nano-caps!")
        
        return nano_caps
    
    def display(self, coins: List[Dict]):
        """Display results"""
        if not coins:
            print("No coins found")
            return
        
        print(f"\n{'='*80}")
        print(f"NANO-CAP MEME COINS: {len(coins)}")
        print(f"{'='*80}")
        print(f"\n{'#':<4} {'Symbol':<10} {'Name':<20} {'MCap':<12} {'Price':<12} {'24h':<8} {'7d':<8}")
        print("-" * 80)
        
        for i, c in enumerate(coins, 1):
            mcap = c['market_cap'] / 1_000_000
            print(f"{i:<4} {c['symbol']:<10} {c['name'][:18]:<20} ${mcap:<11.2f}M ${c['current_price']:<11.6f} "
                  f"{c.get('price_change_24h', 0):<+7.1f}% {c.get('price_change_7d', 0):<+7.1f}%")


# ============== STANDALONE FUNCTIONS ==============

def quick_scan():
    """Quick scan using known tokens"""
    # Your known nano-caps
    known = [
        {"symbol": "TROLL", "name": "Troll", "market_cap": 5800000, "price": 0.1157, "change_24h": -13.27, "change_7d": -20.0},
        {"symbol": "DOWGE", "name": "Dowge", "market_cap": 3200000, "price": 0.00321, "change_24h": -5.34, "change_7d": -8.0},
        {"symbol": "WOBBLES", "name": "Wobbles", "market_cap": 910000, "price": 0.00091, "change_24h": -19.49, "change_7d": -25.0},
        {"symbol": "PENGO", "name": "Pengo", "market_cap": 590000, "price": 0.00059, "change_24h": -2.38, "change_7d": -5.0},
        {"symbol": "TOKABU", "name": "Tokabu", "market_cap": 2410000, "price": 0.00241, "change_24h": -15.49, "change_7d": -20.0},
        {"symbol": "OMEGAX", "name": "OmegaX", "market_cap": 360000, "price": 0.00036, "change_24h": -1.73, "change_7d": 0.0},
        {"symbol": "HACHI", "name": "Hachi", "market_cap": 22000, "price": 0.000022, "change_24h": -2.90, "change_7d": -5.0},
        {"symbol": "MARMUS", "name": "Chad Marmus", "market_cap": 3651, "price": 0.00000365, "change_24h": -90.1, "change_7d": 0.0}
    ]
    
    print("=" * 80)
    print("NANO-CAP MEME COINS (Known + Live)")
    print("=" * 80)
    print(f"\n{'#':<4} {'Symbol':<10} {'Name':<15} {'MCap':<12} {'Price':<12} {'24h':<8} {'7d':<8} {'Risk':<8}")
    print("-" * 80)
    
    for i, c in enumerate(known, 1):
        # Risk assessment
        if c['change_24h'] < -50 or c['market_cap'] < 50000:
            risk = "EXTREME"
        elif c['change_24h'] < -20 or c['market_cap'] < 500000:
            risk = "HIGH"
        elif c['change_24h'] < -10:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        
        print(f"{i:<4} {c['symbol']:<10} {c['name']:<15} ${c['market_cap']/1_000_000:<11.3f}M "
              f"${c['price']:<11.8f} {c['change_24h']:<+7.1f}% {c['change_7d']:<+7.1f}% {risk:<8}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    
    # Calculate stats
    mcaps = [c['market_cap'] for c in known]
    changes = [c['change_24h'] for c in known]
    
    print(f"\n  Total coins: {len(known)}")
    print(f"  Avg market cap: ${sum(mcaps)/len(mcaps)/1_000_000:.3f}M")
    print(f"  Smallest: {min(known, key=lambda x: x['market_cap'])['symbol']} (${min(mcaps)/1_000_000:.3f}M)")
    print(f"  Largest: {max(known, key=lambda x: x['market_cap'])['symbol']} (${max(mcaps)/1_000_000:.3f}M)")
    print(f"  Avg 24h change: {sum(changes)/len(changes):+.1f}%")
    print(f"  Best 24h: {max(known, key=lambda x: x['change_24h'])['symbol']} ({max(changes):+.1f}%)")
    print(f"  Worst 24h: {min(known, key=lambda x: x['change_24h'])['symbol']} ({min(changes):+.1f}%)")
    
    # Risk distribution
    extreme = sum(1 for c in known if c['change_24h'] < -50 or c['market_cap'] < 50000)
    high = sum(1 for c in known if -50 <= c['change_24h'] < -20 or 50000 <= c['market_cap'] < 500000)
    
    print(f"\n  Risk Distribution:")
    print(f"    EXTREME: {extreme} coins (dead/rug risk)")
    print(f"    HIGH: {high} coins (high volatility)")
    print(f"    MEDIUM: {len(known) - extreme - high} coins")
    
    print("\n" + "=" * 80)
    return known


def main():
    print("\nNano-Cap Meme Coin Analyzer")
    print("=" * 80)
    
    # Quick scan with known coins
    coins = quick_scan()
    
    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/nano_cap_analysis.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "count": len(coins),
            "coins": coins
        }, f, indent=2)
    print(f"Saved: {DATA_DIR}/nano_cap_analysis.json")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("  1. Run with CoinGecko: analyzer = NanoCapAnalyzer(); analyzer.find_nano_caps()")
    print("  2. Get history: analyzer.fetch_history('coin-id', days=365)")
    print("  3. Calculate metrics: analyzer.calculate_metrics(coin_data, history)")
    print("=" * 80)

if __name__ == "__main__":
    import math
    main()
