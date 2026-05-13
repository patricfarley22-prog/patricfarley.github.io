#!/usr/bin/env node
/**
 * SECURITY WEEK 3: Cloud Security & Deployment Hardening
 * AWS-ready security configuration
 * 
 * Usage:
 *   node week3-cloud-security.mjs --generate-docker
 *   node week3-cloud-security.mjs --aws-config
 *   node week3-cloud-security.mjs --compliance
 */

import fs from 'fs/promises';

// ─── CLOUD SECURITY CONFIGURATIONS ────────────────────────────────────────

const DOCKERFILE = `# Cortex AI - Production Dockerfile
# Multi-stage build for security and efficiency

# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Install security updates
RUN apk update && apk upgrade
RUN apk add --no-cache dumb-init

# Copy package files
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app

# Security: Run as non-root
RUN addgroup -g 1001 -S cortex && \\
    adduser -S -u 1001 -G cortex cortex

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy application
COPY --chown=cortex:cortex . .

# Security: Remove write permissions
RUN chmod -R 555 /app && \\
    chmod -R 755 /app/logs /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
  CMD node healthcheck.mjs || exit 1

# Expose port
EXPOSE 3000

# Switch to non-root user
USER cortex

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "server.mjs"]
`;

const DOCKER_COMPOSE = `version: '3.8'

services:
  cortex:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: cortex-ai
    restart: unless-stopped
    
    # Security: Read-only root filesystem
    read_only: true
    
    # Security: No new privileges
    security_opt:
      - no-new-privileges:true
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    
    # Environment
    env_file:
      - .env
    environment:
      - NODE_ENV=production
      - PORT=3000
    
    # Volumes (minimal, read-only where possible)
    volumes:
      - ./logs:/app/logs:rw
      - ./data:/app/data:rw
      - /tmp:/tmp:rw
    
    # Network
    networks:
      - cortex-network
    
    # Health check
    healthcheck:
      test: ["CMD", "node", "healthcheck.mjs"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "production,security"

  # Reverse proxy with security headers
  nginx:
    image: nginx:alpine
    container_name: cortex-proxy
    restart: unless-stopped
    
    ports:
      - "80:80"
      - "443:443"
    
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx:rw
    
    networks:
      - cortex-network
    
    depends_on:
      - cortex
    
    security_opt:
      - no-new-privileges:true
    
    read_only: true
    tmpfs:
      - /var/cache/nginx:noexec,nosuid,size=100m
      - /var/run:noexec,nosuid,size=100m

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: cortex-metrics
    restart: unless-stopped
    
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    
    networks:
      - cortex-network
    
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

networks:
  cortex-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  prometheus-data:
`;

const NGINX_CONFIG = `user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format security '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       '$request_time $upstream_response_time '
                       '$http_x_forwarded_for';

    access_log /var/log/nginx/access.log security;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self';" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # Hide nginx version
    server_tokens off;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript;

    upstream cortex {
        server cortex:3000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;
        
        # Redirect to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Client body limits
        client_max_body_size 10m;
        client_body_buffer_size 16k;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Security: Limit methods
        if ($request_method !~ ^(GET|POST|PUT|DELETE|OPTIONS)$ ) {
            return 405;
        }

        # Rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://cortex;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://cortex/health;
            access_log off;
        }

        # Block sensitive paths
        location ~ /(\\.env|config|backup|\\.git) {
            deny all;
            return 404;
        }
    }
}
`;

const AWS_CLOUDFORMATION = `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cortex AI - Secure Production Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
  
  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues: [t3.micro, t3.small, t3.medium, t3.large]

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: cortex-production-vpc

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: false
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: cortex-production-public

  # Private Subnet
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      MapPublicIpOnLaunch: false
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: cortex-production-private

  # Security Group
  CortexSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Cortex AI
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP redirect
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: cortex-production-sg

  # IAM Role (Least Privilege)
  CortexRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Policies:
        - PolicyName: CortexMinimalPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:PutLogEvents
                  - logs:CreateLogStream
                Resource: '*'

  # WAF WebACL
  CortexWAF:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: cortex-production-waf
      Scope: REGIONAL
      DefaultAction:
        Allow: {}
      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: cortex-production-waf
      Rules:
        - Name: RateLimit
          Priority: 1
          Statement:
            RateBasedStatement:
              Limit: 2000
              AggregateKeyType: IP
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: RateLimit
        - Name: SQLInjection
          Priority: 2
          Statement:
            SqliMatchStatement:
              FieldToMatch:
                Body: {}
              TextTransformations:
                - Priority: 0
                  Type: URL_DECODE
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: SQLInjection
        - Name: XSSProtection
          Priority: 3
          Statement:
            XssMatchStatement:
              FieldToMatch:
                Body: {}
              TextTransformations:
                - Priority: 0
                  Type: URL_DECODE
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: XSSProtection

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
  SecurityGroupId:
    Description: Security Group ID
    Value: !Ref CortexSecurityGroup
`;

