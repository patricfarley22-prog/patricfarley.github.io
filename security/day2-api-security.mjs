#!/usr/bin/env node
/**
 * SECURITY DAY 2: API Security & Authentication
 * 
 * Module 2 of Patric's AI Engineer Bootcamp
 * Focus: Protect API endpoints from abuse and unauthorized access
 * 
 * What this does:
 * - Rate limiting (prevent abuse)
 * - API key validation (authenticate requests)
 * - IP whitelisting (geographic controls)
 * - Request signing (verify integrity)
 * - Token-based auth (stateless sessions)
 * - Logging & monitoring
 * 
 * Usage:
 *   node security/day2-api-security.mjs --test
 *   node security/day2-api-security.mjs --demo
 */

import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

// ─── CONFIGURATION ───────────────────────────────────────────────────────

const CONFIG = {
  // Rate limiting
  rateLimit: {
    enabled: true,
    windowMs: 60000,        // 1 minute window
    maxRequests: 100,       // Max 100 requests per minute
    burstAllowance: 10,     // Allow burst of 10
    blockDuration: 300000,  // Block for 5 minutes if exceeded
  },
  
  // API key management
  apiKeys: {
    enabled: true,
    headerName: 'X-API-Key',
    keyPrefix: 'ctx_',
    keyLength: 32,
    rotationDays: 90,      // Rotate keys every 90 days
  },
  
  // IP whitelisting
  ipWhitelist: {
    enabled: false,         // Disabled by default (enable for production)
    allowedIPs: [
      '127.0.0.1',         // localhost
      '::1',               // IPv6 localhost
      // Add your IPs here
    ],
    allowedRanges: [
      // CIDR ranges
      // '192.168.1.0/24',
    ],
  },
  
  // Request signing
  requestSigning: {
    enabled: true,
    headerName: 'X-Signature',
    timestampHeader: 'X-Timestamp',
    signatureVersion: 'v1',
    maxTimestampDiff: 300000,  // 5 minutes max
  },
  
  // Token auth (JWT alternative - simpler)
  tokenAuth: {
    enabled: true,
    headerName: 'Authorization',
    tokenPrefix: 'Bearer ',
    secret: process.env.API_AUTH_SECRET || 'cortex-default-secret-change-in-production',
    expiresIn: '1h',
    refreshTokenExpiresIn: '7d',
  },
  
  // Logging
  logFile: 'security/logs/api-security.log',
  logLevel: 'INFO',
};

// ─── IN-MEMORY STORE (replace with Redis in production) ────────────────

class MemoryStore {
  constructor() {
    this.data = new Map();
    this.timestamps = new Map();
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
  }
  
  get(key) {
    const value = this.data.get(key);
    if (value && Date.now() > value.expiresAt) {
      this.data.delete(key);
      return null;
    }
    return value?.data || null;
  }
  
  set(key, value, ttlMs = 3600000) {
    this.data.set(key, {
      data: value,
      expiresAt: Date.now() + ttlMs,
    });
    this.timestamps.set(key, Date.now());
  }
  
  delete(key) {
    this.data.delete(key);
    this.timestamps.delete(key);
  }
  
  cleanup() {
    const now = Date.now();
    for (const [key, value] of this.data) {
      if (now > value.expiresAt) {
        this.data.delete(key);
        this.timestamps.delete(key);
      }
    }
  }
  
  clear() {
    this.data.clear();
    this.timestamps.clear();
  }
}

const store = new MemoryStore();

// ─── RATE LIMITER ────────────────────────────────────────────────────────

class RateLimiter {
  constructor(config = CONFIG.rateLimit) {
    this.config = config;
    this.store = store;
  }
  
