#!/usr/bin/env node
/**
 * UNIFIED ALPHA SCANNER
 * Finds both fresh launches and established opportunities
 * FIXED: Now deduplicates tokens
 * NEW: Optional Quantum AI analysis (--quantum flag)
 */

const CONFIG = {
  newLaunch: {
    maxAgeMinutes: 30,
    minAgeMinutes: 2,
    minLiquidity: 5000,
    minVolume: 1000,
    maxMarketCap: 1000000
  },
  alpha: {
    minLiquidity: 20000,
    minVolume: 50000,
    minMarketCap: 30000,
    maxMarketCap: 5000000,
    earlyPump: { min: 5, max: 35 },
    confirmed: { min: 35, max: 75 },
    dumpRange: { min: -30, max: -5 },
    reversal1H: 3,
    buySellRatio: 1.2,
    alertThreshold: 2
  }
};

async function fetchTokens() {
  // Retry logic for API failures
  const maxRetries = 3;
  const delay = ms => new Promise(r => setTimeout(r, ms));
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('https://api.dexscreener.com/latest/dex/search?q=solana', {
        timeout: 15000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      if (data.pairs && data.pairs.length > 0) {
        return data.pairs;
      }
      
      throw new Error('Empty response');
      
    } catch (e) {
      console.log(`Attempt ${i + 1}/${maxRetries} failed: ${e.message}`);
      if (i < maxRetries - 1) {
        await delay(2000 * (i + 1)); // Exponential backoff
      }
    }
  }
  
  console.error('❌ All fetch attempts failed. DexScreener API may be down.');
  return [];
}

function analyzeNewLaunch(p, now, seenAddresses) {
  const cfg = CONFIG.newLaunch;
  const age = (now - p.pairCreatedAt) / (1000 * 60);
  const address = p.baseToken?.address;
  
  if (!address || seenAddresses.has(address)) return null;
  if (!p.pairCreatedAt || age < cfg.minAgeMinutes || age > cfg.maxAgeMinutes) return null;
  
  const mcap = parseFloat(p.marketCap) || 0;
  const liq = parseFloat(p.liquidity?.usd) || 0;
  const vol = parseFloat(p.volume?.h24) || 0;
  
  if (mcap > cfg.maxMarketCap) return null;
  if (liq < cfg.minLiquidity) return null;
  if (vol < cfg.minVolume) return null;
  
  const buys = parseInt(p.txns?.h24?.buys) || 0;
  const sells = parseInt(p.txns?.h24?.sells) || 1;
  const buyPressure = sells > 0 ? buys / sells : buys;
  const earlyVolume = vol / age;
  const change = parseFloat(p.priceChange?.h24) || 0;
  
  let score = 0;
  if (age < 10) score += 3;
  else if (age < 20) score += 2;
  else score += 1;
  
  if (earlyVolume > 1000) score += 3;
  else if (earlyVolume > 500) score += 2;
  else if (earlyVolume > 100) score += 1;
  
  if (buyPressure > 2) score += 3;
  else if (buyPressure > 1.5) score += 2;
  else if (buyPressure > 1.2) score += 1;
  
  if (change > 0) score += 2;
  
  seenAddresses.add(address);
  
  return {
    type: 'NEW LAUNCH',
    symbol: p.baseToken?.symbol,
    address: address,
    age: Math.floor(age),
    price: parseFloat(p.priceUsd),
    marketCap: mcap,
    liquidity: liq,
    volume24h: vol,
    volumePerMin: earlyVolume,
    change24h: change,
    buyPressure: buyPressure.toFixed(2),
    dex: p.dexId,
    score: score,
    emoji: score >= 8 ? '🚀🚀🚀' : score >= 6 ? '🚀🚀' : score >= 4 ? '🚀' : '⚠️'
  };
}

