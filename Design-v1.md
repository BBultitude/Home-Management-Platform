# Design-v1.md

## Document Metadata

- **Version:** v1
- **Status:** Approved
- **Date Created:** 2025-02-01
- **Author:** Claude (AI Architect)
- **Reviewed By:** Bryan Bultitude

---

## Executive Summary

This document defines the architecture for a private, multi-user home management platform designed for household operations, financial planning, project tracking, and ATO-compliant tax record keeping. The system will be self-hosted on a Raspberry Pi, internet-facing via Cloudflare Tunnel, and support up to 10 authenticated users with MFA and RBAC.

The platform is built on a modular architecture allowing new capabilities to be added over time without major redesign. All modules (except Tax Records) operate on household-wide data with role-based access control. The Tax Records module is strictly per-user isolated with 5-year retention for ATO compliance.

**Six Core Modules:**
1. Financial Management (budget planning, utility tracking)
2. Assets & Documents (insurance, important documents)
3. Projects & Tasks (home improvements, contractor quotes, repair prioritization)
4. Household Knowledge Base (structured household information)
5. Tax Records (per-user WFH/work travel tracking)
6. Meal Planner (weekly planning, shopping lists)

**Key Design Principles:**
- Security-first: MFA, RBAC, encrypted secrets, HTTP-only sessions
- Modular: Six core modules with shared platform services
- Compliant: ATO tax record retention, NIST password policy, audit logging
- Resource-efficient: Optimized for Raspberry Pi hardware
- Extensible: Clear patterns for adding new modules and features
- KISS: Keep It Simple Stupid - avoid over-engineering

---

## System Overview

### Purpose

A unified household management platform providing:
- Financial planning and budget distribution
- Utility cost tracking and long-term trend analysis
- Asset and document management (insurance, quotes, policies)
- Project planning with contractor quotes and repair prioritization
- Household knowledge base with structured information
- Per-user tax record keeping (WFH hours, work travel) for ATO compliance
- Weekly meal planning with automatic shopping list generation

### Target Users

- Household members (up to 10 users)
- Primary users: Adults managing household finances and operations
- Secondary users: Household members with read-only or limited edit access

### System Boundaries

**In Scope:**
- User authentication and authorization
- Multi-user access with RBAC
- Document storage and retrieval
- Financial calculations and projections
- Tax record tracking and ATO-compliant exports
- Dashboard with household metrics and alerts
- Mobile-responsive web interface

**Out of Scope (v1):**
- Direct bank account integration
- Third-party API integrations (calendar, email)
- Automated backups (planned for future)
- Real-time collaboration features
- Mobile native applications (PWA deferred)
- SMTP email notifications
- Month-to-month expense tracking
- Personal finance management

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Cloudflare Tunnel                          │
│                    (HTTPS, WAF, Geo-blocking)                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                       Raspberry Pi Host                             │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  Cloudflared Service (runs on host, not in Docker)           │ │
│  │  - Tunnel to Cloudflare                                       │ │
│  │  - Forwards to localhost:8000                                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Docker Compose Stack                       │ │
│  │                    (2 containers only)                        │ │
│  │                                                               │ │
│  │  ┌─────────────────────┐      ┌──────────────────────────┐  │ │
│  │  │   App Container     │      │   Database Container     │  │ │
│  │  │   (FastAPI)         │◄────►│   (PostgreSQL 16)        │  │ │
│  │  │                     │      │                          │  │ │
│  │  │  Platform Services: │      │  - Users & Auth          │  │ │
│  │  │  - Authentication   │      │  - Tax Records (5yr)     │  │ │
│  │  │  - RBAC             │      │  - Financial Data        │  │ │
│  │  │  - File Upload      │      │  - Assets & Documents    │  │ │
│  │  │  - Audit Logging    │      │  - Projects              │  │ │
│  │  │  - Search           │      │  - Knowledge Base        │  │ │
│  │  │  Modules:           │      │  - Knowledge Base        │  │ │
│  │  │  1. Financial Mgmt  │      │  - Audit Logs            │  │ │
│  │  │  2. Assets & Docs   │      └──────────────────────────┘  │ │
│  │  │  3. Projects +      │               ▲                    │ │
│  │  │     Prioritization  │               │                    │ │
│  │  │  4. Knowledge Base  │               │ Named Volume       │ │
│  │  │  5. Tax Records     │               │ (Persistent)       │ │
│  │  │  6. Meal Planner    │               ▼                    │ │
│  │  └─────────────────────┘      ┌──────────────────────────┐  │ │
│  │           │                    │   postgres_data volume   │  │ │
│  │           │                    └──────────────────────────┘  │ │
│  │           │                                                  │ │
│  │           ▼                                                  │ │
│  │  ┌─────────────────────┐                                    │ │
│  │  │  uploads volume     │                                    │ │
│  │  │  (File Storage)     │                                    │ │
│  │  │                     │                                    │ │
│  │  │  /uploads/          │                                    │ │
│  │  │    /insurance/      │                                    │ │
│  │  │    /quotes/         │                                    │ │
│  │  │    /utilities/      │                                    │ │
│  │  │    /knowledge/      │                                    │ │
│  │  │    /user_{id}/tax/  │  (per-user tax attachments)       │ │
│  │  └─────────────────────┘                                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │               Docker Secrets (Not in Containers)              │ │
│  │  - db_password                                                │ │
│  │  - jwt_secret                                                 │ │
│  │  - mfa_encryption_key                                         │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Note: Raspberry Pi 4 (4GB) also runs other services outside      │
│  Docker, so total available RAM for containers may be ~2-3GB      │
└─────────────────────────────────────────────────────────────────────┘

                                ▲
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Desktop Browser         Mobile Browser
              (React SPA)             (React SPA)
```

---

## Components

### 1. Platform Services (Shared)

#### 1.1 Authentication Service
**Purpose:** Manage user login, sessions, MFA

**Responsibilities:**
- User registration (admin-only)
- Password authentication (NIST-compliant)
- TOTP MFA generation and verification
- Session management (HTTP-only JWT cookies)
- Trusted device management
- Login throttling (10 attempts/min, 15-min lockout)

**Key Features:**
- Argon2 password hashing
- PyOTP for TOTP (compatible with Bitwarden/MS Authenticator)
- MFA secrets encrypted at rest (Fernet)
- Trusted devices: 30-day remember-me tokens
- User can view/revoke trusted devices

**Inputs:**
- Username, password, MFA code
- Remember device preference

**Outputs:**
- HTTP-only session cookie
- HTTP-only remember_device cookie (if opted-in)

**Dependencies:**
- Database (users table)
- Docker secrets (jwt_secret, mfa_encryption_key)

#### 1.2 RBAC Service
**Purpose:** Enforce role-based access control

**Responsibilities:**
- Check user permissions before actions
- Support three roles: Admin, Editor, Reader
- Per-user isolation for Tax Records module
- Admin-only access to user management and audit logs

**Roles:**
- **Admin:** Manage users, reset MFA, view all audit logs, cannot modify others' tax records
- **Editor:** Create/edit/delete data in all modules, modify only own tax records
- **Reader:** Read-only access to all modules except user management

**Permission Model:**
```python
Permissions = {
    "Admin": ["user:manage", "audit:read", "tax:read_own", "*:read", "*:write"],
    "Editor": ["tax:write_own", "tax:read_all", "*:read", "*:write"],
    "Reader": ["tax:read_all", "*:read"]
}

# Special rule: Tax records
# - Owners can R/W their own records
# - All users can read others' tax records (not confidential in household)
# - Admins can read ALL tax records (full visibility including audit logs)
# - Admins cannot modify others' tax records (write operations blocked)
# - Admin read access to other users' tax data is audit logged
```

#### 1.3 File Upload Service
**Purpose:** Platform-wide file handling

**Responsibilities:**
- Accept PDF, image, and document uploads
- Validate file types and sizes
- Generate unique filenames
- Store in structured directories
- Virus scanning (future consideration)

**File Structure:**
```
/uploads/
  /insurance/
    {uuid}_policy.pdf
  /quotes/
    {uuid}_quote.pdf
  /utilities/
    {uuid}_bill.pdf
  /knowledge/
    {uuid}_manual.pdf
    {uuid}_photo.jpg
  /user_{user_id}/
    /tax/
      {uuid}_receipt.pdf
```

**Validation:**
- Max file size: 20MB per file
- Max total storage: 200MB per user (soft limit)
- Allowed types: PDF, JPG, PNG, JPEG, DOCX
- Sanitize filenames

#### 1.4 Audit Logging Service
**Purpose:** Track critical actions for compliance and troubleshooting

**Responsibilities:**
- Log authentication events
- Log CRUD operations for Tax Records
- Log data exports
- Log user management actions
- Log file uploads/downloads

**Log Structure:**
```python
AuditLog = {
    "timestamp": DateTime,
    "user_id": UUID,
    "action": Enum(AuditAction),  # LOGIN, TAX_CREATE, TAX_UPDATE, etc.
    "module": String,  # "auth", "tax", "financial", etc.
    "resource_id": UUID,  # ID of affected resource
    "ip_address": String,
    "user_agent": String,
    "details": JSONB,  # Action-specific context
    "success": Boolean
}
```

**Retention:**
- Tax-related logs: 5 years (ATO compliance)
- Authentication logs: 5 years
- Other logs: 2 years

**Access:**
- Admins: Full access to all logs including all users' tax records
- Users: Read-only access to their own tax-related logs only
- Admin actions on other users' tax data are explicitly logged

#### 1.5 Search Service
**Purpose:** Platform-wide search across modules

**Responsibilities:**
- Full-text search using PostgreSQL FTS
- Search metadata (titles, descriptions, names)
- Search structured fields (dates, amounts, categories)
- Exclude file contents (v1)

**Scope:**
- Search all modules user has access to
- Respect RBAC permissions
- Return results grouped by module

**Implementation:**
- PostgreSQL `tsvector` columns
- GIN indexes for performance
- Rank results by relevance

#### 1.6 Notification Service
**Purpose:** In-app notifications for critical events

**Responsibilities:**
- Insurance renewal alerts (30 days, 7 days before)
- Warranty expiry alerts
- Project quote expiry alerts
- System alerts (disk space, backup status)

**Display:**
- Dashboard notification widget
- Badge count on navbar
- Mark as read functionality

**No SMTP/Email in v1**

---

### 2. Module: Financial Management

**Purpose:** Yearly budget planning and utility cost tracking for the entire household

**Scope:** Household-wide (not per-user)
- Single shared budget for all household members
- Supports joint incomes (family) or split expenses (sharehouses)
- Multiple income sources from multiple household members
- All members contribute to/benefit from shared budget

#### 2.1 Budget & Cash Flow Planner

**Responsibilities:**
- Define household members and their income sources
- Define bank accounts (joint or separate)
- Define expense categories
- Assign expenses to accounts
- Calculate required monthly transfers from each person
- Show surplus/shortfall per account
- Year-on-year projection with inflation adjustment

**Budget Period:** Calendar year (January-December) for v1
- Future versions: Configurable (Calendar year or Financial year)
- Rationale: Calendar year aligns with most bills, insurance, utilities

**Data Model:**
```python
# Total household income (not per-person)
IncomeSource = {
    "id": UUID,
    "source_name": String,  # "Salary", "Rental Income", "Investment"
    "amount": Decimal,
    "frequency": Enum(Daily, Weekly, Fortnightly, Monthly, Yearly),
    "created_at": DateTime,
    "updated_at": DateTime
}

