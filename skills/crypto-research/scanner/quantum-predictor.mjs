#!/usr/bin/env node
/**
 * QUANTUM ML PREDICTOR
 * Integrates PennyLane quantum circuits with Cortex crypto scanner
 * 
 * Features:
 * - Quantum-enhanced signal analysis
 * - Quantum feature extraction for better predictions  
 * - Quantum portfolio optimization
 * - Live integration with scanner pipeline
 * 
 * Requires: quantum_analyzer.py, quantum_features.py, quantum_portfolio.py
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to quantum scripts (in root workspace)
const QUANTUM_DIR = join(__dirname, '..', '..', '..');

class QuantumPredictor {
  constructor() {
    this.pythonPath = 'python';
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Run Python quantum script and get JSON results
   */
  async runQuantumScript(scriptName, args = []) {
    return new Promise((resolve, reject) => {
      const scriptPath = join(QUANTUM_DIR, scriptName);
      const pythonProcess = spawn(this.pythonPath, [scriptPath, ...args]);
      
      let output = '';
      let errorOutput = '';
      
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Quantum script error: ${errorOutput}`);
          reject(new Error(`Script failed: ${errorOutput}`));
        } else {
          try {
            // Extract JSON from output
            const jsonMatch = output.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              resolve(JSON.parse(jsonMatch[0]));
            } else {
              resolve({ raw: output.trim() });
            }
          } catch (e) {
            resolve({ raw: output.trim() });
          }
        }
      });
      
      pythonProcess.on('error', (err) => reject(err));
    });
  }

  /**
   * 1. QUANTUM SIGNAL ANALYSIS
   * Get quantum-enhanced buy/sell/hold signal from market data
   */
  async analyzeSignal(tokenData) {
    const cacheKey = `signal_${tokenData.symbol}_${Date.now()}`;
    
    // Extract features from token data
    const features = this.extractFeatures(tokenData);
    
    // Normalize to 0-1 range
    const args = [
      features.priceChange.toString(),
      features.volumeChange.toString(),
      features.rsi.toString(),
      features.macd.toString(),
      features.sentiment.toString(),
      features.fearGreed.toString(),
      features.btcDominance.toString(),
      features.liquidity.toString(),
      features.whaleActivity.toString(),
      features.socialVolume.toString()
    ];

    try {
      const result = await this.runQuantumScript('quantum_analyzer.py', args);
      
      return {
        symbol: tokenData.symbol,
        signal: result.signal,  // BUY, HOLD, SELL
        confidence: result.confidence,
        probabilities: result.probabilities,
        quantumFeatures: result.quantum_features,
        entanglementStrength: result.entanglement_strength,
        method: 'quantum_hybrid',
        timestamp: new Date().toISOString(),
        rawData: tokenData
      };
    } catch (error) {
      console.error('Quantum analysis failed, using fallback:', error.message);
      return this.fallbackSignal(tokenData);
    }
  }

  /**
   * 2. QUANTUM FEATURE EXTRACTION
   * Get enhanced feature representation for ML models
   */
  async extractQuantumFeatures(featureVector) {
    const args = featureVector.map(f => f.toString());
    
    try {
      const result = await this.runQuantumScript('quantum_features.py', args);
      return {
        enhancedFeatures: result.enhanced_features,
        originalDim: result.original_dim,
        quantumDim: result.quantum_dim,
        totalDim: result.total_dim,
        featureBoost: result.feature_boost,
        method: 'quantum_extraction'
      };
    } catch (error) {
      console.error('Feature extraction failed:', error.message);
      return { features: featureVector, method: 'classical_fallback' };
    }
  }

  /**
   * 3. QUANTUM PORTFOLIO OPTIMIZATION
   * Optimize capital allocation across lead traders
   */
  async optimizePortfolio(traders, capital, riskProfile = 'balanced') {
    try {
      // Create temp file with trader data
      const tempFile = join(QUANTUM_DIR, 'temp_traders.json');
      const fs = await import('fs/promises');
      
      await fs.writeFile(tempFile, JSON.stringify({
        traders,
        capital,
        risk_profile: riskProfile
      }));

      // Run portfolio optimizer
      const result = await this.runQuantumScript('quantum_portfolio.py', [
        '--json'
      ]);

      // Clean up
      await fs.unlink(tempFile).catch(() => {});

      return {
        allocations: result.trader_allocations,
        expectedReturn: result.expected_portfolio_return,
        riskScore: result.portfolio_risk_score,
        method: 'quantum_qaoa',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Portfolio optimization failed:', error.message);
      return this.fallbackPortfolio(traders, capital);
    }
  }

  /**
   * Extract normalized features from token data
   */
  extractFeatures(tokenData) {
    const price = tokenData.price || {};
    const volume = tokenData.volume || {};
    const liquidity = tokenData.liquidity || {};
    
    return {
      priceChange: Math.min(Math.max((tokenData.priceChange24h || 0) / 100, -1), 1),
      volumeChange: Math.min(Math.max((volume.change24h || 0) / 100, 0), 1),
      rsi: (tokenData.rsi || 50) / 100,
      macd: Math.tanh(tokenData.macd || 0),
      sentiment: Math.min(Math.max(tokenData.sentiment || 0.5, 0), 1),
      fearGreed: (tokenData.fearGreed || 50) / 100,
      btcDominance: Math.min(Math.max(tokenData.btcDominance || 0.45, 0), 1),
      liquidity: Math.min(Math.max((liquidity.usd || 0) / 50000, 0), 1),
      whaleActivity: Math.min(Math.max(tokenData.whaleActivity || 0.5, 0), 1),
      socialVolume: Math.min(Math.max(tokenData.socialVolume || 0.5, 0), 1)
    };
  }

  /**
   * Classical fallback when quantum fails
   */
  fallbackSignal(tokenData) {
    const change = tokenData.priceChange24h || 0;
    const volume = tokenData.volume?.change24h || 0;
    const rsi = tokenData.rsi || 50;
    
    let signal = 'HOLD';
    let confidence = 0.5;

    if (change > 10 && volume > 50 && rsi < 70) {
      signal = 'BUY';
      confidence = 0.7;
    } else if (change < -10 && rsi > 60) {
      signal = 'SELL';
      confidence = 0.7;
    }

    return {
      symbol: tokenData.symbol,
      signal,
      confidence,
      method: 'classical_fallback',
      timestamp: new Date().toISOString()
    };
  }

  fallbackPortfolio(traders, capital) {
    const equalAlloc = capital / traders.length;
    return {
      allocations: traders.map((t, i) => ({
        trader_id: i,
        allocation_usd: equalAlloc,
        allocation_pct: (100 / traders.length).toFixed(1),
        metrics: t
      })),
      method: 'classical_equal_weight'
    };
  }

  /**
   * Format quantum signal for display/alerts
   */
  formatSignal(signal) {
    const emojis = { BUY: '🚀', HOLD: '⏸️', SELL: '📉' };
    const emoji = emojis[signal.signal] || '❓';
    
    return `${emoji} **${signal.signal}** ${signal.symbol}
Confidence: ${(signal.confidence * 100).toFixed(1)}%
Method: ${signal.method}
Quantum Features: ${signal.quantumFeatures?.slice(0, 3).join(', ') || 'N/A'}
Entanglement: ${signal.entanglementStrength || 'N/A'}`;
  }
}

// ─── CLI / TEST ───────────────────────────────────────────────

async function runTests() {
  const predictor = new QuantumPredictor();
  
  console.log('🧪 Quantum Predictor Tests\n');
  
  // Test 1: Signal Analysis
  console.log('1️⃣ Testing Signal Analysis...');
  const testToken = {
    symbol: 'TEST_TOKEN',
    priceChange24h: 25,
    volume: { change24h: 150 },
    rsi: 65,
    macd: 0.3,
    sentiment: 0.8,
    fearGreed: 75,
    btcDominance: 0.45,
    liquidity: { usd: 30000 },
    whaleActivity: 0.9,
    socialVolume: 0.85
  };
  
  const signal = await predictor.analyzeSignal(testToken);
  console.log('Result:', JSON.stringify(signal, null, 2));
  console.log();
  
  // Test 2: Feature Extraction
  console.log('2️⃣ Testing Feature Extraction...');
  const features = [0.25, 1.5, 0.45, 2.3, 0.75, 0.68, 0.25, 0.8];
  const enhanced = await predictor.extractQuantumFeatures(features);
  console.log('Enhanced:', enhanced.totalDim, 'features');
  console.log('Boost:', enhanced.featureBoost);
  console.log();
  
  // Test 3: Portfolio
  console.log('3️⃣ Testing Portfolio Optimization...');
  const traders = [
    { win_rate: 0.80, avg_return: 0.15, max_drawdown: 0.20, consistency_score: 0.75 },
    { win_rate: 0.65, avg_return: 0.25, max_drawdown: 0.35, consistency_score: 0.60 },
    { win_rate: 0.90, avg_return: 0.08, max_drawdown: 0.10, consistency_score: 0.90 },
  ];
  const portfolio = await predictor.optimizePortfolio(traders, 500, 'balanced');
  console.log('Portfolio:', JSON.stringify(portfolio, null, 2));
  
  console.log('\n✅ All quantum tests complete!');
}

// Run tests if called directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  runTests().catch(console.error);
}

export default QuantumPredictor;
