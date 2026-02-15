#!/bin/bash
# Reset Password Script for Raspberry Pi
# Usage: ./reset_password_pi.sh <username> <new_password>

set -e

COMPOSE_FILE="docker-compose.pi.yml"

echo "=============================================="
echo "Home Management Platform - Reset Password"
echo "Raspberry Pi Edition"
echo "=============================================="
echo ""

if [ $# -ne 2 ]; then
    echo "Usage: $0 <username> <new_password>"
    echo ""
    echo "Example:"
    echo "  $0 admin MyNewSecurePassword2026"
    echo ""
    echo "Password requirements:"
    echo "  - At least 12 characters"
    echo "  - Must contain uppercase letters (A-Z)"
    echo "  - Must contain lowercase letters (a-z)"
    echo "  - Must contain digits (0-9)"
    exit 1
fi

USERNAME="$1"
PASSWORD="$2"

echo "Resetting password for user: $USERNAME"
echo ""

# Run the reset_password.py script inside the backend container
# The script will automatically read the database password from Docker secrets
docker compose -f "$COMPOSE_FILE" exec -T backend python3 /app/reset_password.py "$USERNAME" "$PASSWORD"

echo ""
echo "Done!"
