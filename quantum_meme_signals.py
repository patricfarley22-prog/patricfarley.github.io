#!/usr/bin/env python3
"""
QUANTUM SIGNALS FOR ALL 78 MEME COINS (BATCH MODE)
Fast batch processing using in-memory quantum calculations
"""

import json
import os
import math
from datetime import datetime

class QuantumMemeSignals:
    def __init__(self, data_dir="meme_coin_data"):
        self.data_dir = data_dir
        
    def load_coins(self):
        """Load all 78 coins"""
        filepath = os.path.join(self.data_dir, "low_cap_meme_coins.json")
        with open(filepath, "r") as f:
            data = json.load(f)
        return data["coins"]
    
    def calculate_quantum_signal(self, coin):
        """Calculate quantum-like signal using math (no subprocess)"""
        # Extract features
        change_24h = coin.get("price_change_percentage_24h", 0) or 0
        change_7d = coin.get("price_change_percentage_7d_in_currency", 0) or 0
        change_30d = coin.get("price_change_percentage_30d_in_currency", 0) or 0
        mcap = coin.get("market_cap", 0) or 1
        volume = coin.get("total_volume", 0) or 0
        ath_change = coin.get("ath_change_percentage", 0) or 0
        
        # Normalize features to -1 to +1 range (centered on neutral)
        features = {
            'price_change': math.tanh(change_24h / 20),  # 20% = near full scale
            'momentum_7d': math.tanh(change_7d / 50),     # 7-day momentum
            'momentum_30d': math.tanh(change_30d / 100),  # 30-day momentum
            'volume': math.tanh(volume / 100_000_000),    # Volume scale
            'mcap_size': 1 - math.tanh(mcap / 50_000_000),  # Small mcap = higher
            'ath_distance': -math.tanh(abs(ath_change) / 100),  # Far from ATH = negative
            'volatility': math.tanh(abs(change_7d) / 50),
            'liquidity': math.tanh(volume / mcap / 10),
        }
        
        # Calculate quantum-inspired metrics
        # Superposition: weighted average of features (now centered on 0)
        weights = {
            'price_change': 0.20,    # Short term price action
            'momentum_7d': 0.15,     # Medium momentum
            'momentum_30d': 0.10,    # Long term momentum
            'volume': 0.10,          # Volume
            'mcap_size': 0.10,       # Market cap size
            'ath_distance': 0.15,    # Distance from ATH
            'volatility': 0.10,      # Volatility
            'liquidity': 0.10        # Liquidity
        }
        
        # Quantum superposition (weighted sum, range -1 to +1)
        superposition = sum(weights[k] * features[k] for k in weights)
        
        # Entanglement (correlation strength between momentum and price)
        entanglement = abs(features['price_change'] * features['momentum_7d'])
        
        # Decoherence (uncertainty from volatility)
        decoherence = features['volatility'] * 0.5 + 0.1
        
        # Probability amplitudes based on superposition
        # Strong positive = BUY, strong negative = SELL, near 0 = HOLD
        buy_strength = max(0, superposition)
        sell_strength = max(0, -superposition)
        
        # Apply entanglement boost
        buy_prob = buy_strength * (0.3 + 0.7 * entanglement)
        sell_prob = sell_strength * (0.3 + 0.7 * entanglement)
        hold_prob = max(0.1, 1 - buy_prob - sell_prob)
        
        # Normalize
        total = buy_prob + sell_prob + hold_prob
        buy_prob /= total
        sell_prob /= total
        hold_prob /= total
        
        # Determine signal
        threshold = 0.35  # Need 35% confidence for signal
        
        if buy_prob > threshold and buy_prob > sell_prob and buy_prob > hold_prob:
            signal = "QUANTUM BUY"
            confidence = buy_prob
        elif sell_prob > threshold and sell_prob > buy_prob and sell_prob > hold_prob:
            signal = "QUANTUM SELL"
            confidence = sell_prob
        else:
            signal = "QUANTUM HOLD"
            confidence = hold_prob
        
        # Override for extreme conditions
        if change_30d > 200:
            signal = "QUANTUM SELL"  # Massively overextended
            confidence = min(0.6, confidence * 0.8)
        elif change_30d < -80:
            signal = "QUANTUM BUY"   # Massively oversold
            confidence = min(0.6, confidence * 0.8)
        
        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "entanglement": round(entanglement, 3),
            "superposition": round(superposition, 3),
            "decoherence": round(decoherence, 3),
            "probabilities": {
                "buy": round(buy_prob, 3),
                "sell": round(sell_prob, 3),
                "hold": round(hold_prob, 3)
            }
        }
    
    def _sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + math.exp(-max(-10, min(10, x))))
    
    def generate_all_signals(self):
        """Generate quantum signals for all coins"""
        print("=" * 80)
        print("QUANTUM SIGNALS FOR ALL 78 LOW-CAP MEME COINS")
        print("=" * 80)
        
        coins = self.load_coins()
        results = []
        
        for i, coin in enumerate(coins, 1):
            print(f"[{i}/78] {coin['symbol']}...", end=" ")
            
            quantum = self.calculate_quantum_signal(coin)
            
            result = {
                "rank": i,
                "symbol": coin["symbol"],
                "name": coin["name"],
                "market_cap": coin.get("market_cap", 0),
                "current_price": coin.get("current_price", 0),
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "price_change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                "price_change_30d": coin.get("price_change_percentage_30d_in_currency", 0),
                "ath_change": coin.get("ath_change_percentage", 0),
                **quantum,
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)
            
            arrow = "+" if "BUY" in result["signal"] else "-" if "SELL" in result["signal"] else "="
            print(f"{arrow} {result['signal']} ({result['confidence']*100:.1f}%)")
        
        return results
    
    def display_signals(self, results):
        """Display signals"""
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        print(f"\n{'='*80}")
        print("TOP QUANTUM SIGNALS (Ranked by Confidence)")
        print(f"{'='*80}")
        
        # BUY signals
        buys = [r for r in results if "BUY" in r["signal"]]
        if buys:
            print(f"\nBUY SIGNALS ({len(buys)} coins):")
            print(f"{'#':<4} {'Symbol':<8} {'Confidence':<12} {'Price':<14} {'24h':<8} {'7d':<8} {'30d':<8} {'Entangle':<10}")
            print("-" * 90)
            for i, r in enumerate(buys[:10], 1):
                print(f"{i:<4} {r['symbol']:<8} {r['confidence']*100:<11.1f}% ${r['current_price']:<13.8f} "
                      f"{r['price_change_24h'] or 0:<+7.1f}% {r['price_change_7d'] or 0:<+7.1f}% {r['price_change_30d'] or 0:<+7.1f}% {r['entanglement']:<10.3f}")
        
        # SELL signals
        sells = [r for r in results if "SELL" in r["signal"]]
        if sells:
            print(f"\nSELL SIGNALS ({len(sells)} coins):")
            print(f"{'#':<4} {'Symbol':<8} {'Confidence':<12} {'Price':<14} {'24h':<8} {'7d':<8} {'30d':<8} {'Entangle':<10}")
            print("-" * 90)
            for i, r in enumerate(sells[:10], 1):
                print(f"{i:<4} {r['symbol']:<8} {r['confidence']*100:<11.1f}% ${r['current_price']:<13.8f} "
                      f"{r['price_change_24h'] or 0:<+7.1f}% {r['price_change_7d'] or 0:<+7.1f}% {r['price_change_30d'] or 0:<+7.1f}% {r['entanglement']:<10.3f}")
        
        # HOLD signals
        holds = [r for r in results if "HOLD" in r["signal"]]
        if holds:
            print(f"\nHOLD SIGNALS ({len(holds)} coins):")
            print(f"{'#':<4} {'Symbol':<8} {'Confidence':<12} {'Price':<14} {'24h':<8} {'7d':<8} {'30d':<8} {'Entangle':<10}")
            print("-" * 90)
            for i, r in enumerate(holds[:10], 1):
                print(f"{i:<4} {r['symbol']:<8} {r['confidence']*100:<11.1f}% ${r['current_price']:<13.8f} "
                      f"{r['price_change_24h'] or 0:<+7.1f}% {r['price_change_7d'] or 0:<+7.1f}% {r['price_change_30d'] or 0:<+7.1f}% {r['entanglement']:<10.3f}")
        
        # Summary
        print(f"\n{'='*80}")
        print("QUANTUM SUMMARY")
        print(f"{'='*80}")
        print(f"BUY: {len(buys)} | SELL: {len(sells)} | HOLD: {len(holds)} | TOTAL: {len(results)}")
        print(f"Avg Confidence: {sum(r['confidence'] for r in results) / len(results) * 100:.1f}%")
        print(f"Avg Entanglement: {sum(r['entanglement'] for r in results) / len(results):.3f}")
        print(f"Avg Decoherence: {sum(r['decoherence'] for r in results) / len(results):.3f}")
    
    def save_signals(self, results):
        """Save signals to JSON"""
        filepath = os.path.join(self.data_dir, "quantum_meme_signals.json")
        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(results),
            "buy_count": sum(1 for r in results if "BUY" in r["signal"]),
            "sell_count": sum(1 for r in results if "SELL" in r["signal"]),
            "hold_count": sum(1 for r in results if "HOLD" in r["signal"]),
            "avg_confidence": round(sum(r["confidence"] for r in results) / len(results), 3),
            "avg_entanglement": round(sum(r["entanglement"] for r in results) / len(results), 3),
            "signals": results
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved to: {filepath}")
    
    def get_top_picks(self, results, min_confidence=0.40):
        """Get top trading picks"""
        picks = [r for r in results if r["confidence"] >= min_confidence]
        picks.sort(key=lambda x: x["confidence"], reverse=True)
        return picks[:10]


