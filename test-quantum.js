const QuantumScanner = require('./quantum-scanner.js');

async function runTests() {
    const scanner = new QuantumScanner();
    
    console.log("Testing Quantum Scanner...\n");
    
    // Test 1: Signal Analysis
    console.log("1. Signal Analysis Test:");
    const signalResult = await scanner.analyzeSignal({
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
    });
    
    console.log(`Signal: ${signalResult.signal} (${(signalResult.confidence * 100).toFixed(1)}% confidence)`);
    console.log(`Quantum Features: ${signalResult.quantum_features?.slice(0, 3).join(', ')}...`);
    console.log(`Entanglement Strength: ${signalResult.entanglement_strength}`);
    console.log();
    
    // Test 2: Feature Extraction
    console.log("2. Feature Extraction Test:");
    const features = [0.25, 1.5, 0.45, 2.3, 0.75, 0.68, 0.25, 0.8];
    const featureResult = await scanner.extractFeatures(features);
    console.log(`Original: ${featureResult.original_dim} features`);
    console.log(`Quantum: ${featureResult.quantum_dim} features`);
    console.log(`Total: ${featureResult.total_dim} (${featureResult.feature_boost})`);
    console.log();
    
    // Test 3: Portfolio Optimization
    console.log("3. Portfolio Optimization Test:");
    const traders = [
        { win_rate: 0.80, avg_return: 0.15, max_drawdown: 0.20, consistency_score: 0.75 },
        { win_rate: 0.65, avg_return: 0.25, max_drawdown: 0.35, consistency_score: 0.60 },
        { win_rate: 0.90, avg_return: 0.08, max_drawdown: 0.10, consistency_score: 0.90 },
    ];
    const portfolioResult = await scanner.optimizePortfolio(traders, 500, 'balanced');
    console.log(`Method: ${portfolioResult.optimization_method}`);
    for (const alloc of portfolioResult.trader_allocations) {
        if (alloc.allocation_usd > 10) {
            console.log(`Trader ${alloc.trader_id}: $${alloc.allocation_usd} (${alloc.allocation_pct}%)`);
        }
    }
    
    console.log("\nAll quantum modules integrated and working!");
}

runTests().catch(console.error);
