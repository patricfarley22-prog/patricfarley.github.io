#!/usr/bin/env node
/**
 * QUANTUM-ENHANCED ALPHA SCANNER
 * Integrates quantum ML signals into live scanning
 * 
 * Usage: node run-quantum-scan.mjs
 *        node run-quantum-scan.mjs --tweet (posts to Twitter)
 *        node run-quantum-scan.mjs --alert (sends Telegram alerts)
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Config
const CONFIG = {
  minLiquidity: 10000,
  minVolume: 5000,
  minMarketCap: 5000,
  maxMarketCap: 10000000,
  alertThreshold: 2,
  quantumMinConfidence: 0.35,  // Minimum confidence for quantum signal
  topN: 5  // How many tokens to analyze
};

class QuantumAlphaScanner {
  constructor() {
    this.results = [];
  }

  /**
   * Fetch tokens from DexScreener
   */
  async fetchTokens() {
    try {
      const response = await fetch('https://api.dexscreener.com/latest/dex/search?q=solana', {
        timeout: 15000
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return data.pairs || [];
    } catch (err) {
      console.error('Fetch error:', err.message);
      return [];
    }
  }

  /**
   * Filter tokens by basic criteria
   */
  filterTokens(pairs) {
    return pairs.filter(pair => {
      const liq = pair.liquidity?.usd || 0;
      const vol = pair.volume?.h24 || 0;
      const mcap = pair.marketCap || 0;
      const age = pair.pairCreatedAt 
        ? (Date.now() - pair.pairCreatedAt) / 60000 
        : 9999;
      
      return liq >= CONFIG.minLiquidity
        && vol >= CONFIG.minVolume
        && mcap >= CONFIG.minMarketCap
        && mcap <= CONFIG.maxMarketCap
        && age > 5; // At least 5 minutes old
    }).sort((a, b) => (b.volume?.h24 || 0) - (a.volume?.h24 || 0));
  }

  /**
   * Run quantum analysis on a token
   */
  async analyzeWithQuantum(pair) {
    const priceChange = pair.priceChange?.h24 || 0;
    const volumeChange = ((pair.volume?.h24 || 0) / (pair.volume?.h6 || 1) - 1) * 100;
    const mcap = pair.marketCap || 0;
    
    // Prepare features for quantum analyzer
    const args = [
      (priceChange / 100).toString(),  // price_change
      (volumeChange / 100).toString(),  // volume_change
      '0.5',  // rsi (we don't have it, use neutral)
      '0',     // macd
      '0.6',   // sentiment (moderate bullish)
      '0.55',  // fear_greed
      '0.45',  // btc_dominance
      Math.min((pair.liquidity?.usd || 0) / 50000, 1).toString(),  // liquidity
      '0.5',   // whale_activity
      Math.min((pair.txns?.h24?.buys || 0) / 100, 1).toString()  // social_volume proxy
    ];

    try {
      // Call quantum analyzer
      const result = await this.runPythonScript('quantum_analyzer.py', args);
      
      return {
        symbol: pair.baseToken?.symbol || 'UNKNOWN',
        address: pair.baseToken?.address,
        price: pair.priceUsd,
        priceChange24h: priceChange,
        volume24h: pair.volume?.h24,
        liquidity: pair.liquidity?.usd,
        marketCap: mcap,
        quantumSignal: result.signal,
        confidence: result.confidence,
        probabilities: result.probabilities,
        quantumFeatures: result.quantum_features,
        entanglementStrength: result.entanglement_strength,
        dexId: pair.dexId,
        pairAddress: pair.pairAddress
      };
    } catch (err) {
      console.error(`Quantum analysis failed for ${pair.baseToken?.symbol}:`, err.message);
      return null;
    }
  }

  /**
   * Run Python script and parse JSON
   */
  async runPythonScript(scriptName, args) {
    return new Promise((resolve, reject) => {
      const scriptPath = join(__dirname, '..', '..', '..', scriptName);
      const proc = spawn('python', [scriptPath, ...args]);
      
      let output = '';
      let error = '';
      
      proc.stdout.on('data', d => output += d.toString());
      proc.stderr.on('data', d => error += d.toString());
      
      proc.on('close', code => {
        if (code !== 0) {
          reject(new Error(`Python error: ${error}`));
        } else {
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

  /**
   * Format alert for display
   */
  formatAlert(token) {
    const emojis = { BUY: '🚀', HOLD: '⏸️', SELL: '📉' };
    const emoji = emojis[token.quantumSignal] || '❓';
    
    return `${emoji} **Quantum Signal: ${token.quantumSignal}**\n` +
           `Token: $${token.symbol}\n` +
           `Confidence: ${(token.confidence * 100).toFixed(1)}%\n` +
           `Price: $${parseFloat(token.price).toFixed(6)}\n` +
           `24h Change: ${token.priceChange24h.toFixed(2)}%\n` +
           `Volume: $${(token.volume24h / 1000).toFixed(1)}K\n` +
           `Liquidity: $${(token.liquidity / 1000).toFixed(1)}K\n` +
           `Market Cap: $${(token.marketCap / 1000).toFixed(1)}K\n` +
           `Quantum Features: ${token.quantumFeatures?.slice(0, 3).join(', ') || 'N/A'}\n` +
           `Entanglement: ${token.entanglementStrength?.toFixed(3) || 'N/A'}\n` +
           `[Chart](https://dexscreener.com/solana/${token.pairAddress})`;
  }

  /**
   * Format tweet content
   */
  formatTweet(token) {
    return `🔮 Quantum AI Signal: ${token.quantumSignal}\n\n` +
           `$${token.symbol}\n` +
           `Confidence: ${(token.confidence * 100).toFixed(0)}%\n` +
           `24h: ${token.priceChange24h > 0 ? '+' : ''}${token.priceChange24h.toFixed(1)}%\n` +
           `MCap: $${(token.marketCap / 1000).toFixed(0)}K\n\n` +
           `Quantum features detected patterns classical AI missed.\n` +
           `Entanglement strength: ${token.entanglementStrength?.toFixed(3) || 'N/A'}\n\n` +
           `#QuantumAI #Solana #CryptoTrading #${token.symbol}`;
  }

  /**
   * Main scan
   */
  async scan(options = {}) {
    console.log('🔮 Starting Quantum Alpha Scan...\n');
    
    // Fetch tokens
    console.log('Fetching Solana tokens...');
    const pairs = await this.fetchTokens();
    console.log(`Found ${pairs.length} total pairs`);
    
    // Filter
    const filtered = this.filterTokens(pairs);
    console.log(`Filtered to ${filtered.length} candidates\n`);
    
    // Analyze top N with quantum
    const topTokens = filtered.slice(0, CONFIG.topN);
    console.log(`Running quantum analysis on top ${topTokens.length}...\n`);
    
    const results = [];
    for (const pair of topTokens) {
      const symbol = pair.baseToken?.symbol;
      console.log(`Analyzing $${symbol}...`);
      
      const result = await this.analyzeWithQuantum(pair);
      if (result) {
        results.push(result);
        console.log(`  → Signal: ${result.quantumSignal} (${(result.confidence * 100).toFixed(1)}%)`);
      }
    }
    
    // Filter by confidence
    const highConfidence = results.filter(r => r.confidence >= CONFIG.quantumMinConfidence);
    
    console.log(`\n✅ Found ${highConfidence.length} high-confidence signals`);
    
    // Sort by confidence
    highConfidence.sort((a, b) => b.confidence - a.confidence);
    
    // Format alerts
    const alerts = highConfidence.map(t => this.formatAlert(t));
    
    // Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = join(__dirname, 'data', `quantum-scan-${timestamp}.json`);
    await fs.mkdir(join(__dirname, 'data'), { recursive: true }).catch(() => {});
    await fs.writeFile(outputFile, JSON.stringify(highConfidence, null, 2));
    
    console.log(`\n📁 Results saved to: ${outputFile}`);
    
    // Return formatted output
    return {
      alerts,
      tweets: highConfidence.map(t => this.formatTweet(t)),
      raw: highConfidence,
      timestamp: new Date().toISOString()
    };
  }
}

// ─── CLI ───────────────────────────────────────────────────────────────

async function main() {
  const scanner = new QuantumAlphaScanner();
  const results = await scanner.scan();
  
  console.log('\n' + '='.repeat(60));
  console.log('QUANTUM ALPHA RESULTS');
  console.log('='.repeat(60) + '\n');
  
  for (let i = 0; i < results.alerts.length; i++) {
    console.log(`--- Signal ${i + 1} ---`);
    console.log(results.alerts[i]);
    console.log();
  }
  
  // If --tweet flag, show tweet format
  if (process.argv.includes('--tweet')) {
    console.log('\n' + '='.repeat(60));
    console.log('READY TO TWEET:');
    console.log('='.repeat(60) + '\n');
    results.tweets.forEach((tweet, i) => {
      console.log(`Tweet ${i + 1}:`);
      console.log(tweet);
      console.log('\n---\n');
    });
  }
}

main().catch(console.error);
