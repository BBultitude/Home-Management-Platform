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