// ─── SOC2 COMPLIANCE CHECKLIST ───────────────────────────────────────────

const SOC2_CHECKLIST = {
  trustServices: {
    security: [
      { id: 'CC6.1', requirement: 'Logical access security', implemented: true, evidence: 'Input validation, API security' },
      { id: 'CC6.2', requirement: 'Access removal', implemented: true, evidence: 'Session management, token revocation' },
      { id: 'CC6.3', requirement: 'Access establishment', implemented: true, evidence: 'API key generation, role-based access' },
      { id: 'CC6.4', requirement: 'Access modifications', implemented: true, evidence: 'Rate limiting, IP whitelist' },
      { id: 'CC6.5', requirement: 'Access reviews', implemented: false, evidence: 'TODO: Quarterly access review' },
      { id: 'CC6.6', requirement: 'Security infrastructure', implemented: true, evidence: 'Docker hardening, security headers' },
      { id: 'CC6.7', requirement: 'Security incident detection', implemented: true, evidence: 'Monitor, alerts, file integrity' },
      { id: 'CC6.8', requirement: 'Incident response', implemented: true, evidence: 'RUNBOOK.md, incident procedures' },
    ],
    availability: [
      { id: 'A1.1', requirement: 'System availability', implemented: true, evidence: 'Health checks, Docker restart policy' },
      { id: 'A1.2', requirement: 'System monitoring', implemented: true, evidence: 'Prometheus, CloudWatch' },
      { id: 'A1.3', requirement: 'Recovery procedures', implemented: false, evidence: 'TODO: Disaster recovery plan' },
    ],
    confidentiality: [
      { id: 'C1.1', requirement: 'Data classification', implemented: true, evidence: 'Security policy, data tiers' },
      { id: 'C1.2', requirement: 'Data encryption', implemented: true, evidence: 'AES-256-GCM, HTTPS/TLS' },
      { id: 'C1.3', requirement: 'Access to confidential data', implemented: true, evidence: '.env, SecretsManager' },
    ],
  },
};

// ─── GENERATOR ─────────────────────────────────────────────────────────

class CloudSecurityGenerator {
  async generateAll() {
    console.log('☁️  Generating Cloud Security Configurations\n');
    console.log('═'.repeat(70));

    await this.generateDocker();
    await this.generateDockerCompose();
    await this.generateNginx();
    await this.generateAWS();
    await this.generateComplianceReport();

    console.log('\n' + '═'.repeat(70));
    console.log('✅ All configurations generated!\n');
  }

  async generateDocker() {
    console.log('\n🐳 Generating Dockerfile...');
    await fs.mkdir('cloud', { recursive: true });
    await fs.writeFile('cloud/Dockerfile', DOCKERFILE);
    console.log('   ✅ cloud/Dockerfile');
  }

  async generateDockerCompose() {
    console.log('\n📦 Generating docker-compose.yml...');
    await fs.writeFile('cloud/docker-compose.yml', DOCKER_COMPOSE);
    console.log('   ✅ cloud/docker-compose.yml');
  }

  async generateNginx() {
    console.log('\n🌐 Generating nginx.conf...');
    await fs.mkdir('cloud/nginx', { recursive: true });
    await fs.writeFile('cloud/nginx/nginx.conf', NGINX_CONFIG);
    console.log('   ✅ cloud/nginx/nginx.conf');
  }

  async generateAWS() {
    console.log('\n☁️  Generating AWS CloudFormation...');
    await fs.writeFile('cloud/aws-infrastructure.yml', AWS_CLOUDFORMATION);
    console.log('   ✅ cloud/aws-infrastructure.yml');
  }