  /**
   * Check if request is within rate limit
   * @param {string} clientId - IP address or API key
   * @returns {object} Rate limit status
   */
  check(clientId) {
    if (!this.config.enabled) {
      return { allowed: true, remaining: Infinity, resetAt: Date.now() + 3600000 };
    }
    
    const key = `rate:${clientId}`;
    const now = Date.now();
    
    // Get current state
    let state = this.store.get(key);
    if (!state || now > state.windowEnd) {
      state = {
        count: 0,
        windowStart: now,
        windowEnd: now + this.config.windowMs,
        blocked: false,
        blockedUntil: null,
      };
    }
    
    // Check if currently blocked
    if (state.blocked && now < state.blockedUntil) {
      return {
        allowed: false,
        remaining: 0,
        resetAt: state.blockedUntil,
        blocked: true,
        reason: 'Rate limit exceeded',
      };
    }
    
    // Reset block if expired
    if (state.blocked && now >= state.blockedUntil) {
      state = {
        count: 0,
        windowStart: now,
        windowEnd: now + this.config.windowMs,
        blocked: false,
        blockedUntil: null,
      };
    }
    
    // Check if within burst allowance
    if (state.count < this.config.burstAllowance) {
      state.count++;
      this.store.set(key, state, this.config.windowMs);
      return {
        allowed: true,
        remaining: this.config.burstAllowance - state.count,
        resetAt: state.windowEnd,
        blocked: false,
      };
    }
    
    // Check regular limit
    if (state.count < this.config.maxRequests) {
      state.count++;
      this.store.set(key, state, this.config.windowMs);
      return {
        allowed: true,
        remaining: this.config.maxRequests - state.count,
        resetAt: state.windowEnd,
        blocked: false,
      };
    }
    
    // Rate limit exceeded - block
    state.blocked = true;
    state.blockedUntil = now + this.config.blockDuration;
    this.store.set(key, state, this.config.blockDuration);
    
    return {
      allowed: false,
      remaining: 0,
      resetAt: state.blockedUntil,
      blocked: true,
      reason: `Rate limit exceeded. Blocked for ${this.config.blockDuration / 1000}s`,
    };
  }
  
  /**
   * Get current rate limit status for client
   */
  getStatus(clientId) {
    const key = `rate:${clientId}`;
    const state = this.store.get(key);
    
    if (!state) {
      return {
        limit: this.config.maxRequests,
        remaining: this.config.maxRequests,
        resetAt: Date.now() + this.config.windowMs,
        blocked: false,
      };
    }
    
    return {
      limit: this.config.maxRequests,
      remaining: Math.max(0, this.config.maxRequests - state.count),
      resetAt: state.windowEnd,
      blocked: state.blocked && Date.now() < state.blockedUntil,
      blockedUntil: state.blockedUntil,
    };
  }
}

// ─── API KEY MANAGER ─────────────────────────────────────────────────────

class APIKeyManager {
  constructor(config = CONFIG.apiKeys) {
    this.config = config;
    this.keys = new Map();
    this.revokedKeys = new Set();
  }
  
  /**
   * Generate a new API key
   * @param {string} name - Key name/label
   * @param {object} metadata - Additional metadata
   * @returns {object} Key info
   */
  generateKey(name, metadata = {}) {
    const key = this.config.keyPrefix + crypto.randomBytes(this.config.keyLength).toString('hex');
    const id = crypto.randomUUID();
    
    const keyInfo = {
      id,
      key,
      name,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + (this.config.rotationDays * 24 * 60 * 60 * 1000)).toISOString(),
      lastUsed: null,
      usageCount: 0,
      metadata,
    };
    
    this.keys.set(key, keyInfo);
    
