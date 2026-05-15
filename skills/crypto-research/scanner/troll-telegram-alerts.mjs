#!/usr/bin/env node
/**
 * TROLL TELEGRAM ALERTS
 * Sends TROLL signals to Telegram
 */

import { spawn } from 'child_process';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Telegram config - USE ENVIRONMENT VARIABLES
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN_HERE';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || '6643728142';

const CONFIG = {
  ca: '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2',
  symbol: 'TROLL',
  checkInterval: 5 * 60 * 1000, // 5 minutes
  alertThreshold: {
    priceChange: 5,
    volumeSpike: 2,
    liquidityDrop: 20,
    confidenceChange: 10
  },
  dataFile: join(__dirname, 'data', 'troll-history.json')
};

async function sendTelegramAlert(message) {
  try {
    const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: 'HTML',
        disable_web_page_preview: true
      })
    });
    
    if (response.ok) {
      console.log('✅ Telegram alert sent');
    } else {
      console.error('❌ Telegram failed:', await response.text());
    }
  } catch (err) {
    console.error('❌ Telegram error:', err.message);
  }
}

class TrollTelegramMonitor {
  constructor() {
    this.history = this.loadHistory();
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

  async checkAndAlert() {
    const data = await this.fetchData();
    if (!data) return;

    const current = {
      timestamp: new Date().toISOString(),
      price: parseFloat(data.priceUsd),
      change24h: parseFloat(data.priceChange?.h24),
      change1h: parseFloat(data.priceChange?.h1),
      volume24h: parseFloat(data.volume?.h24),
      liquidity: parseFloat(data.liquidity?.usd),
      marketCap: parseFloat(data.marketCap)
    };

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
    
    // Send Telegram if alerts or signal change
    if (alerts.length > 0 || this.isSignalChange(record)) {
      await this.sendTrollAlert(record, alerts);
    }
    
    return { record, alerts };
  }

  checkAlerts(current) {
    const alerts = [];
    const prev = this.history.length > 1 ? this.history[this.history.length - 2] : null;
    
    if (!prev) return alerts;

    // Price change
    const priceChange = ((current.price - prev.price) / prev.price) * 100;
    if (Math.abs(priceChange) >= CONFIG.alertThreshold.priceChange) {
      alerts.push({
        type: 'PRICE',
        message: `Price ${priceChange > 0 ? 'UP' : 'DOWN'} ${priceChange.toFixed(2)}%`,
        severity: Math.abs(priceChange) > 10 ? 'HIGH' : 'MEDIUM'
      });
    }

    // Volume spike
    const volumeChange = current.volume24h / prev.volume24h;
    if (volumeChange >= CONFIG.alertThreshold.volumeSpike) {
      alerts.push({
        type: 'VOLUME',
        message: `Volume spike ${volumeChange.toFixed(1)}x`,
        severity: 'HIGH'
      });
    }

    // Liquidity drop
    const liqChange = ((current.liquidity - prev.liquidity) / prev.liquidity) * 100;
    if (liqChange <= -CONFIG.alertThreshold.liquidityDrop) {
      alerts.push({
        type: 'LIQUIDITY',
        message: `Liquidity dropped ${Math.abs(liqChange).toFixed(1)}%`,
        severity: 'HIGH'
      });
    }

    // Signal change
    if (current.signal !== prev.signal) {
      alerts.push({
        type: 'SIGNAL',
        message: `Signal changed to ${current.signal}`,
        severity: 'HIGH'
      });
    }

    return alerts;
  }

  isSignalChange(record) {
    if (this.history.length < 2) return false;
    const prev = this.history[this.history.length - 2];
    return record.signal !== prev.signal;
  }

  async sendTrollAlert(record, alerts) {
    const emoji = record.signal === 'BUY' ? '🚀' : record.signal === 'SELL' ? '📉' : '⏸️';
    const alertEmoji = alerts.some(a => a.severity === 'HIGH') ? '🔥' : '⚠️';
    
    let message = `${alertEmoji} <b>TROLL ALERT</b>\n\n`;
    message += `💰 Price: $${record.price.toFixed(6)}\n`;
    message += `📊 24h: ${record.change24h?.toFixed(2)}% | 1h: ${record.change1h?.toFixed(2)}%\n`;
    message += `📈 Volume: $${(record.volume24h/1000).toFixed(1)}K\n`;
    message += `💎 Liquidity: $${(record.liquidity/1000).toFixed(1)}K\n`;
    message += `🏦 MCap: $${(record.marketCap/1000).toFixed(1)}K\n\n`;
    message += `🔮 Quantum: ${emoji} <b>${record.signal}</b> (${(record.confidence * 100).toFixed(1)}%)\n`;
    message += `🔗 Entanglement: ${record.entanglement?.toFixed(3) || 'N/A'}\n\n`;
    
    if (alerts.length > 0) {
      message += `<b>🚨 Alerts:</b>\n`;
      alerts.forEach(a => {
        const sev = a.severity === 'HIGH' ? '🔥' : '⚠️';
        message += `${sev} ${a.type}: ${a.message}\n`;
      });
      message += '\n';
    }
    
    message += `<a href="https://dexscreener.com/solana/4w2cysotX6czaUGmmWg13hDpY4QEMG2CzeKYEQyK9Ama">View Chart</a>`;
    
    await sendTelegramAlert(message);
  }

  async runOnce() {
    console.log('Checking TROLL...');
    const result = await this.checkAndAlert();
    if (result) {
      console.log(`Signal: ${result.record.signal} (${(result.record.confidence * 100).toFixed(1)}%)`);
      console.log(`Alerts: ${result.alerts.length}`);
    }
  }

  async runContinuous() {
    console.log('🔮 TROLL Telegram Monitor Started');
    console.log(`Checking every ${CONFIG.checkInterval / 60000} minutes`);
    console.log('Alerts will be sent to your Telegram\n');
    
    while (true) {
      await this.runOnce();
      
      const nextCheck = new Date(Date.now() + CONFIG.checkInterval);
      console.log(`Next check: ${nextCheck.toLocaleTimeString()}\n`);
      
      await new Promise(r => setTimeout(r, CONFIG.checkInterval));
    }
  }
}

// CLI
const monitor = new TrollTelegramMonitor();

if (process.argv.includes('--once')) {
  monitor.runOnce();
} else if (process.argv.includes('--continuous')) {
  monitor.runContinuous().catch(console.error);
} else {
  console.log('Usage:');
  console.log('  node troll-telegram-alerts.mjs --once        Single check');
  console.log('  node troll-telegram-alerts.mjs --continuous    Run forever (sends Telegram)');
  monitor.runOnce();
}

export default TrollTelegramMonitor;