def main():
    generator = QuantumMemeSignals()
    
    # Generate all signals
    results = generator.generate_all_signals()
    
    # Display
    generator.display_signals(results)
    
    # Get top picks
    top_picks = generator.get_top_picks(results, min_confidence=0.40)
    
    if top_picks:
        print(f"\n{'='*80}")
        print("TOP PICKS (Confidence >= 40%)")
        print(f"{'='*80}")
        
        for i, pick in enumerate(top_picks, 1):
            action = "BUY" if "BUY" in pick["signal"] else "SELL" if "SELL" in pick["signal"] else "HOLD"
            print(f"\n{i}. {pick['symbol']} - {action}")
            print(f"   Price: ${pick['current_price']:.8f}")
            print(f"   Signal: {pick['signal']} ({pick['confidence']*100:.1f}% confidence)")
            print(f"   24h: {pick['price_change_24h'] or 0:+.1f}% | 7d: {pick['price_change_7d'] or 0:+.1f}% | 30d: {pick['price_change_30d'] or 0:+.1f}%")
            print(f"   ATH: {pick['ath_change']:.1f}% from all-time high")
            print(f"   Quantum: Entanglement={pick['entanglement']:.3f}, Decoherence={pick['decoherence']:.3f}")
            print(f"   Probabilities: BUY={pick['probabilities']['buy']*100:.1f}% SELL={pick['probabilities']['sell']*100:.1f}% HOLD={pick['probabilities']['hold']*100:.1f}%")
    
    # Save
    generator.save_signals(results)
    
    print(f"\n{'='*80}")
    print("QUANTUM SIGNAL GENERATION COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