    return {
      id,
      key,
      name,
      createdAt: keyInfo.createdAt,
      expiresAt: keyInfo.expiresAt,
    };
  }
  
  /**
   * Validate API key
   * @param {string} key - API key to validate
   * @returns {object} Validation result
   */
  validateKey(key) {
    if (!key) {
      return { valid: false, reason: 'No API key provided' };
    }
    
    if (!key.startsWith(this.config.keyPrefix)) {
      return { valid: false, reason: 'Invalid key format' };
    }
    
    if (this.revokedKeys.has(key)) {
      return { valid: false, reason: 'Key has been revoked' };
    }
    
    const keyInfo = this.keys.get(key);
    if (!keyInfo) {
      return { valid: false, reason: 'Invalid API key' };
    }
    
    if (new Date() > new Date(keyInfo.expiresAt)) {
      return { valid: false, reason: 'Key has expired' };
    }
    
    // Update usage
    keyInfo.lastUsed = new Date().toISOString();
    keyInfo.usageCount++;
    
    return {
      valid: true,
      keyInfo: {
        id: keyInfo.id,
        name: keyInfo.name,
        createdAt: keyInfo.createdAt,
        expiresAt: keyInfo.expiresAt,
        metadata: keyInfo.metadata,
      },
    };
  }
  
  /**
   * Revoke API key
   * @param {string} key - API key to revoke
   */
  revokeKey(key) {
    if (this.keys.has(key)) {
      this.revokedKeys.add(key);
      this.keys.delete(key);
      return { revoked: true };
    }
    return { revoked: false, reason: 'Key not found' };
  }
  
  /**
   * List all active keys
   */
  listKeys() {
    return Array.from(this.keys.values()).map(k => ({
      id: k.id,
      name: k.name,
      createdAt: k.createdAt,
      expiresAt: k.expiresAt,
      lastUsed: k.lastUsed,
      usageCount: k.usageCount,
    }));
  }
}

// ─── IP WHITELIST ────────────────────────────────────────────────────────

class IPWhitelist {
  constructor(config = CONFIG.ipWhitelist) {
    this.config = config;
  }
  
  /**
   * Check if IP is allowed
   * @param {string} ip - IP address
   * @returns {object} Check result
   */
  checkIP(ip) {
    if (!this.config.enabled) {
      return { allowed: true, reason: 'Whitelist disabled' };
    }
    
    if (!ip) {
      return { allowed: false, reason: 'No IP provided' };
    }
    
    // Check exact match
    if (this.config.allowedIPs.includes(ip)) {
      return { allowed: true, reason: 'IP whitelisted' };
    }
    
    // Check CIDR ranges
    for (const range of this.config.allowedRanges) {
      if (this.ipInRange(ip, range)) {
        return { allowed: true, reason: 'IP in allowed range' };
      }
    }
    
    return { allowed: false, reason: 'IP not whitelisted' };
  }
  
  /**
   * Check if IP is in CIDR range
   */
  ipInRange(ip, cidr) {
    const [range, bits] = cidr.split('/');
    const mask = parseInt(bits, 10);
    
    const ipLong = this.ipToLong(ip);
    const rangeLong = this.ipToLong(range);
    const maskLong = -1 << (32 - mask);
    
    return (ipLong & maskLong) === (rangeLong & maskLong);
  }
  
  ipToLong(ip) {
    return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0;
  }
}

// ─── REQUEST SIGNER ──────────────────────────────────────────────────────

class RequestSigner {
  constructor(config = CONFIG.requestSigning) {
    this.config = config;
  }
  
  /**
   * Sign a request
   * @param {string} method - HTTP method
   * @param {string} path - Request path
   * @param {string} body - Request body
   * @param {string} secret - Signing secret
   * @returns {object} Signature and timestamp
   */
  sign(method, path, body = '', secret) {
    const timestamp = Date.now().toString();
    const payload = `${method}|${path}|${body}|${timestamp}|${this.config.signatureVersion}`;
    const signature = crypto.createHmac('sha256', secret).update(payload).digest('hex');
    
    return {
      signature,
      timestamp,
      version: this.config.signatureVersion,
    };
  }
  
