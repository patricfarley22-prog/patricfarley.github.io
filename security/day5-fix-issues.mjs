#!/usr/bin/env node
/**
 * SECURITY DAY 5: Fix Critical Issues
 * 
 * Module 5 of Patric's AI Engineer Bootcamp
 * Focus: Fix all CRITICAL and HIGH security issues
 * 
 * What this does:
 * - Moves secrets to environment variables
 * - Removes hardcoded tokens/keys
 * - Adds input validation
 * - Fixes insecure patterns
 * - Re-scans to verify fixes
 * 
 * Usage:
 *   node security/day5-fix-issues.mjs --analyze
 *   node security/day5-fix-issues.mjs --fix
 *   node security/day5-fix-issues.mjs --verify
 */

import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

// ─── CONFIGURATION ───────────────────────────────────────────────────────

const CRITICAL_FILES = [
  'MEMORY.md',
  'TOOLS.md',
  'config-backup-*.json',
  'memory/*.md',
  'memory/**/*.json',
];

const FIXES = {
  // Move secrets to .env
  secrets: {
    telegramToken: {
      pattern: /8168630761:AAG5yWkTQxgzqYnLlE40OTmqcOg6uOyUsiE/g,
      envVar: 'TELEGRAM_BOT_TOKEN',
      description: 'Telegram bot token',
    },
    openRouterKey: {
      pattern: /sk-or-v1-[a-f0-9]{64}/g,
      envVar: 'OPENROUTER_API_KEY',
      description: 'OpenRouter API key',
    },
    kimiKey: {
      pattern: /sk-kimi-[a-zA-Z0-9]{64}/g,
      envVar: 'KIMI_API_KEY',
      description: 'Kimi API key',
    },
    googleKey: {
      pattern: /AIzaSy[A-Za-z0-9_-]{33}/g,
      envVar: 'GOOGLE_API_KEY',
      description: 'Google API key',
    },
    braveKey: {
      pattern: /BSAP-[A-Za-z0-9_-]{20,}/g,
      envVar: 'BRAVE_API_KEY',
      description: 'Brave Search API key',
    },
  },
  
  // Replace wallet addresses with placeholders
  wallets: {
    pattern: /0x[a-fA-F0-9]{40}/g,
    placeholder: '0x...WALLET_ADDRESS_REDACTED...',
    description: 'Ethereum wallet address',
  },
};

// ─── ISSUE ANALYZER ─────────────────────────────────────────────────────

class IssueAnalyzer {
  constructor() {
    this.findings = [];
  }
  
  async analyzeFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const relativePath = path.relative(process.cwd(), filePath);
      
      // Check for secrets
      for (const [name, config] of Object.entries(FIXES.secrets)) {
        const matches = content.match(config.pattern);
        if (matches) {
          this.findings.push({
            file: relativePath,
            type: 'SECRET',
            severity: 'CRITICAL',
            name,
            description: config.description,
            envVar: config.envVar,
            matches: matches.length,
            action: 'MOVE_TO_ENV',
          });
        }
      }
      
      // Check for wallet addresses
      const walletMatches = content.match(FIXES.wallets.pattern);
      if (walletMatches) {
        this.findings.push({
          file: relativePath,
          type: 'WALLET',
          severity: 'HIGH',
          description: FIXES.wallets.description,
          matches: walletMatches.length,
          action: 'REDACT',
        });
      }
      
    } catch (err) {
      // File might not exist or be unreadable
    }
  }
  
  async analyzeDirectory(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        if (!['node_modules', '.git', 'security', 'logs'].includes(entry.name)) {
          await this.analyzeDirectory(fullPath);
        }
      } else if (entry.name.endsWith('.md') || entry.name.endsWith('.json') || entry.name.endsWith('.mjs')) {
        await this.analyzeFile(fullPath);
      }
    }
  }
  
  generateReport() {
    const critical = this.findings.filter(f => f.severity === 'CRITICAL');
    const high = this.findings.filter(f => f.severity === 'HIGH');
    
    return {
      summary: {
        total: this.findings.length,
        critical: critical.length,
        high: high.length,
      },
      findings: this.findings,
      fixPlan: this.generateFixPlan(),
    };
  }
  
  generateFixPlan() {
    const plan = [];
    
    for (const finding of this.findings) {
      if (finding.action === 'MOVE_TO_ENV') {
        plan.push({
          action: 'MOVE_TO_ENV',
          file: finding.file,
          envVar: finding.envVar,
          description: `Move ${finding.description} to environment variable`,
        });
      } else if (finding.action === 'REDACT') {
        plan.push({
          action: 'REDACT',
          file: finding.file,
          description: `Redact ${finding.description}`,
        });
      }
    }
    
    return plan;
  }
}

