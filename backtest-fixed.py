#!/usr/bin/env python3
"""
FIXED QUANTUM BACKTESTER
Lower confidence threshold + better signal generation = actual trades
"""

import json
import os

class FixedQuantumBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
    
    def load_data(self, symbol):
        filepath = f'meme_coin_data/{symbol}_history.json'
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def generate_signal(self, history, index):
        """Generate quantum-like signal with lower threshold"""
        if index < 14:
            return 'HOLD', 0.25
        
        current = history[index]
        price = current['price']
        
        # Lookback prices
        price_1d = history[index-1]['price']
        price_3d = history[index-3]['price']
        price_7d = history[index-7]['price']
        price_14d = history[index-14]['price']
        
        # Calculate returns
        ret_1d = ((price - price_1d) / price_1d * 100) if price_1d > 0 else 0
        ret_3d = ((price - price_3d) / price_3d * 100) if price_3d > 0 else 0
        ret_7d = ((price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        ret_14d = ((price - price_14d) / price_14d * 100) if price_14d > 0 else 0
        
        # Volume analysis
        vol_now = current['volume']
        vol_avg_7 = sum(h['volume'] for h in history[max(0,index-7):index]) / 7
        vol_ratio = vol_now / vol_avg_7 if vol_avg_7 > 0 else 1
        
        # Momentum score (-1 to 1)
        momentum = (ret_7d + ret_3d/2 + ret_1d/4) / 20  # Normalize
        momentum = max(-1, min(1, momentum))
        
        # Trend strength
        trend_up = ret_14d > 0 and ret_7d > 0
        trend_down = ret_14d < 0 and ret_7d < 0
        
        # Mean reversion
        oversold = ret_14d < -30 and ret_7d > -5  # Down long, stabilizing
        overbought = ret_14d > 50 and ret_7d < 5   # Up long, slowing
        
        # Signal generation
        signal = 'HOLD'
        confidence = 0.25
        
        # BUY signals
        if oversold and vol_ratio > 1.2:
            signal = 'BUY'
            confidence = 0.35 + abs(ret_14d) / 100
        elif trend_up and vol_ratio > 1.5 and ret_1d > 0:
            signal = 'BUY'
            confidence = 0.35 + ret_7d / 50
        elif ret_7d > 15 and ret_1d > 0:
            signal = 'BUY'
            confidence = 0.4 + ret_7d / 100
        
        # SELL signals
        elif overbought and vol_ratio > 1.2:
            signal = 'SELL'
            confidence = 0.35 + abs(ret_14d) / 100
        elif trend_down and vol_ratio > 1.5 and ret_1d < 0:
            signal = 'SELL'
            confidence = 0.35 + abs(ret_7d) / 50
        elif ret_7d < -15 and ret_1d < 0:
            signal = 'SELL'
            confidence = 0.4 + abs(ret_7d) / 100
        
        # Breakout signals
        elif abs(ret_1d) > 5 and vol_ratio > 2:
            signal = 'BUY' if ret_1d > 0 else 'SELL'
            confidence = 0.35 + abs(ret_1d) / 50
        
        # Volume spike without price move = potential reversal
        elif vol_ratio > 3 and abs(ret_1d) < 2:
            signal = 'BUY' if ret_7d < 0 else 'SELL'
            confidence = 0.35
        
        confidence = min(0.6, confidence)
        return signal, confidence
    
    def backtest(self, symbol, threshold=0.30, position_size=0.25):
        """Backtest with configurable threshold"""
        data = self.load_data(symbol)
        if not data or 'history' not in data:
            return None
        
        history = data['history']
        if len(history) < 30:
            return None
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity = [capital]
        
        print(f"\nBacktesting {symbol}...")
        print(f"  Threshold: {threshold*100:.0f}% | Position: {position_size*100:.0f}%")
        
        for i in range(14, len(history)):
            signal, confidence = self.generate_signal(history, i)
            price = history[i]['price']
            date = history[i]['date']
            
            # Execute trade
            if confidence >= threshold:
                if signal == 'BUY' and position == 0:
                    invest = capital * position_size
                    shares = invest / price
                    position = shares
                    entry_price = price
                    capital -= invest
                    
                    trades.append({
                        'type': 'BUY',
                        'price': price,
                        'shares': shares,
                        'value': invest,
                        'conf': confidence,
                        'day': i,
                        'date': date
                    })
                
                elif signal == 'SELL' and position > 0:
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    pnl_pct = (pnl / trades[-1]['value']) * 100
                    capital += sell_val
                    
                    trades.append({
                        'type': 'SELL',
                        'price': price,
                        'shares': position,
                        'value': sell_val,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'conf': confidence,
                        'day': i,
                        'date': date,
                        'hold_days': i - trades[-1]['day']
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Record equity
            current_value = capital + (position * price)
            equity.append(current_value)
        
        # Close position at end
        if position > 0:
            final_price = history[-1]['price']
            final_value = position * final_price
            pnl = final_value - trades[-1]['value'] if trades else 0
            capital += final_value
            
            if trades and trades[-1]['type'] == 'BUY':
                trades.append({
                    'type': 'SELL',
                    'price': final_price,
                    'shares': position,
                    'value': final_value,
                    'pnl': pnl,
                    'pnl_pct': (pnl / trades[-1]['value'] * 100) if trades[-1]['value'] > 0 else 0,
                    'day': len(history)-1,
                    'date': history[-1]['date'],
                    'hold_days': len(history) - 1 - trades[-1]['day']
                })
        
        final = capital
        ret = ((final - self.initial_capital) / self.initial_capital) * 100
        
        completed = [t for t in trades if t['type'] == 'SELL']
        wins = [t for t in completed if t.get('pnl', 0) > 0]
        losses = [t for t in completed if t.get('pnl', 0) <= 0]
        
        # Calculate max drawdown
        peak = equity[0]
        max_dd = 0
        for v in equity:
            if v > peak: peak = v
            dd = (peak - v) / peak
            if dd > max_dd: max_dd = dd
        
        # Average hold time
        avg_hold = sum(t.get('hold_days', 0) for t in completed) / len(completed) if completed else 0
        
        return {
            'symbol': symbol,
            'threshold': threshold,
            'initial': self.initial_capital,
            'final': final,
            'return': ret,
            'trades': len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': (len(wins) / len(completed) * 100) if completed else 0,
            'avg_pnl': sum(t.get('pnl_pct', 0) for t in completed) / len(completed) if completed else 0,
            'best_trade': max((t.get('pnl_pct', 0) for t in completed), default=0),
            'worst_trade': min((t.get('pnl_pct', 0) for t in completed), default=0),
            'avg_hold_days': avg_hold,
            'max_dd': max_dd * 100,
            'trade_list': trades,
            'equity': equity
        }
    
    def run(self, symbols, thresholds=[0.25, 0.30, 0.35]):
        """Run backtest with multiple thresholds"""
        print("=" * 80)
        print("FIXED QUANTUM BACKTESTER")
        print("Testing multiple confidence thresholds")
        print("=" * 80)
        
        all_results = []
        
        for threshold in thresholds:
            print(f"\n{'='*80}")
            print(f"THRESHOLD: {threshold*100:.0f}%")
            print(f"{'='*80}")
            
            results = []
            for symbol in symbols:
                r = self.backtest(symbol, threshold)
                if r:
                    results.append(r)
                    
                    # Display
                    status = "PROFIT" if r['return'] > 0 else "LOSS"
                    print(f"\n{status}: {r['symbol']}")
                    print(f"  Return: {r['return']:+.2f}%")
                    print(f"  Trades: {r['trades']} (W: {r['wins']} L: {r['losses']})")
                    print(f"  Win Rate: {r['win_rate']:.1f}%")
                    print(f"  Max DD: {r['max_dd']:.2f}%")
                    print(f"  Avg Hold: {r['avg_hold_days']:.1f} days")
                    
                    if r['trade_list']:
                        print("  Last 3 trades:")
                        for t in r['trade_list'][-3:]:
                            if t['type'] == 'SELL':
                                print(f"    SELL {t['date']} @ ${t['price']:.8f} | PnL: {t['pnl_pct']:+.1f}% | Hold: {t.get('hold_days', 0)}d")
                            else:
                                print(f"    BUY {t['date']} @ ${t['price']:.8f} | Conf: {t['conf']*100:.0f}%")
            
            # Summary for this threshold
            if results:
                avg_ret = sum(r['return'] for r in results) / len(results)
                total_trades = sum(r['trades'] for r in results)
                avg_wr = sum(r['win_rate'] for r in results) / len(results)
                
                print(f"\n{'-'*80}")
                print(f"THRESHOLD {threshold*100:.0f}% SUMMARY:")
                print(f"  Avg Return: {avg_ret:+.2f}%")
                print(f"  Total Trades: {total_trades}")
                print(f"  Avg Win Rate: {avg_wr:.1f}%")
                print(f"{'-'*80}")
            
            all_results.extend(results)
        
        # Final ranking
        if all_results:
            print(f"\n{'='*80}")
            print("FINAL RANKING - ALL THRESHOLDS")
            print(f"{'='*80}")
            
            ranked = sorted(all_results, key=lambda x: x['return'], reverse=True)
            
            print(f"\n{'#':<4} {'Symbol':<8} {'Thresh':<8} {'Return':<10} {'Trades':<8} {'Win%':<8} {'MaxDD':<8}")
            print("-" * 80)
            
            for i, r in enumerate(ranked[:10], 1):
                print(f"{i:<4} {r['symbol']:<8} {r['threshold']*100:<7.0f}% {r['return']:<+9.1f}% {r['trades']:<8} {r['win_rate']:<7.1f}% {r['max_dd']:<7.1f}%")
        
        return all_results


def main():
    bt = FixedQuantumBacktester(initial_capital=10000)
    
    # Test all thresholds
    symbols = ['BONK', 'FLOKI', 'PEPE', 'SHIB']
    results = bt.run(symbols, thresholds=[0.25, 0.30, 0.35])
    
    # Best config
    if results:
        best = max(results, key=lambda x: x['return'])
        print(f"\n{'='*80}")
        print("BEST CONFIGURATION")
        print(f"{'='*80}")
        print(f"Symbol: {best['symbol']}")
        print(f"Threshold: {best['threshold']*100:.0f}%")
        print(f"Return: {best['return']:+.2f}%")
        print(f"Trades: {best['trades']}")
        print(f"Win Rate: {best['win_rate']:.1f}%")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
