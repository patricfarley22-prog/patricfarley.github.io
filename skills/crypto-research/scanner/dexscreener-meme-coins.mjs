#!/usr/bin/env node
/**
 * DEXSCREENER MEME COIN FETCHER
 * Gets Solana meme coins from DexScreener (no rate limits like CoinGecko)
 */

import { writeFileSync, mkdirSync, existsSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const MEME_KEYWORDS = [
  'bonk', 'wif', 'dogwifhat', 'pepe', 'floki', 'shib', 'doge',
  'fartcoin', 'mog', 'giga', 'popcat', 'michi', 'boden', 'tremp',
  'retardio', 'zerebro', 'ai16z', 'fwog', 'pnut', 'sloth',
  'bome', 'wobb', 'pengo', 'toka', 'omegax', 'hachi', 'troll',
  'dust', 'blue', 'chip', 'royal', 'lab', 'apepe', 'bill'
];

class DexScreenerMemeCoins {
  constructor() {
    this.dataDir = join(__dirname, 'data', 'dexscreener');
    mkdirSync(this.dataDir, { recursive: true });
    this.cacheFile = join(this.dataDir, 'meme-coins-cache.json');
  }

  async fetchSolanaTokens() {
    console.log('Fetching Solana tokens from DexScreener...');
    
    try {
      // DexScreener search for Solana
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

  identifyMemeCoins(pairs) {
    console.log('Identifying meme coins...');
    
    const memeCoins = [];
    const seen = new Set();
    
    for (const pair of pairs) {
      const symbol = (pair.baseToken?.symbol || '').toLowerCase();
      const name = (pair.baseToken?.name || '').toLowerCase();
      const ca = pair.baseToken?.address;
      
      if (!ca || seen.has(ca)) continue;
      
      const isMeme = MEME_KEYWORDS.some(kw => 
        symbol.includes(kw) || name.includes(kw)
      );
      
      // Additional heuristics
      const mcap = pair.marketCap || 0;
      const volume = pair.volume?.h24 || 0;
      const liq = pair.liquidity?.usd || 0;
      
      // High volume relative to market cap = meme/speculative
      if (mcap > 0 && volume / mcap > 0.3) {
        // Could be meme
      }
      
      if (isMeme && mcap > 0 && mcap < 1_000_000_000) {
        seen.add(ca);
        memeCoins.push({
          symbol: pair.baseToken?.symbol?.toUpperCase() || 'UNKNOWN',
          name: pair.baseToken?.name || 'Unknown',
          ca: ca,
          price: parseFloat(pair.priceUsd) || 0,
          marketCap: mcap,
          volume24h: volume,
          liquidity: liq,
          priceChange24h: parseFloat(pair.priceChange?.h24) || 0,
          priceChange1h: parseFloat(pair.priceChange?.h1) || 0,
          dexId: pair.dexId,
          pairAddress: pair.pairAddress,
          age: pair.pairCreatedAt 
            ? Math.floor((Date.now() - pair.pairCreatedAt) / 60000)
            : 0,
          txns24h: (pair.txns?.h24?.buys || 0) + (pair.txns?.h24?.sells || 0),
          buyRatio: pair.txns?.h24?.buys / (pair.txns?.h24?.sells || 1)
        });
      }
    }
    
    // Sort by market cap
    memeCoins.sort((a, b) => b.marketCap - a.marketCap);
    
    return memeCoins;
  }

  async fetchWithRetry(ca, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${ca}`, {
          timeout: 10000
        });
        
        if (!response.ok) {
          if (i < maxRetries - 1) {
            await new Promise(r => setTimeout(r, 1000 * (i + 1)));
            continue;
          }
          return null;
        }
        
        const data = await response.json();
        return data.pairs?.[0] || null;
      } catch (err) {
        if (i < maxRetries - 1) {
          await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        }
      }
    }
    return null;
  }

  async collectAll() {
    console.log('=' .repeat(80));
    console.log('DEXSCREENER MEME COIN COLLECTOR');
    console.log('Fetching Solana meme coins with full data');
    console.log('=' .repeat(80));
    console.log();
    
    // Fetch all pairs
    const pairs = await this.fetchSolanaTokens();
    console.log(`Found ${pairs.length} total pairs`);
    
    // Identify meme coins
    const memeCoins = this.identifyMemeCoins(pairs);
    console.log(`Identified ${memeCoins.length} meme coins under $1B`);
    console.log();
    
    // Fetch detailed data for each
    const results = [];
    
    for (let i = 0; i < memeCoins.length; i++) {
      const coin = memeCoins[i];
      console.log(`[${i + 1}/${memeCoins.length}] Fetching ${coin.symbol}...`);
      
      const detailed = await this.fetchWithRetry(coin.ca);
      
      if (detailed) {
        coin.price = parseFloat(detailed.priceUsd) || coin.price;
        coin.marketCap = detailed.marketCap || coin.marketCap;
        coin.volume24h = detailed.volume?.h24 || coin.volume24h;
        coin.liquidity = detailed.liquidity?.usd || coin.liquidity;
        coin.priceChange24h = parseFloat(detailed.priceChange?.h24) || coin.priceChange24h;
        coin.priceChange1h = parseFloat(detailed.priceChange?.h1) || 0;
        coin.priceChange7d = parseFloat(detailed.priceChange?.h7) || 0;
      }
      
      results.push(coin);
      
      // Rate limiting (DexScreener is more generous but let's be nice)
      if (i < memeCoins.length - 1) {
        await new Promise(r => setTimeout(r, 500));
      }
    }
    
    // Save cache
    writeFileSync(this.cacheFile, JSON.stringify({
      timestamp: new Date().toISOString(),
      count: results.length,
      coins: results
    }, null, 2));
    
    // Display summary
    this.displaySummary(results);
    
    return results;
  }

  displaySummary(coins) {
    console.log('\n' + '=' .repeat(80));
    console.log('MEME COINS SUMMARY (Under $1B Market Cap)');
    console.log('=' .repeat(80));
    console.log();
    
    console.log(`${'#':<4} ${'Symbol':<8} ${'Price':<12} ${'MCap':<10} ${'24h Vol':<12} ${'24h':<8} ${'Age':<8} ${'Trend':<8}`);
    console.log('-'.repeat(80));
    
    coins.forEach((coin, i) => {
      const trend = coin.priceChange24h > 0 ? 'UP' : 'DOWN';
      const ageStr = coin.age < 60 ? `${coin.age}m` : 
                      coin.age < 1440 ? `${Math.floor(coin.age/60)}h` : 
                      `${Math.floor(coin.age/1440)}d`;
      
      console.log(
        `${i+1:<4} ${coin.symbol:<8} $${coin.price:<11.8f} ` +
        `${this.formatMcap(coin.marketCap):<10} ` +
        `${this.formatVolume(coin.volume24h):<12} ` +
        `${coin.priceChange24h:>+6.1f}%  ` +
        `${ageStr:<8} ${trend:<8}`
      );
    });
    
    console.log('\n' + '=' .repeat(80));
    console.log(`Total: ${coins.length} meme coins`);
    console.log(`Cache saved to: ${this.cacheFile}`);
    console.log('=' .repeat(80));
  }

  formatMcap(mcap) {
    if (mcap >= 1_000_000_000) return `$${(mcap/1_000_000_000).toFixed(2)}B`;
    if (mcap >= 1_000_000) return `$${(mcap/1_000_000).toFixed(1)}M`;
    if (mcap >= 1_000) return `$${(mcap/1_000).toFixed(1)}K`;
    return `$${mcap.toFixed(0)}`;
  }

  formatVolume(vol) {
    if (vol >= 1_000_000_000) return `$${(vol/1_000_000_000).toFixed(1)}B`;
    if (vol >= 1_000_000) return `$${(vol/1_000_000).toFixed(1)}M`;
    if (vol >= 1_000) return `$${(vol/1_000).toFixed(1)}K`;
    return `$${vol.toFixed(0)}`;
  }

  loadCache() {
    if (existsSync(this.cacheFile)) {
      try {
        const data = JSON.parse(readFileSync(this.cacheFile, 'utf8'));
        return data.coins || [];
      } catch (e) {
        return [];
      }
    }
    return [];
  }
}

// Run
const collector = new DexScreenerMemeCoins();

collector.collectAll().catch(console.error);