BankAccount = {
    "id": UUID,
    "account_name": String,  # "Everyday", "Bills", "Savings"
    "account_type": Enum(Checking, Savings, Offset),
    "current_balance": Decimal,  # Optional tracking
    "created_at": DateTime,
    "updated_at": DateTime
}

ExpenseCategory = {
    "id": UUID,
    "category_name": String,  # "Rent", "Groceries", "Insurance"
    "bank_account_id": UUID,  # Which account pays for this
    "color": String,  # Optional for UI
    "created_at": DateTime,
    "updated_at": DateTime
}

Expense = {
    "id": UUID,
    "expense_name": String,  # "Monthly Rent", "Weekly Groceries"
    "amount": Decimal,
    "frequency": Enum(Daily, Weekly, Fortnightly, Monthly, Yearly),
    "category_id": UUID,  # Links to category → bank account
    "notes": Text,
    "created_at": DateTime,
    "updated_at": DateTime
}
```

**Transfer Calculation:**
```python
# For a given pay cycle (e.g., "fortnightly"):
# 1. Sum all income normalized to pay cycle
# 2. Sum all expenses normalized to pay cycle, grouped by bank account
# 3. Calculate required transfer to each account
# 4. Show surplus/deficit

Example:
  Total Income: $5,000/month
  
  Required Transfers:
  - Bills Account: $2,000 (rent + utilities)
  - Everyday Account: $867 (groceries)
  - Savings Account: $100 (car insurance)
  
  Surplus: $2,033
```

**Simplified from original design:**
- ❌ Removed: HouseholdMember table
- ❌ Removed: Individual income attribution
- ✅ Kept: Total household income + expenses
- ✅ Kept: Category → Bank account mapping
- ✅ Kept: Transfer calculation per pay cycle

**Calculations:**
- Total household income (per pay cycle)
- Total expenses per account (per pay cycle)
- Required transfers from income to bank accounts
- Surplus/shortfall
- Projected costs for next 1-5 years (with inflation adjustment)

**Integrations:**
- Reads insurance renewal amounts from Assets module
- Reads average utility costs from Utility Tracking component

**Outputs:**
- Transfer schedule table
- Account balance projections
- Export to CSV

#### 2.2 Utility Cost Tracking

**Responsibilities:**
- Track electricity, gas, water, internet, mobile
- Store usage, cost, billing periods
- Generate long-term graphs
- Calculate cost per unit
- Provider comparison

**Data Model:**
```python
Utility = {
    "id": UUID,
    "utility_type": Enum(Electricity, Gas, Water, Internet, Mobile),
    "provider": String,
    "billing_period_start": Date,
    "billing_period_end": Date,
    "usage": Decimal,  # kWh, m³, GB, etc.
    "unit": String,
    "cost": Decimal,
    "cost_per_unit": Decimal,  # Calculated
    "attachment_id": UUID,  # Bill PDF
    "notes": String
}
```

**Graphs:**
- Cost over time (line chart)
- Usage over time (line chart)
- Cost per unit trend
- Provider comparison (bar chart)
- Rolling 12-month average

**Outputs:**
- Interactive charts (Chart.js or Recharts)
- Export to CSV

---

### 3. Module: Assets & Documents

**Purpose:** Store and manage important household documents and policies

#### 3.1 Insurance & Policy Vault

**Responsibilities:**
- Store insurance policy metadata
- Track renewal dates
- Generate renewal alerts
- Store policy PDFs

**Data Model:**
```python
InsurancePolicy = {
    "id": UUID,
    "policy_type": Enum(Home, Car, Health, Life, Pet, etc.),
    "provider": String,
    "policy_number": String,
    "coverage_amount": Decimal,
    "premium": Decimal,
    "premium_frequency": Enum(Monthly, Annually),
    "excess": Decimal,
    "renewal_date": Date,
    "coverage_notes": Text,
    "document_id": UUID,  # FK to File
    "vehicle_id": UUID  # Optional FK to Knowledge/Vehicle
}
```

**Features:**
- Renewal alerts (30 days, 7 days)
- Cost summary for budget integration
- Policy document viewer

#### 3.2 Important Documents

**Responsibilities:**
- Store miscellaneous important documents
- Categorize and tag documents
- Search by metadata

**Data Model:**
```python
Document = {
    "id": UUID,
    "document_type": Enum(Contract, Receipt, Warranty, Manual, Other),
    "title": String,
    "description": Text,
    "category": String,
    "tags": Array[String],
    "uploaded_date": Date,
    "expiry_date": Date,  # Optional
    "file_id": UUID
}
```

---

### 4. Module: Projects & Tasks

**Purpose:** Prioritize repairs/upgrades, plan home improvement projects, and track contractor quotes

**Integration Note:** This module combines repair/upgrade prioritization (cost-benefit analysis) with project planning and execution - creating a unified workflow from identification → prioritization → planning → execution.

**Workflow:**
```
1. Add repairs/upgrades to Priority List (cost-benefit scoring)
2. System auto-sorts by priority (net score)
3. Convert high-priority item → Create Project
4. Get contractor quotes
5. Execute project
```

#### 4.1 Repair/Upgrade Prioritization

**Purpose:** Prioritize home repairs and upgrades by cost vs benefit

**Ported from:** https://github.com/BBultitude/Cost-Benefit-Decision

**Responsibilities:**
- Track home repairs, upgrades, and improvements
- Score items by severity and frequency
- Calculate cost score based on dollar amount
- Automatically prioritize by net score
- Convert prioritized items to Projects

**Data Model:**
```python
PriorityItem = {
    "id": UUID,
    "description": String,  # "Fix leaky tap", "Replace fence"
    "cost": Decimal,  # Estimated cost
    "severity": Integer,  # 1-5 (1=cosmetic, 5=serious/safety)
    "frequency": Integer,  # 1-5 (1=rare, 5=constant)
    "benefit_score": Integer,  # Auto-calculated: severity + frequency
    "cost_score": Integer,  # Auto-calculated: log10(cost) + 1
    "net_score": Integer,  # Auto-calculated: benefit - cost_score
    "status": Enum(Pending, ConvertedToProject, Done, Dismissed),
    "project_id": UUID,  # Link if converted to project
    "created_at": DateTime,
    "updated_at": DateTime,
    "completed_at": DateTime
}
```

**Scoring Algorithm:**
```python
# Benefit Score (2-10)
benefit_score = severity + frequency

# Cost Score (logarithmic)
if cost <= 0:
    cost_score = 1
else:
    cost_score = max(1, int(round(math.log10(cost))) + 1)

# Examples:
# $10 → cost_score = 2
# $100 → cost_score = 3
# $1000 → cost_score = 4
# $10000 → cost_score = 5

# Net Score (Priority)
net_score = benefit_score - cost_score
# Higher = better value, higher priority
# Range: -3 to 9
```

**Severity Scale (1-5):**
- 1 — Cosmetic only
- 2 — Minor annoyance
- 3 — Moderate issue
- 4 — Major disruption
- 5 — Serious issue or safety risk

**Frequency Scale (1-5):**
- 1 — Rare
- 2 — Occasional
- 3 — Regular
- 4 — Frequent
- 5 — Constant

**Features:**
- Prioritized list (sorted by net_score DESC)
- Mark as "Done" (completed without project)
- Mark as "Dismissed" (decided not to do)
- "Convert to Project" action (creates Project + links PriorityItem)
- Filter: Show pending / Show all

**UI Integration:**
- Dashboard widget: Top 3-5 priorities
- Quick-add form on dashboard
- Full list in Projects module

**Porting Notes:**
- Original: Python/FastAPI + SQLite + vanilla JavaScript
- Target: Python/FastAPI + PostgreSQL + React
- Scoring algorithm: Keep as-is (already perfect)
- Changes: Integrate with Projects (add "Convert to Project" workflow)

#### 4.2 Project Planning

**Responsibilities:**
- Create and manage projects
- Track project status
- Store decision history
- Link to quotes
- Link from priority items

**Data Model:**
```python
Project = {
    "id": UUID,
    "project_name": String,
    "description": Text,
    "priority_item_id": UUID,  # Optional: link to originating priority item
    "status": Enum(Planned, Approved, InProgress, Completed, Cancelled),
    "start_date": Date,
    "completion_date": Date,
    "budget": Decimal,
    "actual_cost": Decimal,
    "notes": Text,
    "quotes": [Quote],
    "created_at": DateTime,
    "updated_at": DateTime
}
```

**Status Workflow:**
```
Planned → Approved → In Progress → Completed
   ↓                                    