  /**
   * Verify request signature
   * @param {string} signature - Provided signature
   * @param {string} timestamp - Provided timestamp
   * @param {string} method - HTTP method
   * @param {string} path - Request path
   * @param {string} body - Request body
   * @param {string} secret - Signing secret
   * @returns {object} Verification result
   */
  verify(signature, timestamp, method, path, body = '', secret) {
    // Check timestamp
    const now = Date.now();
    const reqTime = parseInt(timestamp, 10);
    
    if (isNaN(reqTime)) {
      return { valid: false, reason: 'Invalid timestamp' };
    }
    
    if (Math.abs(now - reqTime) > this.config.maxTimestampDiff) {
      return {
        valid: false,
        reason: `Request too old or timestamp in future (${Math.abs(now - reqTime)}ms diff)`,
      };
    }
    
    // Verify signature
    const payload = `${method}|${path}|${body}|${timestamp}|${this.config.signatureVersion}`;
    const expectedSignature = crypto.createHmac('sha256', secret).update(payload).digest('hex');
    
    if (signature !== expectedSignature) {
      return { valid: false, reason: 'Invalid signature' };
    }
    
    return { valid: true, timestamp: reqTime };
  }
}

// ─── TOKEN AUTH (Simple JWT Alternative) ─────────────────────────────────

class TokenAuth {
  constructor(config = CONFIG.tokenAuth) {
    this.config = config;
    this.revokedTokens = new Set();
  }
  
  /**
   * Generate token
   * @param {object} payload - Token payload
   * @returns {object} Token and refresh token
   */
  generateToken(payload) {
    const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
    
    const now = Math.floor(Date.now() / 1000);
    const tokenPayload = {
      ...payload,
      iat: now,
      exp: now + this.parseTime(this.config.expiresIn),
      jti: crypto.randomUUID(),
    };
    
    const payloadB64 = Buffer.from(JSON.stringify(tokenPayload)).toString('base64url');
    const signature = crypto.createHmac('sha256', this.config.secret)
      .update(`${header}.${payloadB64}`)
      .digest('base64url');
    
    const token = `${header}.${payloadB64}.${signature}`;
    
    // Generate refresh token
    const refreshPayload = {
      ...payload,
      iat: now,
      exp: now + this.parseTime(this.config.refreshTokenExpiresIn),
      jti: crypto.randomUUID(),
      type: 'refresh',
    };
    
    const refreshPayloadB64 = Buffer.from(JSON.stringify(refreshPayload)).toString('base64url');
    const refreshSignature = crypto.createHmac('sha256', this.config.secret)
      .update(`${header}.${refreshPayloadB64}`)
      .digest('base64url');
    
    const refreshToken = `${header}.${refreshPayloadB64}.${refreshSignature}`;
    
    return {
      token,
      refreshToken,
      expiresAt: tokenPayload.exp,
    };
  }
  
  /**
   * Verify token
   * @param {string} token - Token to verify
   * @returns {object} Verification result
   */
  verifyToken(token) {
    if (!token) {
      return { valid: false, reason: 'No token provided' };
    }
    
    if (this.revokedTokens.has(token)) {
      return { valid: false, reason: 'Token revoked' };
    }
    
    const parts = token.split('.');
    if (parts.length !== 3) {
      return { valid: false, reason: 'Invalid token format' };
    }
    
    const [header, payload, signature] = parts;
    
    // Verify signature
    const expectedSignature = crypto.createHmac('sha256', this.config.secret)
      .update(`${header}.${payload}`)
      .digest('base64url');
    
    if (signature !== expectedSignature) {
      return { valid: false, reason: 'Invalid signature' };
    }
    
    // Decode payload
    try {
      const decodedPayload = JSON.parse(Buffer.from(payload, 'base64url').toString());
      
      // Check expiration
      if (decodedPayload.exp && Date.now() > decodedPayload.exp * 1000) {
        return { valid: false, reason: 'Token expired' };
      }
      
      return {
        valid: true,
        payload: decodedPayload,
      };
    } catch {
      return { valid: false, reason: 'Invalid payload' };
    }
  }
  
  /**
   * Revoke token
   */
  revokeToken(token) {
    this.revokedTokens.add(token);
    return { revoked: true };
  }
  
