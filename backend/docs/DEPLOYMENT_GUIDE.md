## Deployment Guide - Home Management Platform

**Version:** 1.0.0
**Target Platform:** Raspberry Pi 4/5 (or any Linux server)
**Last Updated:** 2026-02-13

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Production Deployment](#production-deployment)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

**Minimum (Raspberry Pi 4):**
- 2GB RAM
- 16GB SD card
- Network connection

**Recommended (Raspberry Pi 5):**
- 4GB+ RAM
- 32GB+ SD card/SSD
- Gigabit Ethernet or WiFi 6

### Software Requirements

- **OS:** Debian/Ubuntu based Linux (Raspberry Pi OS recommended)
- **Python:** 3.11 or higher
- **PostgreSQL:** 14 or higher
- **Node.js:** 18+ (for frontend, when implemented)
- **Docker:** 20.10+ and Docker Compose v2 (optional but recommended)

---

## Installation

### Option 1: Docker Compose (Recommended)

#### Step 1: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/your-username/Home-Management-Platform.git
cd Home-Management-Platform
```

#### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**

```bash
# Database
POSTGRES_USER=homemanager
POSTGRES_PASSWORD=<generate-strong-password>
POSTGRES_DB=homemanagement
DATABASE_URL=postgresql://homemanager:<password>@db:5432/homemanagement

# Security
JWT_SECRET_KEY=<generate-random-64-char-string>
MFA_ENCRYPTION_KEY=<generate-fernet-key>

# Application
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=localhost,your-domain.com
CORS_ORIGINS=https://your-domain.com
```

**Generate Secrets:**

```bash
# Generate JWT secret (64 characters)
openssl rand -hex 32

# Generate Fernet key for MFA encryption
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### Step 4: Start Services

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f backend

# Verify services are running
docker compose ps
```

#### Step 5: Initialize Database

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user (interactive)
docker compose exec backend python3 scripts/create_admin.py
```

### Option 2: Manual Installation

#### Step 1: Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git
```

#### Step 2: Setup PostgreSQL

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER homemanager WITH PASSWORD 'your-strong-password';
CREATE DATABASE homemanagement OWNER homemanager;
GRANT ALL PRIVILEGES ON DATABASE homemanagement TO homemanager;
\q
EOF
```

#### Step 3: Clone and Setup Application

```bash
# Clone repository
git clone https://github.com/your-username/Home-Management-Platform.git
cd Home-Management-Platform/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment

```bash
# Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://homemanager:your-password@localhost:5432/homemanagement
JWT_SECRET_KEY=$(openssl rand -hex 32)
MFA_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENVIRONMENT=production
DEBUG=false
EOF
```

#### Step 5: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Create admin user
python3 scripts/create_admin.py
```

#### Step 6: Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/homemanagement.service
```

```ini
[Unit]
Description=Home Management Platform API
After=network.target postgresql.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/Home-Management-Platform/backend
Environment="PATH=/home/your-username/Home-Management-Platform/backend/venv/bin"
ExecStart=/home/your-username/Home-Management-Platform/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable homemanagement
sudo systemctl start homemanagement

# Check status
sudo systemctl status homemanagement
```

---

## Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | - | Secret for JWT tokens (64+ chars) |
| `MFA_ENCRYPTION_KEY` | Yes | - | Fernet key for MFA secrets |
| `ENVIRONMENT` | No | `development` | Environment (development/production) |
| `DEBUG` | No | `false` | Enable debug mode |
| `ALLOWED_HOSTS` | No | `*` | Comma-separated allowed hosts |
| `CORS_ORIGINS` | No | `*` | Comma-separated CORS origins |
| `SESSION_COOKIE_SECURE` | No | `true` | Require HTTPS for cookies |
| `SESSION_COOKIE_SAMESITE` | No | `strict` | Cookie SameSite policy |
| `MAX_FILE_SIZE_MB` | No | `10` | Maximum upload file size |
| `FILE_STORAGE_PATH` | No | `./uploads` | File upload directory |

### Security Configuration

**Production Checklist:**

- [ ] Strong database password (16+ chars, mixed case, numbers, symbols)
- [ ] Unique JWT secret (64+ chars)
- [ ] Unique MFA encryption key (Fernet format)
- [ ] HTTPS enabled (via reverse proxy)
- [ ] Secure cookies enabled (`SESSION_COOKIE_SECURE=true`)
- [ ] Strict CORS policy (specific origins only)
- [ ] Debug mode disabled (`DEBUG=false`)
- [ ] Database accessible only from localhost
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Regular backups configured
- [ ] Log rotation enabled

---

## Database Setup

### Running Migrations

```bash
# Docker
docker compose exec backend alembic upgrade head

# Manual
source venv/bin/activate
alembic upgrade head
```

### Creating Migrations

```bash
# After model changes
alembic revision --autogenerate -m "description"

# Review generated migration
cat alembic/versions/<newest_file>.py

# Apply migration
alembic upgrade head
```

### Database Backups

**Automated Backup Script:**

```bash
#!/bin/bash
# /home/user/scripts/backup-db.sh

BACKUP_DIR="/home/user/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="homemanagement"

# Create backup
docker compose exec -T db pg_dump -U homemanager $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

**Setup Cron Job:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/user/scripts/backup-db.sh
```

### Database Restore

```bash
# Docker
gunzip < backup_20260213.sql.gz | docker compose exec -T db psql -U homemanager homemanagement

# Manual
gunzip < backup_20260213.sql.gz | psql -U homemanager homemanagement
```

---

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (Docker)

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Stop services
docker compose down

# Restart services
docker compose restart backend
```

### Production Mode (Systemd)

```bash
# Start
sudo systemctl start homemanagement

# Stop
sudo systemctl stop homemanagement

# Restart
sudo systemctl restart homemanagement

# View logs
sudo journalctl -u homemanagement -f
```

---

## Production Deployment

### Nginx Reverse Proxy

**Install Nginx:**

```bash
sudo apt-get install nginx
```

**Configure Site:**

```bash
sudo nano /etc/nginx/sites-available/homemanagement
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Proxy settings
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Frontend (when implemented)
    location / {
        root /var/www/homemanagement/frontend;
        try_files $uri $uri/ /index.html;
    }

    # File uploads
    client_max_body_size 10M;
}
```

**Enable Site:**

```bash
sudo ln -s /etc/nginx/sites-available/homemanagement /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Cloudflare Tunnel (Alternative)

For home deployments without static IP:

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create homemanagement

# Configure tunnel
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: <tunnel-id>
credentials-file: /home/user/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: homemanagement.your-domain.com
    service: http://localhost:8000
  - service: http_status:404
```

```bash
# Run tunnel
cloudflared tunnel run homemanagement

# Install as service
sudo cloudflared service install
```

---

## Maintenance

### Log Management

**Docker Logs:**

```bash
# View logs
docker compose logs backend

# Follow logs
docker compose logs -f backend --tail=100

# Clear logs
docker compose down
sudo truncate -s 0 $(docker inspect --format='{{.LogPath}}' <container-id>)
docker compose up -d
```

**Systemd Logs:**

```bash
# View logs
sudo journalctl -u homemanagement

# Follow logs
sudo journalctl -u homemanagement -f

# Clear old logs
sudo journalctl --vacuum-time=30d
```

### Updates

**Docker Deployment:**

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker compose build backend

# Restart services
docker compose up -d backend

# Run migrations
docker compose exec backend alembic upgrade head
```

**Manual Deployment:**

```bash
# Pull latest code
git pull origin main

# Activate virtualenv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart homemanagement
```

### Performance Monitoring

**Check Resource Usage:**

```bash
# CPU and Memory
docker stats

# Or for manual installation
top
htop
```

**Database Performance:**

```bash
# Check slow queries
docker compose exec db psql -U homemanager homemanagement -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Check database size
docker compose exec db psql -U homemanager homemanagement -c "
SELECT pg_size_pretty(pg_database_size('homemanagement'));
"
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Failed**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
grep DATABASE_URL .env

# Test connection
psql postgresql://homemanager:password@localhost:5432/homemanagement
```

**2. Permission Denied Errors**

```bash
# Fix file permissions
chmod -R 755 /home/user/Home-Management-Platform
chown -R user:user /home/user/Home-Management-Platform

# Fix upload directory
mkdir -p uploads
chmod 755 uploads
```

**3. Port Already in Use**

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
kill -9 <PID>
```

**4. Migration Errors**

```bash
# Check current version
alembic current

# Check pending migrations
alembic heads

# Downgrade one revision
alembic downgrade -1

# Re-apply
alembic upgrade head
```

**5. Out of Memory (Raspberry Pi)**

```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Debug Mode

**Enable Debug Logging:**

```bash
# Edit .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart application
docker compose restart backend
```

**View Detailed Logs:**

```bash
docker compose logs backend --tail=200
```

---

## Security Hardening

### Firewall Setup

```bash
# Install UFW
sudo apt-get install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt-get install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
```

```bash
# Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Next Steps

- Review [API Guide](./API_GUIDE.md) for endpoint documentation
- Configure [automated backups](#database-backups)
- Set up monitoring (Prometheus + Grafana)
- Configure log aggregation (ELK stack)
- Plan disaster recovery procedures
- Schedule regular security audits

---

**Need Help?** Check the [GitHub Issues](https://github.com/your-username/Home-Management-Platform/issues) or review the [troubleshooting section](#troubleshooting).