Cancelled
```

#### 4.3 Quote Tracking

**Responsibilities:**
- Upload quote PDFs
- Track contractor details
- Compare multiple quotes
- Track quote expiry

**Data Model:**
```python
Quote = {
    "id": UUID,
    "project_id": UUID,
    "contractor_name": String,
    "contact_phone": String,
    "contact_email": String,
    "quote_amount": Decimal,
    "quote_date": Date,
    "expiry_date": Date,
    "scope_of_work": Text,
    "selected": Boolean,
    "document_id": UUID,
    "notes": Text
}
```

**Features:**
- Quote comparison table
- Expiry alerts
- Link to Vendors in Knowledge Base (read-only)

**Access Control (RBAC):**
- **Admin/Editor:** Create/edit priority items, create/edit projects, add/edit quotes
- **Reader:** View all (read-only)

---

### 5. Module: Household Knowledge Base

**Purpose:** Structured storage of household reference information

**Architecture:**
- Predefined article types with fixed schemas
- Template-based data entry
- Consistent structure for searchability

#### Article Types

**5.1 Measurements**
```python
Measurement = {
    "id": UUID,
    "location": String,  # "Master Bedroom", "Kitchen Window 2"
    "measurement_type": Enum(RoomDimensions, WindowSize, DoorWidth, etc.),
    "value": Decimal,
    "unit": Enum(cm, m, inches, feet),
    "notes": Text,
    "date_measured": Date,
    "photo_id": UUID
}
```

**5.2 Paint & Finishes**
```python
PaintRecord = {
    "id": UUID,
    "room_area": String,
    "surface_type": Enum(Wall, Ceiling, Trim, Door),
    "brand": String,
    "product_line": String,
    "color_name": String,
    "color_code": String,
    "finish": Enum(Matte, Satin, SemiGloss, Gloss),
    "retailer": String,
    "purchase_date": Date,
    "quantity_used": String,
    "coverage_area": String,
    "notes": Text,
    "photo_id": UUID
}
```

**5.3 Network & Tech Info**
```python
TechDevice = {
    "id": UUID,
    "device_type": Enum(Router, Modem, AccessPoint, SmartDevice),
    "brand_model": String,
    "location": String,
    "ip_address": String,
    "mac_address": String,
    "wifi_ssid": String,
    "wifi_password": String,  # Encrypted
    "admin_url": String,
    "admin_username": String,
    "admin_password": String,  # Encrypted
    "purchase_date": Date,
    "warranty_expiry": Date,
    "notes": Text,
    "manual_id": UUID
}
```

**Security:** Passwords encrypted, extra auth check before reveal

**5.4 Storage Locations**
```python
StorageLocation = {
    "id": UUID,
    "storage_area": String,  # "Garage - Top Shelf Left"
    "items_stored": Array[String],
    "category": Enum(Seasonal, Tools, Documents, Holiday, etc.),
    "notes": Text,
    "photo_id": UUID,
    "last_updated": Date
}
```

**5.5 Vehicle Details**
```python
Vehicle = {
    "id": UUID,
    "vehicle_type": Enum(Car, Motorcycle, Bicycle, etc.),
    "make": String,
    "model": String,
    "year": Integer,
    "vin": String,
    "registration_number": String,
    "registration_expiry": Date,
    "insurance_policy_id": UUID,  # Link to Assets module
    "service_history": [ServiceRecord],
    "next_service_due": Date,
    "next_service_km": Integer,
    "notes": Text,
    "photos": Array[UUID],
    "manual_id": UUID
}

ServiceRecord = {
    "date": Date,
    "odometer": Integer,
    "service_type": String,
    "cost": Decimal,
    "provider": String,
    "notes": Text
}
```

**5.6 Emergency Contacts**
```python
EmergencyContact = {
    "id": UUID,
    "name": String,
    "relationship_role": String,  # "Family", "Electrician", "Plumber"
    "primary_phone": String,
    "secondary_phone": String,
    "email": String,
    "address": String,
    "when_to_call": String,  # "Power outage", "Medical emergency"
    "category": Enum(Medical, Utilities, Trades, Family, etc.),
    "notes": Text,
    "pinned": Boolean  # Quick access on dashboard
}
```

**5.7 Appliances & Equipment**
```python
Appliance = {
    "id": UUID,
    "appliance_type": Enum(Fridge, Washer, HVAC, Oven, etc.),
    "brand": String,
    "model_number": String,
    "serial_number": String,
    "location": String,
    "purchase_date": Date,
    "purchase_price": Decimal,
    "retailer": String,
    "warranty_expiry": Date,
    "manual_id": UUID,
    "service_history": [ServiceRecord],
    "energy_rating": String,
    "notes": Text
}
```

**5.8 Vendors & Contractors**
```python
Vendor = {
    "id": UUID,
    "business_name": String,
    "contact_person": String,
    "service_type": Enum(Electrician, Plumber, Landscaper, etc.),
    "phone": String,
    "email": String,
    "website": String,
    "address": String,
    "rating": Integer,  # 1-5 stars
    "last_used_date": Date,
    "services_performed": Array[String],
    "cost_range": String,
    "notes_review": Text,
    "recommended_by": String
}
```

**Knowledge Base Features:**
- Template-based entry (select type → form auto-generates)
- Full-text search across all article types
- Filter by type, tags, date
- Export to CSV per article type
- Bulk import from CSV (future)

**Access Control (RBAC):**
- **Admin:** Full access (create, edit, delete all articles)
- **Editor:** Full access (create, edit, delete all articles)
- **Reader:** Read-only access (cannot create, edit, or delete)
- **Rationale:** Household-wide knowledge base, standard RBAC applies
- **Note:** Unlike Tax module, no per-user isolation (all articles are household-shared)

---

### 6. Module: Tax Records & Compliance

**Purpose:** Per-user tax record tracking for ATO compliance

**Key Characteristics:**
- **Per-user data isolation**
- **5-year retention requirement**
- **Owner: Read/Write, Others: Read-only**
- **Admins cannot modify others' tax records**

#### 6.1 Work-From-Home (WFH) Tracking

**Responsibilities:**
- Track days and hours worked from home
- Calculate FY totals
- Support revised fixed-rate method (67c/hour)
- Export ATO-compliant summary

**Data Model:**
```python
WFHEntry = {
    "id": UUID,
    "user_id": UUID,  # Owner
    "date": Date,
    "hours": Decimal,
    "notes": Text,
    "created_at": DateTime,
    "updated_at": DateTime
}
```

**Calculations:**
- Daily total
- Weekly total
- Monthly total
- FY total (July 1 - June 30)
- Total deduction @ 67c/hour

**Views:**
- Calendar view (read-only, shows days worked)
- List view (with edit/delete)
- Summary view (FY totals)

**Quick-Add:**
- Dashboard widget: "Add WFH Day"
- Pre-fills today's date, user enters hours

**Export:**
```
ATO WFH Summary - FY 2024/2025
User: John Smith
Total Days: 180
Total Hours: 1440
Deduction (@ $0.67/hour): $964.80
```

#### 6.2 Work Travel Calculator

**Responsibilities:**
- Track work-related vehicle travel
- Calculate FY total km
- Export ATO-compliant logbook summary

**Data Model:**
```python
WorkTravelEntry = {
    "id": UUID,
    "user_id": UUID,  # Owner
    "date": Date,
    "purpose": String,  # "Client meeting", "Site visit"
    "start_location": String,
    "end_location": String,
    "distance_km": Decimal,
    "notes": Text,
    "created_at": DateTime,
    "updated_at": DateTime
}
```

**Calculations:**
- Daily total km
- Weekly total km
- Monthly total km
- FY total km
- Deduction (user enters rate, e.g., ATO standard 85c/km)

**Quick-Add:**
- Dashboard widget: "Add Work Travel"
- Pre-fills today's date

**Export:**
```
ATO Work Travel Logbook - FY 2024/2025
User: Jane Doe
Total Trips: 45
Total Distance: 1250 km
Deduction (@ $0.85/km): $1,062.50

Detailed Log:
Date       | Purpose         | Start       | End         | Distance
2024-07-15 | Client meeting  | Home        | CBD Office  | 25 km
...
```

**Tax Module Access Rules:**
```python
# User can R/W their own records
if current_user.id == tax_record.user_id:
    return FULL_ACCESS

# All users can read others' records (household transparency)
return READ_ONLY

# Admins cannot write to others' tax records (compliance)
if current_user.role == "Admin" and current_user.id != tax_record.user_id:
    return READ_ONLY
```

**Audit Logging for Tax:**
- Log all CREATE, UPDATE, DELETE operations
- Include before/after values for updates
- Log export events
- Retain for 5 years

**Data Retention:**
- Soft-delete: Tax records marked deleted but retained for 5 years
- Hard-delete: Automatic purge after 5 years + 1 day
- User account deletion: Anonymize user but retain tax records for 5 years

**Financial Year Archival:**
- **Archival trigger:** December 31 following the end of the financial year
  - Example: FY 2024-2025 (July 1, 2024 - June 30, 2025)
  - Tax due: October 31, 2025
  - Archive date: December 31, 2025
- **Archived FY behavior:**
  - Status changes to `archived` (database flag)
  - All records become **read-only** (no create/edit/delete)
  - Still visible in UI (filter: "Show archived years")
  - Still exportable
  - Still included in audit logs
- **UI indicators:**
  - Archived years marked with "Archived" badge
  - Warning when attempting to edit: "This financial year is archived and read-only"
- **Rationale:** Prevents accidental modification after tax lodgement, maintains data integrity
- **Future:** Manual un-archive option for admin (if ATO audit requires correction)

---

### 6. Module: Meal Planner

**Purpose:** Weekly meal planning with automatic shopping list generation

**Scope:** Household-wide (shared meal planning)
- Single weekly plan for entire household
- All users can view and edit meal plan
- Admin can manage recipe database

**Source:** Ported from https://github.com/BBultitude/Meal-Planner

#### 6.1 Weekly Meal Planner

**Responsibilities:**
- Plan meals for each day of the week
- Select from recipe database
- View planned meals in calendar format
- Print weekly meal plan

**Data Model:**
```python
WeekPlan = {
    "id": UUID,
    "week_starting": Date,  # Monday of the week
    "monday_meal_id": UUID,
    "tuesday_meal_id": UUID,
    "wednesday_meal_id": UUID,
    "thursday_meal_id": UUID,
    "friday_meal_id": UUID,
    "saturday_meal_id": UUID,
    "sunday_meal_id": UUID,
    "created_at": DateTime,
    "updated_at": DateTime
}
```

#### 6.2 Recipe Management

**Responsibilities:**
- Store recipe collection (starts empty - users add their own)
- Add/edit/delete recipes (Admin/Editor only)
- View recipe details (instructions, ingredients)
- Search recipes by name or ingredient

**Data Model:**
```python
Recipe = {
    "id": UUID,
    "name": String,
    "steps": Text,  # HTML-formatted cooking instructions
    "created_at": DateTime,
    "updated_at": DateTime
}