  parseTime(timeStr) {
    const match = timeStr.match(/^(\d+)([smhd])$/);
    if (!match) return 3600;
    
    const value = parseInt(match[1], 10);
    const unit = match[2];
    
    const multipliers = { s: 1, m: 60, h: 3600, d: 86400 };
    return value * (multipliers[unit] || 1);
  }
}

// ─── API SECURITY GUARD (Main class) ────────────────────────────────────

class APISecurityGuard {
  constructor(config = CONFIG) {
    this.config = config;
    this.rateLimiter = new RateLimiter(config.rateLimit);
    this.keyManager = new APIKeyManager(config.apiKeys);
    this.ipWhitelist = new IPWhitelist(config.ipWhitelist);
    this.requestSigner = new RequestSigner(config.requestSigning);
    this.tokenAuth = new TokenAuth(config.tokenAuth);
  }
  
  /**
   * Main middleware function - checks all security layers
   * @param {object} request - Request object
   * @returns {object} Security check result
   */
  async checkRequest(request) {
    const result = {
      allowed: true,
      checks: {},
      errors: [],
      warnings: [],
      requestId: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    };
    
    const { ip, headers, method, path, body } = request;
    const clientId = ip || 'unknown';
    
    // 1. IP Whitelist check
    const ipCheck = this.ipWhitelist.checkIP(ip);
    result.checks.ipWhitelist = ipCheck;
    if (!ipCheck.allowed) {
      result.allowed = false;
      result.errors.push(ipCheck.reason);
    }
    
    // 2. Rate limit check
    const rateCheck = this.rateLimiter.check(clientId);
    result.checks.rateLimit = rateCheck;
    if (!rateCheck.allowed) {
      result.allowed = false;
      result.errors.push(rateCheck.reason);
    }
    
    // 3. API Key validation (only if enabled and key provided)
    if (this.config.apiKeys.enabled) {
      const apiKey = headers[this.config.apiKeys.headerName.toLowerCase()];
      if (apiKey) {
        const keyCheck = this.keyManager.validateKey(apiKey);
        result.checks.apiKey = keyCheck;
        if (!keyCheck.valid) {
          result.allowed = false;
          result.errors.push(keyCheck.reason);
        }
      }
    }
    
    // 4. Request signature validation (only if enabled and signature provided)
    if (this.config.requestSigning.enabled) {
      const signature = headers[this.config.requestSigning.headerName.toLowerCase()];
      const timestamp = headers[this.config.requestSigning.timestampHeader.toLowerCase()];
      
      if (signature && timestamp) {
        const sigCheck = this.requestSigner.verify(
          signature,
          timestamp,
          method,
          path,
          JSON.stringify(body || ''),
          this.config.tokenAuth.secret
        );
        result.checks.signature = sigCheck;
        if (!sigCheck.valid) {
          result.allowed = false;
          result.errors.push(sigCheck.reason);
        }
      }
    }
    
    // 5. Token validation (only if no API key, or both)
    if (this.config.tokenAuth.enabled) {
      const authHeader = headers[this.config.tokenAuth.headerName.toLowerCase()];
      if (authHeader) {
        const token = authHeader.replace(this.config.tokenAuth.tokenPrefix, '');
        const tokenCheck = this.tokenAuth.verifyToken(token);
        result.checks.token = tokenCheck;
        if (!tokenCheck.valid) {
          result.allowed = false;
          result.errors.push(tokenCheck.reason);
        }
      }
    }
    
    // Log result
    this.log(result);
    
    return result;
  }
  
  async log(result) {
    if (this.config.logLevel === 'NONE') return;
    
    try {
      await fs.mkdir(path.dirname(this.config.logFile), { recursive: true });
      await fs.appendFile(
        this.config.logFile,
        JSON.stringify(result) + '\n'
      );
    } catch (err) {
      console.error('Failed to log:', err.message);
    }
  }
}

// ─── TEST SUITE ──────────────────────────────────────────────────────────

