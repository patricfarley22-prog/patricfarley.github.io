#!/usr/bin/env node
/**
 * BACKTEST ENGINE
 * Tests quantum signals against historical data to prove they work
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

class BacktestEngine {
  constructor(initialCapital = 1000) {
    this.initialCapital = initialCapital;
    this.trades = [];
    this.equity = [initialCapital];
  }

  backtest(signals, historicalData) {
    console.log('🔬 Running Backtest\n');
    console.log(`Initial Capital: $${this.initialCapital}`);
    console.log(`Testing ${signals.length} signals\n`);
    
    let capital = this.initialCapital;
    let wins = 0;
    let losses = 0;
    
    for (let i = 0; i < signals.length - 1; i++) {
      const signal = signals[i];
      const nextDay = historicalData[i + 1];
      
      if (!nextDay) continue;
      
      const entryPrice = signal.price;
      const exitPrice = nextDay.price;
      const change = (exitPrice - entryPrice) / entryPrice;
      
      // Only trade on high confidence signals
      if (signal.confidence < 0.6) continue;
      
      const position = capital * 0.1; // 10% position size
      const pnl = position * change * (signal.signal.includes('BUY') ? 1 : -1);
      
      capital += pnl;
      
      const trade = {
        entry: entryPrice,
        exit: exitPrice,
        signal: signal.signal,
        confidence: signal.confidence,
        pnl: pnl,
        capital: capital,
        win: pnl > 0
      };
      
      this.trades.push(trade);
      this.equity.push(capital);
      
      if (pnl > 0) wins++;
      else losses++;
    }
    
    // Calculate metrics
    const totalReturn = ((capital - this.initialCapital) / this.initialCapital) * 100;
    const winRate = this.trades.length > 0 ? (wins / this.trades.length) * 100 : 0;
    const maxDrawdown = this.calculateMaxDrawdown();
    const sharpe = this.calculateSharpe();
    
    const results = {
      initialCapital: this.initialCapital,
      finalCapital: capital,
      totalReturn: totalReturn,
      winRate: winRate,
      totalTrades: this.trades.length,
      wins: wins,
      losses: losses,
      maxDrawdown: maxDrawdown,
      sharpeRatio: sharpe,
      trades: this.trades,
      equity: this.equity
    };
    
    this.printResults(results);
    return results;
  }

  calculateMaxDrawdown() {
    let maxDrawdown = 0;
    let peak = this.equity[0];
    
    for (const value of this.equity) {
      if (value > peak) peak = value;
      const drawdown = (peak - value) / peak;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }
    
    return maxDrawdown * 100;
  }

  calculateSharpe() {
    if (this.trades.length < 2) return 0;
    
    const returns = this.trades.map(t => t.pnl / this.initialCapital);
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    
    return stdDev > 0 ? (mean / stdDev) * Math.sqrt(252) : 0; // Annualized
  }

  printResults(results) {
    console.log('='.repeat(60));
    console.log('BACKTEST RESULTS');
    console.log('='.repeat(60));
    console.log(`Initial Capital: $${results.initialCapital.toFixed(2)}`);
    console.log(`Final Capital: $${results.finalCapital.toFixed(2)}`);
    console.log(`Total Return: ${results.totalReturn.toFixed(2)}%`);
    console.log(`Win Rate: ${results.winRate.toFixed(1)}%`);
    console.log(`Trades: ${results.totalTrades} (${results.wins}W / ${results.losses}L)`);
    console.log(`Max Drawdown: ${results.maxDrawdown.toFixed(2)}%`);
    console.log(`Sharpe Ratio: ${results.sharpeRatio.toFixed(2)}`);
    
    if (results.totalTrades > 0) {
      console.log('\nLast 5 Trades:');
      results.trades.slice(-5).forEach((t, i) => {
        console.log(`  ${i+1}. ${t.signal} | PnL: $${t.pnl.toFixed(2)} | ${t.win ? 'WIN' : 'LOSS'}`);
      });
    }
    
    console.log('='.repeat(60));
  }

  saveResults(filename) {
    const filePath = join(__dirname, 'data', filename);
    writeFileSync(filePath, JSON.stringify({
      trades: this.trades,
      equity: this.equity,
      metrics: {
        initialCapital: this.initialCapital,
        finalCapital: this.equity[this.equity.length - 1],
        totalReturn: ((this.equity[this.equity.length - 1] - this.initialCapital) / this.initialCapital) * 100
      }
    }, null, 2));
    console.log(`\n📁 Results saved to ${filePath}`);
  }
}

export default BacktestEngine;
