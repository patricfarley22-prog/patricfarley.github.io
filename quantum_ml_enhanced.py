#!/usr/bin/env python3
"""
QUANTUM ML ENHANCED
Machine learning to improve quantum signal confidence
Uses historical performance to weight quantum features
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List

DATA_DIR = "meme_coin_data"

class QuantumMLEnhancer:
    """ML-enhanced quantum confidence"""
    
    def __init__(self):
        self.weights = {
            "momentum": 0.25,
            "volume": 0.20,
            "volatility": 0.15,
            "coherence": 0.20,
            "entanglement": 0.10,
            "decoherence": 0.10
        }
        self.performance_history = []
        self.load_weights()
    
    def load_weights(self):
        """Load learned weights from history"""
        f = os.path.join(DATA_DIR, "quantum_ml_weights.json")
        if os.path.exists(f):
            with open(f) as fh:
                data = json.load(fh)
                self.weights = data.get("weights", self.weights)
                self.performance_history = data.get("history", [])
    
    def save_weights(self):
        """Save learned weights"""
        f = os.path.join(DATA_DIR, "quantum_ml_weights.json")
        with open(f, "w") as fh:
            json.dump({
                "weights": self.weights,
                "history": self.performance_history[-100:],  # Keep last 100
                "last_updated": datetime.now().isoformat()
            }, fh, indent=2)
    
    def calculate_features(self, coin: Dict) -> Dict:
        """Calculate quantum features"""
        chg_24h = coin.get("change_24h", 0)
        chg_7d = coin.get("change_7d", 0)
        vol = coin.get("volume_24h", 0)
        mcap = coin.get("market_cap", 1)
        
        # Feature 1: Momentum (normalized)
        momentum = math.tanh(chg_7d / 50) if chg_7d != 0 else 0
        
        # Feature 2: Volume intensity
        volume = math.tanh(vol / mcap) if mcap > 0 else 0
        
        # Feature 3: Volatility (inverse)
        volatility = math.exp(-abs(chg_24h) / 30)
        
        # Feature 4: Coherence (trend consistency)
        coherence = 1.0 if chg_7d * chg_24h > 0 else 0.5
        
        # Feature 5: Entanglement (market correlation)
        entanglement = 1.0 - abs(math.tanh(chg_24h / 20))  # Inverse correlation
        
        # Feature 6: Decoherence (stability)
        decoherence = math.exp(-abs(chg_24h - chg_7d/7) / 10)
        
        return {
            "momentum": momentum,
            "volume": volume,
            "volatility": volatility,
            "coherence": coherence,
            "entanglement": entanglement,
            "decoherence": decoherence
        }
    
    def ml_confidence(self, coin: Dict) -> Dict:
        """Calculate ML-enhanced confidence"""
        features = self.calculate_features(coin)
        
        # Weighted sum (ML-enhanced)
        weighted_score = sum(
            features[key] * self.weights[key] for key in features
        )
        
        # Historical adjustment (if we have history)
        if self.performance_history:
            # Adjust based on past performance of similar features
            similar = [h for h in self.performance_history[-50:] 
                      if abs(h.get("momentum", 0) - features["momentum"]) < 0.2]
            if similar:
                avg_pnl = sum(h.get("pnl", 0) for h in similar) / len(similar)
                # Adjust confidence based on historical PnL
                if avg_pnl > 0:
                    weighted_score *= (1 + avg_pnl / 100)
                elif avg_pnl < 0:
                    weighted_score *= (1 + avg_pnl / 200)
        
        # Normalize to 0-1
        confidence = min(0.95, max(0.05, weighted_score))
        
        # Signal
        if confidence > 0.6 and features["momentum"] > 0:
            signal = "BUY"
        elif confidence > 0.6 and features["momentum"] < 0:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {
            "symbol": coin.get("symbol", "UNK"),
            "signal": signal,
            "ml_confidence": round(confidence, 3),
            "quantum_confidence": round(confidence, 3),  # Combined
            "features": {k: round(v, 3) for k, v in features.items()},
            "weights": {k: round(v, 3) for k, v in self.weights.items()},
            "score": round(weighted_score, 3)
        }
    
    def learn_from_result(self, prediction: Dict, actual_pnl: float):
        """Learn from trade result and adjust weights"""
        # Record performance
        self.performance_history.append({
            **prediction.get("features", {}),
            "signal": prediction.get("signal"),
            "confidence": prediction.get("ml_confidence"),
            "pnl": actual_pnl,
            "timestamp": datetime.now().isoformat()
        })
        
        # Adjust weights (simple gradient descent)
        if len(self.performance_history) > 10:
            recent = self.performance_history[-10:]
            profitable = [r for r in recent if r.get("pnl", 0) > 0]
            losing = [r for r in recent if r.get("pnl", 0) <= 0]
            
            if profitable and losing:
                # Increase weights that were high in profitable trades
                for key in self.weights:
                    avg_prof = sum(r.get(key, 0) for r in profitable) / len(profitable)
                    avg_loss = sum(r.get(key, 0) for r in losing) / len(losing)
                    
                    if avg_prof > avg_loss:
                        self.weights[key] = min(0.5, self.weights[key] * 1.05)
                    elif avg_prof < avg_loss:
                        self.weights[key] = max(0.05, self.weights[key] * 0.95)
                
                # Normalize
                total = sum(self.weights.values())
                self.weights = {k: v/total for k, v in self.weights.items()}
        
        self.save_weights()
    
    def scan_coins(self, coins: List[Dict]) -> List[Dict]:
        """Scan with ML-enhanced confidence"""
        print("=" * 80)
        print("QUANTUM ML ENHANCED SCANNER")
        print("=" * 80)
        print("\nML Features:")
        print("  - Adaptive weights based on performance")
        print("  - Historical pattern matching")
        print("  - Confidence calibration")
        print("=" * 80)
        
        results = []
        for coin in coins:
            result = self.ml_confidence(coin)
            results.append(result)
        
        # Sort by confidence
        results.sort(key=lambda x: x["ml_confidence"], reverse=True)
        return results
    
    def display(self, results: List[Dict]):
        """Display ML-enhanced results"""
        print(f"\n{'#':<4} {'Symbol':<10} {'Signal':<10} {'ML Conf':<10} {'Score':<8} {'Momentum':<10} {'Volume':<8} {'Coherence':<10}")
        print("-" * 80)
        
        for i, r in enumerate(results[:10], 1):
            f = r["features"]
            print(f"{i:<4} {r['symbol']:<10} {r['signal']:<10} {r['ml_confidence']:<9.1%} {r['score']:<7.2f} "
                  f"{f['momentum']:<9.2f} {f['volume']:<7.2f} {f['coherence']:<9.2f}")
        
        # High confidence picks
        high = [r for r in results if r["ml_confidence"] > 0.6]
        if high:
            print(f"\n{'='*80}\nHIGH CONFIDENCE PICKS: {len(high)}\n{'='*80}")
            for r in high:
                print(f"\n  {r['symbol']}: {r['signal']} ({r['ml_confidence']*100:.0f}%)")
                print(f"    Features: {r['features']}")
                print(f"    Weights: {r['weights']}")
        
        # Current learned weights
        print(f"\n{'='*80}")
        print("LEARNED WEIGHTS (Performance-Optimized)")
        print(f"{'='*80}")
        for key, val in sorted(self.weights.items(), key=lambda x: -x[1]):
            bar = "#" * int(val * 20)
            print(f"  {key:15s} {val:.3f} {bar}")
        
        print(f"\nTrades in history: {len(self.performance_history)}")


def main():
    enhancer = QuantumMLEnhancer()
    
    test_coins = [
        {"symbol": "TROLL", "change_24h": -13.27, "change_7d": -20.0, "volume_24h": 6340000, "market_cap": 5800000},
        {"symbol": "DOWGE", "change_24h": -5.34, "change_7d": -8.0, "volume_24h": 22000, "market_cap": 3200000},
        {"symbol": "WOBBLES", "change_24h": -19.49, "change_7d": -25.0, "volume_24h": 90000, "market_cap": 910000},
        {"symbol": "PENGO", "change_24h": -2.38, "change_7d": -5.0, "volume_24h": 12000, "market_cap": 590000},
        {"symbol": "TOKABU", "change_24h": -15.49, "change_7d": -20.0, "volume_24h": 153000, "market_cap": 2410000},
        {"symbol": "OMEGAX", "change_24h": -1.73, "change_7d": 0.0, "volume_24h": 3000, "market_cap": 360000},
        {"symbol": "HACHI", "change_24h": -2.90, "change_7d": -5.0, "volume_24h": 500, "market_cap": 22000}
    ]
    
    results = enhancer.scan_coins(test_coins)
    enhancer.display(results)
    
    # Save
    with open(os.path.join(DATA_DIR, "quantum_ml_results.json"), "w") as f:
        json.dump({"last": datetime.now().isoformat(), "count": len(results), "results": results}, f, indent=2)
    
    print(f"\n{'='*80}")
    print("QUANTUM ML COMPLETE")
    print(f"{'='*80}")
    print(f"\nTo use in trading:")
    print("  prediction = enhancer.ml_confidence(coin)")
    print("  if prediction['ml_confidence'] > 0.6:")
    print("      # Execute trade")
    print("  # Later, after trade closes:")
    print("  enhancer.learn_from_result(prediction, actual_pnl)")

if __name__ == "__main__":
    main()