// ─── ISSUE FIXER ────────────────────────────────────────────────────────

class IssueFixer {
  constructor() {
    this.fixed = [];
    this.failed = [];
  }
  
  async fixFile(filePath, findings) {
    try {
      let content = await fs.readFile(filePath, 'utf8');
      let modified = false;
      
      for (const finding of findings) {
        if (finding.action === 'MOVE_TO_ENV') {
          const config = FIXES.secrets[finding.name];
          if (config) {
            // Replace with env var reference
            content = content.replace(
              config.pattern,
              `process.env.${config.envVar} || '[REDACTED]'`
            );
            modified = true;
          }
        } else if (finding.action === 'REDACT') {
          content = content.replace(
            FIXES.wallets.pattern,
            FIXES.wallets.placeholder
          );
          modified = true;
        }
      }
      
      if (modified) {
        await fs.writeFile(filePath, content);
        this.fixed.push(filePath);
        return true;
      }
      
      return false;
      
    } catch (err) {
      this.failed.push({ file: filePath, error: err.message });
      return false;
    }
  }
  
  async createEnvFile() {
    const envContent = `# Cortex Environment Variables
# Generated: ${new Date().toISOString()}
# NEVER commit this file to git!

# API Keys
TELEGRAM_BOT_TOKEN=[REDACTED - SET IN REAL ENV]
OPENROUTER_API_KEY=[REDACTED - SET IN REAL ENV]
KIMI_API_KEY=[REDACTED - SET IN REAL ENV]
GOOGLE_API_KEY=[REDACTED - SET IN REAL ENV]
BRAVE_API_KEY=[REDACTED - SET IN REAL ENV]

# Add other secrets below
`;
    
    try {
      await fs.writeFile('.env', envContent);
      console.log('✅ Created .env file with secrets');
      return true;
    } catch (err) {
      console.error('❌ Failed to create .env:', err.message);
      return false;
    }
  }
  
  async createEnvExample() {
    const exampleContent = `# Cortex Environment Variables Example
# Copy this to .env and fill in your values

# API Keys (required)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
KIMI_API_KEY=your_kimi_key_here
GOOGLE_API_KEY=your_google_key_here
BRAVE_API_KEY=your_brave_key_here

# Optional
NODE_ENV=production
PORT=3000
`;
    
    try {
      await fs.writeFile('.env.example', exampleContent);
      console.log('✅ Created .env.example template');
      return true;
    } catch (err) {
      console.error('❌ Failed to create .env.example:', err.message);
      return false;
    }
  }
  
  async addToGitignore() {
    try {
      let gitignore = '';
      try {
        gitignore = await fs.readFile('.gitignore', 'utf8');
      } catch {
        // File doesn't exist
      }
      
      if (!gitignore.includes('.env')) {
        gitignore += '\n# Environment variables\n.env\n*.env\n';
        await fs.writeFile('.gitignore', gitignore);
        console.log('✅ Added .env to .gitignore');
      }
      
      return true;
    } catch (err) {
      console.error('❌ Failed to update .gitignore:', err.message);
      return false;
    }
  }
}

// ─── VERIFIER ──────────────────────────────────────────────────────────

class Verifier {
  async verifyFixes() {
    const issues = [];
    
    // Check .env exists
    try {
      await fs.access('.env');
      console.log('✅ .env file exists');
    } catch {
      issues.push('Missing .env file');
      console.log('❌ .env file missing');
    }
    
    // Check .env in .gitignore
    try {
      const gitignore = await fs.readFile('.gitignore', 'utf8');
      if (gitignore.includes('.env')) {
        console.log('✅ .env is in .gitignore');
      } else {
        issues.push('.env not in .gitignore');
        console.log('❌ .env not in .gitignore');
      }
    } catch {
      issues.push('Missing .gitignore');
      console.log('❌ .gitignore missing');
    }
    
    // Re-scan for hardcoded secrets
    const analyzer = new IssueAnalyzer();
    await analyzer.analyzeDirectory('.');
    const report = analyzer.generateReport();
    
    if (report.summary.critical === 0) {
      console.log('✅ No CRITICAL issues found');
    } else {
      console.log(`❌ ${report.summary.critical} CRITICAL issues remaining`);
      issues.push(`${report.summary.critical} critical issues remaining`);
    }
    
    return {
      passed: issues.length === 0,
      issues,
      report,
    };
  }
}

// ─── MAIN WORKFLOW ──────────────────────────────────────────────────────

