# ============================================
# Multi-stage build for production frontend
# Stage 1: Build React application
# Stage 2: Serve with Nginx
# ============================================

# ============================================
# Stage 1: Build
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
# Note: TypeScript, Vite, and other build tools are in devDependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
RUN npm run build

# ============================================
# Stage 2: Production with Nginx
# ============================================
FROM nginx:1.25-alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create a script to inject runtime environment variables
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-inject-env.sh && \
    echo 'echo "window.ENV = { VITE_API_URL: \"${VITE_API_URL}\" };"' \
      '> /usr/share/nginx/html/env-config.js' \
      >> /docker-entrypoint.d/40-inject-env.sh && \
    chmod +x /docker-entrypoint.d/40-inject-env.sh && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

USER nginx
EXPOSE 8080

# Nginx will start automatically (from base image)
