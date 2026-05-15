#!/usr/bin/env node
/**
 * SENTIMENT ANALYZER
 * Tracks social sentiment, community growth, influencer mentions
 * Sources: DexScreener social data, manual Twitter scraping
 */

import { mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

class SentimentAnalyzer {
  constructor() {
    this.dataDir = join(__dirname, 'data', 'sentiment');
    mkdirSync(this.dataDir, { recursive: true });
  }

  async analyzeToken(symbol, ca) {
    console.log(`Analyzing sentiment for ${symbol}...`);
    
    // Fetch current DexScreener data which includes some social metrics
    const dexData = await this.fetchDexScreenerData(ca);
    
    // Calculate sentiment scores
    const sentiment = {
      symbol,
      ca,
      timestamp: new Date().toISOString(),
      
      // Volume-based sentiment (high volume = interest)
      volumeSentiment: this.calculateVolumeSentiment(dexData),
      
      // Transaction sentiment (buy/sell ratio)
      transactionSentiment: this.calculateTransactionSentiment(dexData),
      
      // Price momentum sentiment
      priceSentiment: this.calculatePriceSentiment(dexData),
      
      // Liquidity health
      liquidityHealth: this.calculateLiquidityHealth(dexData),
      
      // Age vs performance (new tokens with volume = hype)
      hypeScore: this.calculateHypeScore(dexData),
      
      // Overall composite
      composite: 0,
      
      // Raw data
      raw: dexData
    };
    
    // Calculate composite
    sentiment.composite = (
      sentiment.volumeSentiment * 0.25 +
      sentiment.transactionSentiment * 0.25 +
      sentiment.priceSentiment * 0.20 +
      sentiment.liquidityHealth * 0.15 +
      sentiment.hypeScore * 0.15
    );
    
    return sentiment;
  }

  async fetchDexScreenerData(ca) {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${ca}`, {
        timeout: 10000
      });
      
      if (!response.ok) return {};
      
      const data = await response.json();
      return data.pairs?.[0] || {};
    } catch (err) {
      return {};
    }
  }

  calculateVolumeSentiment(data) {
    const volume24h = parseFloat(data.volume?.h24) || 0;
    const volume1h = parseFloat(data.volume?.h1) || 0;
    const liquidity = parseFloat(data.liquidity?.usd) || 1;
    
    // Volume to liquidity ratio (high = active trading)
    const volLiqRatio = volume24h / liquidity;
    
    // Hourly momentum
    const hourlyRatio = volume1h * 24 / volume24h;
    
    let score = 0.5;
    
    if (volLiqRatio > 10) score += 0.3;
    else if (volLiqRatio > 5) score += 0.2;
    else if (volLiqRatio > 2) score += 0.1;
    else score -= 0.1;
    
    if (hourlyRatio > 1.5) score += 0.2; // Accelerating
    else if (hourlyRatio < 0.5) score -= 0.2; // Decelerating
    
    return Math.min(Math.max(score, 0), 1);
  }

  calculateTransactionSentiment(data) {
    const buys = parseInt(data.txns?.h24?.buys) || 0;
    const sells = parseInt(data.txns?.h24?.sells) || 1;
    const buySellRatio = buys / sells;
    
    const buy1h = parseInt(data.txns?.h1?.buys) || 0;
    const sell1h = parseInt(data.txns?.h1?.sells) || 1;
    const hourlyRatio = buy1h / sell1h;
    
    let score = 0.5;
    
    if (buySellRatio > 2) score += 0.3;
    else if (buySellRatio > 1.5) score += 0.2;
    else if (buySellRatio > 1.2) score += 0.1;
    else score -= 0.1;
    
    if (hourlyRatio > buySellRatio) score += 0.2; // Improving
    else if (hourlyRatio < buySellRatio) score -= 0.1; // Worsening
    
    return Math.min(Math.max(score, 0), 1);
  }

  calculatePriceSentiment(data) {
    const change24h = parseFloat(data.priceChange?.h24) || 0;
    const change1h = parseFloat(data.priceChange?.h1) || 0;
    const change5min = parseFloat(data.priceChange?.m5) || 0;
    
    let score = 0.5;
    
    // 24h trend
    if (change24h > 50) score += 0.3;
    else if (change24h > 20) score += 0.2;
    else if (change24h > 0) score += 0.1;
    else if (change24h < -50) score -= 0.3;
    else if (change24h < -20) score -= 0.2;
    else score -= 0.1;
    
    // Short term momentum
    if (change1h > 10) score += 0.2;
    else if (change1h < -10) score -= 0.2;
    
    if (change5min > 5) score += 0.1;
    else if (change5min < -5) score -= 0.1;
    
    return Math.min(Math.max(score, 0), 1);
  }

  calculateLiquidityHealth(data) {
    const liquidity = parseFloat(data.liquidity?.usd) || 0;
    const marketCap = parseFloat(data.marketCap) || 1;
    const liqMcapRatio = liquidity / marketCap;
    
    let score = 0.5;
    
    if (liqMcapRatio > 0.3) score += 0.4; // Very healthy
    else if (liqMcapRatio > 0.15) score += 0.2;
    else if (liqMcapRatio > 0.05) score += 0.0;
    else score -= 0.3; // Unhealthy
    
    // Absolute liquidity
    if (liquidity > 100000) score += 0.1;
    else if (liquidity < 5000) score -= 0.2;
    
    return Math.min(Math.max(score, 0), 1);
  }

  calculateHypeScore(data) {
    const age = data.pairCreatedAt 
      ? (Date.now() - data.pairCreatedAt) / 60000 
      : 9999;
    const volume24h = parseFloat(data.volume?.h24) || 0;
    const txns = (data.txns?.h24?.buys || 0) + (data.txns?.h24?.sells || 0);
    
    let score = 0.5;
    
    // New token with volume = hype
    if (age < 60 && volume24h > 10000) score += 0.4;
    else if (age < 240 && volume24h > 50000) score += 0.3;
    else if (age < 1440 && volume24h > 100000) score += 0.2;
    
    // High transaction count = active community
    if (txns > 1000) score += 0.2;
    else if (txns > 500) score += 0.1;
    else if (txns < 50) score -= 0.2;
    
    return Math.min(Math.max(score, 0), 1);
  }

  getSentimentLabel(score) {
    if (score >= 0.8) return 'VERY BULLISH';
    if (score >= 0.6) return 'BULLISH';
    if (score >= 0.4) return 'NEUTRAL';
    if (score >= 0.2) return 'BEARISH';
    return 'VERY BEARISH';
  }

  async saveSentiment(sentiment) {
    const filePath = join(this.dataDir, `${sentiment.symbol}-sentiment.json`);
    writeFileSync(filePath, JSON.stringify(sentiment, null, 2));
    return filePath;
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
  const analyzer = new SentimentAnalyzer();
  
  console.log('🔮 Sentiment Analysis\n');
  
  for (const [symbol, ca] of Object.entries(TRACKED_TOKENS)) {
    const sentiment = await analyzer.analyzeToken(symbol, ca);
    const label = analyzer.getSentimentLabel(sentiment.composite);
    
    console.log(`${symbol}: ${label} (${(sentiment.composite * 100).toFixed(1)}%)`);
    console.log(`  Volume: ${(sentiment.volumeSentiment * 100).toFixed(0)}%`);
    console.log(`  Transactions: ${(sentiment.transactionSentiment * 100).toFixed(0)}%`);
    console.log(`  Price: ${(sentiment.priceSentiment * 100).toFixed(0)}%`);
    console.log(`  Liquidity: ${(sentiment.liquidityHealth * 100).toFixed(0)}%`);
    console.log(`  Hype: ${(sentiment.hypeScore * 100).toFixed(0)}%\n`);
    
    await analyzer.saveSentiment(sentiment);
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(console.error);
}

export default SentimentAnalyzer;
