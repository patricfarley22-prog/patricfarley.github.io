#!/usr/bin/env node
/**
 * SECURITY DAY 4: Secure Coding Patterns
 * 
 * Module 4 of Patric's AI Engineer Bootcamp
 * Focus: Write secure code by design
 * 
 * What this does:
 * - Validates code against security rules
 * - Detects hardcoded secrets
 * - Checks for insecure configurations
 * - Enforces secure coding standards
 * - Scans for common vulnerabilities
 * 
 * Usage:
 *   node security/day4-secure-coding.mjs --scan [directory]
 *   node security/day4-secure-coding.mjs --test
 */

import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

// ─── CONFIGURATION ───────────────────────────────────────────────────────

const CONFIG = {
  // Secret detection patterns
  secretPatterns: [
    {
      name: 'API_KEY',
      pattern: /(?:api[_-]?key|apikey)\s*[:=]\s*['"`][a-zA-Z0-9\-_]{20,}['"`]/gi,
      severity: 'CRITICAL',
      description: 'Hardcoded API key detected',
    },
    {
      name: 'TOKEN',
      pattern: /(?:token|auth[_-]?token|bearer)\s*[:=]\s*['"`][a-zA-Z0-9\-_]{20,}['"`]/gi,
      severity: 'CRITICAL',
      description: 'Hardcoded token detected',
    },
    {
      name: 'PASSWORD',
      pattern: /(?:password|passwd|pwd)\s*[:=]\s*['"`][^'"`\s]{8,}['"`]/gi,
      severity: 'HIGH',
      description: 'Hardcoded password detected',
    },
    {
      name: 'PRIVATE_KEY',
      pattern: /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----/gi,
      severity: 'CRITICAL',
      description: 'Private key detected',
    },
    {
      name: 'SECRET',
      pattern: /(?:secret|client[_-]?secret)\s*[:=]\s*['"`][a-zA-Z0-9\-_]{16,}['"`]/gi,
      severity: 'CRITICAL',
      description: 'Hardcoded secret detected',
    },
    {
      name: 'DATABASE_URL',
      pattern: /(?:mongodb|postgres|mysql|redis):\/\/[^\s"'`]+/gi,
      severity: 'HIGH',
      description: 'Database connection string detected',
    },
    {
      name: 'TELEGRAM_TOKEN',
      pattern: /\d{9,10}:[a-zA-Z0-9_-]{35}/g,
      severity: 'CRITICAL',
      description: 'Telegram bot token detected',
    },
    {
      name: 'WALLET_KEY',
      pattern: /0x[a-fA-F0-9]{40}/g,
      severity: 'HIGH',
      description: 'Ethereum wallet address detected',
    },
  ],
  
  // Insecure code patterns
  insecurePatterns: [
    {
      name: 'EVAL_USAGE',
      pattern: /\beval\s*\(/gi,
      severity: 'CRITICAL',
      description: 'Dangerous eval() usage',
      fix: 'Use JSON.parse() or a safer alternative',
    },
    {
      name: 'EXEC_USAGE',
      pattern: /(?:child_process|exec|execSync|spawn)\s*\(/gi,
      severity: 'HIGH',
      description: 'Command execution detected',
      fix: 'Use parameterized commands or safer alternatives',
    },
    {
      name: 'INSECURE_HTTP',
      pattern: /http:\/\/(?!localhost|127\.0\.0\.1)/gi,
      severity: 'MEDIUM',
      description: 'Insecure HTTP instead of HTTPS',
      fix: 'Use HTTPS for all external connections',
    },
    {
      name: 'DISABLED_SSL',
      pattern: /rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED['"]\s*:\s*['"]0['"]/gi,
      severity: 'HIGH',
      description: 'SSL verification disabled',
      fix: 'Never disable SSL verification in production',
    },
    {
      name: 'DEBUG_MODE',
      pattern: /(?:DEBUG|debug)\s*[:=]\s*(?:true|1|['"`](?:true|yes)['"`])/gi,
      severity: 'MEDIUM',
      description: 'Debug mode enabled',
      fix: 'Disable debug mode in production',
    },
    {
      name: 'CORS_WILDCARD',
      pattern: /origin\s*[:=]\s*['"`]\*['"`]|Access-Control-Allow-Origin\s*:\s*\*/gi,
      severity: 'MEDIUM',
      description: 'CORS wildcard allowed',
      fix: 'Restrict CORS to specific origins',
    },
    {
      name: 'HARDCODED_PORT',
      pattern: /(?:listen|port)\s*\(\s*(?:3000|8080|8000|5000)\s*\)/gi,
      severity: 'LOW',
      description: 'Hardcoded port',
      fix: 'Use environment variables for ports',
    },
    {
      name: 'NO_INPUT_VALIDATION',
      pattern: /req\.body|req\.query|req\.params/gi,
      severity: 'MEDIUM',
      description: 'User input used without validation',
      fix: 'Validate all user inputs before use',
      context: true,
    },
  ],
  
  // Secure coding rules
  codingRules: [
    {
      id: 'SEC-001',
      name: 'No Hardcoded Secrets',
      description: 'All secrets must be in environment variables',
      check: (content) => {
        const violations = [];
        for (const pattern of CONFIG.secretPatterns) {
          const matches = content.match(pattern.pattern);
          if (matches) {
            violations.push({
              rule: 'SEC-001',
              severity: pattern.severity,
              message: pattern.description,
              matches: matches.slice(0, 3),
            });
          }
        }
        return violations;
      },
    },
    {
      id: 'SEC-002',
      name: 'No Insecure Functions',
      description: 'Avoid dangerous functions like eval()',
      check: (content) => {
        const violations = [];
        for (const pattern of CONFIG.insecurePatterns) {
          const matches = content.match(pattern.pattern);
          if (matches) {
            violations.push({
              rule: 'SEC-002',
              severity: pattern.severity,
              message: pattern.description,
              fix: pattern.fix,
              matches: matches.slice(0, 3),
            });
          }
        }
        return violations;
      },
    },
    {
      id: 'SEC-003',
      name: 'Error Handling',
      description: 'All async operations must have error handling',
      check: (content) => {
        const violations = [];
        // Check for async without try/catch
        const asyncMatches = content.match(/async\s+function|async\s*\(/g);
        const tryCatchMatches = content.match(/try\s*\{/g);
        
        if (asyncMatches && (!tryCatchMatches || asyncMatches.length > tryCatchMatches.length * 2)) {
          violations.push({
            rule: 'SEC-003',
            severity: 'MEDIUM',
            message: 'Async functions without adequate error handling',
            fix: 'Add try/catch blocks to all async operations',
          });
        }
        return violations;
      },
    },
    {
      id: 'SEC-004',
      name: 'Input Validation',
      description: 'All user inputs must be validated',
      check: (content) => {
        const violations = [];
        const inputUsage = content.match(/req\.body\.|req\.query\.|req\.params\./g);
        const validation = content.match(/validate|sanitize|escape/gi);
        
        if (inputUsage && (!validation || inputUsage.length > validation.length)) {
          violations.push({
            rule: 'SEC-004',
            severity: 'HIGH',
            message: 'User input used without adequate validation',
            fix: 'Add input validation before using user data',
          });
        }
        return violations;
      },
    },
  ],
  
  // Scan settings
  scanSettings: {
    extensions: ['.js', '.mjs', '.ts', '.json', '.md'],
    excludeDirs: ['node_modules', '.git', 'logs', 'archive'],
    maxFileSize: 1024 * 1024, // 1MB
  },
  
  // Logging
  logFile: 'security/logs/secure-coding.log',
};

// ─── CODE SCANNER ────────────────────────────────────────────────────────

class CodeScanner {
  constructor(config = CONFIG) {
    this.config = config;
    this.findings = [];
    this.stats = {
      filesScanned: 0,
      filesWithIssues: 0,
      totalIssues: 0,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    };
  }
  
  /**
   * Scan a directory for security issues
   * @param {string} targetDir - Directory to scan
   * @returns {object} Scan results
   */
  async scanDirectory(targetDir) {
    console.log(`🔍 Scanning ${targetDir} for security issues...\n`);
    
    const files = await this.getFiles(targetDir);
    
    for (const file of files) {
      await this.scanFile(file);
    }
    
    return this.generateReport();
  }
  
  /**
   * Scan a single file
   * @param {string} filePath - File to scan
   */
  async scanFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      
      // Skip large files
      if (content.length > this.config.scanSettings.maxFileSize) {
        return;
      }
      
      this.stats.filesScanned++;
      const fileFindings = [];
      
      // Run all rules
      for (const rule of this.config.codingRules) {
        const violations = rule.check(content);
        
        for (const violation of violations) {
          fileFindings.push({
            ...violation,
            file: filePath,
            rule: rule.id,
            ruleName: rule.name,
          });
          
          this.stats.totalIssues++;
          this.stats[violation.severity.toLowerCase()]++;
        }
      }
      
      if (fileFindings.length > 0) {
        this.stats.filesWithIssues++;
        this.findings.push(...fileFindings);
      }
      
    } catch (err) {
      console.error(`❌ Error scanning ${filePath}:`, err.message);
    }
  }
  
  /**
   * Get all scannable files in directory
   */
  async getFiles(dir, files = []) {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory()) {
          if (!this.config.scanSettings.excludeDirs.includes(entry.name)) {
            await this.getFiles(fullPath, files);
          }
        } else if (this.config.scanSettings.extensions.some(ext => entry.name.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    } catch (err) {
      console.error(`❌ Error reading ${dir}:`, err.message);
    }
    
    return files;
  }
  
  /**
   * Generate scan report
   */
  generateReport() {
    const report = {
      summary: {
        filesScanned: this.stats.filesScanned,
        filesWithIssues: this.stats.filesWithIssues,
        totalIssues: this.stats.totalIssues,
        critical: this.stats.critical,
        high: this.stats.high,
        medium: this.stats.medium,
        low: this.stats.low,
        riskScore: this.calculateRiskScore(),
      },
      findings: this.findings,
      timestamp: new Date().toISOString(),
    };
    
    return report;
  }
  
  calculateRiskScore() {
    return (
      this.stats.critical * 10 +
      this.stats.high * 5 +
      this.stats.medium * 2 +
      this.stats.low * 0.5
    );
  }
  
  /**
   * Display report
   */
  displayReport(report) {
    const { summary } = report;
    
    console.log('\n' + '═'.repeat(70));
    console.log('📊 SECURITY SCAN REPORT');
    console.log('═'.repeat(70));
    console.log(`\nFiles Scanned: ${summary.filesScanned}`);
    console.log(`Files with Issues: ${summary.filesWithIssues}`);
    console.log(`Total Issues: ${summary.totalIssues}`);
    console.log(`\nRisk Score: ${summary.riskScore.toFixed(1)}`);
    console.log(`Critical: ${summary.critical} 🔴`);
    console.log(`High: ${summary.high} 🟠`);
    console.log(`Medium: ${summary.medium} 🟡`);
    console.log(`Low: ${summary.low} 🟢`);
    
    if (report.findings.length > 0) {
      console.log('\n' + '─'.repeat(70));
      console.log('🔍 FINDINGS');
      console.log('─'.repeat(70));
      
      for (const finding of report.findings.slice(0, 20)) {
        const severity = finding.severity;
        const icon = severity === 'CRITICAL' ? '🔴' : severity === 'HIGH' ? '🟠' : severity === 'MEDIUM' ? '🟡' : '🟢';
        
        console.log(`\n${icon} ${finding.rule} - ${finding.ruleName}`);
        console.log(`   File: ${finding.file}`);
        console.log(`   Severity: ${finding.severity}`);
        console.log(`   Message: ${finding.message}`);
        if (finding.fix) {
          console.log(`   Fix: ${finding.fix}`);
        }
        if (finding.matches) {
          console.log(`   Matches: ${finding.matches.length} found`);
        }
      }
      
      if (report.findings.length > 20) {
        console.log(`\n... and ${report.findings.length - 20} more findings`);
      }
    }
    
    console.log('\n' + '═'.repeat(70));
  }
}

// ─── SECRETS MANAGER ─────────────────────────────────────────────────────

class SecretsManager {
  constructor() {
    this.secrets = new Map();
    this.encryptionKey = null;
  }
  
  /**
   * Initialize with encryption key
   */
  async initialize(keyPath = 'security/.master-key') {
    try {
      const key = await fs.readFile(keyPath, 'utf8').catch(() => null);
      
      if (!key) {
        // Generate new key
        this.encryptionKey = crypto.randomBytes(32);
        await fs.mkdir(path.dirname(keyPath), { recursive: true });
        await fs.writeFile(keyPath, this.encryptionKey.toString('hex'));
      } else {
        this.encryptionKey = Buffer.from(key.trim(), 'hex');
      }
      
      return true;
    } catch (err) {
      console.error('Failed to initialize secrets manager:', err.message);
      return false;
    }
  }
  
  /**
   * Encrypt a secret
   */
  encrypt(plainText) {
    if (!this.encryptionKey) {
      throw new Error('Secrets manager not initialized');
    }
    
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-gcm', this.encryptionKey, iv);
    
    let encrypted = cipher.update(plainText, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      encrypted,
    };
  }
  
  /**
   * Decrypt a secret
   */
  decrypt(encryptedData) {
    if (!this.encryptionKey) {
      throw new Error('Secrets manager not initialized');
    }
    
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      this.encryptionKey,
      Buffer.from(encryptedData.iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
  
  /**
   * Store a secret securely
   */
  async store(name, value, file = 'security/secrets.enc') {
    const encrypted = this.encrypt(value);
    
    this.secrets.set(name, encrypted);
    
    // Save to file
    const data = Object.fromEntries(this.secrets);
    await fs.writeFile(file, JSON.stringify(data, null, 2));
    
    return true;
  }
  
  /**
   * Retrieve a secret
   */
  async retrieve(name, file = 'security/secrets.enc') {
    if (this.secrets.has(name)) {
      return this.decrypt(this.secrets.get(name));
    }
    
    // Try loading from file
    try {
      const data = JSON.parse(await fs.readFile(file, 'utf8'));
      if (data[name]) {
        return this.decrypt(data[name]);
      }
    } catch {
      // File doesn't exist or is empty
    }
    
    return null;
  }
}

// ─── TEST SUITE ──────────────────────────────────────────────────────────

const TEST_CASES = [
  // ✅ Clean code
  {
    name: 'Clean code - no secrets',
    content: `
      const config = {
        port: process.env.PORT || 3000,
        apiKey: process.env.API_KEY,
      };
    `,
    expectedIssues: 0,
  },
  {
    name: 'Clean code - proper error handling',
    content: `
      async function fetchData() {
        try {
          const response = await fetch(url);
          return response.json();
        } catch (error) {
          console.error('Fetch failed:', error);
          throw error;
        }
      }
    `,
    expectedIssues: 0,
  },
  
  // ❌ Hardcoded secrets
  {
    name: 'Hardcoded API key',
    content: `
      const apiKey = 'sk-abc123def456ghi789';
      const config = { api_key: 'abc123def456' };
    `,
    expectedIssues: 1,
    expectedSeverity: 'CRITICAL',
  },
  {
    name: 'Hardcoded token',
    content: `
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
    `,
    expectedIssues: 1,
    expectedSeverity: 'CRITICAL',
  },
  {
    name: 'Telegram token',
    content: `
      const botToken = '8168630761:AAG5yWkTQxgzqYnLlE40OTmqcOg6uOyUsiE';
    `,
    expectedIssues: 1,
    expectedSeverity: 'CRITICAL',
  },
  
  // ❌ Insecure patterns
  {
    name: 'Eval usage',
    content: `
      const result = eval(userInput);
    `,
    expectedIssues: 1,
    expectedSeverity: 'CRITICAL',
  },
  {
    name: 'Command execution',
    content: `
      const { exec } = require('child_process');
      exec(userCommand);
    `,
    expectedIssues: 1,
    expectedSeverity: 'HIGH',
  },
  {
    name: 'Insecure HTTP',
    content: `
      const url = 'http://api.example.com/data';
    `,
    expectedIssues: 1,
    expectedSeverity: 'MEDIUM',
  },
  {
    name: 'Disabled SSL',
    content: `
      const agent = new https.Agent({
        rejectUnauthorized: false
      });
    `,
    expectedIssues: 1,
    expectedSeverity: 'HIGH',
  },
];

async function runTests() {
  console.log('🧪 Running Secure Coding Tests\n');
  console.log('═'.repeat(70));
  
  const scanner = new CodeScanner();
  let passed = 0;
  let failed = 0;
  
  for (const test of TEST_CASES) {
    // Create temp file
    const tempFile = `test-${Date.now()}.js`;
    await fs.writeFile(tempFile, test.content);
    
    // Scan
    await scanner.scanFile(tempFile);
    
    // Check
    const fileFindings = scanner.findings.filter(f => f.file === tempFile);
    
    const testPassed = fileFindings.length >= test.expectedIssues;
    
    if (testPassed) {
      passed++;
      console.log(`✅ ${test.name}`);
      console.log(`   Issues found: ${fileFindings.length} (expected ${test.expectedIssues}+)`);
      
      if (fileFindings.length > 0) {
        console.log(`   Severity: ${fileFindings[0].severity}`);
      }
    } else {
      failed++;
      console.log(`❌ ${test.name}`);
      console.log(`   Expected: ${test.expectedIssues}+ issues`);
      console.log(`   Got: ${fileFindings.length}`);
    }
    
    // Cleanup
    await fs.unlink(tempFile).catch(() => {});
  }
  
  console.log('\n' + '═'.repeat(70));
  console.log(`📊 Results: ${passed}/${TEST_CASES.length} passed`);
  console.log(`   ${failed} tests failed`);
  console.log(`   Pass rate: ${((passed / TEST_CASES.length) * 100).toFixed(1)}%`);
  
  return { passed, failed, total: TEST_CASES.length };
}

async function runDemo() {
  console.log('🎮 Secure Coding Demo\n');
  console.log('═'.repeat(70));
  
  // Demo 1: Secrets Manager
  console.log('\n1️⃣  Secrets Manager:');
  const secrets = new SecretsManager();
  await secrets.initialize();
  
  const secretValue = 'my-super-secret-api-key-12345';
  await secrets.store('apiKey', secretValue);
  
  const retrieved = await secrets.retrieve('apiKey');
  console.log(`   Original: ${secretValue}`);
  console.log(`   Retrieved: ${retrieved}`);
  console.log(`   Match: ${secretValue === retrieved ? '✅' : '❌'}`);
  
  // Demo 2: Code Scan
  console.log('\n2️⃣  Code Security Scan:');
  const scanner = new CodeScanner();
  
  // Create test file
  const testContent = `
    // Bad practice
    const API_KEY = 'sk-abc123def456';
    const password = 'superSecret123';
    
    // Dangerous
    eval(userInput);
    
    // Insecure
    const url = 'http://api.example.com';
    
    async function fetch() {
      return await fetch(url);
    }
  `;
  
  await fs.writeFile('test-scan.js', testContent);
  await scanner.scanFile('test-scan.js');
  const report = scanner.generateReport();
  scanner.displayReport(report);
  
  // Cleanup
  await fs.unlink('test-scan.js').catch(() => {});
  
  console.log('\n' + '═'.repeat(70));
  console.log('✅ Demo complete!\n');
}

// ─── CLI ─────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--test')) {
    return await runTests();
  }
  
  if (args.includes('--demo')) {
    return await runDemo();
  }
  
  if (args.includes('--scan')) {
    const dirIndex = args.indexOf('--scan') + 1;
    const targetDir = args[dirIndex] || '.';
    
    const scanner = new CodeScanner();
    const report = await scanner.scanDirectory(targetDir);
    scanner.displayReport(report);
    
    // Save report
    await fs.mkdir('security/reports', { recursive: true });
    await fs.writeFile(
      `security/reports/scan-${Date.now()}.json`,
      JSON.stringify(report, null, 2)
    );
    
    return report;
  }
  
  console.log('🛡️  SECURITY DAY 4: Secure Coding Patterns');
  console.log('═'.repeat(70));
  console.log('\nUsage:');
  console.log('  node day4-secure-coding.mjs --test        # Run tests');
  console.log('  node day4-secure-coding.mjs --demo        # Run demo');
  console.log('  node day4-secure-coding.mjs --scan [dir]  # Scan directory');
  console.log('\nComponents:');
  console.log('  • CodeScanner      - Scan for security issues');
  console.log('  • SecretsManager   - Encrypt/decrypt secrets');
  console.log('  • Coding Rules     - Enforce secure patterns');
  console.log('\nRunning demo...\n');
  
  return await runDemo();
}

main().catch(console.error);

export { CodeScanner, SecretsManager };