Ingredient = {
    "id": UUID,
    "recipe_id": UUID,
    "name": String,  # "Chicken breast", "Carrot", etc.
    "quantity": String,  # "300 g", "1 medium", "2 cups", etc.
    "sort_order": Integer
}
```

**Note on Porting:**
- Original Meal Planner repo includes 20 default recipes
- Home Management Platform starts with **empty recipe database**
- Users must manually add their own recipes
- Rationale: Personal preference, dietary requirements vary per household

#### 6.3 Shopping List Generation

**Responsibilities:**
- Automatically generate shopping list from weekly meal plan
- Consolidate duplicate ingredients across meals
- Convert Australian measurements (cups → grams)
- Handle pantry staples (salt, pepper, oil) as "As needed"

**Consolidation Logic:**
```python
# Example:
# Monday: "1 medium carrot"
# Wednesday: "1 medium carrot"
# Shopping List: "2 medium carrots"

# Measurement conversions (Australian standard):
# 1 cup = 250g (for most ingredients)
# 1 tablespoon = 15ml
# 1 teaspoon = 5ml
```

**Features:**
- Print-friendly shopping list
- Group by category (optional future enhancement)
- Quantity consolidation
- Mark items as "purchased" (optional future enhancement)

**Access Control (RBAC):**
- **Admin/Editor:** Create/edit weekly plan, add/edit/delete recipes
- **Reader:** View meal plan, view shopping list, view recipes (read-only)

**Porting from Standalone App:**
- **Current stack:** Node.js/Express + JSON file storage + vanilla JavaScript
- **Target stack:** Python/FastAPI + PostgreSQL + React
- **Changes required:**
  - Rewrite backend API in FastAPI
  - Migrate data model to PostgreSQL (recipes, ingredients, week_plans tables)
  - Build React components for meal planner UI
  - Integrate platform authentication (replace PIN system)
  - Remove 20 default recipes (start with empty database)
  - Maintain Australian measurement conversions
- **Source repository:** https://github.com/BBultitude/Meal-Planner

---

### 7. Dashboard

**Purpose:** Unified landing page with high-value household information

**Dashboard Widgets:**

1. **Upcoming Renewals**
   - Insurance renewals (next 60 days)
   - Vehicle registration (next 60 days)
   - Warranty expiries (next 60 days)

2. **Active Projects**
   - Projects in "Approved" or "In Progress" status
   - Quote expiry alerts

3. **Repair/Upgrade Priorities**
   - Top 3-5 highest priority items from Projects module
   - Net score indicator
   - Quick link to full list

4. **Budget Summary**
   - Current month surplus/shortfall
   - Account balance overview

5. **Utility Cost Mini-Graphs**
   - Last 12 months electricity cost (sparkline)
   - Last 12 months gas cost (sparkline)

6. **Tax Management Summary** (Per-User)
   - WFH hours FY-to-date
   - Work travel km FY-to-date
   - Quick-add buttons

7. **Meal Planner Widget**
   - Current week's meal plan (7 days)
   - Quick link to shopping list
   - Quick link to edit plan

8. **Quick Actions**
   - Add WFH Entry
   - Add Work Travel Entry
   - Add Utility Bill
   - Add Priority Item (quick repair/upgrade tracking)
   - Add Project
   - Add Project Quote
   - Upload Insurance Policy
   - View This Week's Meals

9. **Notifications/Alerts**
   - Insurance expiring soon
   - Quote expiring soon
   - Warranty expiring soon
   - System alerts (disk space, errors)

10. **Pinned Emergency Contacts**
    - Top 3-5 most important contacts

**Dashboard Customization (Future):**
- User can reorder widgets
- User can hide/show widgets
- Per-user dashboard preferences

---

## Data Flow

### 1. User Login Flow

```
User → Enter credentials
     → Submit login form
     → Backend validates username/password (Argon2)
     → Check: Is device trusted?
        ├─ YES → Generate session JWT → Set HTTP-only cookie → Redirect to dashboard
        └─ NO → Request MFA code
                → User enters TOTP code
                → Backend decrypts MFA secret, verifies TOTP (PyOTP)
                → Valid?
                   ├─ YES → User opts to remember device?
                   │        ├─ YES → Generate remember token → Set HTTP-only cookie
                   │        └─ NO → (skip)
                   │     → Generate session JWT → Set HTTP-only cookie → Redirect to dashboard
                   └─ NO → Return error, increment failed attempts, throttle if needed
```

### 2. Tax Record Creation Flow

```
User → Navigate to Tax Management → WFH Tracking
     → Click "Add Entry"
     → Fill form (date, hours, notes)
     → Submit
     → Backend validates:
        - User is authenticated (session cookie)
        - RBAC check (user can write to own tax records)
        - Data validation (date format, hours > 0)
     → Insert into database (user_id = current_user.id)
     → Audit log: TAX_WFH_CREATE
     → Return success
     → Frontend updates calendar view
```

### 3. Budget Calculation Flow

```
User → Navigate to Financial Management → Budget Planner
     → System loads:
        - Household members & income sources
        - Bank accounts
        - Expense categories
        - Insurance renewal amounts (from Assets module, read-only)
        - Average utility costs (from Utility Tracking, calculated)
     → Calculate:
        - Total household income (monthly)
        - Total expenses per account
        - Required transfers
        - Surplus/shortfall
     → Display:
        - Transfer schedule table
        - Projected costs (with inflation)
     → User can export to CSV
```

### 4. File Upload Flow

```
User → Navigate to any module (e.g., Insurance)
     → Click "Upload Policy"
     → Select file from device
     → Submit
     → Backend validates:
        - File type (PDF, JPG, PNG, etc.)
        - File size (< 10MB)
        - User has write permission
     → Generate UUID filename
     → Save to /uploads/{category}/{uuid}_{original_name}.pdf
     → Store file metadata in database
     → Audit log: FILE_UPLOAD
     → Return file_id to frontend
     → Frontend displays uploaded file with viewer link
```

### 5. Global Search Flow

```
User → Enter search query in global search bar
     → Submit
     → Backend:
        - Build PostgreSQL FTS query
        - Search across modules user has access to (RBAC filter)
        - Exclude Tax records of other users (per-user isolation)
        - Rank results by relevance
     → Return results grouped by module:
        - Financial: [Budget items, Utility entries]
        - Assets: [Insurance policies, Documents]
        - Projects: [Projects, Quotes]
        - Knowledge: [Articles matching query]
        - Tax: [Own tax records only]
     → Frontend displays results with links to detail pages
```

---

## Data Model

### Core Entities

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- Argon2
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Editor', 'Reader')),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret_encrypted BYTEA,  -- Fernet encrypted TOTP secret
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,  -- Soft delete
    last_login_at TIMESTAMP
);

CREATE TABLE trusted_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,  -- SHA256 hash of remember token
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,  -- 30 days from creation
    last_used_at TIMESTAMP,
    device_name VARCHAR(255),  -- Optional: "Chrome on Windows"
    ip_address INET,  -- For display purposes only
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_trusted_devices_user ON trusted_devices(user_id);
CREATE INDEX idx_trusted_devices_token ON trusted_devices(token_hash);

-- Note: No device fingerprinting (KISS principle)
-- Simple token-based trust: HTTP-only cookie + hash in DB
-- User can manually revoke devices from their account settings

-- Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,  -- LOGIN, TAX_CREATE, FILE_UPLOAD, etc.
    module VARCHAR(50) NOT NULL,
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    success BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_module ON audit_logs(module);

-- Files
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    category VARCHAR(50) NOT NULL  -- 'insurance', 'quote', 'utility', etc.
);

-- Financial Management
CREATE TABLE household_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE income_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES household_members(id) ON DELETE CASCADE,
    source_name VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    frequency VARCHAR(50) NOT NULL CHECK (frequency IN ('Monthly', 'Fortnightly', 'Weekly')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('Savings', 'Checking', 'Offset')),
    current_balance DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expense_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_name VARCHAR(255) NOT NULL,
    assigned_account UUID REFERENCES bank_accounts(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    frequency VARCHAR(50) NOT NULL CHECK (frequency IN ('Monthly', 'Quarterly', 'Annually')),
    inflation_rate DECIMAL(5, 2) DEFAULT 0.03,  -- 3% default
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE utility_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utility_type VARCHAR(50) NOT NULL CHECK (utility_type IN ('Electricity', 'Gas', 'Water', 'Internet', 'Mobile')),
    provider VARCHAR(255) NOT NULL,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    usage DECIMAL(10, 2),
    unit VARCHAR(20),  -- 'kWh', 'm³', 'GB'
    cost DECIMAL(10, 2) NOT NULL,
    cost_per_unit DECIMAL(10, 4),  -- Calculated
    attachment_id UUID REFERENCES files(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_utility_type ON utility_entries(utility_type);
CREATE INDEX idx_utility_period ON utility_entries(billing_period_end);

-- Assets & Documents
CREATE TABLE insurance_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_type VARCHAR(50) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    policy_number VARCHAR(255),
    coverage_amount DECIMAL(12, 2),
    premium DECIMAL(10, 2) NOT NULL,
    premium_frequency VARCHAR(50) NOT NULL CHECK (premium_frequency IN ('Monthly', 'Annually')),
    excess DECIMAL(10, 2),
    renewal_date DATE NOT NULL,
    coverage_notes TEXT,
    document_id UUID REFERENCES files(id) ON DELETE SET NULL,
    vehicle_id UUID,  -- FK to knowledge_articles (vehicles)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_insurance_renewal ON insurance_policies(renewal_date);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags TEXT[],
    uploaded_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_expiry ON documents(expiry_date);

-- Projects & Tasks

-- Priority Items (Repair/Upgrade Prioritization)
CREATE TABLE priority_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description VARCHAR(500) NOT NULL,
    cost DECIMAL(12, 2) NOT NULL,
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    frequency INTEGER NOT NULL CHECK (frequency BETWEEN 1 AND 5),
    benefit_score INTEGER NOT NULL,  -- Auto-calculated: severity + frequency
    cost_score INTEGER NOT NULL,     -- Auto-calculated: log10(cost) + 1
    net_score INTEGER NOT NULL,      -- Auto-calculated: benefit - cost_score
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pending', 'ConvertedToProject', 'Done', 'Dismissed')),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,  -- Link if converted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_priority_items_status ON priority_items(status);
CREATE INDEX idx_priority_items_net_score ON priority_items(net_score DESC);
CREATE INDEX idx_priority_items_project ON priority_items(project_id);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    priority_item_id UUID REFERENCES priority_items(id) ON DELETE SET NULL,  -- Optional: originating priority item
    status VARCHAR(50) NOT NULL CHECK (status IN ('Planned', 'Approved', 'InProgress', 'Completed', 'Cancelled')),
    start_date DATE,
    completion_date DATE,
    budget DECIMAL(12, 2),
    actual_cost DECIMAL(12, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_priority_item ON projects(priority_item_id);

CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    contractor_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    quote_amount DECIMAL(12, 2) NOT NULL,
    quote_date DATE NOT NULL,
    expiry_date DATE,
    scope_of_work TEXT,
    selected BOOLEAN DEFAULT FALSE,
    document_id UUID REFERENCES files(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quotes_project ON quotes(project_id);
CREATE INDEX idx_quotes_expiry ON quotes(expiry_date);

-- Household Knowledge Base
CREATE TABLE knowledge_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_type VARCHAR(50) NOT NULL CHECK (article_type IN (
        'Measurement', 'Paint', 'TechDevice', 'StorageLocation', 
        'Vehicle', 'EmergencyContact', 'Appliance', 'Vendor'
    )),
    title VARCHAR(255) NOT NULL,  -- Auto-generated or user-defined
    data JSONB NOT NULL,  -- Structured data per article type
    tags TEXT[],
    search_vector TSVECTOR,  -- Full-text search
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_type ON knowledge_articles(article_type);
CREATE INDEX idx_knowledge_search ON knowledge_articles USING GIN(search_vector);

CREATE TABLE knowledge_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES knowledge_articles(id) ON DELETE CASCADE,
    file_id UUID REFERENCES files(id) ON DELETE CASCADE
);

-- Tax Records (Per-User Isolation)
CREATE TABLE tax_wfh_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- Owner
    date DATE NOT NULL,
    hours DECIMAL(4, 2) NOT NULL CHECK (hours > 0),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)  -- One entry per user per day
);

CREATE INDEX idx_tax_wfh_user ON tax_wfh_entries(user_id);
CREATE INDEX idx_tax_wfh_date ON tax_wfh_entries(date);

CREATE TABLE tax_travel_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- Owner
    date DATE NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    start_location VARCHAR(255) NOT NULL,
    end_location VARCHAR(255) NOT NULL,
    distance_km DECIMAL(8, 2) NOT NULL CHECK (distance_km > 0),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tax_travel_user ON tax_travel_entries(user_id);
CREATE INDEX idx_tax_travel_date ON tax_travel_entries(date);

-- Notifications (In-App)
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,  -- 'INSURANCE_RENEWAL', 'QUOTE_EXPIRY', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(500),  -- Optional link to relevant page
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(user_id, read);
```

