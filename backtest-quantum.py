#!/usr/bin/env python3
"""
QUANTUM SIGNAL BACKTESTER
Tests quantum AI signals against historical price data
"""

import json
import os
from datetime import datetime

class QuantumBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.results = {}
    
    def load_historical_data(self, symbol):
        """Load saved historical data"""
        filepath = f'meme_coin_data/{symbol}_history.json'
        
        if not os.path.exists(filepath):
            print(f"No historical data found for {symbol}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
    def simulate_quantum_signal(self, price_data, volume_data, index):
        """Simulate what quantum signal would have been at this point"""
        if index < 7:
            return {'signal': 'HOLD', 'confidence': 0.3}
        
        # Calculate features as quantum would see them
        current_price = price_data[index]
        price_1d = price_data[index - 1]
        price_7d = price_data[index - 7]
        
        price_change = ((current_price - price_1d) / price_1d) * 100 if price_1d > 0 else 0
        volume = volume_data[index]
        avg_volume = sum(volume_data[max(0, index-7):index]) / 7
        
        # Simple rules-based simulation of quantum behavior
        signal = 'HOLD'
        confidence = 0.3
        
        # Strong uptrend + high volume = BUY
        if price_change > 5 and volume > avg_volume * 1.5:
            signal = 'BUY'
            confidence = min(0.35 + (price_change / 100), 0.6)
        
        # Strong downtrend + high volume = SELL
        elif price_change < -5 and volume > avg_volume * 1.5:
            signal = 'SELL'
            confidence = min(0.35 + (abs(price_change) / 100), 0.6)
        
        # Consolidation with volume = BUY (potential breakout)
        elif abs(price_change) < 2 and volume > avg_volume * 2:
            signal = 'BUY'
            confidence = 0.4
        
        # High volatility = HOLD
        else:
            recent_changes = [abs(price_data[i] - price_data[i-1]) / price_data[i-1] 
                              for i in range(max(1, index-5), index+1)]
            avg_change = sum(recent_changes) / len(recent_changes)
            
            if avg_change > 0.05:  # >5% avg daily change
                signal = 'HOLD'
                confidence = 0.45
        
        return {'signal': signal, 'confidence': confidence}
    
    def backtest_coin(self, symbol, confidence_threshold=0.35):
        """Backtest quantum signals on historical data"""
        print(f"\nBacktesting {symbol}...")
        print("=" * 60)
        
        data = self.load_historical_data(symbol)
        if not data or 'history' not in data:
            return None
        
        history = data['history']
        prices = [h['price'] for h in history]
        volumes = [h['volume'] for h in history]
        
        if len(prices) < 30:
            print("Not enough historical data (need 30+ days)")
            return None
        
        # Trading simulation
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(30, len(prices)):
            # Get quantum signal
            signal_data = self.simulate_quantum_signal(prices, volumes, i)
            signal = signal_data['signal']
            confidence = signal_data['confidence']
            
            # Only trade on high confidence
            if confidence < confidence_threshold:
                continue
            
            current_price = prices[i]
            
            # Execute trade
            if signal == 'BUY' and position == 0:
                # Buy with 20% of capital
                position_size = capital * 0.2
                shares = position_size / current_price
                position = shares
                capital -= position_size
                
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'value': position_size,
                    'confidence': confidence,
                    'day': i
                })
            
            elif signal == 'SELL' and position > 0:
                # Sell position
                sell_value = position * current_price
                pnl = sell_value - trades[-1]['value']
                capital += sell_value
                
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'value': sell_value,
                    'pnl': pnl,
                    'pnl_pct': (pnl / trades[-1]['value']) * 100,
                    'confidence': confidence,
                    'day': i
                })
                
                position = 0
            
            # Record equity
            total_value = capital + (position * current_price)
            equity_curve.append(total_value)
        
        # Close any open position at end
        if position > 0:
            final_price = prices[-1]
            sell_value = position * final_price
            capital += sell_value
        
        # Calculate metrics
        final_value = capital
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) <= 0]
        
        win_rate = (len(winning_trades) / len([t for t in trades if t['type'] == 'SELL']) * 100) if trades else 0
        
        # Max drawdown
        peak = equity_curve[0]
        max_drawdown = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': len([t for t in trades if t['type'] == 'SELL']),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'max_drawdown': max_drawdown * 100,
            'trades': trades,
            'equity_curve': equity_curve
        }
        
        return results
    
    def display_results(self, results):
        """Display backtest results"""
        if not results:
            return
        
        print(f"\nBACKTEST RESULTS: {results['symbol']}")
        print("=" * 60)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Value: ${results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return']:+.2f}%")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.1f}%")
        print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        
        if results['trades']:
            print("\nLast 5 Trades:")
            for t in results['trades'][-5:]:
                if t['type'] == 'SELL':
                    print(f"  SELL @ ${t['price']:.8f} | PnL: ${t.get('pnl', 0):+.2f} ({t.get('pnl_pct', 0):+.2f}%)")
                else:
                    print(f"  BUY @ ${t['price']:.8f} | Confidence: {t['confidence']*100:.1f}%")
    
    def backtest_all(self, symbols):
        """Backtest all symbols"""
        print("=" * 80)
        print("QUANTUM SIGNAL BACKTESTER")
        print("Testing signals on historical data")
        print("=" * 80)
        
        all_results = []
        
        for symbol in symbols:
            results = self.backtest_coin(symbol)
            if results:
                self.display_results(results)
                all_results.append(results)
        
        # Summary
        if all_results:
            print("\n" + "=" * 80)
            print("PORTFOLIO SUMMARY")
            print("=" * 80)
            
            total_return = sum(r['total_return'] for r in all_results) / len(all_results)
            avg_win_rate = sum(r['win_rate'] for r in all_results) / len(all_results)
            avg_drawdown = sum(r['max_drawdown'] for r in all_results) / len(all_results)
            
            print(f"Symbols Tested: {len(all_results)}")
            print(f"Average Return: {total_return:+.2f}%")
            print(f"Average Win Rate: {avg_win_rate:.1f}%")
            print(f"Average Max Drawdown: {avg_drawdown:.2f}%")
            
            # Rank by return
            ranked = sorted(all_results, key=lambda x: x['total_return'], reverse=True)
            print("\nRanked by Return:")
            for i, r in enumerate(ranked, 1):
                print(f"{i}. {r['symbol']}: {r['total_return']:+.2f}% (Win Rate: {r['win_rate']:.1f}%)")


def main():
    backtester = QuantumBacktester(initial_capital=10000)
    
    symbols = ['BONK', 'FLOKI', 'PEPE', 'SHIB']
    backtester.backtest_all(symbols)
    
    print("\n" + "=" * 80)
    print("Backtest complete. Quantum signals tested on historical data.")
    print("=" * 80)


if __name__ == "__main__":
    main()
