# Use the official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application code
COPY dist/ ./dist/
COPY .env* ./

# Create a non-root user to run the application
RUN addgroup -g 1001 -S nodejs
RUN adduser -S jira-automation -u 1001

# Create directories with proper permissions
RUN mkdir -p /app/logs && chown -R jira-automation:nodejs /app

# Switch to the non-root user
USER jira-automation

# Expose port (if needed for health checks)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "console.log('Health check passed')" || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV LOG_LEVEL=info

# Default command - can be overridden
CMD ["node", "dist/customer-field-automation.js", "continuous", "1440", "60000"]