  async generateComplianceReport() {
    console.log('\n📋 Generating SOC2 Compliance Report...');

    const report = {
      generatedAt: new Date().toISOString(),
      company: 'Cortex Systems',
      system: 'Cortex AI',
      version: '1.0',
      summary: this.calculateCompliance(),
      details: SOC2_CHECKLIST,
    };

    await fs.writeFile('cloud/SOC2-COMPLIANCE.json', JSON.stringify(report, null, 2));
    console.log('   ✅ cloud/SOC2-COMPLIANCE.json');

    const readable = this.generateReadableReport(report);
    await fs.writeFile('cloud/SOC2-COMPLIANCE.md', readable);
    console.log('   ✅ cloud/SOC2-COMPLIANCE.md');
  }

  calculateCompliance() {
    let total = 0;
    let implemented = 0;

    for (const category of Object.values(SOC2_CHECKLIST.trustServices)) {
      for (const control of category) {
        total++;
        if (control.implemented) implemented++;
      }
    }

    return {
      total,
      implemented,
      notImplemented: total - implemented,
      complianceRate: `${((implemented / total) * 100).toFixed(1)}%`,
      status: implemented / total >= 0.8 ? 'COMPLIANT' : 'IN_PROGRESS',
    };
  }

  generateReadableReport(report) {
    const { summary } = report;
    let md = `# SOC 2 Compliance Report\n\n`;
    md += `**Generated:** ${report.generatedAt}\n`;
    md += `**System:** ${report.system}\n`;
    md += `**Status:** ${summary.status}\n\n`;

    md += `## Summary\n\n`;
    md += `- **Total Controls:** ${summary.total}\n`;
    md += `- **Implemented:** ${summary.implemented} ✅\n`;
    md += `- **Not Implemented:** ${summary.notImplemented} ❌\n`;
    md += `- **Compliance Rate:** ${summary.complianceRate}\n\n`;

    md += `## Trust Services Criteria\n\n`;
    for (const [service, controls] of Object.entries(report.details.trustServices)) {
      md += `### ${service.charAt(0).toUpperCase() + service.slice(1)}\n\n`;
      md += `| Control | Requirement | Status | Evidence |\n`;
      md += `|---------|-------------|--------|----------|\n`;

      for (const control of controls) {
        const status = control.implemented ? '✅' : '❌';
        md += `| ${control.id} | ${control.requirement} | ${status} | ${control.evidence} |\n`;
      }
      md += `\n`;
    }

    md += `## Next Steps\n\n`;
    md += `### To Achieve Full Compliance:\n\n`;
    for (const [service, controls] of Object.entries(report.details.trustServices)) {
      const missing = controls.filter(c => !c.implemented);
      if (missing.length > 0) {
        md += `**${service}:**\n`;
        for (const control of missing) {
          md += `- [ ] ${control.id}: ${control.requirement}\n`;
        }
        md += `\n`;
      }
    }

    return md;
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--generate-docker')) {
    const gen = new CloudSecurityGenerator();
    return await gen.generateDocker();
  }

  if (args.includes('--aws-config')) {
    const gen = new CloudSecurityGenerator();
    return await gen.generateAWS();
  }

  if (args.includes('--compliance')) {
    const gen = new CloudSecurityGenerator();
    return await gen.generateComplianceReport();
  }

  if (args.includes('--all')) {
    const gen = new CloudSecurityGenerator();
    return await gen.generateAll();
  }

  console.log('☁️  SECURITY WEEK 3: Cloud Security & Deployment');
  console.log('═'.repeat(70));
  console.log('\nUsage:');
  console.log('  node week3-cloud-security.mjs --all              # Generate everything');
  console.log('  node week3-cloud-security.mjs --generate-docker  # Dockerfile only');
  console.log('  node week3-cloud-security.mjs --aws-config         # AWS only');
  console.log('  node week3-cloud-security.mjs --compliance       # SOC2 report');
  console.log('\nThis generates:');
  console.log('  • Hardened Dockerfile (non-root, read-only)');
  console.log('  • Docker Compose with security options');
  console.log('  • Nginx reverse proxy with WAF rules');
  console.log('  • AWS CloudFormation (VPC, WAF, IAM)');
  console.log('  • SOC2 compliance checklist');
  console.log('\nGenerating all configurations...\n');

  const gen = new CloudSecurityGenerator();
  return await gen.generateAll();
}

main().catch(console.error);

export { CloudSecurityGenerator, SOC2_CHECKLIST };
