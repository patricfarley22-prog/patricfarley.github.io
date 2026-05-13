# CORTEX SECURITY RUNBOOK
## Incident Response Procedures
## Updated: 2026-05-12

---

## 🚨 INCIDENT RESPONSE FLOW

```
DETECT → ASSESS → RESPOND → RECOVER → LEARN
   ↑_____________________________________|
```

---

## 1. DETECT

### How to Detect Incidents

#### Automated Detection
- Security Monitor alerts (`security/monitor.mjs`)
- File integrity changes
- Rate limit violations
- Failed authentication attempts
- Prompt injection attempts

#### Manual Detection
- Unusual system behavior
- Unexpected API responses
- Slow performance
- Error spikes in logs

#### Check Commands
```bash
# Check security status
node security/monitor.mjs --status

# View recent alerts
tail -n 20 security/logs/alerts.jsonl

# Check file integrity
node security/monitor.mjs --check

# Scan for issues
node security/day4-secure-coding.mjs --scan .
```

---

## 2. ASSESS

### Severity Classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **CRITICAL** | System compromise, data breach | Exposed secrets, unauthorized access |
| **HIGH** | Active attack, service disruption | Injection attempts, DDoS |
| **MEDIUM** | Policy violation, potential risk | Missing validation, debug mode |
| **LOW** | Minor issue, monitoring needed | Formatting issues, warnings |

### Impact Assessment

1. **What systems are affected?**
   - Trading system?
   - Telegram bot?
   - Dashboard?
   - All systems?

2. **What data is at risk?**
   - API keys?
   - Wallet addresses?
   - User data?
   - Financial data?

3. **Scope of exposure**
   - Local only?
   - External access?
   - Public exposure?

---

## 3. RESPOND

### CRITICAL: Secret Exposure

#### Immediate Actions (First 5 minutes)
1. **Revoke exposed API keys**
   - Telegram: Contact @BotFather
   - OpenRouter: Regenerate at platform
   - Kimi: Regenerate at platform
   - Google: Regenerate in Cloud Console
   - Brave: Regenerate at dashboard

2. **Remove from repository**
   ```bash
   # Remove from git history
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     HEAD
   ```

3. **Generate new keys**
   - Update `.env` file
   - Never commit to git

4. **Restart services**
   ```bash
   # Restart Cortex
   node scripts/restart.mjs
   ```

5. **Notify stakeholders**
   - Send Telegram alert
   - Document in incident log

#### Verification (Within 1 hour)
- [ ] Old keys revoked
- [ ] New keys working
- [ ] No secrets in code
- [ ] Services restarted
- [ ] Logs reviewed

---

### HIGH: Injection Attack

#### Immediate Actions
1. **Block source**
   - Add IP to blocklist
   - Increase rate limits

2. **Review attempts**
   ```bash
   # Check injection logs
   grep "CRITICAL_INJECTION" security/logs/alerts.jsonl
   ```

3. **Update patterns**
   - Add new attack patterns
   - Update detector rules

4. **Check for success**
   - Did any attempts succeed?
   - Review system behavior

---

### MEDIUM: API Abuse

#### Response
1. Review rate limit logs
2. Identify abusive clients
3. Adjust rate limits if needed
4. Consider blocking persistent abusers

---

## 4. RECOVER

### Post-Incident Checklist

- [ ] Issue fixed
- [ ] Systems verified
- [ ] Services restarted
- [ ] Monitoring active
- [ ] Logs reviewed
- [ ] Documentation updated

### Verification Commands
```bash
# Run all security tests
node security/day1-input-validator.mjs --test
node security/day2-api-security.mjs --test
node security/day3-prompt-injection-defense.mjs --test

# Run penetration test
node security/penetration-test.mjs --all

# Re-scan for issues
node security/day4-secure-coding.mjs --scan .

# Check secrets
node security/day5-fix-issues.mjs --verify
```

---

## 5. LEARN

### Post-Incident Review

1. **What happened?**
   - Timeline of events
   - Root cause analysis

2. **How was it detected?**
   - Automated or manual?
   - Detection time?

3. **How was it resolved?**
   - Response time?
   - Effectiveness?

4. **What can improve?**
   - Detection rules
   - Response procedures
   - Monitoring coverage

### Update Security
- [ ] Add new detection patterns
- [ ] Update runbook
- [ ] Improve monitoring
- [ ] Share lessons learned

---

## 📋 QUICK REFERENCE

### Emergency Contacts
- **Telegram:** @SOL_GUYS
- **Cortex Admin:** Direct message

### Critical Files
- `.env` — Secrets
- `security/` — All security modules
- `security/logs/` — Security logs
- `security/baseline.json` — File integrity

### Key Commands
```bash
# Check status
node security/monitor.mjs --status

# Run all tests
node security/penetration-test.mjs --all

# Fix issues
node security/day5-fix-issues.mjs --fix

# Verify
node security/day5-fix-issues.mjs --verify
```

---

## 🔄 REGULAR TASKS

### Daily
- [ ] Check security alerts
- [ ] Review blocked attempts
- [ ] Monitor system health

### Weekly
- [ ] Run security scan
- [ ] Check for new vulnerabilities
- [ ] Review access logs

### Monthly
- [ ] Full penetration test
- [ ] Rotate API keys
- [ ] Update dependencies
- [ ] Review security policy

### Quarterly
- [ ] External security audit
- [ ] Update runbook
- [ ] Team training
- [ ] Compliance check

---

## 📞 ESCALATION

| Level | Criteria | Action |
|-------|----------|--------|
| **Level 1** | Single system, low impact | Self-service fix |
| **Level 2** | Multiple systems, medium impact | Team response |
| **Level 3** | All systems, high impact | Full incident response |
| **Level 4** | Data breach, legal risk | Executive notification |

---

**Last Updated: 2026-05-12**
**Version: 1.0**
**Owner: Cortex Security Team**
