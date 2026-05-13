#!/usr/bin/env node
/**
 * SECURITY DAY 6: Security Monitor
 * Real-time security monitoring for Cortex
 * 
 * Usage:
 *   node security/monitor.mjs --status
 *   node security/monitor.mjs --watch
 */

import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

// ─── SECURITY MONITOR ────────────────────────────────────────────────────

class SecurityMonitor {
  constructor() {
    this.metrics = {
      validations: 0,
      blocked: 0,
      injections: 0,
      apiAbuse: 0,
      secretsExposed: 0,
      integrityChanges: 0,
    };
    this.alerts = [];
    this.startTime = Date.now();
    this.maxAlerts = 100;
  }

  trackValidation(result) {
    this.metrics.validations++;
    if (!result.isValid) {
      this.metrics.blocked++;
    }
    if (result.riskLevel === 'CRITICAL') {
      this.metrics.injections++;
      this.triggerAlert('CRITICAL_INJECTION', result);
    }
  }

  trackAPIRequest(result) {
    if (!result.allowed) {
      this.metrics.apiAbuse++;
      if (result.checks?.rateLimit?.blocked) {
        this.triggerAlert('RATE_LIMIT_EXCEEDED', result);
      }
    }
  }

  triggerAlert(type, details) {
    const alert = {
      id: crypto.randomUUID(),
      type,
      severity: type === 'CRITICAL_INJECTION' ? 'CRITICAL' : 'HIGH',
      timestamp: new Date().toISOString(),
      details: this.sanitizeDetails(details),
      acknowledged: false,
    };

    this.alerts.push(alert);
    if (this.alerts.length > this.maxAlerts) {
      this.alerts = this.alerts.slice(-this.maxAlerts);
    }

    this.logAlert(alert);
    return alert;
  }

  sanitizeDetails(details) {
    const safe = JSON.parse(JSON.stringify(details));
    if (safe.original) safe.original = '[REDACTED]';
    if (safe.sanitized) safe.sanitized = '[REDACTED]';
    return safe;
  }

  async logAlert(alert) {
    try {
      const logDir = 'security/logs';
      await fs.mkdir(logDir, { recursive: true });
      await fs.appendFile(
        path.join(logDir, 'alerts.jsonl'),
        JSON.stringify(alert) + '\n'
      );
    } catch (err) {
      console.error('Failed to log alert:', err.message);
    }
  }

  getStatus() {
    const uptime = (Date.now() - this.startTime) / 1000;
    return {
      uptime: `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`,
      metrics: { ...this.metrics },
      activeAlerts: this.alerts.filter(a => !a.acknowledged).length,
      totalAlerts: this.alerts.length,
      health: this.calculateHealth(),
      lastCheck: new Date().toISOString(),
    };
  }

  calculateHealth() {
    const total = this.metrics.validations;
    const blocked = this.metrics.blocked;
    if (total === 0) return 100;
    const blockRate = blocked / total;
    if (blockRate > 0.5) return 40;
    if (blockRate > 0.2) return 70;
    if (blockRate > 0.05) return 90;
    return 100;
  }

  displayStatus() {
    const status = this.getStatus();
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║           CORTEX SECURITY MONITOR                          ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log(`║ Uptime:     ${status.uptime.padEnd(45)}║`);
    console.log(`║ Health:     ${status.health}% ${' '.repeat(42)}║`);
    console.log(`║ Active:     ${status.activeAlerts} alerts${' '.repeat(38)}║`);
    console.log(`║ Total:      ${status.totalAlerts} alerts${' '.repeat(38)}║`);
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log('║ METRICS                                                    ║');
    console.log(`║ Validations:  ${String(status.metrics.validations).padEnd(43)}║`);
    console.log(`║ Blocked:     ${String(status.metrics.blocked).padEnd(44)}║`);
    console.log(`║ Injections:  ${String(status.metrics.injections).padEnd(43)}║`);
    console.log(`║ API Abuse:   ${String(status.metrics.apiAbuse).padEnd(44)}║`);
    console.log(`║ Integrity:   ${String(status.metrics.integrityChanges).padEnd(43)}║`);
    console.log('╚════════════════════════════════════════════════════════════╝');
    return status;
  }
}

