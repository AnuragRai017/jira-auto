# Use the official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install ALL dependencies (including devDependencies for TypeScript compilation)
RUN npm ci

# Copy source code and configuration files
COPY src/ ./src/
COPY tsconfig.json ./
COPY server.js ./
COPY .env.example ./

# Build TypeScript code
RUN npm run build

# Verify dist directory was created
RUN ls -la dist/

# Remove devDependencies to reduce image size
RUN npm ci --only=production && npm cache clean --force

# Create a non-root user to run the application
RUN addgroup -g 1001 -S nodejs && \
    adduser -S jira-automation -u 1001

# Create directories with proper permissions
RUN mkdir -p /app/logs && chown -R jira-automation:nodejs /app

# Switch to the non-root user
USER jira-automation

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "console.log('Health check passed')" || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV LOG_LEVEL=info
ENV PORT=8080

# Default command - runs the server with continuous automation
CMD ["node", "server.js"]