async function runTests() {
  console.log('🧪 Running API Security Tests\n');
  console.log('═'.repeat(70));
  
  const guard = new APISecurityGuard();
  let passed = 0;
  let failed = 0;
  
  const tests = [
    // Test 1: Valid request
    {
      name: 'Valid request (no auth)',
      request: {
        ip: '127.0.0.1',
        headers: {},
        method: 'GET',
        path: '/api/health',
        body: '',
      },
      expected: { allowed: true },
    },
    
    // Test 2: Rate limiting
    {
      name: 'Rate limit (exceeding)',
      request: {
        ip: '192.168.1.100',
        headers: {},
        method: 'GET',
        path: '/api/data',
        body: '',
      },
      setup: async (guard) => {
        // Make 105 requests to exceed limit
        for (let i = 0; i < 105; i++) {
          guard.rateLimiter.check('192.168.1.100');
        }
      },
      expected: { allowed: false },
    },
    
    // Test 3: API key validation
    {
      name: 'Valid API key',
      request: {
        ip: '127.0.0.1',
        headers: { 'x-api-key': '' },
        method: 'GET',
        path: '/api/protected',
        body: '',
      },
      setup: (guard) => {
        const keyInfo = guard.keyManager.generateKey('test-key');
        guard.config.apiKeys.enabled = true;
        return keyInfo.key;
      },
      modifyRequest: (request, key) => {
        request.headers['x-api-key'] = key;
      },
      expected: { allowed: true },
    },
    
    // Test 4: Invalid API key
    {
      name: 'Invalid API key',
      request: {
        ip: '127.0.0.1',
        headers: { 'x-api-key': 'invalid-key' },
        method: 'GET',
        path: '/api/protected',
        body: '',
      },
      setup: (guard) => {
        guard.config.apiKeys.enabled = true;
      },
      expected: { allowed: false },
    },
    
    // Test 5: IP whitelist (blocked)
    {
      name: 'IP whitelist (blocked)',
      request: {
        ip: '10.0.0.1',
        headers: {},
        method: 'GET',
        path: '/api/data',
        body: '',
      },
      setup: (guard) => {
        guard.config.ipWhitelist.enabled = true;
      },
      expected: { allowed: false },
    },
    
    // Test 6: Token generation and validation
    {
      name: 'Token auth (valid)',
      request: {
        ip: '127.0.0.1',
        headers: { authorization: '' },
        method: 'GET',
        path: '/api/user',
        body: '',
      },
      setup: (guard) => {
        const tokenInfo = guard.tokenAuth.generateToken({ userId: '123', role: 'admin' });
        guard.config.tokenAuth.enabled = true;
        return tokenInfo.token;
      },
      modifyRequest: (request, token) => {
        request.headers.authorization = `Bearer ${token}`;
      },
      expected: { allowed: true },
    },
    
    // Test 7: Request signing
    {
      name: 'Request signing (valid)',
      request: {
        ip: '127.0.0.1',
        headers: {},
        method: 'POST',
        path: '/api/webhook',
        body: { event: 'test' },
      },
      setup: (guard) => {
        const { signature, timestamp } = guard.requestSigner.sign(
          'POST',
          '/api/webhook',
          JSON.stringify({ event: 'test' }),
          guard.config.tokenAuth.secret
        );
        guard.config.requestSigning.enabled = true;
        return { signature, timestamp };
      },
      modifyRequest: (request, sig) => {
        request.headers['x-signature'] = sig.signature;
        request.headers['x-timestamp'] = sig.timestamp;
      },
      expected: { allowed: true },
    },
  ];
  
  for (const test of tests) {
    // Setup
    let setupResult = null;
    if (test.setup) {
      setupResult = await test.setup(guard);
    }
    
    // Modify request if needed
    if (test.modifyRequest) {
      test.modifyRequest(test.request, setupResult);
    }
    
    // Run check
    const result = await guard.checkRequest(test.request);
    
    const testPassed = result.allowed === test.expected.allowed;
    
    if (testPassed) {
      passed++;
      console.log(`✅ ${test.name}`);
    } else {
      failed++;
      console.log(`❌ ${test.name}`);
      console.log(`   Expected: allowed=${test.expected.allowed}`);
      console.log(`   Got: allowed=${result.allowed}`);
      if (result.errors.length > 0) {
        console.log(`   Errors: ${result.errors.join(', ')}`);
      }
    }
  }
  
  console.log('\n' + '═'.repeat(70));
  console.log(`📊 Results: ${passed}/${tests.length} passed`);
  console.log(`   ${failed} tests failed`);
  console.log(`   Pass rate: ${((passed / tests.length) * 100).toFixed(1)}%`);
  
  return { passed, failed, total: tests.length };
}

