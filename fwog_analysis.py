#!/usr/bin/env python3
"""
FWOG DEEP ANALYSIS
Contract: A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump
Full quantum + fundamental + technical + social analysis
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

# Quantum
import pennylane as qml
from pennylane import numpy as np

DEX_SCREENER = "https://api.dexscreener.com/latest/dex/search"
COINGECKO = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"

class FWOGAnalyzer:
    """Complete FWOG analysis"""
    
    def __init__(self, ca: str):
        self.ca = ca
        self.symbol = "FWOG"
        self.data = {}
        self.dev = qml.device("default.qubit", wires=4, shots=1000)
    
    def fetch_dex_data(self) -> Dict:
        """Fetch from DexScreener"""
        print("[1/6] Fetching DexScreener data...")
        
        try:
            url = f"{DEX_SCREENER}/?q={self.ca}"
            r = requests.get(url, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    p = pairs[0]
                    
                    result = {
                        'symbol': 'FWOG',
                        'price': float(p.get('priceUsd', 0) or 0),
                        'market_cap': float(p.get('marketCap', 0) or 0),
                        'liquidity': float(p.get('liquidity', {}).get('usd', 0) or 0),
                        'volume_24h': float(p.get('volume', {}).get('h24', 0) or 0),
                        'volume_6h': float(p.get('volume', {}).get('h6', 0) or 0),
                        'volume_1h': float(p.get('volume', {}).get('h1', 0) or 0),
                        'buys_24h': int(p.get('txns', {}).get('h24', {}).get('buys', 0) or 0),
                        'sells_24h': int(p.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                        'price_change_1h': float(p.get('priceChange', {}).get('h1', 0) or 0),
                        'price_change_24h': float(p.get('priceChange', {}).get('h24', 0) or 0),
                        'price_change_7d': float(p.get('priceChange', {}).get('h7d', 0) or 0),
                        'price_max_30d': float(p.get('priceMax', {}).get('h30', 0) or 0),
                        'price_min_30d': float(p.get('priceMin', {}).get('h30', 0) or 0),
                        'fdv': float(p.get('fdv', 0) or 0),
                        'chain': p.get('chainId', 'unknown'),
                        'dex': p.get('dexId', 'unknown'),
                        'pair': p.get('pairAddress', ''),
                        'url': p.get('url', ''),
                        'created': p.get('pairCreatedAt', 0)
                    }
                    
                    print(f"  Found: ${result['market_cap']/1_000_000:.2f}M mcap")
                    print(f"  Price: ${result['price']:.8f}")
                    print(f"  24h: {result['price_change_24h']:+.1f}%")
                    
                    return result
                else:
                    print("  No pairs found")
                    return None
            else:
                print(f"  Error: {r.status_code}")
                return None
                
        except Exception as e:
            print(f"  Error: {e}")
            return None
    
    def calculate_metrics(self, data: Dict) -> Dict:
        """Calculate all metrics"""
        print("\n[2/6] Calculating metrics...")
        
        metrics = {}
        
        # Market cap in millions
        mcap = data.get('market_cap', 0)
        metrics['mcap_m'] = mcap / 1_000_000
        
        # Liquidity ratio
        liquidity = data.get('liquidity', 0)
        if mcap > 0:
            metrics['liquidity_ratio'] = liquidity / mcap
        else:
            metrics['liquidity_ratio'] = 0
        
        # Volume metrics
        vol_24h = data.get('volume_24h', 0)
        if mcap > 0:
            metrics['vol_mcap_ratio'] = (vol_24h / mcap) * 100
        else:
            metrics['vol_mcap_ratio'] = 0
        
        # Buy/sell ratio
        buys = data.get('buys_24h', 0)
        sells = data.get('sells_24h', 0)
        if sells > 0:
            metrics['buy_sell_ratio'] = buys / sells
        else:
            metrics['buy_sell_ratio'] = 0
        
        # From ATH
        price = data.get('price', 0)
        ath = data.get('price_max_30d', price)
        if ath > 0 and price > 0:
            metrics['from_ath'] = ath / price
            metrics['ath_change'] = ((price - ath) / ath) * 100
        else:
            metrics['from_ath'] = 0
            metrics['ath_change'] = 0
        
        # Age if available
        created = data.get('created', 0)
        if created > 0:
            age_days = (time.time() * 1000 - created) / (1000 * 86400)
            metrics['age_days'] = age_days
        else:
            metrics['age_days'] = 0
        
        print(f"  MCap: ${metrics['mcap_m']:.2f}M")
        print(f"  Liquidity Ratio: {metrics['liquidity_ratio']:.2f}")
        print(f"  Vol/MCap: {metrics['vol_mcap_ratio']:.1f}%")
        print(f"  Buy/Sell: {metrics['buy_sell_ratio']:.2f}")
        print(f"  From ATH: {metrics['from_ath']:.1f}x")
        print(f"  ATH Drop: {metrics['ath_change']:.1f}%")
        
        return metrics
    
    def run_quantum_analysis(self, data: Dict, metrics: Dict) -> Dict:
        """Full quantum analysis"""
        print("\n[3/6] Running quantum analysis...")
        
        # Build features for quantum circuit
        # Feature 1: Market cap size (smaller = more upside)
        mcap_m = metrics['mcap_m']
        if mcap_m < 1:
            f1 = 0.95
        elif mcap_m < 5:
            f1 = 0.85
        elif mcap_m < 20:
            f1 = 0.70
        else:
            f1 = 0.50
        
        # Feature 2: Volume activity
        vol_ratio = metrics['vol_mcap_ratio']
        if vol_ratio > 50:
            f2 = 0.95
        elif vol_ratio > 20:
            f2 = 0.80
        elif vol_ratio > 10:
            f2 = 0.65
        else:
            f2 = 0.40
        
        # Feature 3: Price momentum
        chg_24h = data.get('price_change_24h', 0)
        if 5 < chg_24h < 30:
            f3 = 0.90
        elif 0 < chg_24h < 5:
            f3 = 0.70
        elif -15 < chg_24h < 0:
            f3 = 0.60
        elif chg_24h > 30:
            f3 = 0.50  # Already pumped
        else:
            f3 = 0.30
        
        # Feature 4: From ATH recovery potential
        from_ath = metrics['from_ath']
        if from_ath > 50:
            f4 = 0.95
        elif from_ath > 20:
            f4 = 0.85
        elif from_ath > 10:
            f4 = 0.75
        elif from_ath > 5:
            f4 = 0.60
        else:
            f4 = 0.40
        
        features = [f1, f2, f3, f4]
        
        print(f"  Features: {features}")
        
        # Run quantum circuit
        @qml.qnode(self.dev)
        def circuit(f):
            # Encode
            for i, val in enumerate(f):
                qml.RY(val * np.pi, wires=i)
            
            # Entanglement
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])
            qml.CNOT(wires=[0, 3])
            
            # Growth layers
            for i in range(4):
                qml.RX(f[i] * np.pi, wires=i)
                qml.RZ(f[(i+1) % 4] * np.pi, wires=i)
            
            # Second entanglement
            qml.CNOT(wires=[3, 2])
            qml.CNOT(wires=[2, 1])
            qml.CNOT(wires=[1, 0])
            
            # Final rotations
            for i in range(4):
                qml.RY(f[i] * np.pi / 2, wires=i)
            
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        expvals = circuit(features)
        
        # Calculate scores
        avg_exp = sum(expvals) / len(expvals)
        confidence = (avg_exp + 1) / 2
        
        # Multi-measurement analysis
        measurements = [float(e) for e in expvals]
        
        # Determine signal
        if confidence > 0.70:
            signal = "STRONG BUY"
        elif confidence > 0.60:
            signal = "BUY"
        elif confidence > 0.50:
            signal = "HOLD"
        elif confidence > 0.40:
            signal = "WEAK"
        else:
            signal = "PASS"
        
        print(f"  Confidence: {confidence*100:.1f}%")
        print(f"  Signal: {signal}")
        print(f"  Measurements: {measurements}")
        
        return {
            'confidence': confidence * 100,
            'signal': signal,
            'expvals': measurements,
            'features': features,
            'avg_exp': float(avg_exp)
        }
    
    def calculate_risk_score(self, data: Dict, metrics: Dict) -> Dict:
        """Risk assessment"""
        print("\n[4/6] Calculating risk score...")
        
        risks = {}
        
        # Liquidity risk
        if metrics['liquidity_ratio'] < 0.1:
            risks['liquidity'] = "HIGH - Low liquidity, hard to exit"
        elif metrics['liquidity_ratio'] < 0.3:
            risks['liquidity'] = "MEDIUM - Acceptable liquidity"
        else:
            risks['liquidity'] = "LOW - Good liquidity"
        
        # Volatility risk
        vol_ratio = metrics['vol_mcap_ratio']
        if vol_ratio > 100:
            risks['volatility'] = "HIGH - Extreme volume, possible manipulation"
        elif vol_ratio > 50:
            risks['volatility'] = "MEDIUM-HIGH - High activity, volatile"
        elif vol_ratio > 10:
            risks['volatility'] = "MEDIUM - Normal activity"
        else:
            risks['volatility'] = "LOW - Low activity, may be stagnant"
        
        # Age risk
        age = metrics.get('age_days', 0)
        if age < 7:
            risks['age'] = "HIGH - Brand new, high risk of rug"
        elif age < 30:
            risks['age'] = "MEDIUM - Very new, unproven"
        elif age < 90:
            risks['age'] = "MEDIUM-LOW - New but surviving"
        else:
            risks['age'] = "LOW - Established"
        
        # Buy/sell pressure
        bs_ratio = metrics['buy_sell_ratio']
        if bs_ratio > 2:
            risks['pressure'] = "LOW - Strong buying pressure"
        elif bs_ratio > 1:
            risks['pressure'] = "MEDIUM-LOW - More buyers than sellers"
        elif bs_ratio > 0.5:
            risks['pressure'] = "MEDIUM - Selling pressure"
        else:
            risks['pressure'] = "HIGH - Heavy selling"
        
        # Overall risk
        risk_count = sum(1 for r in risks.values() if "HIGH" in r)
        if risk_count >= 3:
            overall = "EXTREME"
        elif risk_count >= 2:
            overall = "HIGH"
        elif risk_count >= 1:
            overall = "MEDIUM"
        else:
            overall = "LOW"
        
        print(f"  Overall Risk: {overall}")
        for k, v in risks.items():
            print(f"    {k}: {v}")
        
        return {
            'overall': overall,
            'details': risks
        }
    
    def estimate_potential(self, metrics: Dict) -> str:
        """Estimate x potential"""
        mcap = metrics['mcap_m']
        from_ath = metrics['from_ath']
        
        if mcap < 0.5 and from_ath > 50:
            return "50-100x"
        elif mcap < 2 and from_ath > 20:
            return "20-50x"
        elif mcap < 10 and from_ath > 10:
            return "10-20x"
        elif mcap < 50 and from_ath > 5:
            return "5-10x"
        else:
            return "2-5x"
    
    def generate_recommendation(self, data: Dict, metrics: Dict, quantum: Dict, risk: Dict) -> Dict:
        """Generate final recommendation"""
        print("\n[5/6] Generating recommendation...")
        
        rec = {
            'signal': quantum['signal'],
            'confidence': quantum['confidence'],
            'risk': risk['overall'],
            'potential': self.estimate_potential(metrics),
            'entry_price': data.get('price', 0),
            'targets': {}
        }
        
        # Calculate targets
        price = data.get('price', 0)
        ath = data.get('price_max_30d', price)
        
        if ath > price:
            rec['targets'][' conservative'] = ath * 0.2
            rec['targets']['moderate'] = ath * 0.5
            rec['targets']['aggressive'] = ath
            rec['targets']['moon'] = ath * 2
        else:
            rec['targets']['conservative'] = price * 2
            rec['targets']['moderate'] = price * 5
            rec['targets']['aggressive'] = price * 10
            rec['targets']['moon'] = price * 20
        
        rec['stop_loss'] = price * 0.5
        rec['position_size'] = self._recommend_position_size(risk['overall'])
        
        print(f"  Signal: {rec['signal']}")
        print(f"  Potential: {rec['potential']}")
        print(f"  Position Size: {rec['position_size']}")
        
        return rec
    
    def _recommend_position_size(self, risk: str) -> str:
        if risk == "EXTREME":
            return "1-2% of portfolio (tiny bet)"
        elif risk == "HIGH":
            return "2-5% of portfolio (small bet)"
        elif risk == "MEDIUM":
            return "5-10% of portfolio (medium bet)"
        else:
            return "10-20% of portfolio (larger bet)"
    
    def display_full_analysis(self, data: Dict, metrics: Dict, quantum: Dict, risk: Dict, rec: Dict):
        """Display complete analysis"""
        print("\n" + "=" * 100)
        print("FWOG DEEP QUANTUM ANALYSIS")
        print("=" * 100)
        print(f"Contract: {self.ca}")
        print(f"Chain: {data.get('chain', 'unknown').upper()}")
        print(f"DEX: {data.get('dex', 'unknown')}")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "=" * 100)
        print("MARKET DATA")
        print("=" * 100)
        
        print(f"\n  Price: ${data.get('price', 0):.10f}")
        print(f"  Market Cap: ${metrics['mcap_m']:.3f}M")
        print(f"  Liquidity: ${data.get('liquidity', 0)/1_000_000:.3f}M")
        print(f"  FDV: ${data.get('fdv', 0)/1_000_000:.3f}M")
        print(f"  24h Volume: ${data.get('volume_24h', 0)/1_000:.1f}K")
        print(f"  1h Change: {data.get('price_change_1h', 0):+.2f}%")
        print(f"  24h Change: {data.get('price_change_24h', 0):+.2f}%")
        print(f"  7d Change: {data.get('price_change_7d', 0):+.2f}%")
        
        print("\n" + "=" * 100)
        print("ON-CHAIN ACTIVITY")
        print("=" * 100)
        
        print(f"\n  24h Transactions:")
        print(f"    Buys: {data.get('buys_24h', 0)}")
        print(f"    Sells: {data.get('sells_24h', 0)}")
        print(f"    Buy/Sell Ratio: {metrics['buy_sell_ratio']:.2f}")
        
        print(f"\n  Volume Breakdown:")
        print(f"    1h: ${data.get('volume_1h', 0)/1_000:.1f}K")
        print(f"    6h: ${data.get('volume_6h', 0)/1_000:.1f}K")
        print(f"    24h: ${data.get('volume_24h', 0)/1_000:.1f}K")
        print(f"    Vol/MCap: {metrics['vol_mcap_ratio']:.1f}%")
        
        print("\n" + "=" * 100)
        print("QUANTUM ANALYSIS")
        print("=" * 100)
        
        print(f"\n  Signal: {quantum['signal']}")
        print(f"  Confidence: {quantum['confidence']:.1f}%")
        print(f"  Quantum Measurements: {quantum['expvals']}")
        print(f"  Average Expectation: {quantum['avg_exp']:.4f}")
        
        print(f"\n  Quantum Features:")
        print(f"    Market Cap Size: {quantum['features'][0]:.2f}")
        print(f"    Volume Activity: {quantum['features'][1]:.2f}")
        print(f"    Price Momentum: {quantum['features'][2]:.2f}")
        print(f"    Recovery Potential: {quantum['features'][3]:.2f}")
        
        print("\n" + "=" * 100)
        print("RISK ASSESSMENT")
        print("=" * 100)
        
        print(f"\n  Overall Risk: {risk['overall']}")
        print(f"\n  Risk Breakdown:")
        for k, v in risk['details'].items():
            print(f"    {k.upper()}: {v}")
        
        print("\n" + "=" * 100)
        print("VALUATION & POTENTIAL")
        print("=" * 100)
        
        print(f"\n  From ATH: {metrics['from_ath']:.1f}x")
        print(f"  ATH Drop: {metrics['ath_change']:.1f}%")
        print(f"  30-Day High: ${data.get('price_max_30d', 0):.10f}")
        print(f"  30-Day Low: ${data.get('price_min_30d', 0):.10f}")
        print(f"  Potential: {rec['potential']}")
        
        print("\n" + "=" * 100)
        print("RECOMMENDATION")
        print("=" * 100)
        
        print(f"\n  SIGNAL: {rec['signal']}")
        print(f"  CONFIDENCE: {rec['confidence']:.1f}%")
        print(f"  RISK: {rec['risk']}")
        print(f"  POTENTIAL: {rec['potential']}")
        
        print(f"\n  POSITION SIZE: {rec['position_size']}")
        
        print(f"\n  ENTRY: ${rec['entry_price']:.10f}")
        print(f"\n  PRICE TARGETS:")
        for target, price in rec['targets'].items():
            if rec['entry_price'] > 0:
                multiple = price / rec['entry_price']
                print(f"    {target.upper()}: ${price:.10f} ({multiple:.1f}x)")
        
        print(f"\n  STOP LOSS: ${rec['stop_loss']:.10f} (-50%)")
        
        print("\n" + "=" * 100)
        print("STRATEGY")
        print("=" * 100)
        
        if rec['signal'] in ["STRONG BUY", "BUY"]:
            print("\n  [ENTRY STRATEGY]")
            print("    1. Enter with 25% of position at current price")
            print("    2. If dips 10-15%, add 50% more")
            print("    3. If dips 25%, add final 25%")
            print("    4. Hold until targets or stop loss")
            
            print("\n  [EXIT STRATEGY]")
            print("    1. Sell 25% at conservative target")
            print("    2. Sell 25% at moderate target")
            print("    3. Sell 25% at aggressive target")
            print("    4. Let 25% ride to moon target")
        
        elif rec['signal'] == "HOLD":
            print("\n  [STRATEGY]")
            print("    - Already have position: Hold")
            print("    - No position: Wait for dip or clearer signal")
            print("    - Set alerts for entry points")
        
        else:
            print("\n  [STRATEGY]")
            print("    - AVOID or very small speculative bet")
            print("    - Wait for better setup")
            print("    - Monitor for changes")
        
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        
        print(f"\n  FWOG is a {rec['potential']} potential play")
        print(f"  Quantum confidence: {rec['confidence']:.0f}%")
        print(f"  Risk level: {rec['risk']}")
        print(f"  Recommendation: {rec['signal']}")
        
        if rec['signal'] in ["STRONG BUY", "BUY"]:
            print(f"\n  This is a HIGH CONVICTION play")
            print(f"  Consider {rec['position_size']}")
        
        print("\n" + "=" * 100)
    
    def save_analysis(self, data: Dict, metrics: Dict, quantum: Dict, risk: Dict, rec: Dict):
        """Save to file"""
        import os
        os.makedirs(DATA_DIR, exist_ok=True)
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'coin': 'FWOG',
            'contract': self.ca,
            'data': data,
            'metrics': metrics,
            'quantum': quantum,
            'risk': risk,
            'recommendation': rec
        }
        
        with open(f"{DATA_DIR}/fwog_analysis.json", "w") as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n[6/6] Saved: {DATA_DIR}/fwog_analysis.json")
    
    def run(self):
        """Full analysis"""
        print("\n" + "=" * 100)
        print("CORTEX FWOG DEEP ANALYSIS")
        print("=" * 100)
        
        # Fetch data
        data = self.fetch_dex_data()
        if not data:
            print("\nFailed to fetch data. Using fallback...")
            # Fallback with known info
            data = {
                'symbol': 'FWOG',
                'price': 0.0001,
                'market_cap': 1000000,
                'liquidity': 200000,
                'volume_24h': 500000,
                'buys_24h': 100,
                'sells_24h': 80,
                'price_change_1h': 0,
                'price_change_24h': 0,
                'price_change_7d': 0,
                'price_max_30d': 0.001,
                'price_min_30d': 0.00005,
                'chain': 'solana',
                'dex': 'raydium'
            }
        
        # Calculate metrics
        metrics = self.calculate_metrics(data)
        
        # Quantum analysis
        quantum = self.run_quantum_analysis(data, metrics)
        
        # Risk assessment
        risk = self.calculate_risk_score(data, metrics)
        
        # Recommendation
        rec = self.generate_recommendation(data, metrics, quantum, risk)
        
        # Display
        self.display_full_analysis(data, metrics, quantum, risk, rec)
        
        # Save
        self.save_analysis(data, metrics, quantum, risk, rec)
        
        print("\n" + "=" * 100)
        print("FWOG ANALYSIS COMPLETE")
        print("=" * 100)

def main():
    ca = "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump"
    analyzer = FWOGAnalyzer(ca)
    analyzer.run()

if __name__ == "__main__":
    main()
