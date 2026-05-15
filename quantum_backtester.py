#!/usr/bin/env python3
"""
QUANTUM BACKTESTER
Tests quantum signals on historical meme coin data
Validates performance over time
"""

import json
import os
import math
import random
from datetime import datetime
from typing import List, Dict

DATA_DIR = "meme_coin_data"

class QuantumBacktester:
    """Backtest quantum signals on historical data"""
    
    def __init__(self, initial_capital=10000):
        self.initial = initial_capital
        self.reset()
    
    def reset(self):
        self.balance = self.initial
        self.positions = {}
        self.trades = []
        self.signals_generated = []
        self.equity_curve = [self.initial]
    
    def generate_quantum_signal(self, price_data: List[float], volume_data: List[float]) -> Dict:
        """Generate quantum signal from historical data"""
        if len(price_data) < 10:
            return {"signal": "HOLD", "confidence": 0.5}
        
        # Calculate metrics from history
        changes = [(price_data[i] - price_data[i-1]) / price_data[i-1] 
                   for i in range(1, len(price_data)) if price_data[i-1] > 0]
        
        if not changes:
            return {"signal": "HOLD", "confidence": 0.5}
        
        avg_change = sum(changes) / len(changes)
        volatility = (sum((c - avg_change)**2 for c in changes) / len(changes)) ** 0.5
        
        # Trend
        trend = (price_data[-1] - price_data[0]) / price_data[0] if price_data[0] > 0 else 0
        
        # Volume trend
        if volume_data and len(volume_data) > 1:
            vol_trend = (volume_data[-1] - volume_data[0]) / max(volume_data[0], 1)
        else:
            vol_trend = 0
        
        # Quantum features
        momentum = math.tanh(trend * 10)  # Trend strength
        vol_signal = math.tanh(vol_trend * 2)  # Volume momentum
        stability = math.exp(-volatility * 5)  # Inverse of volatility
        
        # Superposition
        superposition = momentum * 0.5 + vol_signal * 0.3 + stability * 0.2
        
        # Signal
        if superposition > 0.3 and trend > 0:
            signal = "BUY"
            confidence = min(0.9, 0.5 + superposition * 0.4)
        elif superposition < -0.2 and trend < 0:
            signal = "SELL"
            confidence = min(0.9, 0.5 + abs(superposition) * 0.4)
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "superposition": round(superposition, 3),
            "momentum": round(momentum, 3),
            "trend": round(trend, 3),
            "volatility": round(volatility, 4)
        }
    
    def backtest_coin(self, symbol: str, history: List[Dict], 
                     threshold=0.45, position_size=0.1, stop_loss=-0.15) -> Dict:
        """Backtest on single coin history"""
        self.reset()
        
        if len(history) < 20:
            return {"error": "Insufficient history"}
        
        prices = [h["price"] for h in history]
        volumes = [h.get("volume", 0) for h in history]
        
        trades = 0
        wins = 0
        
        for i in range(15, len(history) - 5):
            # Generate signal using last 15 days
            lookback = prices[max(0, i-15):i]
            vol_lookback = volumes[max(0, i-15):i]
            
            signal = self.generate_quantum_signal(lookback, vol_lookback)
            
            price = prices[i]
            next_price = prices[i+1]  # Price next day
            
            # Record signal
            self.signals_generated.append({
                "day": i,
                "signal": signal["signal"],
                "confidence": signal["confidence"],
                "price": price,
                "superposition": signal["superposition"]
            })
            
            # Execute if confidence > threshold
            if signal["confidence"] >= threshold:
                if signal["signal"] == "BUY" and symbol not in self.positions:
                    # Buy
                    invest = self.balance * position_size
                    if invest > 10:  # Min $10
                        shares = invest / price
                        self.balance -= invest
                        self.positions[symbol] = {
                            "entry": price,
                            "shares": shares,
                            "cost": invest,
                            "stop": price * (1 + stop_loss),
                            "day": i
                        }
                
                elif signal["signal"] == "SELL" and symbol in self.positions:
                    # Sell
                    pos = self.positions[symbol]
                    sell_val = pos["shares"] * next_price
                    pnl = sell_val - pos["cost"]
                    pnl_pct = (pnl / pos["cost"]) * 100
                    
                    self.balance += sell_val
                    self.trades.append({
                        "entry": pos["entry"],
                        "exit": next_price,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "days": i - pos["day"]
                    })
                    
                    if pnl > 0: wins += 1
                    trades += 1
                    del self.positions[symbol]
            
            # Check stop loss
            if symbol in self.positions:
                pos = self.positions[symbol]
                if next_price <= pos["stop"]:
                    sell_val = pos["shares"] * next_price
                    pnl = sell_val - pos["cost"]
                    pnl_pct = (pnl / pos["cost"]) * 100
                    
                    self.balance += sell_val
                    self.trades.append({
                        "entry": pos["entry"],
                        "exit": next_price,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "days": i - pos["day"],
                        "stop_hit": True
                    })
                    
                    trades += 1
                    del self.positions[symbol]
            
            # Update equity
            equity = self.balance
            if symbol in self.positions:
                equity += self.positions[symbol]["shares"] * next_price
            self.equity_curve.append(equity)
        
        # Close any open positions
        if self.positions:
            final_price = prices[-1]
            for sym, pos in list(self.positions.items()):
                sell_val = pos["shares"] * final_price
                pnl = sell_val - pos["cost"]
                pnl_pct = (pnl / pos["cost"]) * 100
                self.balance += sell_val
                self.trades.append({
                    "entry": pos["entry"],
                    "exit": final_price,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct
                })
                if pnl > 0: wins += 1
                trades += 1
        
        # Calculate metrics
        total_return = ((self.balance - self.initial) / self.initial) * 100
        
        if trades > 0:
            avg_pnl = sum(t["pnl_pct"] for t in self.trades) / trades
            win_rate = (wins / trades) * 100
            best = max(t["pnl_pct"] for t in self.trades)
            worst = min(t["pnl_pct"] for t in self.trades)
            avg_days = sum(t.get("days", 0) for t in self.trades) / trades
        else:
            avg_pnl = win_rate = best = worst = avg_days = 0
        
        # Max drawdown
        peak = self.initial
        max_dd = 0
        for e in self.equity_curve:
            if e > peak: peak = e
            dd = (peak - e) / peak
            if dd > max_dd: max_dd = dd
        
        return {
            "symbol": symbol,
            "initial": self.initial,
            "final": round(self.balance, 2),
            "total_return": round(total_return, 2),
            "trades": trades,
            "wins": wins,
            "win_rate": round(win_rate, 1),
            "avg_pnl": round(avg_pnl, 2),
            "best_trade": round(best, 1),
            "worst_trade": round(worst, 1),
            "avg_hold_days": round(avg_days, 1),
            "max_drawdown": round(max_dd * 100, 2),
            "signals_generated": len(self.signals_generated),
            "buy_signals": sum(1 for s in self.signals_generated if s["signal"] == "BUY"),
            "equity_curve": self.equity_curve
        }
    
    def display_result(self, result: Dict):
        """Display backtest result"""
        if "error" in result:
            print(f"  {result['error']}")
            return
        
        status = "PROFIT" if result["total_return"] > 0 else "LOSS"
        print(f"\n  {status}: {result['symbol']}")
        print(f"    Return: {result['total_return']:+.2f}%")
        print(f"    Trades: {result['trades']} (W: {result['wins']})")
        print(f"    Win Rate: {result['win_rate']:.1f}%")
        print(f"    Avg PnL: {result['avg_pnl']:+.2f}%")
        print(f"    Best: {result['best_trade']:+.1f}% | Worst: {result['worst_trade']:+.1f}%")
        print(f"    Avg Hold: {result['avg_hold_days']:.1f} days")
        print(f"    Max DD: {result['max_drawdown']:.2f}%")
        print(f"    Signals: {result['signals_generated']} (BUYs: {result['buy_signals']})")


