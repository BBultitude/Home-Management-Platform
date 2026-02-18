#!/bin/bash
# Emergency MFA Disable Script for Raspberry Pi
# BREAK-GLASS ONLY - Use when locked out
#
# Usage: ./disable_mfa_pi.sh <username>
#
# Example:
#   ./disable_mfa_pi.sh admin
#   ./disable_mfa_pi.sh Bryan

set -e

COMPOSE_FILE="docker-compose.pi.yml"

echo "=============================================="
echo "🚨 EMERGENCY MFA DISABLE SCRIPT"
echo "Raspberry Pi Edition"
echo "=============================================="
echo ""

if [ $# -ne 1 ]; then
    echo "Usage: $0 <username>"
    echo ""
    echo "Example:"
    echo "  $0 admin"
    echo "  $0 Bryan"
    echo ""
    echo "⚠️  WARNING: This will disable MFA and allow password-only login"
    exit 1
fi

USERNAME="$1"

echo "⚠️  WARNING: You are about to DISABLE MFA for user: $USERNAME"
echo ""
echo "This will:"
echo "  - Disable MFA requirement"
echo "  - Revoke all trusted devices"
echo "  - Allow password-only login"
echo ""
read -p "Are you sure? Type 'YES' to confirm: " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "❌ Operation cancelled"
    exit 0
fi

echo ""
echo "Disabling MFA for user: $USERNAME"
echo ""

# Run the disable_mfa.py script inside the backend container
docker compose -f "$COMPOSE_FILE" exec -T backend python3 /app/disable_mfa.py "$USERNAME"

echo ""
echo "Done!"
