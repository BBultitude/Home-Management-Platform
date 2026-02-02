# Home Management Platform

A private, self-hosted household management system for financial planning, document storage, project tracking, and ATO-compliant tax record keeping.

**Current Version:** v0.1.0 (Pre-release / Development)  
**Status:** 🏗️ Planning & Architecture Phase  
**Target Platform:** Raspberry Pi 4/5 (self-hosted)

---

## Overview

The Home Management Platform is a modular, multi-user web application designed to centralize household operations:

- **Financial Management:** Budget planning and utility cost tracking
- **Assets & Documents:** Insurance policies, important documents
- **Projects & Tasks:** Repair prioritization, home improvement planning, and contractor quotes
- **Knowledge Base:** Structured household information (measurements, paint colors, network info, etc.)
- **Tax Records:** Per-user work-from-home and work travel tracking (ATO compliant)
- **Meal Planner:** Weekly meal planning with automatic shopping list generation

**Key Features:**
- ✅ Multi-user support (up to 10 users)
- ✅ Role-based access control (Admin, Editor, Reader)
- ✅ MFA authentication (TOTP compatible with Bitwarden, Microsoft Authenticator)
- ✅ Trusted device remember-me (30 days)
- ✅ Per-user tax record isolation (5-year retention)
- ✅ Secure file uploads (insurance policies, quotes, receipts)
- ✅ Mobile-responsive web interface
- ✅ Cloudflare Tunnel for secure public access

---

## Project Status

**Current Phase:** Architecture Definition  
**Design Document:** [Design-v1.md](./Design-v1.md) _(Draft - Pending Approval)_  
**Project Status:** [PROJECT_STATUS.md](./PROJECT_STATUS.md)  
**Known Issues:** [KNOWN_ISSUES.md](./KNOWN_ISSUES.md)  
**UI Issues:** [UI_ISSUES.md](./UI_ISSUES.md)

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for detailed sprint planning and milestones.

---

## Documentation

- **[Design-v1.md](./Design-v1.md)** - Complete system architecture
- **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** - Sprint planning and task tracking
- **[KNOWN_ISSUES.md](./KNOWN_ISSUES.md)** - Known technical issues and limitations
- **[UI_ISSUES.md](./UI_ISSUES.md)** - UI/UX issues and design decisions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Development workflow and guidelines
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and release notes
- **[FUTURE_PLANS.md](./FUTURE_PLANS.md)** - Roadmap and planned features

---

## Quick Start

> **Note:** This project is currently in the planning phase. Installation instructions will be available after Design-v1.md is approved and initial implementation begins.

### Prerequisites (Planned)

- Raspberry Pi 4 (4GB RAM minimum, may run other services alongside)
- Raspberry Pi OS (64-bit)
- Docker and Docker Compose
- Cloudflare account (for Tunnel - runs on host, not in Docker)
- Domain name (for Cloudflare Tunnel)

**Note:** System designed for Raspberry Pi 4 4GB, but also supports Pi 5 with better performance.

### Installation (Planned)

```bash
# Clone repository
git clone https://github.com/BBultitude/Home-Management-Platform.git
cd Home-Management-Platform

# Generate secrets
./scripts/generate_secrets.sh

# Setup Cloudflare Tunnel (on Pi host, not in Docker)
cloudflared tunnel login
cloudflared tunnel create home-manager
# ... follow Cloudflare setup in Design-v1.md

# Configure environment
cp .env.example .env
# Edit .env with your domain and settings

# Start services (2 containers: app + database)
docker-compose up -d

# Initialize database
docker-compose exec app alembic upgrade head

# Create admin user
docker-compose exec app python scripts/create_admin.py

# Access the app
open https://home.yourdomain.com
```

Detailed installation instructions will be provided in the project wiki after v1.0 release.

---

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 16
- **Authentication:** FastAPI-Users + PyOTP (MFA)
- **ORM:** SQLAlchemy 2.0
- **Password Hashing:** Argon2 (via Passlib)

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **UI Library:** Tailwind CSS + shadcn/ui
- **State Management:** React Context + TanStack Query
- **Charts:** Recharts
- **Forms:** React Hook Form + Zod

### Infrastructure
- **Containerization:** Docker + Docker Compose (2 containers: app + database)
- **Tunnel:** Cloudflare Tunnel (cloudflared, runs on Pi host)
- **Secrets Management:** Docker Secrets
- **Host OS:** Raspberry Pi OS (Debian-based)

### Localization
- **Target Locale:** Australia (en-AU)
- **Date Format:** DD/MM/YYYY (hardcoded, not customizable)
- **Time Format:** 12-hour with AM/PM (hardcoded)
- **Financial Year:** FY YYYY-YYYY (e.g., FY 2024-2025, July-June)
- **Currency:** AUD (assumed for all financial data)

---

## Architecture Highlights

### Modular Design

The platform consists of five core modules:

1. **Financial Management**
   - Budget & cash flow planning
   - Utility cost tracking and graphing

2. **Assets & Documents**
   - Insurance policy vault
   - Important document storage

3. **Projects & Tasks**
   - Project planning
   - Contractor quote tracking and comparison