// ─── FILE INTEGRITY MONITOR ───────────────────────────────────────────────

class FileIntegrityMonitor {
  constructor() {
    this.baseline = new Map();
    this.checkInterval = 3600000;
    this.monitor = null;
  }

  async hashFile(filePath) {
    try {
      const content = await fs.readFile(filePath);
      return crypto.createHash('sha256').update(content).digest('hex');
    } catch {
      return null;
    }
  }

  async createBaseline(dirs = ['.']) {
    console.log('🔐 Creating security baseline...');
    const files = [];
    for (const dir of dirs) {
      await this.collectFiles(dir, files);
    }

    for (const file of files) {
      const hash = await this.hashFile(file);
      if (hash) this.baseline.set(file, hash);
    }

    await fs.mkdir('security', { recursive: true });
    await fs.writeFile(
      'security/baseline.json',
      JSON.stringify(Object.fromEntries(this.baseline), null, 2)
    );

    console.log(`   Baseline created: ${this.baseline.size} files`);
    return this.baseline.size;
  }

  async collectFiles(dir, files) {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (!['node_modules', '.git', 'logs', 'security'].includes(entry.name)) {
            await this.collectFiles(fullPath, files);
          }
        } else if (['.js', '.mjs', '.json', '.md'].some(ext => entry.name.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    } catch {}
  }

  async checkIntegrity() {
    const changes = [];
    for (const [file, expectedHash] of this.baseline) {
      const currentHash = await this.hashFile(file);
      if (!currentHash) {
        changes.push({ file, type: 'DELETED', expectedHash });
      } else if (currentHash !== expectedHash) {
        changes.push({ file, type: 'MODIFIED', expectedHash, currentHash });
      }
    }
    return changes;
  }

  startMonitoring(monitor) {
    if (this.monitor) clearInterval(this.monitor);
    this.monitor = setInterval(async () => {
      const changes = await this.checkIntegrity();
      if (changes.length > 0) {
        monitor.metrics.integrityChanges += changes.length;
        for (const change of changes) {
          monitor.triggerAlert('FILE_INTEGRITY', change);
        }
      }
    }, this.checkInterval);
    console.log('👁️  File integrity monitoring started (1hr intervals)');
  }

  stopMonitoring() {
    if (this.monitor) {
      clearInterval(this.monitor);
      this.monitor = null;
    }
  }
}

// ─── SECURITY HEADERS ────────────────────────────────────────────────────

const securityHeaders = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.telegram.org https://api.coingecko.com; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), payment=()',
  'Cross-Origin-Embedder-Policy': 'require-corp',
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Resource-Policy': 'same-origin',
};

function applySecurityHeaders(response) {
  for (const [header, value] of Object.entries(securityHeaders)) {
    response.setHeader?.(header, value);
  }
}

// ─── SESSION MANAGER ────────────────────────────────────────────────────

class SessionManager {
  constructor(config = {}) {
    this.sessions = new Map();
    this.maxAge = config.maxAge || 3600000;
    this.renewThreshold = config.renewThreshold || 0.5;
  }

  create(userId, metadata = {}) {
    const session = {
      id: crypto.randomUUID(),
      userId,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      expiresAt: Date.now() + this.maxAge,
      ip: metadata.ip || null,
      userAgent: metadata.userAgent || null,
      fingerprint: metadata.fingerprint || null,
    };
    this.sessions.set(session.id, session);
    return session;
  }

  validate(sessionId, metadata = {}) {
    const session = this.sessions.get(sessionId);
    if (!session) return { valid: false, reason: 'Session not found' };

    if (Date.now() > session.expiresAt) {
      this.sessions.delete(sessionId);
      return { valid: false, reason: 'Session expired' };
    }

    if (session.ip && metadata.ip && session.ip !== metadata.ip) {
      return { valid: false, reason: 'IP mismatch' };
    }

    if (session.fingerprint && metadata.fingerprint && session.fingerprint !== metadata.fingerprint) {
      return { valid: false, reason: 'Fingerprint mismatch' };
    }

    session.lastActivity = Date.now();

    const age = Date.now() - session.createdAt;
    const shouldRenew = age > this.maxAge * this.renewThreshold;

    return {
      valid: true,
      session,
      renew: shouldRenew,
    };
  }