### Relationships

```
users 1:N trusted_devices
users 1:N audit_logs
users 1:N files (uploaded_by)
users 1:N knowledge_articles (created_by)
users 1:N tax_wfh_entries (owner)
users 1:N tax_travel_entries (owner)
users 1:N notifications

household_members 1:N income_sources
bank_accounts 1:N expense_categories

files 1:1 insurance_policies (document_id)
files 1:1 documents (file_id)
files 1:1 quotes (document_id)
files 1:1 utility_entries (attachment_id)
files N:M knowledge_articles (via knowledge_attachments)

projects 1:N quotes

knowledge_articles 1:N knowledge_attachments
```

---

## Security Architecture

### 1. Authentication Security

**Password Policy (NIST SP 800-63B):**
```python
PASSWORD_POLICY = {
    "min_length": 8,
    "max_length": 64,
    "require_complexity": False,  # No forced symbols/numbers
    "check_common_passwords": True,  # Check against breach DB
    "check_compromised": True,  # Have I Been Pwned API (future)
    "allow_paste": True,  # Support password managers
    "show_strength_meter": True,
    "no_expiration": True,  # No forced rotation
    "allow_unicode": True
}
```

**Password Hashing:**
- Algorithm: Argon2id (OWASP recommended)
- Library: `passlib` (Python)
- Parameters: Default recommended settings (time cost, memory cost)

**MFA Implementation:**
- Standard: TOTP (RFC 6238)
- Library: PyOTP
- Secret storage: Encrypted with Fernet (symmetric encryption)
- Encryption key: Stored in Docker secrets (never in code/env)
- QR code: Shown once during setup, never stored
- Recovery codes: Not implemented in v1 (future consideration)

**Session Management:**
```python
# JWT payload
{
    "user_id": "uuid",
    "username": "string",
    "role": "Admin|Editor|Reader",
    "iat": timestamp,  # Issued at
    "exp": timestamp   # Expires in 1 hour
}

# Session cookie
Set-Cookie: session_token=<jwt>; 
  HttpOnly; 
  Secure; 
  SameSite=Strict; 
  Max-Age=3600; 
  Domain=yourdomain.com;
```

**Trusted Device Tokens:**
```python
# Remember-me cookie (simple token-based, no fingerprinting)
Set-Cookie: remember_device=<random_token>; 
  HttpOnly; 
  Secure; 
  SameSite=Strict; 
  Max-Age=2592000;  # 30 days
  Domain=yourdomain.com;

# Token storage (hashed)
# Client stores plain token in HTTP-only cookie
# Server stores SHA256 hash in database
# On subsequent visits: validate token hash matches
# No device fingerprinting (KISS principle)
```

**Login Throttling:**
- Max 10 login attempts per 1 minute (per username + IP)
- After 10 attempts: 15-minute lockout
- Lockout applies to IP + username combination
- Implemented with Redis or in-memory cache (simple counter)

**Failed Login Tracking:**
```python
# In-memory or Redis
login_attempts[f"{username}:{ip}"] = {
    "count": int,
    "first_attempt": timestamp,
    "locked_until": timestamp
}

# Reset counter after successful login
# Reset counter after 15 minutes of no attempts
```

### 2. Authorization (RBAC)

**Permission Matrix:**

| Resource                  | Admin           | Editor          | Reader         |
|---------------------------|-----------------|-----------------|----------------|
| User Management           | R/W             | -               | -              |
| MFA Reset                 | W (others only) | -               | -              |
| Audit Logs (all)          | R               | -               | -              |
| Audit Logs (own tax)      | R               | R               | R              |
| Financial Module          | R/W             | R/W             | R              |
| Assets Module             | R/W             | R/W             | R              |
| Projects Module           | R/W             | R/W             | R              |
| Knowledge Base            | R/W             | R/W             | R              |
| Tax Records (own)         | R/W             | R/W             | R              |
| Tax Records (others)      | R               | R               | R              |

**RBAC Implementation:**
```python
# Decorator pattern
@require_role("Editor", "Admin")
@require_permission("financial:write")
def update_budget():
    pass

# Tax module special rules
@require_tax_ownership  # User can only modify own records
def update_wfh_entry(entry_id):
    entry = db.query(WFHEntry).get(entry_id)
    if entry.user_id != current_user.id:
        raise ForbiddenError("Cannot modify others' tax records")
    # ... update logic

@allow_tax_read  # All users can read others' records
def get_tax_summary(user_id):
    # ... return summary
```

### 3. Data Protection

**Encryption at Rest:**
- Database: Not encrypted (v1), relies on OS-level encryption (future)
- MFA secrets: Encrypted with Fernet before storage
- Network passwords (Knowledge Base): Encrypted with Fernet
- File uploads: Not encrypted (stored on filesystem), relies on OS encryption

**Encryption in Transit:**
- HTTPS enforced (Cloudflare Tunnel provides TLS)
- All API requests over HTTPS
- No HTTP fallback

**Secrets Management:**
```yaml
# docker-compose.yml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
  mfa_encryption_key:
    file: ./secrets/mfa_encryption_key.txt

# Secrets directory (NOT in git)
/secrets/
  db_password.txt
  jwt_secret.txt
  mfa_encryption_key.txt
  .gitignore  # Ignore entire secrets directory
```

**Secret Rotation (Future):**
- JWT secret rotation: Generate new key, issue new tokens, deprecate old key after 24h
- MFA encryption key rotation: Requires re-encrypting all MFA secrets (complex, future consideration)

### 4. Input Validation

**Backend Validation (FastAPI Pydantic):**
```python
from pydantic import BaseModel, validator, Field
from datetime import date, datetime
from decimal import Decimal

class WFHEntryCreate(BaseModel):
    date: date
    hours: Decimal = Field(gt=0, le=24, decimal_places=2)
    notes: str = Field(max_length=500)
    
    @validator('date')
    def date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Date cannot be in the future')
        return v

class FileUpload(BaseModel):
    file: UploadFile
    
    @validator('file')
    def validate_file(cls, v):
        # Check MIME type
        if v.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError('Invalid file type')
        
        # Check file size
        if v.size > MAX_FILE_SIZE:
            raise ValueError('File too large')
        
        # Sanitize filename
        v.filename = secure_filename(v.filename)
        
        return v
```

**SQL Injection Prevention:**
- Use SQLAlchemy ORM (parameterized queries)
- Never construct raw SQL with user input
- Use prepared statements if raw SQL is necessary

**XSS Prevention:**
- Frontend: React auto-escapes by default
- Backend: Sanitize text inputs, validate HTML if rich text is needed (future)
- Content-Security-Policy headers (future)

**CSRF Prevention:**
- SameSite=Strict cookies
- Double-submit cookie pattern (future, if needed)

### 5. File Upload Security

**File Validation:**
```python
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # DOCX
]

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

def validate_upload(file: UploadFile):
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Invalid file type")
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Reset
    if size > MAX_FILE_SIZE:
        raise ValidationError("File too large")
    
    # Sanitize filename
    safe_filename = secure_filename(file.filename)
    
    # Generate UUID filename (prevent overwrites)
    uuid_filename = f"{uuid4()}_{safe_filename}"
    
    return uuid_filename
```