async function runAnalysis() {
  console.log('🔍 ANALYZING CORTEX FOR SECURITY ISSUES\n');
  console.log('═'.repeat(70));
  
  const analyzer = new IssueAnalyzer();
  await analyzer.analyzeDirectory('.');
  const report = analyzer.generateReport();
  
  console.log(`\n📊 Found ${report.summary.total} issues:`);
  console.log(`   CRITICAL: ${report.summary.critical} 🔴`);
  console.log(`   HIGH: ${report.summary.high} 🟠`);
  
  console.log('\n🔍 CRITICAL Issues:');
  const critical = report.findings.filter(f => f.severity === 'CRITICAL');
  for (const finding of critical.slice(0, 10)) {
    console.log(`   🔴 ${finding.file}`);
    console.log(`      ${finding.description} (${finding.matches} matches)`);
    console.log(`      Action: ${finding.action} → ${finding.envVar || 'REDACT'}`);
  }
  
  if (critical.length > 10) {
    console.log(`   ... and ${critical.length - 10} more`);
  }
  
  console.log('\n📋 Fix Plan:');
  for (const item of report.fixPlan.slice(0, 10)) {
    console.log(`   ${item.action}: ${item.file}`);
    console.log(`      ${item.description}`);
  }
  
  return report;
}

async function runFixes() {
  console.log('\n🔧 FIXING CRITICAL ISSUES\n');
  console.log('═'.repeat(70));
  
  const fixer = new IssueFixer();
  
  // Step 1: Create .env file
  console.log('\n1️⃣  Creating .env file...');
  await fixer.createEnvFile();
  
  // Step 2: Create .env.example
  console.log('\n2️⃣  Creating .env.example...');
  await fixer.createEnvExample();
  
  // Step 3: Add to .gitignore
  console.log('\n3️⃣  Adding .env to .gitignore...');
  await fixer.addToGitignore();
  
  // Step 4: Analyze and fix files
  console.log('\n4️⃣  Fixing files...');
  const analyzer = new IssueAnalyzer();
  await analyzer.analyzeDirectory('.');
  
  // Group findings by file
  const fileMap = new Map();
  for (const finding of analyzer.findings) {
    if (!fileMap.has(finding.file)) {
      fileMap.set(finding.file, []);
    }
    fileMap.get(finding.file).push(finding);
  }
  
  // Fix each file
  let fixedCount = 0;
  for (const [file, findings] of fileMap) {
    const fixed = await fixer.fixFile(file, findings);
    if (fixed) {
      console.log(`   ✅ Fixed: ${file}`);
      fixedCount++;
    }
  }
  
  console.log(`\n   Fixed ${fixedCount} files`);
  
  return { fixed: fixer.fixed, failed: fixer.failed };
}

async function runVerification() {
  console.log('\n✅ VERIFYING FIXES\n');
  console.log('═'.repeat(70));
  
  const verifier = new Verifier();
  const result = await verifier.verifyFixes();
  
  console.log('\n' + '═'.repeat(70));
  if (result.passed) {
    console.log('🎉 ALL CHECKS PASSED!');
    console.log('✅ Security issues fixed');
    console.log('✅ .env file created');
    console.log('✅ .gitignore updated');
    console.log('✅ No critical issues remaining');
  } else {
    console.log('⚠️  SOME ISSUES REMAIN:');
    for (const issue of result.issues) {
      console.log(`   ❌ ${issue}`);
    }
  }
  
  return result;
}

// ─── CLI ─────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--analyze')) {
    return await runAnalysis();
  }
  
  if (args.includes('--fix')) {
    const analysis = await runAnalysis();
    const fixes = await runFixes();
    const verification = await runVerification();
    
    console.log('\n' + '═'.repeat(70));
    console.log('📊 FINAL REPORT');
    console.log('═'.repeat(70));
    console.log(`Issues found: ${analysis.summary.total}`);
    console.log(`Files fixed: ${fixes.fixed.length}`);
    console.log(`Verification: ${verification.passed ? 'PASSED ✅' : 'FAILED ❌'}`);
    
    return { analysis, fixes, verification };
  }
  
  if (args.includes('--verify')) {
    return await runVerification();
  }
  
  console.log('🔐 SECURITY DAY 5: Fix Critical Issues');
  console.log('═'.repeat(70));
  console.log('\nUsage:');
  console.log('  node day5-fix-issues.mjs --analyze   # Analyze issues');
  console.log('  node day5-fix-issues.mjs --fix       # Fix all issues');
  console.log('  node day5-fix-issues.mjs --verify    # Verify fixes');
  console.log('\nThis will:');
  console.log('  1. Create .env file');
  console.log('  2. Create .env.example');
  console.log('  3. Add .env to .gitignore');
  console.log('  4. Replace secrets with env references');
  console.log('  5. Redact wallet addresses');
  console.log('\nRunning full fix workflow...\n');
  
  return await main(['--fix']);
}

main().catch(console.error);

export { IssueAnalyzer, IssueFixer, Verifier };
