#!/bin/bash

# Script to generate secure secrets for the Home Management Platform
# Run this once during initial setup

set -e

SECRETS_DIR="./secrets"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Home Management Platform - Secret Generation ===${NC}\n"

# Create secrets directory if it doesn't exist
if [ ! -d "$SECRETS_DIR" ]; then
    echo -e "${YELLOW}Creating secrets directory...${NC}"
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
fi

# Check if secrets already exist
if [ -f "$SECRETS_DIR/db_password.txt" ] || \
   [ -f "$SECRETS_DIR/jwt_secret.txt" ] || \
   [ -f "$SECRETS_DIR/mfa_encryption_key.txt" ]; then
    echo -e "${RED}WARNING: Some secrets already exist!${NC}"
    echo "Existing secrets will NOT be overwritten."
    echo "If you want to regenerate secrets, delete them first:"
    echo "  rm $SECRETS_DIR/*.txt"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Function to generate a random secret
generate_secret() {
    openssl rand -base64 32 | tr -d '\n'
}

# Generate database password
if [ ! -f "$SECRETS_DIR/db_password.txt" ]; then
    echo -e "${YELLOW}Generating database password...${NC}"
    generate_secret > "$SECRETS_DIR/db_password.txt"
    chmod 600 "$SECRETS_DIR/db_password.txt"
    echo -e "${GREEN}✓ Database password generated${NC}"
else
    echo -e "${YELLOW}✓ Database password already exists (skipped)${NC}"
fi

# Generate JWT secret
if [ ! -f "$SECRETS_DIR/jwt_secret.txt" ]; then
    echo -e "${YELLOW}Generating JWT secret...${NC}"
    generate_secret > "$SECRETS_DIR/jwt_secret.txt"
    chmod 600 "$SECRETS_DIR/jwt_secret.txt"
    echo -e "${GREEN}✓ JWT secret generated${NC}"
else
    echo -e "${YELLOW}✓ JWT secret already exists (skipped)${NC}"
fi

# Generate MFA encryption key (Fernet key format)
if [ ! -f "$SECRETS_DIR/mfa_encryption_key.txt" ]; then
    echo -e "${YELLOW}Generating MFA encryption key...${NC}"
    # Fernet keys must be 32 bytes, URL-safe base64-encoded
    # Use openssl to generate 32 random bytes and encode as base64
    openssl rand -base64 32 | tr -d '\n' > "$SECRETS_DIR/mfa_encryption_key.txt"
    chmod 600 "$SECRETS_DIR/mfa_encryption_key.txt"
    echo -e "${GREEN}✓ MFA encryption key generated${NC}"
else
    echo -e "${YELLOW}✓ MFA encryption key already exists (skipped)${NC}"
fi

echo ""
echo -e "${GREEN}=== Secret Generation Complete ===${NC}\n"
echo -e "${YELLOW}IMPORTANT SECURITY NOTES:${NC}"
echo "1. These secrets are stored in $SECRETS_DIR/"
echo "2. This directory is .gitignored (never commit secrets to Git!)"
echo "3. Backup these secrets securely (external drive, password manager)"
echo "4. If secrets are lost, users will be locked out (MFA reset required)"
echo "5. When deploying to Raspberry Pi, copy secrets/ directory securely"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Review and customize .env file (if needed)"
echo "2. Start the Docker stack: docker-compose up -d"
echo "3. Initialize the database: docker-compose exec app alembic upgrade head"
echo ""
