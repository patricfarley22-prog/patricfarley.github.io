const { spawn } = require('child_process');
const path = require('path');

/**
 * Quantum-Enhanced Crypto Scanner
 * Integrates PennyLane QML modules with existing Cortex systems
 * 
 * Features:
 * - Quantum signal analysis for buy/sell/hold decisions
 * - Quantum feature extraction for ML models
 * - Quantum portfolio optimization for copy trading
 */

class QuantumScanner {
    constructor() {
        this.pythonPath = 'python';
        this.scriptsDir = __dirname;
    }

    /**
     * Run a Python script and return JSON output
     */
    async runPythonScript(scriptName, args = []) {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(this.scriptsDir, scriptName);
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
                    console.error(`Python script error: ${errorOutput}`);
                    reject(new Error(`Script failed with code ${code}: ${errorOutput}`));
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
            
            pythonProcess.on('error', (err) => {
                reject(err);
            });
        });
    }

    /**
     * Run a Python script with stdin input and return JSON output
     */
    async runPythonScriptStdin(scriptName, args = [], stdinData = '') {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(this.scriptsDir, scriptName);
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
                    console.error(`Python script error: ${errorOutput}`);
                    reject(new Error(`Script failed with code ${code}: ${errorOutput}`));
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
            
            pythonProcess.on('error', (err) => {
                reject(err);
            });
            
            // Write stdin data
            if (stdinData) {
                pythonProcess.stdin.write(stdinData);
                pythonProcess.stdin.end();
            }
        });
    }

    /**
     * 1. QUANTUM SIGNAL ANALYSIS
     * Get quantum-enhanced buy/sell/hold signal
     */
    async analyzeSignal(marketData) {
        const {
            priceChange = 0,
            volumeChange = 0,
            rsi = 50,
            macd = 0,
            sentiment = 0.5,
            fearGreed = 50,
            btcDominance = 0.45,
            liquidity = 0.5,
            whaleActivity = 0.5,
            socialVolume = 0.5
        } = marketData;

        // Normalize inputs to 0-1 range
        const args = [
            (priceChange / 100).toString(),
            (volumeChange / 100).toString(),
            (rsi / 100).toString(),
            (macd / 10).toString(),
            sentiment.toString(),
            (fearGreed / 100).toString(),
            btcDominance.toString(),
            liquidity.toString(),
            whaleActivity.toString(),
            socialVolume.toString()
        ];

        try {
            const result = await this.runPythonScript('quantum_analyzer.py', args);
            return {
                ...result,
                timestamp: new Date().toISOString(),
                market_data: marketData,
                method: 'quantum_hybrid'
            };
        } catch (error) {
            console.error('Quantum analyzer error:', error);
            return this.fallbackSignal(marketData);
        }
    }

    /**
     * 2. QUANTUM FEATURE EXTRACTION
     * Extract quantum-enhanced features for ML models
     */
    async extractFeatures(featureVector) {
        const args = featureVector.map(f => f.toString());
        
        try {
            const result = await this.runPythonScript('quantum_features.py', args);
            return {
                ...result,
                timestamp: new Date().toISOString(),
                method: 'quantum_feature_extraction'
            };
        } catch (error) {
            console.error('Feature extraction error:', error);
            return { error: error.message, features: featureVector };
        }
    }

    /**
     * 3. QUANTUM PORTFOLIO OPTIMIZATION
     * Optimize copy trading capital allocation
     */
    async optimizePortfolio(traders, capital, riskProfile = 'balanced') {
        try {
            // Pass data via stdin to avoid temp files
            const inputData = JSON.stringify({
                traders,
                capital,
                risk_profile: riskProfile
            });
            
            const result = await this.runPythonScriptStdin('quantum_portfolio.py', ['--json'], inputData);

            return {
                ...result,
                timestamp: new Date().toISOString(),
                method: 'quantum_qaoa'
            };
        } catch (error) {
            console.error('Portfolio optimization error:', error);
            return this.fallbackPortfolio(traders, capital);
        }
    }

    /**
     * Fallback signal if quantum module fails
     */
    fallbackSignal(marketData) {
        const { priceChange, volumeChange, rsi } = marketData;
        let signal = 'HOLD';
        let confidence = 0.5;

        if (priceChange > 10 && volumeChange > 50 && rsi < 70) {
            signal = 'BUY';
            confidence = 0.7;
        } else if (priceChange < -10 && rsi > 60) {
            signal = 'SELL';
            confidence = 0.7;
        }

        return {
            signal,
            confidence,
            method: 'classical_fallback',
            market_data: marketData
        };
    }

    /**
     * Fallback portfolio if quantum module fails
     */
    fallbackPortfolio(traders, capital) {
        const equalAlloc = capital / traders.length;
        return {
            trader_allocations: traders.map((t, i) => ({
                trader_id: i,
                allocation_usd: equalAlloc,
                allocation_pct: (100 / traders.length).toFixed(1),
                metrics: t
            })),
            total_capital: capital,
            method: 'classical_equal_weight',
            fallback: true
        };
    }

    /**
     * Run all quantum analyses on a token
     */
    async fullAnalysis(tokenData, traders = null, capital = null) {
        const results = {
            signal: null,
            features: null,
            portfolio: null,
            timestamp: new Date().toISOString()
        };

        // 1. Signal Analysis
        if (tokenData) {
            results.signal = await this.analyzeSignal(tokenData);
        }

        // 2. Feature Extraction
        if (tokenData.features) {
            results.features = await this.extractFeatures(tokenData.features);
        }

        // 3. Portfolio Optimization
        if (traders && capital) {
            results.portfolio = await this.optimizePortfolio(traders, capital);
        }

        return results;
    }

    /**
     * Format results for display
     */
    formatResults(results) {
        const lines = [];
        
        if (results.signal) {
            const s = results.signal;
            lines.push(`Quantum Signal: ${s.signal} (${(s.confidence * 100).toFixed(1)}% confidence)`);
            if (s.quantum_features) {
                lines.push(`  Quantum Features: ${s.quantum_features.slice(0, 4).join(', ')}...`);
            }
        }

        if (results.features) {
            const f = results.features;
            lines.push(`Feature Enhancement: ${f.feature_boost || 'N/A'}`);
        }

        if (results.portfolio) {
            const p = results.portfolio;
            lines.push(`Portfolio Optimization: ${p.optimization_method || 'QAOA'}`);
            if (p.trader_allocations) {
                p.trader_allocations.forEach(ta => {
                    if (ta.allocation_usd > 10) {
                        lines.push(`  Trader ${ta.trader_id}: $${ta.allocation_usd} (${ta.allocation_pct}%)`);
                    }
                });
            }
        }

        return lines.join('\n');
    }
}