function analyzeAlpha(p, now, seenAddresses) {
  const cfg = CONFIG.alpha;
  const age = (now - p.pairCreatedAt) / (1000 * 60);
  const address = p.baseToken?.address;
  
  if (!address || seenAddresses.has(address)) return null;
  if (age < CONFIG.newLaunch.maxAgeMinutes) return null;
  
  const mcap = parseFloat(p.marketCap) || 0;
  const liq = parseFloat(p.liquidity?.usd) || 0;
  const vol = parseFloat(p.volume?.h24) || 0;
  const change24h = parseFloat(p.priceChange?.h24) || 0;
  const change1h = parseFloat(p.priceChange?.h1) || 0;
  const buys = parseInt(p.txns?.h24?.buys) || 0;
  const sells = parseInt(p.txns?.h24?.sells) || 1;
  
  if (mcap < cfg.minMarketCap || mcap > cfg.maxMarketCap) return null;
  if (liq < cfg.minLiquidity) return null;
  if (vol < cfg.minVolume) return null;
  
  let score = 0;
  let pattern = null;
  let emoji = '📊';
  
  if (change24h >= cfg.dumpRange.min && change24h <= cfg.dumpRange.max) {
    if (change1h > cfg.reversal1H) {
      score += 3;
      pattern = '💎 BOTTOM';
      emoji = '💎';
    }
  }
  else if (change24h >= cfg.earlyPump.min && change24h <= cfg.earlyPump.max) {
    score += 2;
    pattern = '🚀 EARLY';
    emoji = '🚀';
  }
  else if (change24h >= cfg.confirmed.min && change24h <= cfg.confirmed.max) {
    score += 1;
    pattern = '📈 CONFIRMED';
    emoji = '📈';
  }
  
  if (buys/sells >= cfg.buySellRatio) score++;
  if (change1h > 5 && change24h < change1h) score++;
  
  if (score < cfg.alertThreshold) return null;
  
  seenAddresses.add(address);
  
  return {
    type: 'ALPHA',
    pattern: pattern,
    symbol: p.baseToken?.symbol,
    address: address,
    age: Math.floor(age / 60) + 'h',
    price: parseFloat(p.priceUsd),
    marketCap: mcap,
    liquidity: liq,
    volume24h: vol,
    change24h: change24h,
    change1h: change1h,
    buyPressure: (buys/sells).toFixed(2),
    dex: p.dexId,
    score: score,
    emoji: emoji
  };
}

// ─── QUANTUM AI INTEGRATION ─────────────────────────────────────────────

