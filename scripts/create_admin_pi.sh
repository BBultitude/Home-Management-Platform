#!/bin/bash
# Create Admin User Script for Raspberry Pi
# Wrapper for creating an admin user in the Home Management Platform

set -e

COMPOSE_FILE="docker-compose.pi.yml"

echo "=============================================="
echo "Home Management Platform - Create Admin User"
echo "Raspberry Pi Edition"
echo "=============================================="
echo ""

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Error: Docker is not running or you don't have permission to access it"
    exit 1
fi

# The scripts will automatically read the database password from Docker secrets
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

echo ""
echo "Done!"
