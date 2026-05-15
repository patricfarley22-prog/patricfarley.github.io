#!/usr/bin/env node
/**
 * QUANTUM AI V2 - COMPLETE ANALYSIS
 * Historical data + Sentiment + Advanced Quantum + Backtest
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import SentimentAnalyzer from './sentiment-analyzer.mjs';
import BacktestEngine from './backtest-engine.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

class QuantumV2Analyzer {
  constructor() {
    this.sentimentAnalyzer = new SentimentAnalyzer();
  }

  async fetchTokenData(ca) {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${ca}`, {
        timeout: 10000
      });
      
      if (!response.ok) return null;
      
      const data = await response.json();
      return data.pairs?.[0] || null;
    } catch (err) {
      return null;
    }
  }

  async runAdvancedQuantum(tokenData, sentiment) {
    const priceChange = parseFloat(tokenData.priceChange?.h24) || 0;
    const volume = parseFloat(tokenData.volume?.h24) || 0;
    const liq = parseFloat(tokenData.liquidity?.usd) || 0;
    const mcap = parseFloat(tokenData.marketCap) || 1;
    
    const args = [
      (priceChange / 100).toString(),
      (volume / 100000).toString(),
      '0.5',  // rsi
      '0',     // macd
      sentiment.composite.toString(),  // sentiment
      '0.55',  // fear_greed
      '0.45',  // btc_dominance
      Math.min(liq / 50000, 1).toString(),
      '0.5',   // whale_activity
      Math.min(volume / 100000, 1).toString(),
      (priceChange / 30).toString(),  // historical trend (simplified)
      sentiment.composite.toString(),  // market regime
      sentiment.composite.toString(),  // sentiment score
      '0.4'    // volatility
    ];

    return new Promise((resolve, reject) => {
      const proc = spawn('python', [join(__dirname, 'advanced-quantum-analyzer.py'), ...args]);
      let output = '';
      let error = '';
      
      proc.stdout.on('data', d => output += d.toString());
      proc.stderr.on('data', d => error += d.toString());
      
      proc.on('close', code => {
        if (code !== 0) reject(new Error(error));
        else {
          try {
            const jsonMatch = output.match(/\{[\s\S]*\}/);
            resolve(jsonMatch ? JSON.parse(jsonMatch[0]) : {});
          } catch (e) {
            resolve({});
          }
        }
      });
    });
  }

  async analyzeToken(symbol, ca) {
    console.log(`\n🔮 Analyzing ${symbol}...`);
    console.log('='.repeat(60));
    
    // Step 1: Fetch data
    const tokenData = await this.fetchTokenData(ca);
    if (!tokenData) {
      console.log('❌ No data found');
      return null;
    }
    
    // Step 2: Analyze sentiment
    console.log('\n📊 Sentiment Analysis:');
    const sentiment = await this.sentimentAnalyzer.analyzeToken(symbol, ca);
    console.log(`  Composite: ${(sentiment.composite * 100).toFixed(1)}% (${this.getSentimentLabel(sentiment.composite)})`);
    console.log(`  Volume: ${(sentiment.volumeSentiment * 100).toFixed(0)}%`);
    console.log(`  Transactions: ${(sentiment.transactionSentiment * 100).toFixed(0)}%`);
    console.log(`  Price: ${(sentiment.priceSentiment * 100).toFixed(0)}%`);
    console.log(`  Liquidity: ${(sentiment.liquidityHealth * 100).toFixed(0)}%`);
    console.log(`  Hype: ${(sentiment.hypeScore * 100).toFixed(0)}%`);
    
    // Step 3: Run advanced quantum
    console.log('\n🔮 Quantum AI v2.0 Analysis:');
    const quantum = await this.runAdvancedQuantum(tokenData, sentiment);
    
    if (quantum.signal) {
      const emoji = quantum.signal.includes('BUY') ? '🚀' : quantum.signal.includes('SELL') ? '📉' : '⏸️';
      console.log(`  ${emoji} Signal: ${quantum.signal}`);
      console.log(`  Raw Confidence: ${(quantum.raw_confidence * 100).toFixed(1)}%`);
      console.log(`  Trend Alignment: ${(quantum.trend_alignment * 100).toFixed(1)}%`);
      console.log(`  Uncertainty: ${(quantum.uncertainty * 100).toFixed(1)}%`);
      console.log(`  ${'='.repeat(40)}`);
      console.log(`  FINAL CONFIDENCE: ${(quantum.final_confidence * 100).toFixed(1)}%`);
      console.log(`  ${'='.repeat(40)}`);
      
      // Market regime
      if (quantum.market_regime) {
        console.log(`\n  Market Regime:`);
        console.log(`    Bull: ${(quantum.market_regime.bull * 100).toFixed(0)}%`);
        console.log(`    Bear: ${(quantum.market_regime.bear * 100).toFixed(0)}%`);
        console.log(`    Sideways: ${(quantum.market_regime.sideways * 100).toFixed(0)}%`);
      }
      
      console.log(`\n  Quantum Features: ${quantum.quantum_features?.slice(0, 4).join(', ')}`);
      console.log(`  Entanglement: ${quantum.entanglement_strength}`);
      
      if (quantum.recommendation) {
        console.log(`\n  💡 Recommendation: ${quantum.recommendation}`);
      }
    }
    
    return {
      symbol,
      ca,
      sentiment,
      quantum,
      price: parseFloat(tokenData.priceUsd),
      marketCap: parseFloat(tokenData.marketCap),
      liquidity: parseFloat(tokenData.liquidity?.usd),
      volume24h: parseFloat(tokenData.volume?.h24),
      change24h: parseFloat(tokenData.priceChange?.h24),
      timestamp: new Date().toISOString()
    };
  }

  getSentimentLabel(score) {
    if (score >= 0.8) return 'VERY BULLISH';
    if (score >= 0.6) return 'BULLISH';
    if (score >= 0.4) return 'NEUTRAL';
    if (score >= 0.2) return 'BEARISH';
    return 'VERY BEARISH';
  }

  async analyzeMultiple(tokens) {
    const results = [];
    
    for (const [symbol, ca] of Object.entries(tokens)) {
      const result = await this.analyzeToken(symbol, ca);
      if (result) results.push(result);
      
      // Rate limiting
      await new Promise(r => setTimeout(r, 1000));
    }
    
    // Rank by final confidence
    results.sort((a, b) => (b.quantum?.final_confidence || 0) - (a.quantum?.final_confidence || 0));
    
    console.log('\n' + '='.repeat(60));
    console.log('RANKED BY CONFIDENCE');
    console.log('='.repeat(60));
    
    results.forEach((r, i) => {
      const signal = r.quantum?.signal || 'UNKNOWN';
      const conf = r.quantum?.final_confidence || 0;
      const emoji = signal.includes('BUY') ? '🚀' : signal.includes('SELL') ? '📉' : '⏸️';
      console.log(`${i+1}. ${emoji} ${r.symbol}: ${signal} (${(conf*100).toFixed(1)}%)`);
    });
    
    return results;
  }
}

// Usage
const TRACKED_TOKENS = {
  'TROLL': '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2',
  'DOWGE': 'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump',
  'HACHI': 'AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh',
  'WOBBLES': '9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump',
  'PENGO': 'F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump'
};

async function main() {
  const analyzer = new QuantumV2Analyzer();
  
  console.log('🔮 CORTEX QUANTUM AI v2.0');
  console.log('Advanced Analysis with Historical + Sentiment\n');
  
  const results = await analyzer.analyzeMultiple(TRACKED_TOKENS);
  
  // Show best opportunity
  if (results.length > 0) {
    const best = results[0];
    console.log('\n' + '='.repeat(60));
    console.log('BEST OPPORTUNITY');
    console.log('='.repeat(60));
    console.log(`Token: $${best.symbol}`);
    console.log(`Price: $${best.price?.toFixed(10)}`);
    console.log(`Signal: ${best.quantum?.signal}`);
    console.log(`Confidence: ${(best.quantum?.final_confidence * 100).toFixed(1)}%`);
    console.log(`Sentiment: ${analyzer.getSentimentLabel(best.sentiment.composite)}`);
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(console.error);
}

export default QuantumV2Analyzer;