4. **Household Knowledge Base**
   - Structured articles (measurements, paint colors, network info, etc.)
   - Eight predefined article types with template-based entry

5. **Tax Records** _(Per-User Isolated)_
   - Work-from-home hour tracking
   - Work travel logbook
   - ATO-compliant exports

### Security Architecture

- **Authentication:** Username/password + MFA (TOTP)
- **Sessions:** HTTP-only JWT cookies (1-hour expiry)
- **Trusted Devices:** 30-day remember-me tokens
- **Passwords:** NIST-compliant policy (8 char min, no forced complexity, breach check)
- **Login Throttling:** 10 attempts/min, 15-minute lockout
- **RBAC:** Three roles (Admin, Editor, Reader)
- **Audit Logging:** 5-year retention for tax records, 2 years for other logs
- **Encryption:** MFA secrets encrypted at rest (Fernet), HTTP-only cookies prevent XSS

### Data Isolation

- **Household-wide data:** Financial, Assets, Projects, Knowledge (RBAC controls access)
- **Per-user data:** Tax records (user can R/W own, all users can read others)
- **Admin restrictions:** Cannot modify others' tax records (ATO compliance)

---

## Modules Overview

### 1. Financial Management

**Budget & Cash Flow Planner:**
- Define household members and income sources
- Define bank accounts and expense categories
- Calculate required monthly transfers
- Year-on-year cost projection with inflation

**Utility Cost Tracking:**
- Track electricity, gas, water, internet, mobile
- Long-term trend graphs (cost, usage, cost per unit)
- Provider comparison

### 2. Assets & Documents

**Insurance & Policy Vault:**
- Store policy metadata (provider, premium, renewal date, excess)
- Upload policy PDFs
- Renewal alerts (30 days, 7 days)
- Cost integration with budget module

**Important Documents:**
- Store miscellaneous documents
- Categorize and tag
- Expiry tracking

### 3. Projects & Tasks

**Repair/Upgrade Prioritization:**
- Add repairs/upgrades with cost estimate
- Score by severity (1-5) and frequency (1-5)
- Auto-calculate priority (net score = benefit - cost)
- View sorted list (highest priority first)
- Convert priority item → Create project

**Project Planning:**
- Create and track home improvement projects
- Link projects to originating priority items
- Status workflow (Planned → Approved → In Progress → Completed)
- Budget tracking (estimated vs actual)

**Quote Tracking:**
- Upload contractor quotes (PDF)
- Track expiry dates
- Compare multiple quotes
- Select winning quote

**Integration Note:** This module combines the ported Cost-Benefit Decision Tracker with project management, creating a unified workflow: prioritize → plan → quote → execute.

**Source:** Cost-benefit scoring ported from https://github.com/BBultitude/Cost-Benefit-Decision

### 4. Household Knowledge Base

**Eight Structured Article Types:**
1. **Measurements** (room dimensions, window sizes)
2. **Paint & Finishes** (colors, brands, codes)
3. **Network & Tech Info** (Wi-Fi passwords, device IPs) _(passwords encrypted)_
4. **Storage Locations** (where things are kept)
5. **Vehicle Details** (registration, service history)
6. **Emergency Contacts** (tradespeople, family, medical)
7. **Appliances & Equipment** (warranties, manuals)
8. **Vendors & Contractors** (ratings, services, contact info)

**Features:**
- Template-based data entry (select type → form auto-generates)
- Full-text search
- Filter by type, tags, date
- Export to CSV

### 5. Tax Records _(Per-User)_

**Work-From-Home Tracking:**
- Track date and hours worked from home
- FY totals (July 1 - June 30)
- Deduction calculation (@ 67c/hour)
- ATO-compliant export
- Calendar view and quick-add widget

**Work Travel Calculator:**
- Track date, purpose, start/end location, distance
- FY total kilometers
- Deduction calculation (user-defined rate)
- ATO-compliant logbook export
- Quick-add widget

**Access Rules:**
- Users can create/edit/delete their own records
- All users can read others' records (household transparency)
- Admins cannot modify others' records (compliance)
- 5-year retention requirement (ATO)

### 6. Meal Planner _(Household-Wide)_

**Weekly Meal Planning:**
- Plan meals for each day of the week
- Select from your recipe database
- View planned meals in calendar format
- Print weekly meal plan for kitchen

**Smart Shopping List:**
- Automatically generates from weekly plan
- Consolidates duplicate ingredients across meals
- Converts Australian measurements (cups → grams)
- Handles pantry staples as "As needed"
- Print-friendly format

**Recipe Management:**
- Admin/Editor can add, edit, delete recipes
- Each recipe includes ingredients and cooking steps
- Search recipes by name or ingredient
- View detailed cooking instructions
- **Starts empty** - users add their own recipes

**Integration Notes:**
- Ported from standalone app: https://github.com/BBultitude/Meal-Planner
- Original app includes 20 default recipes
- Home Management Platform starts with empty recipe database
- Users build their own recipe collection based on preferences

---

## Dashboard

