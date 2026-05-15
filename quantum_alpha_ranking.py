#!/usr/bin/env python3
"""
ALPHA HUNTER v2.1 - With Full Quantum Analysis
Runs top 10 through PennyLane quantum circuit for final ranking
"""

import requests
import json
import math
import time
from datetime import datetime
from typing import Dict, List

# Quantum
import pennylane as qml
from pennylane import numpy as np

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"

class QuantumAlphaAnalyzer:
    """Quantum-enhanced alpha analyzer"""
    
    def __init__(self):
        self.dev = qml.device("default.qubit", wires=4, shots=1000)
        self.results = []
    
    def run_quantum(self, features):
        """Run quantum circuit"""
        @qml.qnode(self.dev)
        def circuit(f):
            for i, val in enumerate(f[:4]):
                qml.RY(val * np.pi, wires=i)
            
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])
            
            for i in range(4):
                qml.RX(f[i % len(f)] * np.pi, wires=i)
                qml.RZ(f[(i+1) % len(f)] * np.pi, wires=i)
            
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        return circuit(features)
    
    def analyze_coin(self, coin: Dict) -> Dict:
        """Run quantum analysis on single coin"""
        symbol = coin['symbol']
        
        # Build features
        mcap_norm = min(1.0, coin['market_cap'] / 100_000_000)
        volume_norm = min(1.0, coin.get('volume_mcap_ratio', 0) / 100)
        momentum_norm = (coin['change_24h'] + 50) / 100  # -50 to +50 mapped to 0-1
        trend_norm = (coin['change_7d'] + 50) / 100
        
        features = [mcap_norm, volume_norm, momentum_norm, trend_norm]
        
        try:
            # Run quantum circuit
            expvals = self.run_quantum(features)
            
            # Calculate confidence
            avg_exp = sum(expvals) / len(expvals)
            confidence = (avg_exp + 1) / 2  # Map from [-1,1] to [0,1]
            
            # Determine signal
            if confidence > 0.65:
                signal = "STRONG BUY"
            elif confidence > 0.55:
                signal = "BUY"
            elif confidence > 0.45:
                signal = "HOLD"
            else:
                signal = "SELL"
            
            return {
                'symbol': symbol,
                'confidence': confidence * 100,
                'signal': signal,
                'quantum_score': confidence,
                'expvals': [float(e) for e in expvals],
                'features': features,
                'success': True
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'confidence': 50.0,
                'signal': "HOLD",
                'error': str(e),
                'success': False
            }

def load_top10() -> List[Dict]:
    """Load top 10 from alpha hunter results"""
    try:
        with open(f"{DATA_DIR}/alpha_hunter_results.json", "r") as f:
            data = json.load(f)
            return data.get('top_10', [])
    except:
        print("No previous results found")
        return []

def display_quantum_results(results: List[Dict]):
    """Display quantum-ranked results"""
    print("\n" + "=" * 90)
    print("QUANTUM ALPHA RANKING - FINAL RESULTS")
    print("=" * 90)
    
    # Sort by quantum confidence
    ranked = sorted(results, key=lambda x: x.get('quantum_confidence', 0), reverse=True)
    
    print("\n{:<4} {:<10} {:<20} {:<12} {:<12} {:<12} {:<12}".format(
        "#", "Symbol", "Name", "Score", "Quantum", "Signal", "Potential"))
    print("-" * 90)
    
    for i, r in enumerate(ranked[:10], 1):
        coin = r.get('coin', {})
        symbol = coin.get('symbol', 'N/A')
        name = coin.get('name', 'Unknown')
        score = r.get('total_score', 0)
        quantum = r.get('quantum_confidence', 0) * 100
        signal = r.get('quantum_signal', 'HOLD')
        
        # Potential calculation
        mcap = coin.get('market_cap', 0)
        if mcap < 20_000_000:
            potential = "HIGH"
        elif mcap < 50_000_000:
            potential = "MEDIUM"
        else:
            potential = "LOW"
        
        print("{:<4} {:<10} {:<20} {:<12.1f} {:<12.1f}% {:<12} {:<12}".format(
            i, symbol, name[:18], score, quantum, signal, potential))
    
    # Top pick analysis
    if ranked:
        top = ranked[0]
        coin = top.get('coin', {})
        print(f"\n{'='*90}")
        print("TOP PICK: {}".format(coin.get('symbol', 'N/A')))
        print(f"{'='*90}")
        print(f"  Name: {coin.get('name', 'Unknown')}")
        print(f"  Market Cap: ${coin.get('market_cap', 0)/1_000_000:.2f}M")
        print(f"  Price: ${coin.get('price', 0):.6f}")
        print(f"  24h: {coin.get('change_24h', 0):+.1f}%")
        print(f"  Score: {top.get('total_score', 0):.1f}/100")
        print(f"  Quantum Confidence: {top.get('quantum_confidence', 0)*100:.1f}%")
        print(f"  Signal: {top.get('quantum_signal', 'HOLD')}")
        
        if 'quantum_expvals' in top:
            print(f"  Quantum Measurements: {[f'{e:.3f}' for e in top['quantum_expvals']]}")
        
        reasons = []
        if coin.get('change_24h', 0) > 10:
            reasons.append("Strong momentum (+10%+ today)")
        if coin.get('volume_mcap_ratio', 0) > 50:
            reasons.append("Very high volume activity")
        elif coin.get('volume_mcap_ratio', 0) > 20:
            reasons.append("High volume activity")
        if coin.get('market_cap', 0) < 20_000_000:
            reasons.append("Small cap = high upside")
        if coin.get('change_24h', 0) < -5:
            reasons.append("Dip buy opportunity")
        
        print(f"\n  Why it won:")
        for r in reasons:
            print(f"    - {r}")
    
    print(f"\n{'='*90}")

def save_results(results: List[Dict]):
    """Save quantum results"""
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(f"{DATA_DIR}/quantum_alpha_ranking.json", "w") as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'ranking': results
        }, f, indent=2, default=str)
    
    print(f"Saved: {DATA_DIR}/quantum_alpha_ranking.json")

def main():
    print("\n" + "=" * 90)
    print("QUANTUM ALPHA RANKING v2.1")
    print("=" * 90)
    
    # Load top 10 from alpha hunter
    top10 = load_top10()
    if not top10:
        print("Run alpha_hunter_v2.py first!")
        return
    
    print(f"Loaded {len(top10)} coins from Alpha Hunter")
    
    # Initialize quantum analyzer
    qa = QuantumAlphaAnalyzer()
    
    # Run quantum on each
    results = []
    for coin in top10:
        print(f"\nAnalyzing {coin['symbol']}...")
        q_result = qa.analyze_coin(coin)
        
        # Merge with alpha data
        combined = {
            'coin': coin,
            'total_score': coin.get('total_score', 0),
            'quantum_confidence': q_result['confidence'] / 100,
            'quantum_signal': q_result['signal'],
            'quantum_expvals': q_result.get('expvals', []),
            'quantum_features': q_result.get('features', [])
        }
        
        results.append(combined)
        
        print(f"  Quantum: {q_result['signal']} {q_result['confidence']:.1f}%")
    
    # Display
    display_quantum_results(results)
    
    # Save
    save_results(results)
    
    print("\n" + "=" * 90)
    print("QUANTUM RANKING COMPLETE")
    print("=" * 90)

if __name__ == "__main__":
    main()
