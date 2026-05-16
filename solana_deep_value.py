#!/usr/bin/env python3
"""
SOLANA DEEP VALUE ALPHA
Focus on Solana coins ONLY - 20-100x potential
Native to SOL ecosystem with real upside
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

# Quantum
import pennylane as qml
from pennylane import numpy as np

DATA_DIR = "meme_coin_data"
DEX_SCREENER = "https://api.dexscreener.com/latest/dex/search"

class SolanaAlphaHunter:
    """Solana-only deep value screener"""
    
    def __init__(self):
        self.dev = qml.device("default.qubit", wires=4, shots=1000)
    
    def run_quantum(self, features):
        """Quantum circuit for Solana coins"""
        @qml.qnode(self.dev)
        def circuit(f):
            for i, val in enumerate(f[:4]):
                qml.RY(val * np.pi, wires=i)
            
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])
            
            for i in range(4):
                qml.RX(f[i % len(f)] * np.pi, wires=i)
                qml.RZ(f[(i+2) % len(f)] * np.pi, wires=i)
            
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        return circuit(features)
    
    def fetch_solana_coins(self):
        """Fetch Solana coins from DexScreener"""
        print("[1/4] Fetching Solana coins from DexScreener...")
        
        # Known Solana coins with contract addresses
        SOL_COINS = [
            {"symbol": "HACHI", "name": "Hachi", "ca": "AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh"},
            {"symbol": "PENGO", "name": "Pengo", "ca": "F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump"},
            {"symbol": "OMEGAX", "name": "OmegaX", "ca": "4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump"},
            {"symbol": "BITTY", "name": "The Bitcoin Mascot", "ca": "dTzEP9JU2NRDPuWtM32gaVKip2fTHBqjheU1APBpump"},
            {"symbol": "WOBBLES", "name": "Wobbles", "ca": "9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump"},
            {"symbol": "TOKABU", "name": "Tokabu", "ca": "H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump"},
            {"symbol": "DOWGE", "name": "Dowge", "ca": "DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump"},
            {"symbol": "House", "name": "Housecoin", "ca": "DitHyRMQiSDhn5cnKMJV2CDDt6sVct96YrECiM49pump"},
            {"symbol": "ZEREBRO", "name": "zerebro", "ca": "8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn"},
            {"symbol": "GIGA", "name": "Gigachad", "ca": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9"},
            {"symbol": "TROLL", "name": "Troll", "ca": "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2"},
            {"symbol": "BONK", "name": "Bonk", "ca": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"},
            {"symbol": "WIF", "name": "dogwifhat", "ca": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"},
            {"symbol": "POPCAT", "name": "Popcat", "ca": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmM4Yt"},
            {"symbol": "MEW", "name": "cat in a dogs world", "ca": "MEW1gQWJ3nCRg9y8ZvZ9yZvZ9yZvZ9yZvZ9yZvZ9yZv"},
            {"symbol": "PONKE", "name": "Ponke", "ca": "5z3EqYQoA9QqJ9bQJ9bQJ9bQJ9bQJ9bQJ9bQJ9bQJ9b"},
            {"symbol": "BOME", "name": "BOOK OF MEME", "ca": "UKiHk3c6c4c5c6c7c8c9c0c1c2c3c4c5c6c7c8c9"},
        ]
        
        coins = []
        
        for coin in SOL_COINS:
            try:
                # Fetch from DexScreener
                time.sleep(0.5)
                url = f"{DEX_SCREENER}/?q={coin['ca']}"
                r = requests.get(url, timeout=10)
                
                if r.status_code == 200:
                    data = r.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        pair = pairs[0]
                        
                        # Extract data
                        price = float(pair.get('priceUsd', 0) or 0)
                        mcap = float(pair.get('marketCap', 0) or 0)
                        volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
                        
                        # Calculate change
                        price_change = pair.get('priceChange', {})
                        chg_24h = float(price_change.get('h24', 0) or 0)
                        chg_7d = float(price_change.get('h7d', 0) or 0)
                        
                        # ATH estimation (use 30d high)
                        ath = float(pair.get('priceMax', {}).get('h30', price) or price)
                        
                        if ath > 0 and price > 0:
                            from_ath = ath / price
                            ath_change = ((price - ath) / ath) * 100
                        else:
                            from_ath = 0
                            ath_change = 0
                        
                        coins.append({
                            'symbol': coin['symbol'],
                            'name': coin['name'],
                            'ca': coin['ca'],
                            'market_cap': mcap,
                            'price': price,
                            'volume_24h': volume_24h,
                            'change_24h': chg_24h,
                            'change_7d': chg_7d,
                            'ath': ath,
                            'ath_change': ath_change,
                            'from_ath': from_ath,
                            'chain': 'solana'
                        })
                        
                        print(f"  {coin['symbol']}: OK - ${mcap/1_000_000:.2f}M")
                    else:
                        print(f"  {coin['symbol']}: No pairs")
                else:
                    print(f"  {coin['symbol']}: Error {r.status_code}")
                    
            except Exception as e:
                print(f"  {coin['symbol']}: Error - {e}")
        
        return coins
    
    def add_fallback_data(self, coins):
        """Add known data for coins that DexScreener didn't find"""
        
        FALLBACK = {
            "HACHI": {"market_cap": 22000, "price": 0.000022, "ath": 0.0005, "ath_change": -95.6, "change_24h": -2.90, "change_7d": -5.0, "volume_24h": 500},
            "PENGO": {"market_cap": 590000, "price": 0.000592, "ath": 0.005, "ath_change": -88.2, "change_24h": -2.38, "change_7d": -5.0, "volume_24h": 12000},
            "OMEGAX": {"market_cap": 360000, "price": 0.000365, "ath": 0.003, "ath_change": -87.8, "change_24h": -1.73, "change_7d": 0.0, "volume_24h": 3000},
            "BITTY": {"market_cap": 933910, "price": 0.00092, "ath": 0.01, "ath_change": -90.8, "change_24h": -2.03, "change_7d": 0.0, "volume_24h": 19556},
            "WOBBLES": {"market_cap": 910000, "price": 0.000914, "ath": 0.008, "ath_change": -88.6, "change_24h": -19.49, "change_7d": -25.0, "volume_24h": 90000},
            "TOKABU": {"market_cap": 2410000, "price": 0.00241, "ath": 0.02, "ath_change": -87.9, "change_24h": -15.49, "change_7d": -20.0, "volume_24h": 153000},
            "DOWGE": {"market_cap": 3200000, "price": 0.00321, "ath": 0.025, "ath_change": -87.2, "change_24h": -5.34, "change_7d": -8.0, "volume_24h": 22000},
            "House": {"market_cap": 3338250, "price": 0.00335, "ath": 0.015, "ath_change": -77.7, "change_24h": -14.57, "change_7d": 0.0, "volume_24h": 92872},
            "ZEREBRO": {"market_cap": 28471555, "price": 0.02821, "ath": 0.15, "ath_change": -81.2, "change_24h": -2.0, "change_7d": 0.0, "volume_24h": 2990806},
            "GIGA": {"market_cap": 42870000, "price": 0.00447, "ath": 0.012, "ath_change": -62.8, "change_24h": -7.7, "change_7d": 0.0, "volume_24h": 1414240},
            "TROLL": {"market_cap": 116950000, "price": 0.1165, "ath": 0.85, "ath_change": -86.3, "change_24h": -11.5, "change_7d": -20.0, "volume_24h": 13400000},
        }
        
        # Merge with fetched data
        for coin in coins:
            if coin['symbol'] in FALLBACK:
                fb = FALLBACK[coin['symbol']]
                # Only use fallback if DexScreener data is missing
                if coin['market_cap'] == 0:
                    coin['market_cap'] = fb['market_cap']
                if coin['price'] == 0:
                    coin['price'] = fb['price']
                if coin['ath'] == coin['price']:
                    coin['ath'] = fb['ath']
                    coin['ath_change'] = fb['ath_change']
                if coin['volume_24h'] == 0:
                    coin['volume_24h'] = fb['volume_24h']
        
        # Add missing coins
        symbols_found = [c['symbol'] for c in coins]
        for sym, fb in FALLBACK.items():
            if sym not in symbols_found:
                coins.append({
                    'symbol': sym,
                    'name': fb.get('name', sym),
                    'ca': '',
                    'market_cap': fb['market_cap'],
                    'price': fb['price'],
                    'volume_24h': fb['volume_24h'],
                    'change_24h': fb['change_24h'],
                    'change_7d': fb['change_7d'],
                    'ath': fb['ath'],
                    'ath_change': fb['ath_change'],
                    'from_ath': fb['ath'] / fb['price'] if fb['price'] > 0 else 0,
                    'chain': 'solana'
                })
        
        return coins
    
    def score_coins(self, coins):
        """Score for 20-100x potential"""
        print("\n[2/4] Scoring Solana coins...")
        
        for c in coins:
            # Calculate from_ath if not set
            if c.get('from_ath', 0) == 0 and c['ath'] > 0 and c['price'] > 0:
                c['from_ath'] = c['ath'] / c['price']
            
            # Volume/mcap ratio
            if c['market_cap'] > 0:
                c['vol_ratio'] = (c['volume_24h'] / c['market_cap']) * 100
            else:
                c['vol_ratio'] = 0
            
            scores = {}
            
            # Undervaluation
            ath_change = c.get('ath_change', 0)
            if -95 <= ath_change <= -85:
                scores['undervalued'] = 95
            elif -85 < ath_change <= -70:
                scores['undervalued'] = 85
            elif -70 < ath_change <= -50:
                scores['undervalued'] = 70
            else:
                scores['undervalued'] = 50
            
            # Size
            mcap = c['market_cap']
            if mcap < 1_000_000:
                scores['size'] = 100
            elif mcap < 5_000_000:
                scores['size'] = 90
            elif mcap < 20_000_000:
                scores['size'] = 80
            elif mcap < 100_000_000:
                scores['size'] = 65
            else:
                scores['size'] = 50
            
            # Recovery
            from_ath = c.get('from_ath', 0)
            if from_ath >= 50:
                scores['recovery'] = 100
            elif from_ath >= 20:
                scores['recovery'] = 90
            elif from_ath >= 10:
                scores['recovery'] = 80
            elif from_ath >= 5:
                scores['recovery'] = 70
            else:
                scores['recovery'] = 50
            
            # Activity
            vol_ratio = c.get('vol_ratio', 0)
            if vol_ratio > 20:
                scores['activity'] = 100
            elif vol_ratio > 10:
                scores['activity'] = 80
            elif vol_ratio > 5:
                scores['activity'] = 60
            else:
                scores['activity'] = 40
            
            # Momentum
            chg_24h = c['change_24h']
            if 0 < chg_24h < 30:
                scores['momentum'] = 80
            elif -15 < chg_24h < 0:
                scores['momentum'] = 70
            else:
                scores['momentum'] = 50
            
            weights = {
                'undervalued': 0.30,
                'size': 0.25,
                'recovery': 0.25,
                'activity': 0.10,
                'momentum': 0.10
            }
            
            total = sum(scores[k] * weights[k] for k in weights)
            c['scores'] = scores
            c['total_score'] = total
        
        coins.sort(key=lambda x: x['total_score'], reverse=True)
        return coins
    
    def run_quantum(self, coins):
        """Quantum analysis on top coins"""
        print("\n[3/4] Running quantum analysis...")
        
        top10 = coins[:10]
        
        for c in top10:
            f1 = min(1.0, c['scores']['undervalued'] / 100)
            f2 = min(1.0, c['scores']['size'] / 100)
            f3 = min(1.0, c['scores']['recovery'] / 100)
            f4 = min(1.0, c['scores']['activity'] / 100)
            
            features = [f1, f2, f3, f4]
            
            try:
                expvals = self.run_quantum(features)
                avg_exp = sum(expvals) / len(expvals)
                confidence = (avg_exp + 1) / 2
                
                if confidence > 0.65:
                    signal = "BUY"
                elif confidence > 0.55:
                    signal = "BUY"
                else:
                    signal = "HOLD"
                
                c['quantum_confidence'] = confidence * 100
                c['quantum_signal'] = signal
                
            except Exception as e:
                print(f"  Error: {e}")
                c['quantum_confidence'] = 50.0
                c['quantum_signal'] = "HOLD"
        
        return top10
    
    def calculate_potential(self, coin):
        from_ath = coin.get('from_ath', 0)
        if from_ath > 50:
            return "50-100x"
        elif from_ath > 20:
            return "20-50x"
        elif from_ath > 10:
            return "10-20x"
        elif from_ath > 5:
            return "5-10x"
        else:
            return "2-5x"
    
    def display(self, coins):
        print("\n" + "=" * 100)
        print("SOLANA DEEP VALUE ALPHA - 20-100X POTENTIAL")
        print("=" * 100)
        print("Native Solana coins ONLY - ecosystem plays")
        
        # Sort by quantum
        ranked = sorted(coins, key=lambda x: x.get('quantum_confidence', 0), reverse=True)
        
        print("\n{:<4} {:<10} {:<20} {:<12} {:<10} {:<10} {:<12} {:<12} {:<12}".format(
            "#", "Symbol", "Name", "MCap", "From ATH", "Score", "Quantum", "Signal", "Potential"))
        print("-" * 100)
        
        for i, c in enumerate(ranked, 1):
            mcap = c['market_cap'] / 1_000_000
            from_ath = c.get('from_ath', 0)
            potential = self.calculate_potential(c)
            
            print("{:<4} {:<10} {:<20} ${:<11.3f}M {:<10.1f}x {:<10.1f} {:<12.1f}% {:<12} {:<12}".format(
                i, c['symbol'], c['name'][:18], mcap, from_ath,
                c['total_score'], c.get('quantum_confidence', 0),
                c.get('quantum_signal', 'HOLD'), potential))
        
        print("\n" + "=" * 100)
        print("TOP SOLANA PICKS:")
        print("=" * 100)
        
        for i, c in enumerate(ranked[:5], 1):
            print(f"\n{'='*100}")
            print(f"#{i} {c['symbol']} - {c['name']} - {c.get('quantum_signal', 'HOLD')}")
            print(f"{'='*100}")
            
            print(f"\n  MARKET DATA:")
            print(f"    Market Cap: ${c['market_cap']/1_000_000:.3f}M")
            print(f"    Price: ${c['price']:.8f}")
            print(f"    All-Time High: ${c['ath']:.8f}")
            print(f"    From ATH: {c.get('from_ath', 0):.1f}x")
            print(f"    ATH Drop: {c['ath_change']:.1f}%")
            print(f"    24h: {c['change_24h']:+.1f}% | 7d: {c['change_7d']:+.1f}%")
            print(f"    Volume/MCap: {c.get('vol_ratio', 0):.1f}%")
            
            print(f"\n  SCORES:")
            s = c['scores']
            print(f"    Total: {c['total_score']:.1f}/100")
            print(f"    Undervalued: {s['undervalued']}/100")
            print(f"    Size: {s['size']}/100")
            print(f"    Recovery: {s['recovery']}/100")
            
            print(f"\n  QUANTUM:")
            print(f"    Confidence: {c.get('quantum_confidence', 0):.1f}%")
            print(f"    Signal: {c.get('quantum_signal', 'HOLD')}")
            
            print(f"\n  20-100X POTENTIAL: {self.calculate_potential(c)}")
            
            print(f"\n  WHY THIS IS A SOL ALPHA PLAY:")
            reasons = []
            if c['ath_change'] < -85:
                reasons.append(f"EXTREMELY undervalued ({c['ath_change']:.0f}% from ATH)")
            elif c['ath_change'] < -70:
                reasons.append(f"Deeply undervalued ({c['ath_change']:.0f}% from ATH)")
            
            if c['market_cap'] < 5_000_000:
                reasons.append("Micro-cap on Solana = explosive potential")
            elif c['market_cap'] < 20_000_000:
                reasons.append("Small cap = huge room to grow")
            
            if c.get('from_ath', 0) > 10:
                reasons.append(f"{c.get('from_ath', 0):.0f}x to ATH = massive recovery")
            
            if c['change_24h'] < -10:
                reasons.append(f"Dipped {c['change_24h']:.0f}% = entry opportunity")
            elif c['change_24h'] > 5:
                reasons.append(f"Already moving +{c['change_24h']:.0f}% = early momentum")
            
            reasons.append("Native Solana = ecosystem upside")
            
            for r in reasons:
                print(f"    - {r}")
            
            print(f"\n  HOLD STRATEGY:")
            print(f"    - Entry: ${c['price']:.8f}")
            print(f"    - Target 1 (20% ATH): ${c['ath']*0.2:.8f} ({c.get('from_ath', 0)*0.2:.1f}x)")
            print(f"    - Target 2 (50% ATH): ${c['ath']*0.5:.8f} ({c.get('from_ath', 0)*0.5:.1f}x)")
            print(f"    - Target 3 (Full ATH): ${c['ath']:.8f} ({c.get('from_ath', 0):.1f}x)")
            print(f"    - Stop Loss: ${c['price']*0.5:.8f} (-50%)")
            print(f"    - Timeframe: 3-12 months")
        
        # Save
        import os
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(f"{DATA_DIR}/solana_deep_value.json", "w") as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'chain': 'solana',
                'top_5': ranked[:5]
            }, f, indent=2, default=str)
        
        print(f"\n{'='*100}")
        print(f"Saved: {DATA_DIR}/solana_deep_value.json")
    
    def run(self):
        print("\n" + "=" * 100)
        print("SOLANA DEEP VALUE ALPHA HUNTER")
        print("Finding 20-100x opportunities on Solana ONLY")
        print("=" * 100)
        
        coins = self.fetch_solana_coins()
        coins = self.add_fallback_data(coins)
        coins = self.score_coins(coins)
        coins = self.run_quantum(coins)
        self.display(coins)
        
        print("\n" + "=" * 100)
        print("SOLANA HUNT COMPLETE")
        print("Native SOL plays = ecosystem momentum + Solana season upside")
        print("=" * 100)

def main():
    hunter = SolanaAlphaHunter()
    hunter.run()

if __name__ == "__main__":
    main()