**Unified landing page with:**
- Repair/upgrade priorities (top 3-5 from Projects module)
- Upcoming renewals (insurance, vehicle registration, warranties)
- Active projects and quote expiry alerts
- Budget summary (surplus/shortfall)
- Utility cost mini-graphs (last 12 months)
- Tax summary (FY-to-date WFH hours, travel km)
- Meal planner widget (current week's meals)
- Quick-action buttons (add priority item, add project, add WFH entry, upload document)
- In-app notifications
- Pinned emergency contacts

---

## Security Features

### Authentication & Authorization
- ✅ MFA required (TOTP via Bitwarden/MS Authenticator)
- ✅ Trusted device support (30-day remember-me)
- ✅ NIST-compliant password policy
- ✅ Login throttling (10 attempts/min → 15-min lockout)
- ✅ HTTP-only session cookies (XSS protection)
- ✅ Role-based access control (Admin, Editor, Reader)

### Data Protection
- ✅ MFA secrets encrypted at rest (Fernet encryption)
- ✅ Network passwords encrypted (Knowledge Base)
- ✅ HTTPS enforced (via Cloudflare Tunnel)
- ✅ Geo-blocking (Oceania/Australia only via Cloudflare WAF)
- ✅ Docker secrets for sensitive environment variables

### Audit & Compliance
- ✅ Comprehensive audit logging (authentication, tax CRUD, exports)
- ✅ 5-year log retention for tax records (ATO compliance)
- ✅ Admin-only access to audit logs (except users can view own tax logs)
- ⚠️ Hard-delete for user accounts (admin must manually enforce 5-year tax retention)

### Network Security
- ✅ No inbound ports open on Raspberry Pi (Cloudflare Tunnel)
- ✅ Cloudflare WAF (OWASP Core Ruleset)
- ✅ Geo-blocking (block traffic outside AU/NZ)

### Backups & Data Safety
- ⚠️ **Backups are MANUAL and at admin's discretion** (by design for home use)
- Admin is responsible for establishing backup routine
- Recommended: Weekly backups to external drive, OneDrive, NAS, etc.
- See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for backup procedures

---

## Known Limitations (v1)

- ⚠️ **Manual backups required** (by design, not automated)
- ❌ No email notifications (in-app only, future consideration)
- ❌ No password recovery (admin reset only, future consideration)
- ❌ No PDF content search (metadata only, future consideration)
- ❌ No multi-property support (future consideration)
- ❌ No offline mode (responsive web only)

See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for complete list.

---

## Roadmap

### v1.0 (Target: TBD)
- ✅ All six core modules functional
  - Financial Management
  - Assets & Documents
  - Projects & Tasks (with integrated repair prioritization)
  - Household Knowledge Base
  - Tax Records (ATO compliant)
  - Meal Planner (ported from standalone app)
- ✅ Dashboard with widgets and quick actions
- ✅ User management and authentication
- ✅ Mobile-responsive UI
- ✅ Basic audit logging

### v1.1 (Future)
- 🔜 Budget year configurability (Calendar year vs Financial year)
- 🔜 System monitoring and alerting (disk space, container health)
- 🔜 Password recovery (admin-assisted or self-service if SMTP added)
- 🔜 Improved soft-delete with automated retention enforcement

### v1.2 (Future)
- 🔜 Email notifications (SMTP integration)
- 🔜 PWA support (offline capability, installable)
- 🔜 Dark mode
- 🔜 Bulk operations

### v2.0 (Future)
- 🔜 Receipt scanning (OCR for tax receipts)
- 🔜 Calendar integration (Google Calendar sync)
- 🔜 PDF content search (full-text)
- 🔜 Multi-property support
- 🔜 Investment tracking
- 🔜 Advanced reporting and analytics

See [FUTURE_PLANS.md](./FUTURE_PLANS.md) for detailed roadmap.

---

## Contributing

This is a private household project, but contributions are welcome from household members.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development workflow and coding guidelines.

---

## Development Workflow

> **Note:** Development has not yet started. This section will be updated once implementation begins.

### Local Development (Planned)

```bash
# Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (React)
cd frontend
npm install
npm run dev

# Database
docker-compose up db -d
alembic upgrade head
```

### Testing (Planned)

```bash
# Backend tests
pytest tests/ --cov=app

# Frontend tests
npm test

# E2E tests (future)
npx playwright test
```

---

## Support & Documentation

**Project Documentation:**
- Architecture: [Design-v1.md](./Design-v1.md)
- Sprint Planning: [PROJECT_STATUS.md](./PROJECT_STATUS.md)
- Known Issues: [KNOWN_ISSUES.md](./KNOWN_ISSUES.md)
- UI Issues: [UI_ISSUES.md](./UI_ISSUES.md)

**External References:**
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- PostgreSQL: https://www.postgresql.org/docs
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
- ATO Record Keeping: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/record-keeping-for-business

---

## License

Private household project. Not licensed for public distribution.

---

## Acknowledgments

- Architecture designed following INSTRUCTIONS.md workflow
- Security best practices based on OWASP and NIST guidelines
- Tax compliance requirements based on ATO guidelines

---

**Last Updated:** 2025-02-01  
**Project Status:** Planning & Architecture Phase  
**Next Milestone:** Design-v1.md Approval
