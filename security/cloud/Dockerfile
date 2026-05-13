# Cortex AI - Production Dockerfile
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
RUN addgroup -g 1001 -S cortex && \
    adduser -S -u 1001 -G cortex cortex

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy application
COPY --chown=cortex:cortex . .

# Security: Remove write permissions
RUN chmod -R 555 /app && \
    chmod -R 755 /app/logs /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD node healthcheck.mjs || exit 1

# Expose port
EXPOSE 3000

# Switch to non-root user
USER cortex

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "server.mjs"]
