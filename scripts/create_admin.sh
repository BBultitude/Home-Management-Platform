#!/bin/bash
# Create Admin User Script
# Wrapper for creating an admin user in the Home Management Platform

set -e

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
CONTAINER_NAME="${CONTAINER_NAME:-homemanager_backend_prod}"

echo "=============================================="
echo "Home Management Platform - Create Admin User"
echo "=============================================="
echo ""

# Check if running in Docker or locally
if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "Running in Docker container: $CONTAINER_NAME"
    echo ""

    if [ $# -eq 0 ]; then
        # Interactive mode
        echo "Interactive mode - you will be prompted for details"
        echo ""
        docker compose -f "$COMPOSE_FILE" exec backend python3 /app/create_admin.py
    else
        # Command-line mode with arguments
        echo "Creating admin user with provided credentials..."
        echo ""
        docker compose -f "$COMPOSE_FILE" exec -T backend python3 /app/create_admin.py "$@"
    fi
else
    echo "Running locally (no Docker container found)"
    echo ""

    # Run directly
    cd "$(dirname "$0")/../backend"
    python3 create_admin.py "$@"
fi

echo ""
echo "Done!"