async function runQuantumAnalysis(tokens) {
  console.log('='.repeat(70));
  console.log('🔮 QUANTUM AI ANALYSIS');
  console.log('='.repeat(70) + '\n');
  
  try {
    // Dynamically import quantum predictor
    const { spawn } = await import('child_process');
    const { fileURLToPath } = await import('url');
    const { dirname, join } = await import('path');
    
    const __dirname = dirname(fileURLToPath(import.meta.url));
    
    // Analyze top 3 tokens with quantum
    const topTokens = tokens.slice(0, 3);
    
    for (const token of topTokens) {
      const priceChange = token.change24h || 0;
      const volumeChange = ((token.volume24h || 0) / 1000); // rough estimate
      const liq = token.liquidity || 0;
      
      // Prepare features for quantum analyzer
      const args = [
        (priceChange / 100).toString(),
        (volumeChange / 100).toString(),
        '0.5',  // rsi neutral
        '0',     // macd
        '0.6',   // sentiment
        '0.55',  // fear_greed
        '0.45',  // btc_dominance
        Math.min(liq / 50000, 1).toString(),  // liquidity
        '0.5',   // whale_activity
        Math.min((token.volume24h || 0) / 10000, 1).toString()  // social proxy
      ];
      
      // Run quantum analyzer
      const result = await new Promise((resolve, reject) => {
        const scriptPath = join(__dirname, '..', '..', '..', 'quantum_analyzer.py');
        const proc = spawn('python', [scriptPath, ...args]);
        
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
      
      if (result.signal) {
        const emoji = result.signal === 'BUY' ? '🚀' : result.signal === 'SELL' ? '📉' : '⏸️';
        console.log(`${emoji} Quantum Signal: ${result.signal} ${token.symbol}`);
        console.log(`   Confidence: ${(result.confidence * 100).toFixed(1)}%`);
        console.log(`   Quantum Features: ${result.quantum_features?.slice(0, 3).join(', ') || 'N/A'}`);
        console.log(`   Entanglement: ${result.entanglement_strength?.toFixed(3) || 'N/A'}\n`);
      }
    }
  } catch (err) {
    console.log(`❌ Quantum analysis skipped: ${err.message}\n`);
  }
}

// ─── MAIN ───────────────────────────────────────────────────────────────

async function main() {
  console.log('🔥 UNIFIED ALPHA SCANNER\n');
  console.log('Scanning: Fresh launches (2-30min) + Established setups (30min+)');
  
  const useQuantum = process.argv.includes('--quantum');
  if (useQuantum) {
    console.log('🔮 Quantum AI: ENABLED (--quantum flag)\n');
  } else {
    console.log('💡 Add --quantum for quantum AI analysis\n');
  }
  
  const tokens = await fetchTokens();
  const now = Date.now();
  const seenAddresses = new Set();
  
  const newLaunches = [];
  const alphaPlays = [];
  
  for (const p of tokens) {
    if (p.chainId !== 'solana') continue;
    
    const nl = analyzeNewLaunch(p, now, seenAddresses);
    if (nl) {
      newLaunches.push(nl);
      continue;
    }
    
    const alpha = analyzeAlpha(p, now, seenAddresses);
    if (alpha) alphaPlays.push(alpha);
  }
  
  console.log('='.repeat(70));
  console.log('🚀 NEW LAUNCHES (2-30 minutes old)');
  console.log('='.repeat(70) + '\n');
  
  if (newLaunches.length === 0) {
    console.log('❌ No fresh launches found\n');
  } else {
    newLaunches.sort((a, b) => b.score - a.score);
    for (const t of newLaunches.slice(0, 5)) {
      console.log(`${t.emoji} ${t.symbol}`);
      console.log(`  Age: ${t.age}min | Score: ${t.score}/10 | ${t.type}`);
      console.log(`  MCap: $${(t.marketCap/1000).toFixed(1)}K | Vol/min: $${t.volumePerMin.toFixed(0)}`);
      console.log(`  Buy: ${t.buyPressure}:1 | 24H: ${t.change24h.toFixed(1)}%`);
      console.log(`  ${t.address}\n`);
    }
  }
  
  console.log('='.repeat(70));
  console.log('💎 ALPHA PLAYS (30+ minutes, longer holds)');
  console.log('='.repeat(70) + '\n');
  
  if (alphaPlays.length === 0) {
    console.log('❌ No alpha setups found\n');
  } else {
    const priority = { '💎 BOTTOM': 3, '🚀 EARLY': 2, '📈 CONFIRMED': 1 };
    alphaPlays.sort((a, b) => {
      const pDiff = (priority[b.pattern] || 0) - (priority[a.pattern] || 0);
      if (pDiff !== 0) return pDiff;
      return b.score - a.score;
    });
    
    for (const t of alphaPlays.slice(0, 5)) {
      console.log(`${t.emoji} ${t.symbol}`);
      console.log(`  Pattern: ${t.pattern} | Score: ${t.score}/5`);
      console.log(`  Age: ${t.age} | MCap: $${(t.marketCap/1000).toFixed(1)}K`);
      console.log(`  24H: ${t.change24h >= 0 ? '+' : ''}${t.change24h.toFixed(1)}% | 1H: ${t.change1h >= 0 ? '+' : ''}${t.change1h.toFixed(1)}%`);
      console.log(`  Buy: ${t.buyPressure}:1 | Vol: $${(t.volume24h/1000).toFixed(1)}K`);
      console.log(`  ${t.address}\n`);
    }
  }
  
  // ─── QUANTUM AI ANALYSIS ──────────────────────────────────────
  if (useQuantum) {
    const allTokens = [...newLaunches, ...alphaPlays];
    if (allTokens.length > 0) {
      await runQuantumAnalysis(allTokens);
    } else {
      console.log('='.repeat(70));
      console.log('🔮 QUANTUM AI ANALYSIS');
      console.log('='.repeat(70));
      console.log('❌ No tokens to analyze\n');
    }
  }
  
  console.log('='.repeat(70));
  console.log('SUMMARY');
  console.log('='.repeat(70));
  console.log(`New Launches: ${newLaunches.length}`);
  console.log(`Alpha Plays: ${alphaPlays.length}`);
  console.log(`Total Opportunities: ${newLaunches.length + alphaPlays.length}`);
  if (useQuantum) console.log(`Quantum AI: Active`);
  console.log('='.repeat(70));
}

main().catch(console.error);