**File Storage:**
- Store outside web root
- Serve via backend endpoint (not direct filesystem access)
- Use `X-Sendfile` or similar for efficient serving (future optimization)

**Virus Scanning (Future):**
- Integrate ClamAV or similar
- Scan on upload before accepting

### 6. Audit Logging

**What to Log:**
- All authentication events (login, logout, MFA, failed attempts)
- All Tax module CRUD operations (with before/after values)
- File uploads/downloads
- User management actions (create, update, delete, MFA reset)
- Data exports
- Permission changes

**Log Structure:**
```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "user_id": "uuid",
    "action": "TAX_WFH_CREATE",
    "module": "tax",
    "resource_id": "wfh_entry_uuid",
    "ip_address": "203.0.113.1",
    "user_agent": "Mozilla/5.0...",
    "details": {
        "date": "2024-01-15",
        "hours": 8.0,
        "notes": "Full day WFH"
    },
    "success": true
}
```

**Log Access:**
- Admins: Full access via admin panel
- Users: Own tax-related logs only (read-only)
- Logs cannot be deleted (only by automated retention policy)

**Retention:**
- Tax-related logs: 5 years (ATO compliance)
- Authentication logs: 5 years (security best practice)
- Other logs: 2 years

**Log Storage:**
- PostgreSQL table (same database)
- Indexed by user_id, timestamp, module
- Future: Export to external log aggregation service (e.g., Loki, CloudWatch)

### 7. Network Security (Cloudflare)

**Cloudflare Tunnel Configuration:**
- No inbound ports open on Pi
- All traffic routed through Cloudflare's network
- Automatic HTTPS/TLS

**Cloudflare WAF (Free Tier):**
- Enable OWASP Core Ruleset
- Block traffic outside Oceania/Australia (geo-blocking)
- Rate limiting (future, if needed)

**Cloudflare Settings:**
```yaml
# cloudflared config.yml
tunnel: <tunnel_id>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: home.yourdomain.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true  # Local traffic, HTTPS at Cloudflare edge
  - service: http_status:404
```

**Geo-Blocking:**
- Cloudflare Firewall Rules (free tier):
  - Block all countries except AU, NZ
  - Allow only if country in ["AU", "NZ"]

**Future Considerations:**
- Cloudflare Access (adds extra auth layer before app)
- Cloudflare Zero Trust (more advanced RBAC)

### 8. Dependency Security

**Python Dependencies:**
- Use `pip-audit` to check for known vulnerabilities
- Pin versions in `requirements.txt`
- Regular updates (quarterly review)

**Docker Base Images:**
- Use official images only
- Pin to specific versions (not `latest`)
- Regular updates (when security patches released)

**Example:**
```dockerfile
# Bad
FROM python:latest

# Good
FROM python:3.12-slim-bookworm

# Better (pin specific hash)
FROM python:3.12-slim-bookworm@sha256:abc123...
```

---

## Non-Functional Architecture

### 1. Performance

**Target Metrics:**
- Page load time: < 2 seconds (dashboard, module pages)
- API response time: < 500ms (p95)
- Search results: < 1 second
- File download: Stream immediately (no buffering)

**Optimization Strategies:**
- Database indexes on frequently queried columns
- PostgreSQL query optimization (EXPLAIN ANALYZE)
- React code splitting (lazy load modules)
- Image optimization (compress uploads)
- Pagination for large datasets (50 items per page default)

**Caching (Future):**
- Redis for session storage (instead of database)
- Cache dashboard widget data (5-minute TTL)
- Cache utility graphs (1-hour TTL)

### 2. Scalability

**Current Scale:**
- 10 concurrent users max
- 1000 tax records per user (5 years × ~200 entries/year)
- 500 total insurance policies, projects, knowledge articles
- 10GB file storage (conservative estimate)

**Raspberry Pi Limits:**
- CPU: Adequate for 10 users (FastAPI async handles concurrency well)
- RAM: 4GB sufficient (PostgreSQL + app container + other Pi services)
- Disk: 32GB minimum, 64GB+ recommended
- Network: Home broadband sufficient (Cloudflare handles HTTPS)

**Scaling Strategy (Future):**
- If users grow beyond 10: Move to VPS (DigitalOcean, Linode)
- If storage grows beyond 64GB: External HDD or NAS
- If traffic spikes: Cloudflare caching, CDN for static assets

### 2.5 Localization & Date/Time Formats

**Target Locale:** Australia (en-AU)

**Date Format (Hardcoded):**
- Display format: `DD/MM/YYYY` (e.g., 15/01/2024)
- ISO storage: `YYYY-MM-DD` (database, API)
- Examples:
  - User sees: "15/01/2024"
  - Database stores: "2024-01-15"
  - API returns: "2024-01-15" (ISO 8601)

**Time Format (Hardcoded):**
- Display format: `12-hour with AM/PM` (e.g., 2:30 PM)
- ISO storage: `24-hour HH:MM:SS` (database)
- Examples:
  - User sees: "2:30 PM"
  - Database stores: "14:30:00"
  - API returns: "14:30:00" (ISO 8601)

**DateTime Format:**
- Display: `DD/MM/YYYY h:mm AM/PM` (e.g., "15/01/2024 2:30 PM")
- API: ISO 8601 with timezone (e.g., "2024-01-15T14:30:00+11:00")

**Financial Year Format:**
- Display: `FY YYYY-YYYY` (e.g., "FY 2024-2025")
- Definition: July 1 to June 30 (Australian FY)
- Examples:
  - FY 2024-2025: July 1, 2024 to June 30, 2025
  - Tax due: October 31, 2025
  - Archive cutoff: December 31, 2025 (becomes read-only)

**Currency Format:**
- Display: `$X,XXX.XX` (e.g., "$1,234.56")
- No currency symbol in database (store as Decimal)
- Assume AUD for all financial data

**Number Format:**
- Thousands separator: `,` (comma)
- Decimal separator: `.` (period)
- Examples: "1,234.56", "10,000"

**No Customization:**
- Date/time formats are hardcoded (not user-configurable)
- Users who want different formats must fork and modify code
- Rationale: Home use, Australian household, simplicity over flexibility

### 3. Reliability

**Availability Target:**
- Uptime: 99% (3.65 days downtime per year acceptable for home use)
- Planned maintenance windows: Monthly (Sunday 2am-4am)

**Failure Modes:**
- Pi power loss: Docker auto-restart on boot
- Container crash: Docker restart policy (`restart: unless-stopped`)
- Database corruption: Rely on PostgreSQL crash recovery, backups (future)
- Disk full: Monitor disk space, alert when > 80% full (future)

**Health Checks:**
```yaml
# docker-compose.yml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 4. Observability

**Logging (v1):**
- Application logs: Stdout (captured by Docker)
- Access logs: Nginx (if reverse proxy used) or FastAPI
- Error logs: Structured JSON logs

**Metrics (Future):**
- Prometheus + Grafana
- Track: Request rate, error rate, response time, database connections

**Tracing (Future):**
- OpenTelemetry for distributed tracing

**Monitoring Dashboard (Future):**
- System metrics: CPU, RAM, disk, network
- Application metrics: Request rate, errors, latency
- Business metrics: Active users, tax entries per week, file uploads

---

## Technology Stack

### Backend

**Framework:** FastAPI 0.109+
- **Why:** Modern, async, auto-documentation (OpenAPI), type hints, great for Pi performance
- **Alternatives considered:** Flask (too synchronous), Django (too heavy), Node.js (heavier RAM usage)

**Language:** Python 3.12
- **Why:** Excellent ecosystem, familiar, great for data processing, PDF handling

**ORM:** SQLAlchemy 2.0
- **Why:** Industry standard, supports PostgreSQL well, migration support (Alembic)

**Authentication:** FastAPI-Users 13.0+
- **Why:** Purpose-built for FastAPI, handles users, sessions, RBAC out of the box

**MFA:** PyOTP 2.9+
- **Why:** Pure TOTP implementation, no dependencies, works with all authenticator apps

**Password Hashing:** Passlib (Argon2)
- **Why:** OWASP recommended, supports Argon2id, easy to use

**Validation:** Pydantic 2.5+
- **Why:** Built into FastAPI, excellent validation, type safety

**Task Queue (Future):** Celery + Redis
- **Why:** For background jobs (backups, notifications, report generation)

### Frontend

**Framework:** React 18+
- **Why:** Mature, huge ecosystem, modular components, great mobile support

**Build Tool:** Vite
- **Why:** Fast dev server, optimized builds, HMR, modern

**UI Library:** Tailwind CSS 3+
- **Why:** Utility-first, fast development, consistent design, mobile-first

**Component Library:** shadcn/ui (Radix UI)
- **Why:** Accessible, customizable, React-based, modern

**State Management:** React Context (built-in) + TanStack Query
- **Why:** Simple for v1, TanStack Query handles API caching/sync

**Routing:** React Router 6+
- **Why:** Standard for React SPAs

**Charts:** Recharts
- **Why:** React-native, declarative, good for utility cost graphs

**Forms:** React Hook Form + Zod
- **Why:** Performance, validation, type safety

**Date Handling:** date-fns
- **Why:** Lightweight, tree-shakeable, modern

**HTTP Client:** Axios
- **Why:** Interceptors (for auth), request cancellation, familiar

### Database

**DBMS:** PostgreSQL 16
- **Why:** Best RBAC support, ACID compliant (tax data integrity), JSON support, full-text search, mature

**Migration Tool:** Alembic
- **Why:** De facto standard for SQLAlchemy, revision history, rollback support

**Connection Pooling:** PgBouncer (future optimization)
- **Why:** If concurrent connections become an issue

### Infrastructure

**Containerization:** Docker + Docker Compose
- **Why:** Consistent environments, easy deployment, portable

**Web Server:** FastAPI (uvicorn) with Nginx reverse proxy (optional)
- **Why:** uvicorn is ASGI server (async), Nginx can handle static files (future optimization)

**Tunnel:** Cloudflare Tunnel (cloudflared)
- **Why:** No port forwarding, HTTPS included, WAF, DDoS protection

**Host OS:** Raspberry Pi OS (Debian-based)
- **Why:** Official, well-supported, lightweight

**Secrets Management:** Docker Secrets
- **Why:** Simple, secure, built into Docker

### Development Tools

**Linting:** Ruff (Python), ESLint (JavaScript)
- **Why:** Fast, opinionated, catches errors

**Formatting:** Black (Python), Prettier (JavaScript)
- **Why:** Consistent style, auto-format

**Type Checking:** mypy (Python), TypeScript (optional for frontend)
- **Why:** Catch type errors before runtime

**Testing:** pytest (backend), Vitest (frontend)
- **Why:** Standard tools, great ecosystem

**API Documentation:** FastAPI auto-generated (OpenAPI/Swagger)
- **Why:** Free, always up-to-date, interactive

---

## API Design

### Authentication Endpoints

```
POST   /api/auth/register          # Admin only, create new user
POST   /api/auth/login             # Username/password login
POST   /api/auth/mfa/verify        # Verify TOTP code
POST   /api/auth/logout            # Invalidate session
GET    /api/auth/me                # Get current user info