  renew(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    session.expiresAt = Date.now() + this.maxAge;
    return session;
  }

  destroy(sessionId) {
    this.sessions.delete(sessionId);
    return { destroyed: true };
  }

  cleanup() {
    const now = Date.now();
    let removed = 0;
    for (const [id, session] of this.sessions) {
      if (now > session.expiresAt) {
        this.sessions.delete(id);
        removed++;
      }
    }
    return removed;
  }
}

// ─── DEMO / TEST ────────────────────────────────────────────────────────

async function runDemo() {
  console.log('🎮 Security Monitor Demo\n');
  console.log('═'.repeat(70));

  const monitor = new SecurityMonitor();
  const integrity = new FileIntegrityMonitor();
  const sessions = new SessionManager();

  console.log('\n1️⃣  Security Status:');
  monitor.displayStatus();

  console.log('\n2️⃣  Simulating Events...');

  // Simulate validation
  monitor.trackValidation({ isValid: true, riskLevel: 'CLEAN' });
  monitor.trackValidation({ isValid: false, riskLevel: 'CRITICAL', riskScore: 95 });
  monitor.trackValidation({ isValid: false, riskLevel: 'HIGH', riskScore: 75 });

  console.log('   Events tracked: 3 (1 clean, 2 blocked)');

  // Simulate API abuse
  monitor.trackAPIRequest({
    allowed: false,
    checks: { rateLimit: { blocked: true } },
  });
  console.log('   API abuse detected: 1');

  // Create baseline
  console.log('\n3️⃣  File Integrity Baseline:');
  const baselineSize = await integrity.createBaseline(['security']);
  console.log(`   ${baselineSize} files in baseline`);

  // Session management
  console.log('\n4️⃣  Session Management:');
  const session = sessions.create('user-123', { ip: '127.0.0.1' });
  console.log(`   Session created: ${session.id.substring(0, 8)}...`);

  const validation = sessions.validate(session.id, { ip: '127.0.0.1' });
  console.log(`   Validation: ${validation.valid ? '✅ Valid' : '❌ Invalid'}`);

  const badValidation = sessions.validate(session.id, { ip: '1.2.3.4' });
  console.log(`   Bad IP: ${badValidation.valid ? '✅ Valid' : `❌ ${badValidation.reason}`}`);

  // Final status
  console.log('\n5️⃣  Updated Status:');
  monitor.displayStatus();

  console.log('\n' + '═'.repeat(70));
  console.log('✅ Demo complete!\n');
}

// ─── CLI ─────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--status')) {
    const monitor = new SecurityMonitor();
    monitor.displayStatus();
    return;
  }

  if (args.includes('--watch')) {
    const monitor = new SecurityMonitor();
    const integrity = new FileIntegrityMonitor();

    await integrity.createBaseline(['.']);
    integrity.startMonitoring(monitor);

    console.log('👁️  Security monitoring active...');
    console.log('Press Ctrl+C to stop');

    setInterval(() => {
      monitor.displayStatus();
    }, 30000);

    return;
  }

  if (args.includes('--demo')) {
    return await runDemo();
  }

  console.log('🔐 SECURITY DAY 6: Security Monitor & Hardening');
  console.log('═'.repeat(70));
  console.log('\nComponents:');
  console.log('  • SecurityMonitor      - Real-time security tracking');
  console.log('  • FileIntegrityMonitor - Detect unauthorized changes');
  console.log('  • Security Headers     - HTTP security headers');
  console.log('  • SessionManager       - Secure session handling');
  console.log('\nUsage:');
  console.log('  node monitor.mjs --status    # Show current status');
  console.log('  node monitor.mjs --watch     # Start monitoring');
  console.log('  node monitor.mjs --demo      # Run demo');
  console.log('\nRunning demo...\n');

  return await runDemo();
}

main().catch(console.error);

export { SecurityMonitor, FileIntegrityMonitor, SessionManager, applySecurityHeaders };
