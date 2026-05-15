#!/usr/bin/env node
/**
 * MEME COIN ALERT SYSTEM
 * Monitors meme coins and sends alerts on significant changes
 */

import { spawn } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const ALERT_CONFIG = {
  priceChange: 5,      // Alert on 5% move
  volumeSpike: 2,        // Alert on 2x volume
  signalChange: true,    // Alert when quantum signal flips
  minConfidence: 0.35,   // Only alert on signals above 35%
  checkInterval: 300000   // 5 minutes
};

class MemeCoinAlertSystem {
  constructor() {
    this.dataDir = 'data';
    this.historyFile = join(this.dataDir, 'alert-history.json');
    this.loadHistory();
  }

  loadHistory() {
    if (existsSync(this.historyFile)) {
      try {
        this.history = JSON.parse(readFileSync(this.historyFile, 'utf8'));
      } catch (e) {
        this.history = {};
      }
    } else {
      this.history = {};
    }
  }

  saveHistory() {
    writeFileSync(this.historyFile, JSON.stringify(this.history, null, 2));
  }

  async fetchDexScreenerData(ca) {
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

  async runQuantum(ca) {
    return new Promise((resolve, reject) => {
      const proc = spawn('python', ['../../../quantum_analyzer.py', ca], {
        cwd: __dirname
      });
      let output = '';
      proc.stdout.on('data', d => output += d.toString());
      proc.stderr.on('data', d => {});
      proc.on('close', code => {
        try {
          const match = output.match(/\{[\s\S]*\}/);
          resolve(match ? JSON.parse(match[0]) : {});
        } catch (e) {
          resolve({});
        }
      });
    });
  }

  async checkCoin(symbol, ca) {
    const data = await this.fetchDexScreenerData(ca);
    if (!data) return null;

    const current = {
      symbol,
      ca,
      price: parseFloat(data.priceUsd) || 0,
      priceChange24h: parseFloat(data.priceChange?.h24) || 0,
      priceChange1h: parseFloat(data.priceChange?.h1) || 0,
      volume24h: parseFloat(data.volume?.h24) || 0,
      marketCap: parseFloat(data.marketCap) || 0,
      liquidity: parseFloat(data.liquidity?.usd) || 0,
      timestamp: new Date().toISOString()
    };

    // Get quantum signal
    const quantum = await this.runQuantum(ca);
    current.quantumSignal = quantum.signal || 'UNKNOWN';
    current.quantumConfidence = quantum.confidence || 0;

    // Check for alerts
    const alerts = this.detectAlerts(symbol, current);
    
    // Save to history
    if (!this.history[symbol]) this.history[symbol] = [];
    this.history[symbol].push(current);
    if (this.history[symbol].length > 100) {
      this.history[symbol] = this.history[symbol].slice(-100);
    }
    this.saveHistory();

    return { current, alerts };
  }

  detectAlerts(symbol, current) {
    const alerts = [];
    const prev = this.history[symbol]?.slice(-2, -1)[0];
    
    if (!prev) return alerts;

    // Price change alert
    const priceChange = ((current.price - prev.price) / prev.price) * 100;
    if (Math.abs(priceChange) >= ALERT_CONFIG.priceChange) {
      alerts.push({
        type: 'PRICE',
        severity: Math.abs(priceChange) > 10 ? 'HIGH' : 'MEDIUM',
        message: `Price ${priceChange > 0 ? 'UP' : 'DOWN'} ${priceChange.toFixed(2)}%`,
        details: { oldPrice: prev.price, newPrice: current.price }
      });
    }

    // Volume spike
    if (prev.volume24h > 0) {
      const volRatio = current.volume24h / prev.volume24h;
      if (volRatio >= ALERT_CONFIG.volumeSpike) {
        alerts.push({
          type: 'VOLUME',
          severity: 'HIGH',
          message: `Volume spike ${volRatio.toFixed(1)}x`,
          details: { oldVol: prev.volume24h, newVol: current.volume24h }
        });
      }
    }

    // Signal change
    if (ALERT_CONFIG.signalChange && current.quantumSignal !== prev.quantumSignal) {
      if (current.quantumConfidence >= ALERT_CONFIG.minConfidence) {
        alerts.push({
          type: 'SIGNAL',
          severity: 'HIGH',
          message: `Signal changed: ${prev.quantumSignal} -> ${current.quantumSignal}`,
          details: { 
            oldSignal: prev.quantumSignal, 
            newSignal: current.quantumSignal,
            confidence: current.quantumConfidence 
          }
        });
      }
    }

    // Confidence jump
    const confChange = current.quantumConfidence - prev.quantumConfidence;
    if (Math.abs(confChange) >= 0.15) {
      alerts.push({
        type: 'CONFIDENCE',
        severity: 'MEDIUM',
        message: `Confidence ${confChange > 0 ? 'UP' : 'DOWN'} to ${(current.quantumConfidence * 100).toFixed(1)}%`,
        details: { confidence: current.quantumConfidence }
      });
    }

    return alerts;
  }

  formatAlert(symbol, current, alerts) {
    let msg = `ALERT: ${symbol}\n`;
    msg += `Price: $${current.price.toFixed(10)} (${current.priceChange24h >= 0 ? '+' : ''}${current.priceChange24h.toFixed(2)}%)\n`;
    msg += `Volume: $${(current.volume24h/1000).toFixed(1)}K\n`;
    msg += `MCap: $${(current.marketCap/1000000).toFixed(2)}M\n`;
    msg += `Signal: ${current.quantumSignal} (${(current.quantumConfidence * 100).toFixed(1)}%)\n`;
    msg += '\nAlerts:\n';
    
    alerts.forEach(a => {
      const icon = a.severity === 'HIGH' ? '!!' : '!';
      msg += `${icon} ${a.type}: ${a.message}\n`;
    });
    
    msg += `\nChart: https://dexscreener.com/solana/${current.ca}`;
    
    return msg;
  }

  async monitorCoins(coins) {
    console.log('Starting meme coin alert monitor...');
    console.log(`Checking ${coins.length} coins every ${ALERT_CONFIG.checkInterval/1000}s`);
    console.log('Press Ctrl+C to stop\n');

    while (true) {
      const timestamp = new Date().toLocaleTimeString();
      console.log(`\n[${timestamp}] Checking coins...`);

      for (const coin of coins) {
        try {
          const result = await this.checkCoin(coin.symbol, coin.ca);
          
          if (result && result.alerts.length > 0) {
            const alert = this.formatAlert(coin.symbol, result.current, result.alerts);
            console.log('\n' + '='.repeat(60));
            console.log(alert);
            console.log('='.repeat(60));
            
            // Save alert
            writeFileSync(
              join(this.dataDir, `alert-${coin.symbol}-${Date.now()}.txt`),
              alert
            );
          } else {
            console.log(`${coin.symbol}: ${result?.current?.quantumSignal || 'N/A'} (${(result?.current?.quantumConfidence * 100 || 0).toFixed(1)}%) - No alerts`);
          }
        } catch (err) {
          console.error(`Error checking ${coin.symbol}:`, err.message);
        }
        
        await new Promise(r => setTimeout(r, 500));
      }

      console.log(`Waiting ${ALERT_CONFIG.checkInterval/1000}s until next check...`);
      await new Promise(r => setTimeout(r, ALERT_CONFIG.checkInterval));
    }
  }
}

// Example usage with tracked coins
const TRACKED_COINS = [
  { symbol: 'BONK', ca: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263' },
  { symbol: 'WIF', ca: 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm' },
  { symbol: 'FLOKI', ca: 'FLOKI' },
  { symbol: 'TROLL', ca: '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2' },
  { symbol: 'DOWGE', ca: 'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump' }
];

const alerts = new MemeCoinAlertSystem();
alerts.monitorCoins(TRACKED_COINS).catch(console.error);
