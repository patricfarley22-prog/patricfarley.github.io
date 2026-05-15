#!/usr/bin/env python3
"""
FAST QUANTUM BACKTESTER
Pre-computes quantum signals then backtests
"""

import json
import os
from datetime import datetime

class FastQuantumBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
    
    def load_data(self, symbol):
        filepath = f'meme_coin_data/{symbol}_history.json'
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def simulate_signal(self, history, index):
        """Fast signal simulation based on historical patterns"""
        if index < 14:
            return 'HOLD', 0.3
        
        current = history[index]
        prev_7 = history[index - 7]
        prev_14 = history[index - 14]
        
        price = current['price']
        price_7d = prev_7['price']
        price_14d = prev_14['price']
        
        change_7d = ((price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        change_14d = ((price - price_14d) / price_14d * 100) if price_14d > 0 else 0
        
        # Volume analysis
        vol_now = current['volume']
        vol_avg = sum(h['volume'] for h in history[max(0, index-7):index]) / 7
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
        
        # Signal logic (simulating quantum behavior)
        signal = 'HOLD'
        confidence = 0.3
        
        # Strong momentum + volume = BUY
        if change_7d > 10 and vol_ratio > 1.5:
            signal = 'BUY'
            confidence = min(0.4 + (change_7d / 100), 0.6)
        
        # Strong downtrend + volume = SELL
        elif change_7d < -10 and vol_ratio > 1.5:
            signal = 'SELL'
            confidence = min(0.4 + (abs(change_7d) / 100), 0.6)
        
        # Mean reversion (down 14d, up 7d) = BUY
        elif change_14d < -20 and change_7d > 5:
            signal = 'BUY'
            confidence = 0.45
        
        # Mean reversion (up 14d, down 7d) = SELL
        elif change_14d > 20 and change_7d < -5:
            signal = 'SELL'
            confidence = 0.45
        
        # Consolidation breakout
        elif abs(change_7d) < 5 and vol_ratio > 2:
            signal = 'BUY'
            confidence = 0.4
        
        return signal, confidence
    
    def backtest(self, symbol, threshold=0.35):
        data = self.load_data(symbol)
        if not data or 'history' not in data:
            return None
        
        history = data['history']
        if len(history) < 30:
            return None
        
        capital = self.initial_capital
        position = 0
        trades = []
        equity = [capital]
        
        for i in range(14, len(history)):
            signal, confidence = self.simulate_signal(history, i)
            price = history[i]['price']
            
            if confidence >= threshold:
                if signal == 'BUY' and position == 0:
                    invest = capital * 0.25
                    shares = invest / price
                    position = shares
                    capital -= invest
                    trades.append({'type': 'BUY', 'price': price, 'shares': shares, 'value': invest, 'conf': confidence, 'day': i})
                
                elif signal == 'SELL' and position > 0:
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    capital += sell_val
                    trades.append({'type': 'SELL', 'price': price, 'shares': position, 'value': sell_val, 'pnl': pnl, 'pnl_pct': (pnl/trades[-1]['value'])*100, 'day': i})
                    position = 0
            
            equity.append(capital + (position * price))
        
        # Close position
        if position > 0:
            capital += position * history[-1]['price']
        
        final = capital
        ret = ((final - self.initial_capital) / self.initial_capital) * 100
        
        completed = [t for t in trades if t['type'] == 'SELL']
        wins = [t for t in completed if t.get('pnl', 0) > 0]
        
        peak = equity[0]
        max_dd = 0
        for v in equity:
            if v > peak: peak = v
            dd = (peak - v) / peak
            if dd > max_dd: max_dd = dd
        
        return {
            'symbol': symbol,
            'initial': self.initial_capital,
            'final': final,
            'return': ret,
            'trades': len(completed),
            'wins': len(wins),
            'losses': len(completed) - len(wins),
            'win_rate': (len(wins) / len(completed) * 100) if completed else 0,
            'max_dd': max_dd * 100,
            'trade_list': trades
        }
    
    def run(self, symbols):
        print("=" * 80)
        print("FAST QUANTUM BACKTESTER")
        print("=" * 80)
        
        results = []
        for symbol in symbols:
            print(f"\nBacktesting {symbol}...")
            r = self.backtest(symbol)
            if r:
                results.append(r)
                print(f"  Return: {r['return']:+.2f}% | Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}% | Max DD: {r['max_dd']:.2f}%")
                
                if r['trade_list']:
                    print("  Last 3 trades:")
                    for t in r['trade_list'][-3:]:
                        if t['type'] == 'SELL':
                            print(f"    SELL @ ${t['price']:.8f} | PnL: ${t['pnl']:+.2f}")
                        else:
                            print(f"    BUY @ ${t['price']:.8f} | Conf: {t['conf']*100:.0f}%")
        
        # Summary
        if results:
            print("\n" + "=" * 80)
            print("PORTFOLIO SUMMARY")
            print("=" * 80)
            
            avg_ret = sum(r['return'] for r in results) / len(results)
            avg_wr = sum(r['win_rate'] for r in results) / len(results)
            total_trades = sum(r['trades'] for r in results)
            
            print(f"Symbols: {len(results)} | Total Trades: {total_trades}")
            print(f"Avg Return: {avg_ret:+.2f}% | Avg Win Rate: {avg_wr:.1f}%")
            
            ranked = sorted(results, key=lambda x: x['return'], reverse=True)
            print("\nRanked by Return:")
            for i, r in enumerate(ranked, 1):
                print(f"{i}. {r['symbol']}: {r['return']:+.2f}% (Win Rate: {r['win_rate']:.1f}%, Trades: {r['trades']})")
        
        return results


if __name__ == "__main__":
    bt = FastQuantumBacktester(initial_capital=10000)
    bt.run(['BONK', 'FLOKI', 'PEPE', 'SHIB'])
