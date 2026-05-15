#!/usr/bin/env node
/**
 * TROLL MONITOR - Continuous monitoring with alerts
 * CA: 5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2
 */

import { spawn } from 'child_process';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  ca: '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2',
  symbol: 'TROLL',
  checkInterval: 5 * 60 * 1000, // 5 minutes
  alertThreshold: {
    priceChange: 5,     // Alert on 5% moves
    volumeSpike: 2,     // Alert on 2x volume
    liquidityDrop: 20,  // Alert on 20% liquidity drop
    confidenceChange: 10 // Alert on 10% confidence change
  },
  dataFile: join(__dirname, 'data', 'troll-history.json')
};

class TrollMonitor {
  constructor() {
    this.history = this.loadHistory();
    this.lastAlert = null;
  }

  loadHistory() {
    if (existsSync(CONFIG.dataFile)) {
      try {
        return JSON.parse(readFileSync(CONFIG.dataFile, 'utf8'));
      } catch (e) {
        return [];
      }
    }
    return [];
  }

  saveHistory() {
    writeFileSync(CONFIG.dataFile, JSON.stringify(this.history.slice(-100), null, 2));
  }

  async fetchData() {
    try {
      const response = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${CONFIG.ca}`, {
        timeout: 10000
      });
      
      if (!response.ok) return null;
      
      const data = await response.json();
      return data.pairs?.[0] || null;
    } catch (err) {
      return null;
    }
  }

  async runQuantum(data) {
    const priceChange = parseFloat(data.priceChange?.h24) || 0;
    const volume = parseFloat(data.volume?.h24) || 0;
    const liq = parseFloat(data.liquidity?.usd) || 0;
    
    const args = [
      (priceChange / 100).toString(),
      (volume / 100000).toString(),
      '0.5', '0', '0.6', '0.55', '0.45',
      Math.min(liq / 50000, 1).toString(),
      '0.5',
      Math.min(volume / 100000, 1).toString()
    ];

    return new Promise((resolve, reject) => {
      const proc = spawn('python', [join(__dirname, '..', '..', '..', 'quantum_analyzer.py'), ...args]);
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
          } catch (e) { resolve({}); }
        }
      });
    });
  }

  async check() {
    const data = await this.fetchData();
    if (!data) {
      console.log('❌ Failed to fetch TROLL data');
      return;
    }

    const current = {
      timestamp: new Date().toISOString(),
      price: parseFloat(data.priceUsd),
      change24h: parseFloat(data.priceChange?.h24),
      change1h: parseFloat(data.priceChange?.h1),
      volume24h: parseFloat(data.volume?.h24),
      liquidity: parseFloat(data.liquidity?.usd),
      marketCap: parseFloat(data.marketCap)
    };

    // Get quantum signal
    let quantum = null;
    try {
      quantum = await this.runQuantum(data);
    } catch (err) {
      console.log('Quantum failed:', err.message);
    }

    const record = {
      ...current,
      signal: quantum?.signal || 'UNKNOWN',
      confidence: quantum?.confidence || 0,
      entanglement: quantum?.entanglement_strength || 0
    };

    this.history.push(record);
    this.saveHistory();

    // Check for alerts
    const alerts = this.checkAlerts(record);
    
    return { record, alerts };
  }

  checkAlerts(current) {
    const alerts = [];
    const prev = this.history.length > 1 ? this.history[this.history.length - 2] : null;
    
    if (!prev) return alerts;

    // Price change alert
    const priceChange = ((current.price - prev.price) / prev.price) * 100;
    if (Math.abs(priceChange) >= CONFIG.alertThreshold.priceChange) {
      alerts.push({
        type: 'PRICE',
        message: `Price ${priceChange > 0 ? '🚀 UP' : '📉 DOWN'} ${priceChange.toFixed(2)}%`,
        price: current.price,
        prevPrice: prev.price,
        severity: Math.abs(priceChange) > 10 ? 'HIGH' : 'MEDIUM'
      });
    }

    // Volume spike
    const volumeChange = current.volume24h / prev.volume24h;
    if (volumeChange >= CONFIG.alertThreshold.volumeSpike) {
      alerts.push({
        type: 'VOLUME',
        message: `Volume spike ${volumeChange.toFixed(1)}x`,
        volume: current.volume24h,
        prevVolume: prev.volume24h,
        severity: 'HIGH'
      });
    }

    // Liquidity drop
    const liqChange = ((current.liquidity - prev.liquidity) / prev.liquidity) * 100;
    if (liqChange <= -CONFIG.alertThreshold.liquidityDrop) {
      alerts.push({
        type: 'LIQUIDITY',
        message: `Liquidity dropped ${Math.abs(liqChange).toFixed(1)}%`,
        liquidity: current.liquidity,
        severity: 'HIGH'
      });
    }

    // Confidence change
    if (current.confidence && prev.confidence) {
      const confChange = Math.abs((current.confidence - prev.confidence) / prev.confidence) * 100;
      if (confChange >= CONFIG.alertThreshold.confidenceChange) {
        alerts.push({
          type: 'CONFIDENCE',
          message: `Confidence ${current.confidence > prev.confidence ? 'UP' : 'DOWN'} to ${(current.confidence * 100).toFixed(1)}%`,
          confidence: current.confidence,
          signal: current.signal,
          severity: 'MEDIUM'
        });
      }
    }

    return alerts;
  }

  printStatus(record, alerts) {
    const now = new Date().toLocaleTimeString();
    const emoji = record.signal === 'BUY' ? '🚀' : record.signal === 'SELL' ? '📉' : '⏸️';
    
    console.log(`\n🔮 TROLL Monitor - ${now}`);
    console.log('='.repeat(50));
    console.log(`Price: $${record.price.toFixed(6)}`);
    console.log(`24h: ${record.change24h?.toFixed(2)}% | 1h: ${record.change1h?.toFixed(2)}%`);
    console.log(`Volume: $${(record.volume24h/1000).toFixed(1)}K`);
    console.log(`Liquidity: $${(record.liquidity/1000).toFixed(1)}K`);
    console.log(`Signal: ${emoji} ${record.signal} (${(record.confidence * 100).toFixed(1)}%)`);
    console.log(`Entanglement: ${record.entanglement?.toFixed(3) || 'N/A'}`);
    
    if (alerts.length > 0) {
      console.log('\n🚨 ALERTS:');
      alerts.forEach(a => {
        const sevEmoji = a.severity === 'HIGH' ? '🔥' : '⚠️';
        console.log(`  ${sevEmoji} ${a.type}: ${a.message}`);
      });
    } else {
      console.log('\n✅ No alerts');
    }
    
    console.log(`\nHistory: ${this.history.length} records`);
  }

  async runOnce() {
    const { record, alerts } = await this.check();
    if (record) {
      this.printStatus(record, alerts);
    }
    return { record, alerts };
  }

  async runContinuous() {
    console.log('🔮 TROLL Continuous Monitor Started');
    console.log(`Checking every ${CONFIG.checkInterval / 60000} minutes`);
    console.log('Press Ctrl+C to stop\n');
    
    while (true) {
      await this.runOnce();
      
      // Wait for next check
      const nextCheck = new Date(Date.now() + CONFIG.checkInterval);
      console.log(`\n⏱️  Next check: ${nextCheck.toLocaleTimeString()}`);
      
      await new Promise(r => setTimeout(r, CONFIG.checkInterval));
    }
  }
}

// CLI
const monitor = new TrollMonitor();

if (process.argv.includes('--once')) {
  monitor.runOnce();
} else if (process.argv.includes('--continuous')) {
  monitor.runContinuous().catch(console.error);
} else {
  console.log('Usage:');
  console.log('  node monitor-troll.mjs --once        Single check');
  console.log('  node monitor-troll.mjs --continuous  Run forever');
  
  // Default: run once
  monitor.runOnce();
}

export default TrollMonitor;
