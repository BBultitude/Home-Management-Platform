# Deployment Guide - Raspberry Pi ARM64

This guide covers deploying the Home Management Platform to a Raspberry Pi using either standard Docker Compose or [DockerMate](https://github.com/BBultitude/DockerMate).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Deployment Methods](#deployment-methods)
3. [Network Architecture](#network-architecture)
4. [Standard Deployment](#standard-deployment)
5. [DockerMate Deployment](#dockermate-deployment)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Platform Differences

- **Development (Your Machine):** AMD64 architecture
- **Production (Raspberry Pi):** ARM64 architecture

The same Docker Compose configuration and Dockerfiles work on both architectures because we use multi-arch base images (`python:3.12-slim` and `postgres:16-alpine`).

### Container Architecture

```
┌─────────────────────────────────────────────────┐
│           Cloudflare Tunnel (Host)              │
│           Connects to: container_ip:8000        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        Docker Network (10.20.30.0/29)           │
│                                                 │
│  ┌──────────────────┐    ┌──────────────────┐  │
│  │  homemanager_db  │    │ homemanager_app  │  │
│  │  PostgreSQL 16   │◄───┤  FastAPI         │  │
│  │  10.20.30.2      │    │  10.20.30.3      │  │
│  │  Port: 5432      │    │  Port: 8000      │  │
│  │  (internal only) │    │  (exposed)       │  │
│  └──────────────────┘    └──────────────────┘  │
│                                                 │
│  Reserved IPs for future:                      │
│  - 10.20.30.4 (Redis cache)                    │
│  - 10.20.30.5 (Frontend container)             │
│  - 10.20.30.6 (Monitoring service)             │
└─────────────────────────────────────────────────┘
```

---

## Deployment Methods

### Method 1: Standard Docker Compose (Recommended for Simple Setups)

**Use when:**
- Single stack deployment
- Don't need advanced network management
- Want simplest setup

**File:** `docker-compose.yml`

### Method 2: DockerMate (Recommended for Multi-Stack Environments)

**Use when:**
- Running multiple Docker stacks on the Pi
- Want unified stack management
- Need network isolation between stacks
- Want resource controls per stack

**File:** `docker-compose.dockermate.yml`

**Benefits:**
- Custom /29 network for isolation
- Stack-level management via DockerMate
- Better resource allocation
- Simplified multi-stack deployments

---

## Network Architecture

### /29 Subnet Design

The platform uses a `/29` subnet providing **6 usable IP addresses**:

```
Network:    10.20.30.0/29
Gateway:    10.20.30.1   (Docker host)
Netmask:    255.255.255.248
Broadcast:  10.20.30.7
Usable IPs: 10.20.30.2 - 10.20.30.6

IP Allocation:
├── 10.20.30.1    Gateway (Docker host)
├── 10.20.30.2    homemanager_db (PostgreSQL)
├── 10.20.30.3    homemanager_app (FastAPI)
├── 10.20.30.4    (Reserved - Future: Redis cache)
├── 10.20.30.5    (Reserved - Future: Frontend container)
├── 10.20.30.6    (Reserved - Future: Monitoring service)
```

### Why /29?

- **Current needs:** 2 containers (db + app)
- **Future growth:** 4 additional services possible
- **Security:** Small blast radius, isolated network
- **Efficiency:** No wasted IP space

### Network Isolation Benefits

✅ **Database port (5432) NOT exposed to host**
✅ **Containers communicate via internal network**
✅ **Only API port (8000) exposed for Cloudflare Tunnel**
✅ **Inter-container traffic isolated from host**

---

## Standard Deployment

### Pre-Deployment Checklist

**On Development Machine:**
1. ✅ Test application locally on AMD64
2. ✅ Run all tests and ensure they pass
3. ✅ Commit all changes to Git
4. ✅ Tag a release version (e.g., `v1.0.0-rc1`)

**On Raspberry Pi:**
1. ✅ Raspberry Pi OS 64-bit installed
2. ✅ Docker and Docker Compose installed
3. ✅ Sufficient storage (32GB+ SD card recommended)
4. ✅ Cloudflare account (for Tunnel)

### 1. Prepare Raspberry Pi

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker --version
docker compose version
```

### 2. Transfer Project Files

**Option A: Git Clone (Recommended)**
```bash
# On Raspberry Pi
cd ~
git clone https://github.com/BBultitude/Home-Management-Platform.git
cd Home-Management-Platform
git checkout v1.0.0-rc1  # Or your target release
```

**Option B: SCP Transfer**
```bash
# From development machine
rsync -avz --exclude 'secrets/*.txt' \
  /home/bryan/VSCode/Home-Management-Platform/ \
  pi@raspberrypi.local:~/Home-Management-Platform/
```

### 3. Transfer Secrets Securely

**IMPORTANT:** Never commit secrets to Git!

```bash
# Option 1: Transfer from dev machine
scp -r ./secrets/*.txt pi@raspberrypi.local:~/Home-Management-Platform/secrets/

# Option 2: Regenerate on Pi (recommended for production)
cd ~/Home-Management-Platform
./scripts/generate_secrets.sh
```

### 4. Configure Environment

```bash
cd ~/Home-Management-Platform

# Create .env file
cp .env.example .env

# Edit for production
nano .env

# Key changes:
# - ENVIRONMENT=production
# - DEBUG=false
# - APP_URL=https://home.yourdomain.com
# - ALLOWED_ORIGINS=https://home.yourdomain.com
```

### 5. Build and Start Services

```bash
# Build images natively on Pi (takes 10-15 minutes)
docker compose build

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 6. Initialize Database

```bash
# Run migrations
docker compose exec app alembic upgrade head

# Create admin user
docker compose exec app python scripts/create_admin.py
```

### 7. Configure Cloudflare Tunnel

```bash
# Install cloudflared (ARM64)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create home-manager

# Configure tunnel
sudo nano ~/.cloudflared/config.yml
```

**Cloudflare Tunnel Config:**
```yaml
tunnel: <TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: home.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

```bash
# Run as system service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 8. Verify Deployment

```bash
# Test local access
curl http://localhost:8000/health

# Test via Cloudflare Tunnel
curl https://home.yourdomain.com/health
```

---

## DockerMate Deployment

### Prerequisites

1. **DockerMate installed:**
   ```bash
   cd ~
   git clone https://github.com/BBultitude/DockerMate.git
   cd DockerMate
   # Follow DockerMate installation instructions
   ```

2. **Pi prepared** (same as standard deployment steps 1-4)

### 1. Create DockerMate Network

```bash
# Option A: Via DockerMate (if supported)
dockermate network create homemanager_net --subnet 10.20.30.0/29

# Option B: Via Docker CLI
docker network create \
  --driver bridge \
  --subnet 10.20.30.0/29 \
  --gateway 10.20.30.1 \
  --opt "com.docker.network.bridge.name"="br-homemanager" \
  homemanager_net

# Verify network
docker network ls | grep homemanager
docker network inspect homemanager_net
```

### 2. Transfer Files and Secrets

Same as standard deployment (steps 2-3 above).

### 3. Deploy Stack via DockerMate

**Option A: Using DockerMate Stack Feature (if supported)**
```bash
cd ~/DockerMate
dockermate stack deploy homemanager \
  --compose-file ~/Home-Management-Platform/docker-compose.dockermate.yml \
  --network homemanager_net
```

**Option B: Manual Deployment**
```bash
cd ~/Home-Management-Platform

# Use DockerMate-specific compose file
docker compose -f docker-compose.dockermate.yml build
docker compose -f docker-compose.dockermate.yml up -d

# Verify
docker compose -f docker-compose.dockermate.yml ps
```

### 4. Initialize Database

```bash
cd ~/Home-Management-Platform

# Run migrations
docker compose -f docker-compose.dockermate.yml exec app alembic upgrade head

# Create admin user
docker compose -f docker-compose.dockermate.yml exec app python scripts/create_admin.py
```

### 5. Configure Cloudflare Tunnel (DockerMate)

```bash
# Configure tunnel to point to container internal IP
sudo nano ~/.cloudflared/config.yml
```

**Cloudflare Config for DockerMate:**
```yaml
tunnel: <TUNNEL-ID>
credentials-file: /home/pi/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: home.yourdomain.com
    service: http://10.20.30.3:8000  # App container internal IP
  - service: http_status:404
```

```bash
# Install and start
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 6. Verify DockerMate Deployment

```bash
# Check containers
docker ps | grep homemanager

# Check network and IPs
docker network inspect homemanager_net

# Test internal connectivity
curl http://10.20.30.3:8000/health

# Test external access
curl https://home.yourdomain.com/health
```

### DockerMate Management Commands

```bash
# If DockerMate has stack management
dockermate stack list
dockermate stack status homemanager
dockermate stack restart homemanager
dockermate stack logs homemanager

# Via Docker Compose (if DockerMate doesn't support stacks yet)
docker compose -f docker-compose.dockermate.yml ps
docker compose -f docker-compose.dockermate.yml logs -f
docker compose -f docker-compose.dockermate.yml restart
```

### Network Traffic Verification

```bash
# View network connections
docker network inspect homemanager_net \
  --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'

# Expected output:
# homemanager_db: 10.20.30.2/29
# homemanager_app: 10.20.30.3/29

# Monitor network traffic
sudo tcpdump -i br-homemanager

# Verify database port NOT exposed on host
netstat -tulpn | grep 5432  # Should be empty
```

---

## Post-Deployment

### Backup Strategy

```bash
# Create backup script
cat > ~/backup_homemanager.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/homemanager
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec homemanager_db pg_dump -U homeuser homedb > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
docker run --rm \
  -v home-management-platform_uploads_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads_$DATE.tar.gz -C /data .

# Backup secrets (encrypted)
tar czf $BACKUP_DIR/secrets_$DATE.tar.gz -C ~/Home-Management-Platform secrets/

echo "Backup complete: $BACKUP_DIR"
EOF

chmod +x ~/backup_homemanager.sh

# Test backup
~/backup_homemanager.sh

# Schedule weekly backups (Sunday 2 AM)
crontab -e
# Add: 0 2 * * 0 /home/pi/backup_homemanager.sh
```

### Monitoring

```bash
# Monitor container resources
docker stats

# Check logs
docker compose logs -f app
docker compose logs -f db

# Check disk usage
df -h
du -sh ~/Home-Management-Platform/
```

### Updates

```bash
# Pull latest code
cd ~/Home-Management-Platform
git pull origin main

# Rebuild images
docker compose build

# Restart containers
docker compose down
docker compose up -d

# Run migrations (if any)
docker compose exec app alembic upgrade head
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs app
docker compose logs db

# Check secrets
ls -la secrets/

# Verify environment
docker compose config
```

### Database Connection Issues

```bash
# Check database container
docker compose exec db psql -U homeuser -d homedb

# Check network connectivity
docker compose exec app ping db

# Reset database (CAUTION: destroys data)
docker compose down -v
docker compose up -d
docker compose exec app alembic upgrade head
```

### Network Issues (DockerMate)

```bash
# Verify network exists
docker network ls | grep homemanager

# Check IP assignments
docker network inspect homemanager_net

# Recreate network if needed
docker compose -f docker-compose.dockermate.yml down
docker network rm homemanager_net
docker network create --subnet 10.20.30.0/29 --gateway 10.20.30.1 homemanager_net
docker compose -f docker-compose.dockermate.yml up -d
```

### Out of Memory

```bash
# Check RAM usage
free -h

# Add memory limits to docker-compose.yml
# services:
#   app:
#     mem_limit: 512m
#   db:
#     mem_limit: 512m

# Restart services
docker compose down
docker compose up -d
```

### Slow Performance

```bash
# Check CPU/RAM
htop

# Optimize PostgreSQL for Pi
# Add to docker-compose.yml under db service:
# command: postgres -c shared_buffers=128MB -c max_connections=20

# Restart
docker compose down
docker compose up -d
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f

# Test tunnel connectivity
cloudflared tunnel info home-manager

# Restart tunnel
sudo systemctl restart cloudflared
```

---

## Rollback

### Restore from Backup

```bash
cd ~/Home-Management-Platform

# Stop containers
docker compose down

# Restore database
cat ~/backups/homemanager/db_YYYYMMDD_HHMMSS.sql | \
  docker compose exec -T db psql -U homeuser homedb

# Restore uploads
docker run --rm \
  -v home-management-platform_uploads_data:/data \
  -v ~/backups/homemanager:/backup \
  alpine tar xzf /backup/uploads_YYYYMMDD_HHMMSS.tar.gz -C /data

# Restart
docker compose up -d
```

---

## Performance Optimization

### Raspberry Pi 4 (4GB RAM) Tuning

**Recommended docker-compose.yml settings:**

```yaml
services:
  app:
    mem_limit: 1g
    cpus: 2.0

  db:
    mem_limit: 512m
    cpus: 1.0
    command: >
      postgres
      -c shared_buffers=128MB
      -c effective_cache_size=384MB
      -c max_connections=20
      -c work_mem=4MB
```

### Network Performance

- **Bridge networking overhead:** Minimal (~10MB RAM)
- **Inter-container latency:** <1ms
- **Throughput:** Full gigabit within network

---

## Security Notes

1. **Change default passwords** - Generate new secrets for production
2. **Enable Cloudflare WAF** - Geo-blocking, rate limiting
3. **Keep secrets backed up** - Store securely offline
4. **Regular updates** - `apt update && apt upgrade` monthly
5. **Monitor logs** - Check for suspicious activity
6. **Network isolation** - Database never exposed to internet

---

## Quick Reference

### Standard Deployment
```bash
# Start
docker compose up -d

# Stop
docker compose down

# Logs
docker compose logs -f

# Rebuild
docker compose build && docker compose up -d
```

### DockerMate Deployment
```bash
# Start
docker compose -f docker-compose.dockermate.yml up -d

# Stop
docker compose -f docker-compose.dockermate.yml down

# Logs
docker compose -f docker-compose.dockermate.yml logs -f

# Or via DockerMate (if supported)
dockermate stack start homemanager
dockermate stack logs homemanager
```

---

**Last Updated:** 2026-02-11
**Tested On:** Raspberry Pi 4 Model B (4GB RAM), Raspberry Pi OS 64-bit
**Network:** 10.20.30.0/29 (6 usable IPs)
**Compatible With:** [DockerMate](https://github.com/BBultitude/DockerMate) v1.x
# Financial Module - Production Deployment Guide

## Issue Summary

The Financial Management tables require proper database initialization to work correctly. The database enum types (income_frequency, account_type, expense_frequency, utility_type) must be created with **lowercase values** to match the Python model definitions.

## What Was Fixed (Feb 14, 2026)

1. **Migration File Updated**: `backend/alembic/versions/8d07792f10cc_add_financial_management_tables.py`
   - Enum values are correctly defined as lowercase strings
   - Added 'rates' to utility_type enum

2. **Permissions Added**: `backend/app/api/dependencies.py`
   - Added `"financial:write"` permission for ADMIN and EDITOR roles
   - Added `"financial:read"` permission for all roles

3. **Models Updated**: `backend/app/models/utility.py`
   - Added `UtilityType.RATES` for council rates/land tax

## Production Deployment Requirements

### For Fresh Database (New Production Environment)

When deploying to a **new** production environment with an empty database:

```bash
# 1. Start the database container
docker compose -f docker-compose.prod.yml up -d db

# 2. Run Alembic migrations to create all tables
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 3. Start remaining services
docker compose -f docker-compose.prod.yml up -d
```

### For Existing Database (Current Development)

The current development database has been **manually fixed** with correct enum types. This fix is stored in the Docker volume:
- Volume: `home-management-platform_db_data`
- Location: `/var/lib/docker/volumes/home-management-platform_db_data`

**This volume must be backed up and persisted** for the data to survive container restarts.

### Database Backup (CRITICAL for Production)

```bash
# Backup current database (including the fixed enums)
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres postgres > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres postgres < backup_YYYYMMDD_HHMMSS.sql
```

## Verifying Database is Correct

Run this test to verify enums are created correctly:

```bash
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import SessionLocal
from app.services.income_source_service import IncomeSourceService
from app.models.income_source import IncomeFrequency
from decimal import Decimal

db = SessionLocal()
try:
    result = IncomeSourceService.create_income_source(
        db=db,
        source_name='Test',
        amount=Decimal('100'),
        frequency=IncomeFrequency.MONTHLY
    )
    print('✓ SUCCESS: Database enums are correct')
    db.delete(result)
    db.commit()
except Exception as e:
    print('✗ ERROR:', str(e))
    print('Run: docker compose -f docker-compose.prod.yml exec backend alembic upgrade head')
finally:
    db.close()
"
```

## Migration File Reference

The migration file defines enums correctly:

```python
# income_frequency
sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='income_frequency')

# account_type
sa.Enum('checking', 'savings', 'offset', name='account_type')

# expense_frequency
sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='expense_frequency')

# utility_type
sa.Enum('electricity', 'gas', 'water', 'internet', 'mobile', 'rates', name='utility_type')
```

## Production Checklist

- [ ] Database volume is configured for persistence (outside container)
- [ ] Regular database backups are scheduled
- [ ] Alembic migrations run on initial deployment
- [ ] Test script confirms enum types are correct
- [ ] User roles have `financial:write` and `financial:read` permissions
- [ ] Database connection uses production credentials
- [ ] SSL/TLS enabled for database connections (if applicable)

## Troubleshooting

### Error: "invalid input value for enum income_frequency: 'MONTHLY'"

**Cause:** Database enum types were created with uppercase values instead of lowercase.

**Solution:** Drop and recreate financial tables (ONLY safe if no production data):

```bash
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS expenses CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS expense_categories CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS bank_accounts CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS income_sources CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS utilities CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS income_frequency CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS account_type CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS expense_frequency CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS utility_type CASCADE'))
    conn.commit()

# Then run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Permission Denied Errors (HTTP 500)

**Cause:** `financial:write` or `financial:read` permissions not in PERMISSION_MATRIX.

**Solution:** Verify `backend/app/api/dependencies.py` contains:

```python
# Financial Management (Active)
"financial:write": [UserRole.ADMIN, UserRole.EDITOR],
"financial:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
```

## Important Notes

1. **Never use SQLAlchemy's `create_all()` in production** - always use Alembic migrations
2. **Database volumes must be persistent** - configure volume mapping in docker-compose.prod.yml
3. **Backup before any schema changes** - especially before running migrations
4. **Test migrations in staging first** - verify enum creation works correctly

## Contact

If issues persist, check:
- Backend logs: `docker compose -f docker-compose.prod.yml logs backend --tail=100`
- Database connectivity: `docker compose -f docker-compose.prod.yml exec backend python -c "from app.db.database import engine; print(engine.url)"`
- Migration status: `docker compose -f docker-compose.prod.yml exec backend alembic current`

---

## Raspberry Pi Production Deployment

Complete guide for deploying to Raspberry Pi with custom network, persistent database, and Cloudflare tunnel integration.

### Prerequisites

**On Raspberry Pi:**
- Raspberry Pi 4 or newer (ARM64)
- Raspberry Pi OS 64-bit (Debian Bookworm or newer)
- Docker Engine installed
- Docker Compose installed
- Git installed
- Sufficient storage for database (recommend 32GB+ SD card or external SSD)

**On Development Machine:**
- Git repository access
- SSH access to Raspberry Pi

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│           Cloudflare Tunnel (Host)                  │
│           Connects to: frontend_ip:80               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│     Docker Network "homemanagement" (Bridge)        │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  postgres_db │  │   backend    │  │ frontend │  │
│  │  PostgreSQL  │◄─┤   FastAPI    │◄─┤  Nginx   │  │
│  │  (internal)  │  │  (internal)  │  │ (exposed)│  │
│  │  Port: 5432  │  │  Port: 8000  │  │ Port: 80 │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│         ▲                                           │
│         │ Persistent Volume                         │
│         │ (Host directory)                          │
└─────────┴───────────────────────────────────────────┘
         /your/data/path/postgres
```

### Step 1: Clone Repository on Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@your-raspberry-pi-ip

# Clone the repository
cd ~
git clone https://github.com/BBultitude/Home-Management-Platform.git
cd Home-Management-Platform
```

### Step 2: Create Production Docker Compose Configuration

Create a new file `docker-compose.pi.yml` for Raspberry Pi deployment:

```bash
nano docker-compose.pi.yml
```

Paste the following configuration (update `/your/data/path` to your desired database location):

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: homemanager_db_pi
    restart: unless-stopped
    environment:
      POSTGRES_DB: homemanager
      POSTGRES_USER: homemanager
      POSTGRES_PASSWORD: ${DB_PASSWORD:-change_this_password_in_production}
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
      POSTGRES_INITDB_ARGS: --auth-host=scram-sha-256
    volumes:
      # IMPORTANT: Update this path to your desired location
      - /your/data/path/postgres:/var/lib/postgresql/data
    networks:
      - homemanagement
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homemanager -d homemanager"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    image: homemanager-backend:latest
    container_name: homemanager_backend_pi
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      # Database
      DATABASE_URL: postgresql://homemanager:${DB_PASSWORD:-change_this_password_in_production}@db:5432/homemanager
      
      # Security
      SECRET_KEY: ${SECRET_KEY:-generate_a_secure_random_key_here}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY:-generate_32_byte_fernet_key_here}
      
      # Environment
      ENVIRONMENT: production
      DEBUG: "false"
      
      # CORS (allow frontend container and cloudflare tunnel)
      CORS_ORIGINS: http://frontend,http://localhost,https://your-domain.com
      
      # File Upload
      MAX_FILE_SIZE_MB: 20
      MAX_STORAGE_MB: 200
    volumes:
      - ./backend/uploads:/app/uploads
    networks:
      - homemanagement
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    image: homemanager-frontend:latest
    container_name: homemanager_frontend_pi
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    environment:
      VITE_API_URL: http://backend:8000/api/v1
    ports:
      # Expose on specific IP for Cloudflare tunnel
      # Replace 192.168.1.100 with your Pi's IP or use 0.0.0.0 for all interfaces
      - "192.168.1.100:80:80"
    networks:
      - homemanagement
      # Optional: Connect to host network for Cloudflare tunnel
      # Uncomment the line below if you need external access
      # - host

networks:
  homemanagement:
    driver: bridge
    name: homemanagement
```

### Step 3: Configure Environment Variables

Create `.env` file with secure credentials:

```bash
nano .env
```

Add the following (generate secure random values):

```bash
# Database Password (use a strong password)
DB_PASSWORD=your_secure_database_password_here

# Backend Secret Key (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_secret_key_here

# Encryption Key for TechDevice passwords (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your_fernet_key_here
```

**Generate secure keys:**

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### Step 4: Create Database Directory

```bash
# Create directory for PostgreSQL data
# Update this path to your preferred location
sudo mkdir -p /your/data/path/postgres
sudo chown -R 999:999 /your/data/path/postgres  # PostgreSQL runs as user 999 in container
sudo chmod 700 /your/data/path/postgres
```

**Recommended locations:**
- External SSD: `/mnt/external/homemanager/postgres`
- SD Card: `/home/pi/homemanager-data/postgres`
- NAS Mount: `/mnt/nas/homemanager/postgres`

### Step 5: Build Container Images

Build all images on the Raspberry Pi (this takes 10-15 minutes):

```bash
# Build backend
docker compose -f docker-compose.pi.yml build backend

# Build frontend
docker compose -f docker-compose.pi.yml build frontend
```

### Step 6: Create Docker Network

```bash
# Create the homemanagement network
docker network create homemanagement
```

### Step 7: Start Services

```bash
# Start all services
docker compose -f docker-compose.pi.yml up -d

# Check status
docker compose -f docker-compose.pi.yml ps

# View logs
docker compose -f docker-compose.pi.yml logs -f
```

### Step 8: Run Database Migrations

```bash
# Run Alembic migrations to set up database schema
docker compose -f docker-compose.pi.yml exec backend alembic upgrade head

# Verify migration status
docker compose -f docker-compose.pi.yml exec backend alembic current
```

### Step 9: Create Admin User

```bash
# Access backend container
docker compose -f docker-compose.pi.yml exec backend bash

# Inside container, run Python to create admin user
python3 << 'PYTHON_EOF'
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.user import UserRole

db = SessionLocal()

# Create admin user
admin = User(
    email="admin@homemanager.local",
    hashed_password=get_password_hash("changeme123"),
    full_name="System Administrator",
    role=UserRole.ADMIN,
    is_active=True
)

db.add(admin)
db.commit()
print(f"Admin user created: {admin.email}")
db.close()
PYTHON_EOF

exit
```

**Default credentials:**
- Email: `admin@homemanager.local`
- Password: `changeme123`

**⚠️ IMPORTANT:** Change the password immediately after first login!

### Step 10: Configure Cloudflare Tunnel

#### Option A: Using Cloudflare Tunnel CLI

```bash
# Install cloudflared on Raspberry Pi
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create homemanager

# Configure tunnel (replace YOUR_TUNNEL_ID)
sudo nano ~/.cloudflared/config.yml
```

Add configuration:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/pi/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: homemanager.yourdomain.com
    service: http://192.168.1.100:80
  - service: http_status:404
```

Start tunnel:

```bash
# Run as service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

#### Option B: Using Cloudflare Dashboard

1. Go to Cloudflare Zero Trust Dashboard
2. Navigate to Networks > Tunnels
3. Create new tunnel named "homemanager"
4. Install connector on Raspberry Pi
5. Configure public hostname:
   - Subdomain: `homemanager`
   - Domain: `yourdomain.com`
   - Service: `http://192.168.1.100:80`

### Step 11: Verify Deployment

```bash
# Check all containers are running
docker compose -f docker-compose.pi.yml ps

# Should show:
# homemanager_db_pi        running (healthy)
# homemanager_backend_pi   running (healthy)
# homemanager_frontend_pi  running

# Test backend health endpoint
curl http://localhost:8000/health

# Test frontend (from Pi)
curl http://192.168.1.100:80

# View logs
docker compose -f docker-compose.pi.yml logs -f backend
docker compose -f docker-compose.pi.yml logs -f frontend
```

### Maintenance Commands

```bash
# View logs
docker compose -f docker-compose.pi.yml logs -f

# Restart specific service
docker compose -f docker-compose.pi.yml restart backend

# Stop all services
docker compose -f docker-compose.pi.yml down

# Update code and rebuild
cd ~/Home-Management-Platform
git pull
docker compose -f docker-compose.pi.yml build
docker compose -f docker-compose.pi.yml up -d

# Run new migrations
docker compose -f docker-compose.pi.yml exec backend alembic upgrade head

# Backup database
docker compose -f docker-compose.pi.yml exec db pg_dump -U homemanager homemanager > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup.sql | docker compose -f docker-compose.pi.yml exec -T db psql -U homemanager homemanager
```

### Troubleshooting

#### Container won't start

```bash
# Check logs
docker compose -f docker-compose.pi.yml logs backend

# Check database connection
docker compose -f docker-compose.pi.yml exec backend env | grep DATABASE_URL
```

#### Database permission issues

```bash
# Fix permissions on data directory
sudo chown -R 999:999 /your/data/path/postgres
sudo chmod 700 /your/data/path/postgres
```

#### Frontend can't reach backend

```bash
# Verify network
docker network inspect homemanagement

# Check backend is accessible from frontend container
docker compose -f docker-compose.pi.yml exec frontend wget -O- http://backend:8000/health
```

#### Cloudflare tunnel not connecting

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f

# Verify frontend is accessible locally
curl http://192.168.1.100:80
```

### Performance Optimization for Raspberry Pi

#### 1. Use External SSD

Mount PostgreSQL data on SSD instead of SD card:

```bash
# Mount SSD
sudo mkdir -p /mnt/ssd
sudo mount /dev/sda1 /mnt/ssd
sudo chown -R 999:999 /mnt/ssd/postgres

# Update docker-compose.pi.yml volume path to /mnt/ssd/postgres
```

#### 2. Limit Docker Log Size

Add to each service in `docker-compose.pi.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### 3. Enable PostgreSQL Shared Memory

Add to db service:

```yaml
shm_size: 256mb
```

#### 4. Configure PostgreSQL for Pi

Create `postgresql.conf` tuning:

```bash
# Inside container
docker compose -f docker-compose.pi.yml exec db bash
nano /var/lib/postgresql/data/postgresql.conf
```

Recommended settings for Pi 4 (4GB RAM):

```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Security Hardening

1. **Change default credentials immediately**
2. **Use strong passwords in .env file**
3. **Enable firewall on Pi:**

```bash
sudo apt install ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # Frontend (if not using tunnel)
sudo ufw enable
```

4. **Keep system updated:**

```bash
sudo apt update && sudo apt upgrade -y
```

5. **Use HTTPS with Cloudflare Tunnel** (automatic with tunnel)

### Backup Strategy

#### Automated Daily Backups

Create backup script:

```bash
sudo nano /usr/local/bin/backup-homemanager.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/your/backup/path"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker compose -f /home/pi/Home-Management-Platform/docker-compose.pi.yml exec -T db \
  pg_dump -U homemanager homemanager | gzip > "${BACKUP_DIR}/db_${DATE}.sql.gz"

# Backup uploads
tar -czf "${BACKUP_DIR}/uploads_${DATE}.tar.gz" \
  /home/pi/Home-Management-Platform/backend/uploads/

# Keep only last 7 days
find ${BACKUP_DIR} -name "*.gz" -mtime +7 -delete

echo "Backup completed: ${DATE}"
```

Make executable and add to cron:

```bash
sudo chmod +x /usr/local/bin/backup-homemanager.sh
sudo crontab -e

# Add line (runs daily at 2 AM):
0 2 * * * /usr/local/bin/backup-homemanager.sh >> /var/log/homemanager-backup.log 2>&1
```

### Monitoring

```bash
# Check resource usage
docker stats

# Check disk usage
df -h
docker system df

# Clean up unused images
docker system prune -a
```

---

## Quick Reference

### Essential Commands

```bash
# Start/Stop
docker compose -f docker-compose.pi.yml up -d
docker compose -f docker-compose.pi.yml down

# View status
docker compose -f docker-compose.pi.yml ps
docker compose -f docker-compose.pi.yml logs -f

# Update application
git pull
docker compose -f docker-compose.pi.yml build
docker compose -f docker-compose.pi.yml up -d
docker compose -f docker-compose.pi.yml exec backend alembic upgrade head

# Backup database
docker compose -f docker-compose.pi.yml exec db pg_dump -U homemanager homemanager > backup.sql

# Access database
docker compose -f docker-compose.pi.yml exec db psql -U homemanager
```

### URLs

- **Local Frontend:** http://192.168.1.100
- **Cloudflare Tunnel:** https://homemanager.yourdomain.com
- **Backend API (internal):** http://backend:8000
- **API Docs:** http://192.168.1.100/api/docs