async function runDemo() {
  console.log('🎮 API Security Demo\n');
  console.log('═'.repeat(70));
  
  const guard = new APISecurityGuard();
  
  // Generate API key
  console.log('\n1️⃣  Generating API Key...');
  const keyInfo = guard.keyManager.generateKey('demo-key', { tier: 'pro' });
  console.log(`   Key: ${keyInfo.key.substring(0, 20)}...`);
  console.log(`   Expires: ${keyInfo.expiresAt}`);
  
  // Generate token
  console.log('\n2️⃣  Generating Auth Token...');
  const tokenInfo = guard.tokenAuth.generateToken({ userId: 'demo-user', role: 'admin' });
  console.log(`   Token: ${tokenInfo.token.substring(0, 40)}...`);
  console.log(`   Expires: ${new Date(tokenInfo.expiresAt * 1000).toISOString()}`);
  
  // Sign request
  console.log('\n3️⃣  Signing Request...');
  const sigInfo = guard.requestSigner.sign('POST', '/api/trade', '{"symbol":"SOL"}', CONFIG.tokenAuth.secret);
  console.log(`   Signature: ${sigInfo.signature.substring(0, 40)}...`);
  console.log(`   Timestamp: ${sigInfo.timestamp}`);
  
  // Check rate limit
  console.log('\n4️⃣  Checking Rate Limit...');
  for (let i = 1; i <= 5; i++) {
    const check = guard.rateLimiter.check('demo-client');
    console.log(`   Request ${i}: ${check.allowed ? '✅ Allowed' : '❌ Blocked'} (remaining: ${check.remaining})`);
  }
  
  // Test full security check
  console.log('\n5️⃣  Full Security Check...');
  const secureRequest = {
    ip: '127.0.0.1',
    headers: {
      'x-api-key': keyInfo.key,
      'authorization': `Bearer ${tokenInfo.token}`,
      'x-signature': sigInfo.signature,
      'x-timestamp': sigInfo.timestamp,
    },
    method: 'POST',
    path: '/api/trade',
    body: { symbol: 'SOL', amount: 100 },
  };
  
  const result = await guard.checkRequest(secureRequest);
  console.log(`   Allowed: ${result.allowed ? '✅ YES' : '❌ NO'}`);
  console.log(`   Checks performed: ${Object.keys(result.checks).length}`);
  console.log(`   Request ID: ${result.requestId}`);
  
  if (!result.allowed) {
    console.log(`   Errors: ${result.errors.join(', ')}`);
  }
  
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
  
  console.log('🔐 SECURITY DAY 2: API Security & Authentication');
  console.log('═'.repeat(70));
  console.log('\nUsage:');
  console.log('  node day2-api-security.mjs --test     # Run all tests');
  console.log('  node day2-api-security.mjs --demo     # Run demo');
  console.log('\nComponents:');
  console.log('  • Rate Limiter      - Prevent API abuse');
  console.log('  • API Key Manager   - Authenticate requests');
  console.log('  • IP Whitelist      - Geographic controls');
  console.log('  • Request Signer    - Verify integrity');
  console.log('  • Token Auth        - Stateless sessions');
  console.log('\nRunning demo...\n');
  
  return await runDemo();
}

main().catch(console.error);

export { APISecurityGuard, RateLimiter, APIKeyManager, IPWhitelist, RequestSigner, TokenAuth };
