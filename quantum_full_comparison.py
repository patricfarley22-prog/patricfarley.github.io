#!/usr/bin/env python3
"""
QUANTUM FULL BACKEND COMPARISON
Runs all 3 backends on all 9+ coins
Generates consensus signals
"""

import json
import math
import random
import os
from datetime import datetime
from typing import List, Dict

# Quantum backends
try:
    import pennylane as qml
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

try:
    import dimod
    from dwave.system import DWaveSampler, EmbeddingComposite
    DWAVE_AVAILABLE = True
except ImportError:
    DWAVE_AVAILABLE = False

DATA_DIR = "meme_coin_data"

# All tracked coins
COINS = [
    {"symbol": "TROLL", "name": "Troll", "market_cap": 5800000, "price": 0.1157, "change_24h": -13.27, "change_7d": -20.0, "volume_24h": 6340000, "ca": "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2"},
    {"symbol": "DOWGE", "name": "Dowge", "market_cap": 3200000, "price": 0.00321, "change_24h": -5.34, "change_7d": -8.0, "volume_24h": 22000, "ca": "DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump"},
    {"symbol": "WOBBLES", "name": "Wobbles", "market_cap": 910000, "price": 0.00091, "change_24h": -19.49, "change_7d": -25.0, "volume_24h": 90000, "ca": "9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump"},
    {"symbol": "PENGO", "name": "Pengo", "market_cap": 590000, "price": 0.00059, "change_24h": -2.38, "change_7d": -5.0, "volume_24h": 12000, "ca": "F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump"},
    {"symbol": "TOKABU", "name": "Tokabu", "market_cap": 2410000, "price": 0.00241, "change_24h": -15.49, "change_7d": -20.0, "volume_24h": 153000, "ca": "H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump"},
    {"symbol": "OMEGAX", "name": "OmegaX", "market_cap": 360000, "price": 0.00036, "change_24h": -1.73, "change_7d": 0.0, "volume_24h": 3000, "ca": "4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump"},
    {"symbol": "HACHI", "name": "Hachi", "market_cap": 22000, "price": 0.000022, "change_24h": -2.90, "change_7d": -5.0, "volume_24h": 500, "ca": "AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh"},
    {"symbol": "MARMUS", "name": "Chad Marmus", "market_cap": 3651, "price": 0.00000365, "change_24h": -90.1, "change_7d": 0.0, "volume_24h": 166136, "ca": "ANfTyWJada5fhKffEX6PeoB486uKCHmuHdm"},
    {"symbol": "GIGA", "name": "GIGACHAD", "market_cap": 43700000, "price": 0.004550, "change_24h": -5.03, "change_7d": 0.0, "volume_24h": 1414240, "ca": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9"}
]

class FullQuantumComparison:
    def __init__(self):
        self.backends = {
            'pennylane': PENNYLANE_AVAILABLE,
            'qiskit': QISKIT_AVAILABLE,
            'dwave': DWAVE_AVAILABLE
        }
        
    def extract_features(self, coin: Dict) -> List[float]:
        chg_24h = coin.get('change_24h', 0)
        chg_7d = coin.get('change_7d', 0)
        mcap = coin.get('market_cap', 1)
        vol = coin.get('volume_24h', 0)
        
        momentum = math.tanh(chg_7d / 50) if chg_7d != 0 else 0
        volume_signal = math.tanh(vol / mcap) if mcap > 0 else 0
        volatility = math.exp(-abs(chg_24h) / 30)
        mcap_norm = math.tanh(mcap / 50_000_000)
        
        return [momentum, volume_signal, volatility, mcap_norm]
    
    def pennylane_result(self, features: List[float]) -> List[float]:
        if not PENNYLANE_AVAILABLE:
            return [random.uniform(-1, 1) for _ in range(4)]
        
        dev = qml.device("default.qubit", wires=4)
        
        @qml.qnode(dev)
        def circuit(x):
            for i in range(4):
                qml.RY(x[i] * math.pi, wires=i)
            for i in range(3):
                qml.CNOT(wires=[i, i+1])
            params = [random.uniform(-0.5, 0.5) for _ in range(8)]
            for i in range(4):
                qml.RX(params[i], wires=i)
                qml.RZ(params[i+4], wires=i)
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        return circuit(features)
    
    def qiskit_result(self, features: List[float]) -> List[float]:
        if not QISKIT_AVAILABLE:
            return [random.uniform(-1, 1) for _ in range(4)]
        
        qc = QuantumCircuit(4, 4)
        for i, f in enumerate(features):
            qc.ry(f * math.pi, i)
        for i in range(3):
            qc.cx(i, i+1)
        params = [random.uniform(-0.5, 0.5) for _ in range(8)]
        for i in range(4):
            qc.rx(params[i], i)
            qc.rz(params[i+4], i)
        qc.measure_all()
        
        simulator = AerSimulator()
        transpiled = transpile(qc, simulator)
        job = simulator.run(transpiled, shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        expectations = []
        for i in range(4):
            exp_val = 0
            for bitstring, count in counts.items():
                bit = int(bitstring[3-i])
                exp_val += (1 if bit == 0 else -1) * count / 1024
            expectations.append(exp_val)
        
        return expectations
    
    def dwave_result(self, features: List[float]) -> List[float]:
        if not DWAVE_AVAILABLE:
            return [random.uniform(-1, 1) for _ in range(4)]
        
        try:
            bqm = dimod.BinaryQuadraticModel(
                {i: features[i] for i in range(4)},
                {(i, j): 0.1 for i in range(4) for j in range(i+1, 4)},
                'BINARY'
            )
            sampler = dimod.SimulatedAnnealingSampler()
            sampleset = sampler.sample(bqm, num_reads=100)
            best = sampleset.first.sample
            return [best[i] * 2 - 1 for i in range(4)]
        except:
            return [random.uniform(-1, 1) for _ in range(4)]
    
    def run_backend(self, backend: str, features: List[float]) -> Dict:
        if backend == 'pennylane':
            result = self.pennylane_result(features)
        elif backend == 'qiskit':
            result = self.qiskit_result(features)
        elif backend == 'dwave':
            result = self.dwave_result(features)
        else:
            result = [random.uniform(-1, 1) for _ in range(4)]
        
        trend = result[0]
        vol_conf = result[1]
        risk = result[2]
        stability = result[3]
        
        combined = trend * 0.3 + vol_conf * 0.25 + stability * 0.25 - risk * 0.2
        
        if combined > 0.3 and trend > 0:
            signal = "BUY"
            confidence = min(0.9, 0.5 + combined * 0.4)
        elif combined < -0.3 and trend < 0:
            signal = "SELL"
            confidence = min(0.9, 0.5 + abs(combined) * 0.4)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return {
            'signal': str(signal),
            'confidence': float(confidence),
            'score': float(combined),
            'trend': float(trend),
            'volume_conf': float(vol_conf),
            'risk': float(risk),
            'stability': float(stability)
        }
    
    def analyze_coin(self, coin: Dict) -> Dict:
        features = self.extract_features(coin)
        
        results = {}
        for backend, available in self.backends.items():
            if available:
                results[backend] = self.run_backend(backend, features)
        
        # Consensus
        signals = [r['signal'] for r in results.values()]
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        hold_count = signals.count('HOLD')
        
        if buy_count >= 2:
            consensus = 'STRONG_BUY' if buy_count == 3 else 'BUY'
        elif sell_count >= 2:
            consensus = 'STRONG_SELL' if sell_count == 3 else 'SELL'
        elif buy_count == 1 and hold_count == 2:
            consensus = 'WEAK_BUY'
        elif sell_count == 1 and hold_count == 2:
            consensus = 'WEAK_SELL'
        else:
            consensus = 'HOLD'
        
        avg_score = sum(r['score'] for r in results.values()) / len(results)
        avg_conf = sum(r['confidence'] for r in results.values()) / len(results)
        
        return {
            'symbol': coin['symbol'],
            'name': coin['name'],
            'ca': coin.get('ca', ''),
            'market_cap': coin['market_cap'],
            'price': coin['price'],
            'change_24h': coin['change_24h'],
            'change_7d': coin['change_7d'],
            'volume_24h': coin['volume_24h'],
            'backends': results,
            'consensus': consensus,
            'consensus_score': round(avg_score, 3),
            'consensus_confidence': round(avg_conf, 3),
            'agreement': f"{buy_count}B/{sell_count}S/{hold_count}H"
        }
    
    def run_all(self) -> List[Dict]:
        print("=" * 80)
        print("FULL QUANTUM BACKEND COMPARISON")
        print("=" * 80)
        print(f"\nBackends: {', '.join(k for k,v in self.backends.items() if v)}")
        print(f"Coins: {len(COINS)}")
        print(f"\n{'='*80}")
        
        results = []
        for coin in COINS:
            print(f"\nAnalyzing {coin['symbol']}...")
            result = self.analyze_coin(coin)
            results.append(result)
            
            for backend, data in result['backends'].items():
                print(f"  {backend:12s}: {data['signal']:5s} {data['confidence']:4.0%} (Score: {data['score']:+.3f})")
            print(f"  CONSENSUS:  {result['consensus']} {result['consensus_confidence']:.0%}")
        
        # Sort by consensus score
        results.sort(key=lambda x: x['consensus_score'], reverse=True)
        
        return results
    
    def display_full(self, results: List[Dict]):
        print("\n" + "=" * 80)
        print("CONSENSUS RESULTS")
        print("=" * 80)
        
        # Full comparison table
        print(f"\n{'#':<4} {'Symbol':<8} {'PennyLane':<12} {'Qiskit':<12} {'D-Wave':<12} {'Consensus':<12} {'Score':<8} {'Conf':<8}")
        print("-" * 80)
        
        for i, r in enumerate(results, 1):
            pl = r['backends'].get('pennylane', {})
            qi = r['backends'].get('qiskit', {})
            dw = r['backends'].get('dwave', {})
            
            pl_str = f"{pl.get('signal', 'N/A')} {pl.get('confidence', 0):.0%}" if pl else "N/A"
            qi_str = f"{qi.get('signal', 'N/A')} {qi.get('confidence', 0):.0%}" if qi else "N/A"
            dw_str = f"{dw.get('signal', 'N/A')} {dw.get('confidence', 0):.0%}" if dw else "N/A"
            
            print(f"{i:<4} {r['symbol']:<8} {pl_str:<12} {qi_str:<12} {dw_str:<12} {r['consensus']:<12} {r['consensus_score']:<7.2f} {r['consensus_confidence']:<7.0%}")
        
        # Strong signals
        strong = [r for r in results if r['consensus'] in ['STRONG_BUY', 'STRONG_SELL']]
        if strong:
            print(f"\n{'='*80}")
            print(f"STRONG CONSENSUS: {len(strong)}")
            print(f"{'='*80}")
            for r in strong:
                print(f"\n  {r['symbol']} - {r['name']}")
                print(f"    Consensus: {r['consensus']} ({r['consensus_confidence']:.0%})")
                print(f"    Score: {r['consensus_score']:.3f}")
                print(f"    Price: ${r['price']:.8f}")
                print(f"    MCap: ${r['market_cap']/1_000_000:.2f}M")
                print(f"    24h: {r['change_24h']:+.1f}% | 7d: {r['change_7d']:+.1f}%")
                print(f"    Agreement: {r['agreement']}")
                for backend, data in r['backends'].items():
                    print(f"    {backend}: {data['signal']} {data['confidence']:.0%}")
        
        # Buys
        buys = [r for r in results if 'BUY' in r['consensus']]
        if buys:
            print(f"\n{'='*80}")
            print(f"BUY SIGNALS: {len(buys)}")
            print(f"{'='*80}")
            for r in buys:
                print(f"  {r['symbol']}: {r['consensus']} ({r['consensus_confidence']:.0%})")
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        
        consensus_counts = {}
        for r in results:
            c = r['consensus']
            consensus_counts[c] = consensus_counts.get(c, 0) + 1
        
        for c, count in sorted(consensus_counts.items(), key=lambda x: -x[1]):
            print(f"  {c}: {count} coins")
        
        print(f"\n  Total: {len(results)} coins analyzed")
        print(f"  Backends: {sum(self.backends.values())}")
    
    def save(self, results: List[Dict]):
        os.makedirs(DATA_DIR, exist_ok=True)
        
        with open(f"{DATA_DIR}/quantum_full_comparison.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "backends": {k: v for k, v in self.backends.items()},
                "count": len(results),
                "results": results
            }, f, indent=2)
        
        print(f"\nSaved: {DATA_DIR}/quantum_full_comparison.json")

def main():
    print("Quantum Full Comparison")
    print("=" * 80)
    
    analyzer = FullQuantumComparison()
    results = analyzer.run_all()
    analyzer.display_full(results)
    analyzer.save(results)
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