// CLI usage
if (require.main === module) {
    const scanner = new QuantumScanner();
    
    const args = process.argv.slice(2);
    const command = args[0];

    if (command === 'test') {
        console.log('Running Quantum Scanner Tests...\n');
        
        // Test 1: Signal Analysis
        console.log('Test 1: Signal Analysis');
        scanner.analyzeSignal({
            priceChange: 25,
            volumeChange: 150,
            rsi: 65,
            macd: 0.3,
            sentiment: 0.8,
            fearGreed: 75,
            btcDominance: 0.45,
            liquidity: 0.6,
            whaleActivity: 0.9,
            socialVolume: 0.85
        }).then(result => {
            console.log(result);
            console.log();
        });

    } else if (command === 'features') {
        console.log('Test 2: Feature Extraction');
        const features = [0.25, 1.5, 0.45, 2.3, 0.75, 0.68, 0.25, 0.8];
        scanner.extractFeatures(features).then(result => {
            console.log(result);
        });

    } else if (command === 'portfolio') {
        console.log('Test 3: Portfolio Optimization');
        const traders = [
            { win_rate: 0.80, avg_return: 0.15, max_drawdown: 0.20, consistency_score: 0.75 },
            { win_rate: 0.65, avg_return: 0.25, max_drawdown: 0.35, consistency_score: 0.60 },
            { win_rate: 0.90, avg_return: 0.08, max_drawdown: 0.10, consistency_score: 0.90 },
        ];
        scanner.optimizePortfolio(traders, 500, 'balanced').then(result => {
            console.log(JSON.stringify(result, null, 2));
        });

    } else {
        console.log('Quantum Scanner - Usage:');
        console.log('  node quantum-scanner.js test      - Test signal analysis');
        console.log('  node quantum-scanner.js features  - Test feature extraction');
        console.log('  node quantum-scanner.js portfolio  - Test portfolio optimization');
        console.log();
        console.log('Programmatic usage:');
        console.log('  const scanner = new QuantumScanner();');
        console.log('  const results = await scanner.fullAnalysis(tokenData, traders, capital);');
    }
}

module.exports = QuantumScanner;
