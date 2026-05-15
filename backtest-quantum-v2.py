#!/usr/bin/env python3
"""
QUANTUM SIGNAL BACKTESTER v2.0
Tests real quantum AI signals against historical price data
Uses actual quantum_analyzer.py with historical features
"""

import json
import os
import subprocess
from datetime import datetime

class QuantumBacktesterV2:
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
    
    def run_quantum_analyzer(self, features):
        """Run actual quantum analyzer with historical features"""
        try:
            # Convert features to args for quantum_analyzer.py
            args = [
                str(features['price_change'] / 100),
                str(features['volume'] / 1_000_000),
                str(features['rsi'] / 100),
                str(features['macd']),
                str(features['sentiment']),
                str(features['fear_greed'] / 100),
                str(features['btc_dominance']),
                str(features['liquidity']),
                str(features['whale_activity']),
                str(features['social_volume'])
            ]
            
            result = subprocess.run(
                ['python', 'quantum_analyzer.py'] + args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(__file__)
            )
            
            if result.returncode == 0:
                output = result.stdout
                start = output.find('{')
                end = output.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(output[start:end+1])
            
            return {'signal': 'HOLD', 'confidence': 0.3}
        except Exception as e:
            print(f"Quantum error: {e}")
            return {'signal': 'HOLD', 'confidence': 0.3}
    
    def calculate_features(self, history, index):
        """Calculate features for quantum analyzer from historical data"""
        if index < 14:
            return None
        
        current = history[index]
        prev = history[index - 1]
        prev_7 = history[index - 7]
        prev_14 = history[index - 14]
        
        # Price change
        price_change = ((current['price'] - prev['price']) / prev['price'] * 100) if prev['price'] > 0 else 0
        
        # Volume (normalized)
        volume = current['volume']
        avg_volume_7 = sum(h['volume'] for h in history[max(0, index-7):index]) / 7
        volume_change = (volume / avg_volume_7 - 1) * 100 if avg_volume_7 > 0 else 0
        
        # RSI approximation
        gains = []
        losses = []
        for i in range(index-13, index+1):
            if i > 0 and history[i-1]['price'] > 0:
                change = history[i]['price'] - history[i-1]['price']
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0.001
        rsi = 100 - (100 / (1 + avg_gain / avg_loss))
        
        # MACD approximation
        ema_12 = sum(h['price'] for h in history[max(0, index-11):index+1]) / 12
        ema_26 = sum(h['price'] for h in history[max(0, index-25):index+1]) / 26
        macd = (ema_12 - ema_26) / ema_26 * 100 if ema_26 > 0 else 0
        
        # Sentiment based on trend
        trend_7 = (current['price'] - prev_7['price']) / prev_7['price'] if prev_7['price'] > 0 else 0
        sentiment = 0.5 + (trend_7 * 2)  # Scale to 0-1
        sentiment = max(0.1, min(0.9, sentiment))
        
        # Fear/greed (based on recent volatility)
        recent_changes = []
        for i in range(max(1, index-6), index+1):
            if history[i-1]['price'] > 0:
                change = (history[i]['price'] - history[i-1]['price']) / history[i-1]['price']
                recent_changes.append(abs(change))
        
        avg_change = sum(recent_changes) / len(recent_changes) if recent_changes else 0
        fear_greed = 50 + (avg_change * 1000)  # Higher volatility = more greed
        fear_greed = max(10, min(90, fear_greed))
        
        # Liquidity proxy (market cap / volume ratio)
        liquidity = min(current['market_cap'] / (current['volume'] + 1), 1.0)
        
        return {
            'price_change': price_change,
            'volume': volume_change,
            'rsi': rsi,
            'macd': macd,
            'sentiment': sentiment,
            'fear_greed': fear_greed,
            'btc_dominance': 0.45,  # Default
            'liquidity': liquidity,
            'whale_activity': 0.5,    # Default
            'social_volume': min(volume_change / 100, 1.0)
        }
    
    def backtest_coin(self, symbol, confidence_threshold=0.35):
        """Backtest using real quantum analyzer"""
        print(f"\nBacktesting {symbol}...")
        print("=" * 60)
        
        data = self.load_historical_data(symbol)
        if not data or 'history' not in data:
            print("No historical data")
            return None
        
        history = data['history']
        if len(history) < 30:
            print("Need 30+ days of data")
            return None
        
        print(f"Historical data: {len(history)} days")
        
        # Trading simulation
        capital = self.initial_capital
        position = 0
        position_value = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(14, len(history)):
            current = history[i]
            
            # Calculate features for quantum
            features = self.calculate_features(history, i)
            if not features:
                continue
            
            # Get quantum signal
            quantum = self.run_quantum_analyzer(features)
            signal = quantum.get('signal', 'HOLD')
            confidence = quantum.get('confidence', 0)
            
            current_price = current['price']
            
            # Execute trade (only on high confidence)
            if confidence >= confidence_threshold:
                if signal == 'BUY' and position == 0:
                    # Buy with 25% of capital
                    invest_amount = capital * 0.25
                    shares = invest_amount / current_price
                    position = shares
                    capital -= invest_amount
                    
                    trades.append({
                        'type': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'value': invest_amount,
                        'confidence': confidence,
                        'day': i,
                        'date': current['date']
                    })
                    print(f"  BUY @ ${current_price:.8f} | Conf: {confidence*100:.1f}% | Day {i}")
                
                elif signal == 'SELL' and position > 0:
                    # Sell position
                    sell_value = position * current_price
                    pnl = sell_value - trades[-1]['value']
                    pnl_pct = (pnl / trades[-1]['value']) * 100
                    capital += sell_value
                    
                    trades.append({
                        'type': 'SELL',
                        'price': current_price,
                        'shares': position,
                        'value': sell_value,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'confidence': confidence,
                        'day': i,
                        'date': current['date']
                    })
                    print(f"  SELL @ ${current_price:.8f} | PnL: ${pnl:+.2f} ({pnl_pct:+.1f}%) | Day {i}")
                    
                    position = 0
            
            # Record equity
            total_value = capital + (position * current_price)
            equity_curve.append(total_value)
        
        # Close any open position
        if position > 0:
            final_price = history[-1]['price']
            sell_value = position * final_price
            capital += sell_value
        
        final_value = capital
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        completed_trades = [t for t in trades if t['type'] == 'SELL']
        winning_trades = [t for t in completed_trades if t.get('pnl', 0) > 0]
        
        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0
        
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
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(completed_trades) - len(winning_trades),
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
                    print(f"  SELL @ ${t['price']:.8f} | PnL: ${t.get('pnl', 0):+.2f} ({t.get('pnl_pct', 0):+.1f}%)")
                else:
                    print(f"  BUY @ ${t['price']:.8f} | Conf: {t['confidence']*100:.1f}%")
    
    def backtest_all(self, symbols, confidence_threshold=0.35):
        """Backtest all symbols with real quantum signals"""
        print("=" * 80)
        print("QUANTUM SIGNAL BACKTESTER v2.0")
        print("Using real quantum_analyzer.py on historical data")
        print("=" * 80)
        print(f"Confidence Threshold: {confidence_threshold*100:.0f}%")
        print()
        
        all_results = []
        
        for symbol in symbols:
            results = self.backtest_coin(symbol, confidence_threshold)
            if results:
                self.display_results(results)
                all_results.append(results)
        
        # Portfolio summary
        if all_results:
            print("\n" + "=" * 80)
            print("PORTFOLIO SUMMARY")
            print("=" * 80)
            
            total_return = sum(r['total_return'] for r in all_results) / len(all_results)
            avg_win_rate = sum(r['win_rate'] for r in all_results) / len(all_results)
            avg_drawdown = sum(r['max_drawdown'] for r in all_results) / len(all_results)
            total_trades = sum(r['total_trades'] for r in all_results)
            
            print(f"Symbols Tested: {len(all_results)}")
            print(f"Total Trades: {total_trades}")
            print(f"Average Return: {total_return:+.2f}%")
            print(f"Average Win Rate: {avg_win_rate:.1f}%")
            print(f"Average Max Drawdown: {avg_drawdown:.2f}%")
            
            ranked = sorted(all_results, key=lambda x: x['total_return'], reverse=True)
            print("\nRanked by Return:")
            for i, r in enumerate(ranked, 1):
                print(f"{i}. {r['symbol']}: {r['total_return']:+.2f}% (Win Rate: {r['win_rate']:.1f}%, Trades: {r['total_trades']})")


def main():
    backtester = QuantumBacktesterV2(initial_capital=10000)
    
    # Test with different confidence thresholds
    for threshold in [0.30, 0.35, 0.40]:
        print(f"\n\n{'='*80}")
        print(f"TESTING WITH CONFIDENCE THRESHOLD: {threshold*100:.0f}%")
        print(f"{'='*80}\n")
        
        symbols = ['BONK', 'FLOKI']
        backtester.backtest_all(symbols, confidence_threshold=threshold)


if __name__ == "__main__":
    main()
