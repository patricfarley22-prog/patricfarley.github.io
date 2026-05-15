#!/usr/bin/env python3
"""
BACKTESTER WITH STOP LOSSES
Tests quantum signals with risk management
"""

import json
import os

class BacktestWithStops:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
    
    def load_data(self, symbol):
        filepath = f'meme_coin_data/{symbol}_history.json'
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def generate_signal(self, history, index):
        """Generate signal with multiple strategies"""
        if index < 14:
            return 'HOLD', 0.25
        
        current = history[index]
        price = current['price']
        
        # Returns
        price_1d = history[index-1]['price']
        price_3d = history[index-3]['price']
        price_7d = history[index-7]['price']
        price_14d = history[index-14]['price']
        
        ret_1d = ((price - price_1d) / price_1d * 100) if price_1d > 0 else 0
        ret_3d = ((price - price_3d) / price_3d * 100) if price_3d > 0 else 0
        ret_7d = ((price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        ret_14d = ((price - price_14d) / price_14d * 100) if price_14d > 0 else 0
        
        # Volume
        vol_now = current['volume']
        vol_avg = sum(h['volume'] for h in history[max(0,index-7):index]) / 7
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
        
        signal = 'HOLD'
        confidence = 0.25
        
        # Momentum
        momentum = (ret_7d + ret_3d/2 + ret_1d/4) / 20
        momentum = max(-1, min(1, momentum))
        
        # Mean reversion
        oversold = ret_14d < -25 and ret_7d > -5
        overbought = ret_14d > 40 and ret_7d < 5
        
        # BUY
        if oversold and vol_ratio > 1.2:
            signal = 'BUY'
            confidence = 0.35 + abs(ret_14d) / 100
        elif ret_7d > 10 and ret_1d > 0 and vol_ratio > 1.3:
            signal = 'BUY'
            confidence = 0.4 + ret_7d / 100
        elif ret_7d > 20:
            signal = 'BUY'
            confidence = 0.5
        
        # SELL
        elif overbought and vol_ratio > 1.2:
            signal = 'SELL'
            confidence = 0.35 + abs(ret_14d) / 100
        elif ret_7d < -10 and ret_1d < 0 and vol_ratio > 1.3:
            signal = 'SELL'
            confidence = 0.4 + abs(ret_7d) / 100
        elif ret_7d < -20:
            signal = 'SELL'
            confidence = 0.5
        
        # Breakout
        elif abs(ret_1d) > 8 and vol_ratio > 2:
            signal = 'BUY' if ret_1d > 0 else 'SELL'
            confidence = 0.4 + abs(ret_1d) / 50
        
        confidence = min(0.6, confidence)
        return signal, confidence
    
    def backtest(self, symbol, threshold=0.30, position_size=0.25, stop_loss=-0.08):
        """Backtest with stop losses"""
        data = self.load_data(symbol)
        if not data or 'history' not in data:
            return None
        
        history = data['history']
        if len(history) < 30:
            print(f"{symbol}: Only {len(history)} days, need 30+")
            return None
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity = [capital]
        stop_hits = 0
        
        print(f"\nBacktesting {symbol}...")
        print(f"  Threshold: {threshold*100:.0f}% | Position: {position_size*100:.0f}% | Stop: {stop_loss*100:.0f}%")
        
        for i in range(14, len(history)):
            signal, confidence = self.generate_signal(history, i)
            price = history[i]['price']
            
            # Check stop loss
            if position > 0 and entry_price > 0:
                pnl_pct = (price - entry_price) / entry_price
                if pnl_pct <= stop_loss:
                    # STOP LOSS HIT
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    pnl_pct = (pnl / trades[-1]['value']) * 100
                    capital += sell_val
                    
                    trades.append({
                        'type': 'STOP',
                        'price': price,
                        'shares': position,
                        'value': sell_val,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'day': i,
                        'date': history[i]['date'],
                        'hold_days': i - trades[-1]['day']
                    })
                    
                    stop_hits += 1
                    position = 0
                    entry_price = 0
                    
                    print(f"  STOP @ ${price:.8f} | PnL: {pnl_pct:+.1f}% | Day {i}")
                    continue
            
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
                        'date': history[i]['date']
                    })
                    print(f"  BUY @ ${price:.8f} | Conf: {confidence*100:.0f}% | Day {i}")
                
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
                        'day': i,
                        'date': history[i]['date'],
                        'hold_days': i - trades[-1]['day']
                    })
                    
                    position = 0
                    entry_price = 0
                    print(f"  SELL @ ${price:.8f} | PnL: {pnl_pct:+.1f}% | Day {i}")
            
            equity.append(capital + (position * price))
        
        # Close at end
        if position > 0:
            final_price = history[-1]['price']
            final_value = position * final_price
            if trades and trades[-1]['type'] == 'BUY':
                pnl = final_value - trades[-1]['value']
                trades.append({
                    'type': 'CLOSE',
                    'price': final_price,
                    'shares': position,
                    'value': final_value,
                    'pnl': pnl,
                    'pnl_pct': (pnl / trades[-1]['value']) * 100,
                    'day': len(history) - 1
                })
            capital += final_value
        
        final = capital
        ret = ((final - self.initial_capital) / self.initial_capital) * 100
        
        completed = [t for t in trades if t['type'] in ['SELL', 'STOP', 'CLOSE']]
        wins = [t for t in completed if t.get('pnl', 0) > 0]
        losses = [t for t in completed if t.get('pnl', 0) <= 0]
        
        # Metrics
        peak = equity[0]
        max_dd = 0
        for v in equity:
            if v > peak: peak = v
            dd = (peak - v) / peak
            if dd > max_dd: max_dd = dd
        
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
            'stops': stop_hits,
            'win_rate': (len(wins) / len(completed) * 100) if completed else 0,
            'avg_pnl': sum(t.get('pnl_pct', 0) for t in completed) / len(completed) if completed else 0,
            'best_trade': max((t.get('pnl_pct', 0) for t in completed), default=0),
            'worst_trade': min((t.get('pnl_pct', 0) for t in completed), default=0),
            'avg_hold': avg_hold,
            'max_dd': max_dd * 100,
            'trade_list': trades
        }
    
    def run_all(self, symbols, thresholds=[0.25, 0.30, 0.35]):
        """Run backtest for all coins"""
        print("=" * 80)
        print("QUANTUM BACKTESTER WITH STOP LOSSES")
        print("=" * 80)
        
        all_results = []
        
        for threshold in thresholds:
            print(f"\n{'='*80}")
            print(f"THRESHOLD: {threshold*100:.0f}%")
            print(f"{'='*80}")
            
            for symbol in symbols:
                r = self.backtest(symbol, threshold)
                if r:
                    all_results.append(r)
                    
                    status = "PROFIT" if r['return'] > 0 else "LOSS"
                    print(f"\n{status}: {r['symbol']}")
                    print(f"  Return: {r['return']:+.2f}% | Trades: {r['trades']} (W:{r['wins']} L:{r['losses']} S:{r['stops']})")
                    print(f"  Win Rate: {r['win_rate']:.1f}% | Stops Hit: {r['stops']}")
                    print(f"  Best: {r['best_trade']:+.1f}% | Worst: {r['worst_trade']:+.1f}%")
                    print(f"  Max DD: {r['max_dd']:.2f}% | Avg Hold: {r['avg_hold']:.1f}d")
                    
                    if r['trade_list']:
                        print("  Trades:")
                        for t in r['trade_list'][-3:]:
                            date_str = t.get('date', f"Day {t.get('day', '?')}")
                            if t['type'] == 'STOP':
                                print(f"    STOP {date_str} @ ${t['price']:.8f} | PnL: {t['pnl_pct']:+.1f}% | Hold: {t['hold_days']}d")
                            elif t['type'] == 'SELL':
                                print(f"    SELL {date_str} @ ${t['price']:.8f} | PnL: {t['pnl_pct']:+.1f}% | Hold: {t['hold_days']}d")
                            elif t['type'] == 'CLOSE':
                                print(f"    CLOSE {date_str} @ ${t['price']:.8f} | PnL: {t['pnl_pct']:+.1f}%")
                            else:
                                print(f"    BUY  {date_str} @ ${t['price']:.8f} | Conf: {t.get('conf',0)*100:.0f}%")
        
        # Summary
        if all_results:
            print("\n" + "=" * 80)
            print("PORTFOLIO SUMMARY")
            print("=" * 80)
            
            for threshold in thresholds:
                t_results = [r for r in all_results if r['threshold'] == threshold]
                if t_results:
                    avg_ret = sum(r['return'] for r in t_results) / len(t_results)
                    total_trades = sum(r['trades'] for r in t_results)
                    total_stops = sum(r['stops'] for r in t_results)
                    
                    print(f"\nThreshold {threshold*100:.0f}%:")
                    print(f"  Avg Return: {avg_ret:+.2f}%")
                    print(f"  Total Trades: {total_trades} (Stops: {total_stops})")
                    
                    ranked = sorted(t_results, key=lambda x: x['return'], reverse=True)
                    print(f"\n  Top Performers:")
                    for i, r in enumerate(ranked[:5], 1):
                        print(f"  {i}. {r['symbol']}: {r['return']:+.2f}% ({r['trades']} trades, {r['stops']} stops)")
        
        return all_results


def main():
    bt = BacktestWithStops(initial_capital=10000)
    
    # Major coins with 91-day history
    major = ['BONK', 'FLOKI', 'PEPE', 'SHIB', 'DOGE']
    
    # Test with stop losses
    print("Testing with stop losses...")
    bt.run_all(major, thresholds=[0.25])
    
    print("\n" + "=" * 80)
    print("BACKTEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
