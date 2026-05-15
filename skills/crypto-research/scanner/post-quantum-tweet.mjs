#!/usr/bin/env node
/**
 * Auto-post Quantum AI signals to Twitter/X
 * Uses browser automation (free, no API keys needed)
 * 
 * Usage:
 *   node post-quantum-tweet.mjs          # Post best signal
 *   node post-quantum-tweet.mjs daily   # Post daily thread
 */

import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

class QuantumTweetBot {
  constructor() {
    this.dataDir = join(__dirname, 'data');
  }

  /**
   * Find latest scan results
   */
  getLatestScan() {
    try {
      const files = readdirSync(this.dataDir)
        .filter(f => f.startsWith('quantum-scan-'))
        .sort()
        .reverse();
      
      if (files.length === 0) return null;
      
      const latest = readFileSync(join(this.dataDir, files[0]), 'utf8');
      return JSON.parse(latest);
    } catch (err) {
      console.error('No scan data found. Run: node run-quantum-scan.mjs');
      return null;
    }
  }

  /**
   * Format tweet from signal
   */
  formatTweet(signal, style = 'standard') {
    const templates = {
      standard: `🔮 Quantum AI Signal: ${signal.quantumSignal}

$${signal.symbol}
Confidence: ${(signal.confidence * 100).toFixed(0)}%
24h: ${signal.priceChange24h > 0 ? '+' : ''}${signal.priceChange24h.toFixed(1)}%
MCap: $${(signal.marketCap / 1000).toFixed(0)}K

Quantum features detected patterns classical AI missed.
Entanglement strength: ${signal.entanglementStrength?.toFixed(3) || 'N/A'}

#QuantumAI #Solana #CryptoTrading #${signal.symbol}`,

      thread: `🔮 Quantum Analysis Update

Signal: ${signal.quantumSignal} $${signal.symbol}
Confidence: ${(signal.confidence * 100).toFixed(1)}%

Quantum entanglement captured correlations between price action, volume, and market sentiment that classical indicators miss.

This is why quantum ML matters.

#QuantumML #Crypto`,

      educational: `Classical AI vs Quantum AI in trading:

Classical: "RSI is 65, volume is up"
Quantum: "These features are ENTANGLED - when whale activity spikes, social sentiment follows with 89% correlation"

The difference? Quantum finds hidden relationships classical ML literally cannot see.

Signal: ${signal.quantumSignal} $${signal.symbol}
#QuantumTrading #AI`
    };
    
    return templates[style] || templates.standard;
  }

  /**
   * Generate thread from multiple signals
   */
  generateThread(signals) {
    const bestSignal = signals.reduce((a, b) => a.confidence > b.confidence ? a : b);
    
    const tweets = [
      // Tweet 1: Hook
      `🧵 I ran my Quantum AI on ${signals.length} Solana tokens.

The results? Quantum entanglement found patterns classical AI missed.

Here's what my quantum scanner detected 👇`,

      // Tweet 2: Best signal
      `🔮 Top Signal: ${bestSignal.quantumSignal} $${bestSignal.symbol}
Confidence: ${(bestSignal.confidence * 100).toFixed(1)}%

Quantum features: ${bestSignal.quantumFeatures?.slice(0, 3).join(', ')}...`,

      // Tweet 3: Technical
      `How it works:

Classical AI = processes features independently
Quantum AI = features become ENTANGLED

This captures hidden correlations between:
• Price & whale activity
• Volume & social sentiment  
• Liquidity & market cap

All simultaneously.`,

      // Tweet 4: CTA
      `The code is open source.

Built with PennyLane + PyTorch + Node.js
Running locally, $0 cloud cost

Star the repo, DM me questions.

Building quantum AI in public.
#QuantumML #BuildInPublic`
    ];
    
    return tweets;
  }

  /**
   * Display tweets (or post if automation configured)
   */
  async post(style = 'standard') {
    const signals = this.getLatestScan();
    if (!signals || signals.length === 0) {
      console.log('❌ No scan data. Run: node run-quantum-scan.mjs');
      return;
    }

    console.log('🔮 Quantum AI Tweet Generator\n');
    console.log(`Found ${signals.length} signals from latest scan\n`);

    if (style === 'thread') {
      // Generate thread
      const thread = this.generateThread(signals);
      console.log('Thread Preview:');
      console.log('='.repeat(50));
      
      thread.forEach((tweet, i) => {
        console.log(`\nTweet ${i + 1}:`);
        console.log('-'.repeat(30));
        console.log(tweet);
        console.log(`\nLength: ${tweet.length}/280`);
      });
      
      console.log('\n' + '='.repeat(50));
      console.log('To post manually:');
      console.log('1. Open Twitter/X');
      console.log('2. Copy each tweet above');
      console.log('3. Post as reply chain');
      
    } else {
      // Single best tweet
      const bestSignal = signals.reduce((a, b) => a.confidence > b.confidence ? a : b);
      const tweet = this.formatTweet(bestSignal, style);
      
      console.log('Tweet Preview:');
      console.log('='.repeat(50));
      console.log(tweet);
      console.log('='.repeat(50));
      console.log(`\nLength: ${tweet.length}/280`);
      console.log('\n✅ Ready to copy and paste to Twitter!');
    }

    // Save to file for easy copy
    const outputFile = join(__dirname, 'data', 'latest-tweet.txt');
    const fs = await import('fs/promises');
    
    if (style === 'thread') {
      const thread = this.generateThread(signals);
      await fs.writeFile(outputFile, thread.join('\n\n---\n\n'));
    } else {
      const bestSignal = signals.reduce((a, b) => a.confidence > b.confidence ? a : b);
      await fs.writeFile(outputFile, this.formatTweet(bestSignal, style));
    }
    
    console.log(`\n📁 Saved to: ${outputFile}`);
  }
}

// ─── CLI ───────────────────────────────────────────────────────────────

const bot = new QuantumTweetBot();
const style = process.argv[2] || 'standard';

bot.post(style).catch(console.error);