POST   /api/auth/mfa/setup         # Generate MFA secret, return QR
POST   /api/auth/mfa/enable        # Verify TOTP and enable MFA
POST   /api/auth/mfa/disable       # Disable MFA (requires password)

GET    /api/auth/trusted-devices   # List user's trusted devices
POST   /api/auth/trusted-devices/{id}/revoke  # Revoke specific device
POST   /api/auth/trusted-devices/revoke-all   # Revoke all devices
```

### Financial Management

```
# Budget
GET    /api/financial/budget                  # Get budget overview
PUT    /api/financial/budget                  # Update budget
POST   /api/financial/budget/calculate       # Calculate transfers

# Household Members
GET    /api/financial/members                # List members
POST   /api/financial/members                # Create member
PUT    /api/financial/members/{id}           # Update member
DELETE /api/financial/members/{id}           # Delete member

# Income Sources
GET    /api/financial/income                 # List income sources
POST   /api/financial/income                 # Create income source
PUT    /api/financial/income/{id}            # Update income
DELETE /api/financial/income/{id}            # Delete income

# Bank Accounts
GET    /api/financial/accounts               # List accounts
POST   /api/financial/accounts               # Create account
PUT    /api/financial/accounts/{id}          # Update account
DELETE /api/financial/accounts/{id}          # Delete account

# Expense Categories
GET    /api/financial/expenses               # List expenses
POST   /api/financial/expenses               # Create expense
PUT    /api/financial/expenses/{id}          # Update expense
DELETE /api/financial/expenses/{id}          # Delete expense

# Utilities
GET    /api/financial/utilities              # List utility entries
POST   /api/financial/utilities              # Create entry
GET    /api/financial/utilities/{id}         # Get entry
PUT    /api/financial/utilities/{id}         # Update entry
DELETE /api/financial/utilities/{id}         # Delete entry
GET    /api/financial/utilities/graphs       # Get graph data (cost, usage trends)
GET    /api/financial/utilities/export       # Export to CSV
```

### Assets & Documents

```
# Insurance
GET    /api/assets/insurance                 # List policies
POST   /api/assets/insurance                 # Create policy
GET    /api/assets/insurance/{id}            # Get policy
PUT    /api/assets/insurance/{id}            # Update policy
DELETE /api/assets/insurance/{id}            # Delete policy
GET    /api/assets/insurance/renewals        # Get upcoming renewals

# Documents
GET    /api/assets/documents                 # List documents
POST   /api/assets/documents                 # Create document
GET    /api/assets/documents/{id}            # Get document
PUT    /api/assets/documents/{id}            # Update document
DELETE /api/assets/documents/{id}            # Delete document
```

### Projects

```
GET    /api/projects                         # List projects
POST   /api/projects                         # Create project
GET    /api/projects/{id}                    # Get project
PUT    /api/projects/{id}                    # Update project
DELETE /api/projects/{id}                    # Delete project

# Quotes
GET    /api/projects/{id}/quotes             # List quotes for project
POST   /api/projects/{id}/quotes             # Create quote
GET    /api/quotes/{id}                      # Get quote
PUT    /api/quotes/{id}                      # Update quote
DELETE /api/quotes/{id}                      # Delete quote
POST   /api/quotes/{id}/select               # Mark quote as selected
GET    /api/quotes/expiring                  # Get expiring quotes
```

### Knowledge Base

```
GET    /api/knowledge                        # List articles (with filters)
POST   /api/knowledge                        # Create article
GET    /api/knowledge/{id}                   # Get article
PUT    /api/knowledge/{id}                   # Update article
DELETE /api/knowledge/{id}                   # Delete article

GET    /api/knowledge/types                  # List article types
GET    /api/knowledge/types/{type}/schema    # Get schema for article type
```

### Tax Records

```
# WFH
GET    /api/tax/wfh                          # List own WFH entries
POST   /api/tax/wfh                          # Create WFH entry
GET    /api/tax/wfh/{id}                     # Get WFH entry
PUT    /api/tax/wfh/{id}                     # Update own WFH entry
DELETE /api/tax/wfh/{id}                     # Delete own WFH entry
GET    /api/tax/wfh/summary                  # Get FY summary
GET    /api/tax/wfh/export                   # Export ATO-compliant summary

GET    /api/tax/wfh/users/{user_id}          # View other user's WFH (read-only)

# Work Travel
GET    /api/tax/travel                       # List own travel entries
POST   /api/tax/travel                       # Create travel entry
GET    /api/tax/travel/{id}                  # Get travel entry
PUT    /api/tax/travel/{id}                  # Update own travel entry
DELETE /api/tax/travel/{id}                  # Delete own travel entry
GET    /api/tax/travel/summary               # Get FY summary
GET    /api/tax/travel/export                # Export ATO-compliant logbook

GET    /api/tax/travel/users/{user_id}       # View other user's travel (read-only)
```

### Dashboard

```
GET    /api/dashboard                        # Get all dashboard widgets
GET    /api/dashboard/renewals               # Get upcoming renewals
GET    /api/dashboard/projects               # Get active projects
GET    /api/dashboard/budget                 # Get budget summary
GET    /api/dashboard/utilities              # Get utility mini-graphs
GET    /api/dashboard/tax                    # Get own tax summary
GET    /api/dashboard/notifications          # Get notifications
```

### Files

```
POST   /api/files/upload                     # Upload file
GET    /api/files/{id}                       # Download file
DELETE /api/files/{id}                       # Delete file (if not referenced)
```

### Search

```
GET    /api/search?q={query}                 # Global search
GET    /api/search?q={query}&module={module} # Module-specific search
```

### Audit Logs

```
GET    /api/audit                            # List audit logs (admin only)
GET    /api/audit/tax                        # Own tax-related logs
GET    /api/audit/export                     # Export logs to CSV (admin only)
```

### Admin

```
GET    /api/admin/users                      # List users
POST   /api/admin/users                      # Create user
GET    /api/admin/users/{id}                 # Get user
PUT    /api/admin/users/{id}                 # Update user
DELETE /api/admin/users/{id}                 # Delete user (soft-delete)
POST   /api/admin/users/{id}/reset-mfa       # Reset user's MFA
```

### Error Handling

All errors return consistent JSON:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Hours must be between 0 and 24",
    "details": {
      "field": "hours",
      "value": 25
    }
  }
}
```

HTTP Status Codes:
- 200: Success
- 201: Created
- 204: No Content (successful delete)
- 400: Bad Request (validation error)
- 401: Unauthorized (not logged in)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 409: Conflict (duplicate entry)
- 429: Too Many Requests (rate limit)
- 500: Internal Server Error

---

## Deployment Architecture

### Docker Compose Stack

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: homemanager_db
    environment:
      POSTGRES_USER: homemanager
      POSTGRES_DB: homemanager
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    secrets:
      - db_password
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homemanager"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: ./backend
    container_name: homemanager_app
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://homemanager@db:5432/homemanager
      JWT_SECRET_FILE: /run/secrets/jwt_secret
      MFA_ENCRYPTION_KEY_FILE: /run/secrets/mfa_encryption_key
    volumes:
      - uploads_data:/app/uploads
    secrets:
      - db_password
      - jwt_secret
      - mfa_encryption_key
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

# Note: Cloudflare Tunnel (cloudflared) runs directly on Pi host (not in Docker)
# This keeps container count to 2 (app + db) and simplifies management

volumes:
  postgres_data:
    driver: local
  uploads_data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
  mfa_encryption_key:
    file: ./secrets/mfa_encryption_key.txt
```

**Cloudflare Tunnel Configuration (On Pi Host, Not in Docker):**
```bash
# Install cloudflared on Pi host
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

# Authenticate and create tunnel
cloudflared tunnel login
cloudflared tunnel create home-manager
cloudflared tunnel route dns home-manager home.yourdomain.com

# Configure tunnel
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

**Cloudflare config.yml:**
```yaml
tunnel: <tunnel-id>
credentials-file: /etc/cloudflared/<tunnel-id>.json

ingress:
  - hostname: home.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

**Run cloudflared as system service:**
```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### Deployment Steps

1. **Prepare Raspberry Pi:**
   - Install Raspberry Pi OS (64-bit recommended)
   - Update OS: `sudo apt update && sudo apt upgrade`
   - Install Docker: `curl -sSL https://get.docker.com | sh`
   - Add user to docker group: `sudo usermod -aG docker $USER`

2. **Clone Repository:**
   ```bash
   git clone https://github.com/BBultitude/Home-Management-Platform.git
   cd Home-Management-Platform
   ```

3. **Generate Secrets:**
   ```bash
   mkdir -p secrets
   openssl rand -base64 32 > secrets/db_password.txt
   openssl rand -base64 32 > secrets/jwt_secret.txt
   openssl rand -base64 32 > secrets/mfa_encryption_key.txt
   chmod 600 secrets/*
   ```

4. **Setup Cloudflare Tunnel (on Pi host, not in Docker):**
   ```bash
   # See Cloudflare Tunnel configuration above
   cloudflared tunnel login
   cloudflared tunnel create home-manager
   # ... follow setup instructions
   ```

4. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with domain, etc.
   ```

5. **Build and Start:**
   ```bash
   docker-compose up -d
   ```

6. **Initialize Database:**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

7. **Create Admin User:**
   ```bash
   docker-compose exec app python scripts/create_admin.py
   ```

8. **Verify:**
   - Check containers: `docker-compose ps`
   - Check logs: `docker-compose logs -f`
   - Access app: `https://home.yourdomain.com`

### Update Procedure

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Stop current containers
docker-compose down

# Run database migrations (if any)
docker-compose run --rm app alembic upgrade head

# Start updated containers
docker-compose up -d

# Verify health
docker-compose ps
docker-compose logs -f app
```

### Rollback Procedure

```bash
# Stop containers
docker-compose down

# Checkout previous version
git checkout <previous_commit>

# Rollback database (if migrations were run)
docker-compose run --rm app alembic downgrade -1

# Start containers
docker-compose up -d
```

---

## Testing Strategy

### Unit Testing (Backend)

**Framework:** pytest

**Coverage Target:** 70% minimum for v1

**Test Structure:**
```
tests/
  unit/
    test_auth.py
    test_tax_calculations.py
    test_budget_calculations.py
    test_rbac.py
    test_file_upload.py
```

**Example Tests:**
- Password hashing and verification
- MFA secret encryption/decryption
- TOTP verification
- RBAC permission checks
- Tax calculation (WFH deduction, travel km)
- Budget transfer calculations
- File upload validation

**Run Tests:**
```bash
pytest tests/unit --cov=app --cov-report=html
```

### Integration Testing (Backend)

**Framework:** pytest + TestClient (FastAPI)

**Test Structure:**
```
tests/
  integration/
    test_auth_endpoints.py
    test_tax_endpoints.py
    test_financial_endpoints.py
```

**Example Tests:**
- Complete login flow (username/password → MFA → session)
- CRUD operations for tax records
- File upload → storage → retrieval
- Search across modules
- Dashboard data aggregation

**Run Tests:**
```bash
pytest tests/integration
```

### Frontend Testing (v2)

**Framework:** Vitest + React Testing Library

**Test Structure:**
```
src/
  __tests__/
    components/
      LoginForm.test.tsx
      BudgetCalculator.test.tsx
    hooks/
      useAuth.test.ts
```

**Example Tests:**
- Form validation
- API error handling
- Authentication state management
- Data fetching and caching

### End-to-End Testing (v2+)

**Framework:** Playwright or Cypress

**Example Scenarios:**
- Complete user journey: Login → Add WFH entry → View summary → Export
- Admin user management workflow
- Project creation with quote upload

### Security Testing

**Tools:**
- `pip-audit` for Python dependency vulnerabilities
- `npm audit` for frontend dependencies (if using npm)
- Manual penetration testing (basic, future)

**Checklist:**
- Verify HTTP-only cookies (dev tools cannot access)
- Verify MFA secret encryption
- Verify RBAC enforcement (try accessing others' tax records)
- Verify login throttling
- Verify file upload restrictions

---

## Risks & Mitigations

### Architectural Risks

**Risk 1: Raspberry Pi Performance Degradation**
- **Impact:** Slow page loads, timeouts, poor UX
- **Likelihood:** Medium (as data grows)
- **Mitigation:** 
  - Optimize queries with indexes
  - Implement pagination
  - Monitor performance metrics
  - Plan for VPS migration if needed

**Risk 2: Data Loss (No Backups in v1)**
- **Impact:** Critical (tax records lost, ATO compliance violated)
- **Likelihood:** Low (but catastrophic)
- **Mitigation:**
  - Prioritize backups in v1.1
  - Manual backups until automated (user responsibility)
  - Educate users on importance

**Risk 3: Security Breach (Weak Password, Stolen Session)**
- **Impact:** High (unauthorized access to tax records, financial data)
- **Likelihood:** Low (with MFA + strong password policy)
- **Mitigation:**
  - Enforce MFA for all users
  - NIST password policy prevents weak passwords
  - HTTP-only cookies prevent XSS token theft
  - Audit logs track all access

**Risk 4: Module Coupling**
- **Impact:** Difficult to modify or extend modules independently
- **Likelihood:** Medium (direct DB access can lead to tight coupling)
- **Mitigation:**
  - Document module dependencies clearly
  - Refactor to internal APIs in v2 if coupling becomes problematic
  - Keep Business Logic in services (not in route handlers)

**Risk 5: Cloudflare Tunnel Downtime**
- **Impact:** App inaccessible externally
- **Likelihood:** Low (Cloudflare is highly reliable)
- **Mitigation:**
  - Local network access as fallback (if on same LAN)
  - Monitor Cloudflare status page
  - Consider backup tunnel configuration (future)

### Delivery Risks

**Risk 1: Scope Creep**
- **Impact:** Delayed v1 launch
- **Likelihood:** High (common in feature-rich projects)
- **Mitigation:**
  - Strict adherence to v1 scope
  - Defer nice-to-haves to v1.1+ (FUTURE_PLANS.md)
  - Incremental delivery (modules one by one)

**Risk 2: Underestimated Complexity**
- **Impact:** Longer development time than planned
- **Likelihood:** Medium
- **Mitigation:**
  - Start with simplest module (Knowledge Base or Tax)
  - Iterate on architecture early
  - Build core platform services first (auth, RBAC, file upload)

**Risk 3: User Adoption (Interface Too Complex)**
- **Impact:** Users don't use the system, effort wasted
- **Likelihood:** Low (household users are motivated)
- **Mitigation:**
  - Simple, intuitive UI
  - Onboarding documentation
  - Quick-add shortcuts for common tasks

### Security Risks

**Risk 1: Brute Force Attacks**
- **Impact:** Account takeover
- **Likelihood:** Low (geo-blocking + MFA)
- **Mitigation:**
  - Login throttling (10 attempts/min, 15-min lockout)
  - Cloudflare WAF blocks most automated attacks
  - MFA prevents password-only attacks

**Risk 2: Session Hijacking**
- **Impact:** Unauthorized access
- **Likelihood:** Very Low (HTTPS + HTTP-only cookies)
- **Mitigation:**
  - HTTPS enforced (Cloudflare)
  - HTTP-only cookies (no JS access)
  - SameSite=Strict (CSRF protection)

**Risk 3: Insider Threat (Household Member)**
- **Impact:** Malicious data modification/deletion
- **Likelihood:** Very Low (trusted household)
- **Mitigation:**
  - Audit logs track all actions
  - RBAC limits damage (Reader role)
  - Soft-delete allows recovery

---

## Assumptions & Open Questions

### Assumptions

1. **Users trust each other** (household members can read each other's tax records)
2. **No sensitive PII in Knowledge Base** (no SSNs, credit cards, etc.)
3. **Users accept in-app notifications** (no email/SMS required in v1)
4. **Users will manually backup data** - backups are manual and at admin's discretion (no automated backup planned)
5. **Internet connection is stable** (no offline mode needed)
6. **Cloudflare Tunnel is reliable** (no fallback tunnel configured)
7. **10 users is a hard maximum** (licensing, architectural decision)
8. **Raspberry Pi is adequate** (4GB+ RAM, 64GB+ storage)
9. **Budget module uses calendar year** (Jan-Dec) for v1, configurable (FY/Calendar) in future versions
10. **Single household budget** (not per-user) - supports joint incomes or shared expenses
11. **Hard-delete for user accounts** (ATO compliance is admin's responsibility, documented in KNOWN_ISSUES.md)

### Open Questions

**All major design questions have been resolved. The following are noted for future consideration:**

1. **Multi-Property Support:**
   - Current design assumes single household
   - Future: Multiple properties (rental, vacation home)?
   - **Status:** Deferred to v2+ (FUTURE_PLANS.md)

2. **Budget Year Configurability:**
   - v1 uses calendar year (Jan-Dec)
   - Future versions should allow user to choose Calendar year or Financial year
   - **Status:** Planned for v1.1+ (FUTURE_PLANS.md)

3. **Soft-Delete vs Hard-Delete:**
   - v1 uses hard-delete (user preference)
   - Future versions should implement automated retention enforcement
   - **Status:** Current approach documented in KNOWN_ISSUES.md, improvement planned for future

**Note:** No blocking open questions remain for v1 implementation.

---

## Appendices

### A. Glossary

- **RBAC:** Role-Based Access Control
- **MFA:** Multi-Factor Authentication
- **TOTP:** Time-based One-Time Password (RFC 6238)
- **ATO:** Australian Taxation Office
- **WFH:** Work From Home
- **FY:** Financial Year (July 1 - June 30 in Australia)
- **NIST:** National Institute of Standards and Technology
- **WAF:** Web Application Firewall
- **PWA:** Progressive Web App
- **FTS:** Full-Text Search
- **RPO:** Recovery Point Objective (acceptable data loss window)
- **RTO:** Recovery Time Objective (acceptable downtime window)

### B. References

- NIST SP 800-63B: Digital Identity Guidelines (Authentication)
- OWASP Top 10: Web Application Security Risks
- FastAPI Documentation: https://fastapi.tiangolo.com
- React Documentation: https://react.dev
- PostgreSQL Documentation: https://www.postgresql.org/docs
- ATO Record Keeping Guidelines: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/record-keeping-for-business

### C. Future Considerations

See FUTURE_PLANS.md for detailed roadmap.

**High-Level Future Features:**
- Automated backups (OneDrive sync)
- Monitoring and alerting (disk space, backups, errors)
- Meal planning module (from existing project)
- Cost-benefit analysis module (from existing project)
- Receipt scanning (OCR for tax receipts)
- Calendar integration (Google Calendar sync)
- Investment tracking
- Mobile native app (iOS/Android)
- API for third-party integrations

---

## Document Review & Approval

**This document requires user approval before implementation begins.**

**Review Checklist:**
- [ ] Architecture aligns with requirements
- [ ] Security measures are adequate
- [ ] Technology choices are acceptable
- [ ] Module structure is clear
- [ ] RBAC model is correct
- [ ] Tax module isolation is sufficient for ATO compliance
- [ ] Open questions are addressed

**Approval:**
- **Reviewed By:** Bryan Bultitude
- **Date:** [2026-02-02]
- **Status:** Approved

**Next Steps After Approval:**
1. Lock Design-v1.md (no further modifications)
2. Create Improvements.md (first sprint tasks)
3. Begin implementation (platform services first)

---

**End of Design-v1.md**