def main():
    print("=" * 80)
    print("QUANTUM SIGNAL BACKTESTER")
    print("=" * 80)
    
    bt = QuantumBacktester(initial_capital=10000)
    
    # Load historical data
    coins_to_test = ["BONK", "FLOKI", "PEPE", "SHIB", "DOGE"]
    results = []
    
    for symbol in coins_to_test:
        filepath = os.path.join(DATA_DIR, f"{symbol}_history.json")
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)
                history = data.get("history", [])
            
            print(f"\nBacktesting {symbol} ({len(history)} days)...")
            result = bt.backtest_coin(symbol, history, threshold=0.45, position_size=0.2)
            bt.display_result(result)
            results.append(result)
        else:
            print(f"\n{symbol}: No history data")
    
    # Summary
    if results:
        print("\n" + "=" * 80)
        print("BACKTEST SUMMARY")
        print("=" * 80)
        
        total_trades = sum(r["trades"] for r in results if "trades" in r)
        total_return = sum(r["total_return"] for r in results if "total_return" in r) / len(results)
        avg_wr = sum(r["win_rate"] for r in results if "win_rate" in r) / len(results)
        
        print(f"\nTotal Coins: {len(results)}")
        print(f"Total Trades: {total_trades}")
        print(f"Avg Return: {total_return:+.2f}%")
        print(f"Avg Win Rate: {avg_wr:.1f}%")
        
        ranked = sorted(results, key=lambda x: x.get("total_return", 0), reverse=True)
        
        print(f"\nRanked:")
        print(f"{'#':<4} {'Symbol':<8} {'Return':<10} {'Trades':<8} {'Win%':<8} {'MaxDD':<8}")
        print("-" * 50)
        for i, r in enumerate(ranked, 1):
            if "symbol" in r:
                print(f"{i:<4} {r['symbol']:<8} {r['total_return']:<+9.1f}% {r['trades']:<8} {r['win_rate']:<7.1f}% {r['max_drawdown']:<7.1f}%")
        
        # Save
        with open(os.path.join(DATA_DIR, "quantum_backtest_results.json"), "w") as f:
            json.dump({
                "last": datetime.now().isoformat(),
                "config": {"initial": 10000, "threshold": 0.45, "position_size": 0.2, "stop_loss": -0.15},
                "summary": {"total_coins": len(results), "total_trades": total_trades, "avg_return": total_return, "avg_win_rate": avg_wr},
                "results": results
            }, f, indent=2)
        
        print(f"\nSaved to: meme_coin_data/quantum_backtest_results.json")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
