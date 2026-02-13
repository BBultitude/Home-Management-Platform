# Improvements.md

## Document Metadata

- **Date Updated:** 2026-02-11
- **Author:** Claude (AI Strategist)
- **Reviewed By:** Bryan Bultitude
- **Active Architecture Version:** Design-v1.md (Approved)

---

## ⚠️ Existing Codebases to Port

Two modules have existing implementations that need to be ported to this platform:

1. **Cost-Benefit Decision Tracker (Sprint 5 - Projects Module)**
   - **Repository:** https://github.com/BBultitude/Cost-Benefit-Decision
   - **Current Stack:** Node.js/Express + JSON file storage
   - **Port to:** Python/FastAPI + PostgreSQL
   - **Key Features to Port:**
     - Cost-benefit scoring algorithm (severity × frequency - cost)
     - Priority calculation logic
     - React UI components (with modifications)

2. **Meal Planner (Sprint 7 - Meal Planner Module)**
   - **Repository:** https://github.com/BBultitude/Meal-Planner
   - **Current Stack:** Node.js/Express + JSON file storage
   - **Port to:** Python/FastAPI + PostgreSQL
   - **Key Features to Port:**
     - Ingredient consolidation algorithm
     - Australian measurement conversions (cups → grams)
     - Shopping list generation with "As needed" for pantry staples
     - React UI components (with modifications)
   - **Note:** Original has 20 default recipes; HMP will start with empty database

**Action Required:** Review these codebases when reaching Sprint 5 and Sprint 7

---

## Summary of Current State

**Project Phase:** Foundation & Planning Complete  
**Design Status:** Design-v1.md approved and locked  
**Repository Status:** Initialized with documentation  
**Next Phase:** Platform services implementation (Sprint 1)

**Current Capabilities:**
- ✅ Architecture defined and approved
- ✅ Documentation complete
- ✅ Git repository initialized
- ⚪ No code implemented yet
- ⚪ No database schema created yet
- ⚪ No containers configured yet

**Immediate Goals:**
- Establish core platform services (authentication, RBAC, file upload)
- Create database foundation
- Implement first functional module (Tax Records - simplest, most critical for ATO compliance)

---

## Improvements List

### SPRINT 0 COMPLETION TASKS

#### IMP-001: Docker Compose Stack Setup

**Category:** Infrastructure  
**Priority:** High

**Description:**
Create initial Docker Compose configuration with app and database containers.

**Motivation:**
- Required before any code can run
- Establishes development environment consistency
- Enables local testing of services

**Impact:**
- Developers can spin up local environment with one command
- Database persistence configured
- Container networking established

**Dependencies:**
- None (foundational)

**Risks:**
- Raspberry Pi resource constraints (4GB RAM)
- Port conflicts with existing Pi services

**Acceptance Criteria:**
- [x] docker-compose.yml created with app + db services
- [x] Backend Dockerfile created
- [ ] Containers start successfully (pending backend structure)
- [ ] Database initializes with empty schema (pending Alembic setup)
- [ ] App container can connect to database (pending backend structure)
- [x] Health checks configured

**Status:** Partially complete - infrastructure ready, pending backend application code

---

#### IMP-002: Secrets Generation and Management

**Category:** Security  
**Priority:** High

**Description:**
Generate and configure Docker secrets for sensitive data.

**Motivation:**
- Security requirement: No secrets in code or environment variables
- Docker secrets provide secure secret management

**Impact:**
- JWT tokens secured
- Database credentials secured
- MFA encryption keys secured

**Dependencies:**
- IMP-001 (Docker Compose stack)

**Risks:**
- Secrets accidentally committed to Git
- Secrets lost if not backed up properly

**Acceptance Criteria:**
- [x] secrets/ directory created with .gitignore entry
- [x] db_password.txt generated (32 bytes random, base64-encoded)
- [x] jwt_secret.txt generated (32 bytes random, base64-encoded)
- [x] mfa_encryption_key.txt generated (32 bytes random, base64-encoded)
- [x] Docker secrets configured in docker-compose.yml
- [x] README instructions for secret generation added (scripts/generate_secrets.sh)

**Status:** Complete ✅ (2026-02-11)

---

#### IMP-003: Backend Project Structure

**Category:** Infrastructure  
**Priority:** High

**Description:**
Create FastAPI project structure with folders for models, schemas, routers, services.

**Motivation:**
- Establishes code organization standards
- Enables parallel development across modules
- Follows Design-v1.md architecture

**Impact:**
- Clear separation of concerns
- Easier to navigate codebase
- Consistent patterns across modules

**Dependencies:**
- IMP-001 (Docker Compose)
- IMP-002 (Secrets)

**Risks:**
- None (structural only)

**Acceptance Criteria:**
- [x] backend/ directory structure created per CONTRIBUTING.md
- [x] main.py with FastAPI app initialization
- [x] dependencies.py for dependency injection (get_db)
- [x] requirements.txt with core dependencies (FastAPI, SQLAlchemy, etc.)
- [x] alembic/ directory for migrations
- [x] tests/ directory structure
- [x] .env.example created

**Status:** Complete ✅ (2026-02-11)
**Notes:**
- Containers running successfully
- Health check endpoint operational
- Database connection configured
- Ready for Sprint 1 (model creation)

---

#### IMP-004: Frontend Project Structure

**Category:** Infrastructure  
**Priority:** High

**Description:**
Initialize React + Vite project with Tailwind CSS and shadcn/ui.

**Motivation:**
- Establishes frontend foundation
- Configures build tooling
- Sets up component library

**Impact:**
- Frontend development can begin
- Design system configured
- Mobile-responsive defaults established

**Dependencies:**
- None (parallel with backend)

**Risks:**
- shadcn/ui component configuration complexity

**Acceptance Criteria:**
- [ ] frontend/ directory created with Vite + React
- [ ] Tailwind CSS configured
- [ ] shadcn/ui installed and configured
- [ ] src/ directory structure created per CONTRIBUTING.md
- [ ] package.json with dependencies
- [ ] .env.example created
- [ ] Basic routing configured (React Router)

---

### SPRINT 1: CORE PLATFORM SERVICES

#### IMP-005: Database Schema - Users & Authentication

**Category:** Feature  
**Priority:** High

**Description:**
Create database tables for users, trusted_devices, and audit_logs.

**Motivation:**
- Foundation for all other modules
- Required before any authentication can work
- Establishes audit trail infrastructure

**Impact:**
- Enables user registration and login
- Supports MFA and trusted devices
- Audit logging functional

**Dependencies:**
- IMP-001 (Docker Compose)
- IMP-003 (Backend structure)

**Risks:**
- Schema changes after initial migration (use Alembic properly)

**Acceptance Criteria:**
- [x] Alembic migration created for users table
- [x] Alembic migration created for trusted_devices table
- [x] Alembic migration created for audit_logs table
- [x] Alembic migration created for files table
- [x] Indexes created per Design-v1.md data model
- [x] Migration runs successfully
- [x] Database inspection shows correct schema

**Status:** Complete ✅ (2026-02-11)
**Migration:** `c550c5dbe794_initial_migration_users_trusted_devices_.py`
**Tables Created:** users, trusted_devices, audit_logs, files, alembic_version

---

#### IMP-006: User Authentication - Registration & Login

**Category:** Feature  
**Priority:** High

**Description:**
Implement user registration (admin-only) and password-based login.

**Motivation:**
- Core security requirement
- Blocks all other features until complete
- NIST-compliant password policy

**Impact:**
- Users can register (via admin)
- Users can log in with username/password
- Sessions managed via HTTP-only cookies
- Password hashing with Argon2

**Dependencies:**
- IMP-005 (Database schema)
- IMP-002 (JWT secret)

**Risks:**
- Session management bugs
- Password policy implementation errors

**Acceptance Criteria:**
- [x] POST /api/auth/register endpoint (admin-only)
- [x] POST /api/auth/login endpoint
- [x] POST /api/auth/logout endpoint
- [x] GET /api/auth/me endpoint (current user info)
- [x] POST /api/auth/change-password endpoint
- [x] Argon2 password hashing implemented
- [x] Enhanced password policy (12 char min, composition + pattern detection)
- [x] Pattern detection adapted from DockerMate (weak words, sequential, repeated chars)
- [x] HTTP-only JWT cookies set on login
- [x] Session expiry configured (1 hour)
- [x] Unit tests for auth service (16 tests, 100% coverage)
- [x] Integration tests for auth endpoints (13 tests, 81% overall coverage)
- [x] Password validation tests (27 tests, all passing)

**Note**: Password policy upgraded from NIST minimum (8 chars) to enhanced security (12 chars + pattern detection) based on DockerMate's battle-tested validation. See `docs/PASSWORD_SECURITY.md` for details.

---

#### IMP-007: Multi-Factor Authentication (MFA)

**Category:** Feature  
**Priority:** High

**Description:**
Implement TOTP-based MFA with setup, verification, and trusted devices.

**Motivation:**
- Security requirement per Design-v1.md
- ATO compliance recommendation
- Protects sensitive tax data

**Impact:**
- Users can enable MFA
- TOTP codes verified via PyOTP
- MFA secrets encrypted at rest (Fernet)
- Trusted devices remember for 30 days

**Dependencies:**
- IMP-006 (Authentication)
- IMP-002 (MFA encryption key)

**Risks:**
- QR code generation bugs
- Fernet encryption key loss (secrets must be backed up)

**Acceptance Criteria:**
- [ ] POST /api/auth/mfa/setup endpoint (generate secret, return QR)
- [ ] POST /api/auth/mfa/enable endpoint (verify TOTP, enable MFA)
- [ ] POST /api/auth/mfa/disable endpoint (verify password, disable MFA)
- [ ] POST /api/auth/mfa/verify endpoint (verify TOTP during login)
- [ ] GET /api/auth/trusted-devices endpoint (list devices)
- [ ] POST /api/auth/trusted-devices/{id}/revoke endpoint
- [ ] POST /api/auth/trusted-devices/revoke-all endpoint
- [ ] MFA secrets encrypted with Fernet
- [ ] QR code generation working (test with Bitwarden/MS Authenticator)
- [ ] Trusted device token generation (30-day expiry)
- [ ] Unit tests for MFA logic
- [ ] Integration tests for MFA flow

---

#### IMP-008: Role-Based Access Control (RBAC)

**Category:** Feature  
**Priority:** High

**Description:**
Implement RBAC decorators and permission checks for Admin/Editor/Reader roles.

**Motivation:**
- Security requirement per Design-v1.md
- Controls access to sensitive operations
- Enforces per-user isolation for tax records

**Impact:**
- API endpoints protected by role checks
- Tax records isolated per user
- Admin can manage users, view all logs

**Dependencies:**
- IMP-006 (Authentication)

**Risks:**
- Permission bypass bugs (critical security issue)

**Acceptance Criteria:**
- [ ] RBAC decorator created: @require_role("Admin", "Editor")
- [ ] RBAC decorator created: @require_permission("module:action")
- [ ] Tax-specific decorators: @require_tax_ownership, @allow_tax_read
- [ ] Permission matrix implemented per Design-v1.md
- [ ] Middleware checks user role on protected routes
- [ ] 403 Forbidden returned when permission denied
- [ ] Unit tests for RBAC logic
- [ ] Integration tests for permission enforcement

---

#### IMP-009: Audit Logging Service

**Category:** Feature  
**Priority:** High

**Description:**
Implement audit logging for authentication, tax CRUD, and admin actions.

**Motivation:**
- ATO compliance requirement (5-year retention)
- Security best practice
- Troubleshooting support

**Impact:**
- All critical actions logged
- Admin can view audit trail
- Users can view own tax-related logs

**Dependencies:**
- IMP-005 (Database schema - audit_logs table)

**Risks:**
- Log volume growth (need retention policy)

**Acceptance Criteria:**
- [ ] Audit logging utility created
- [ ] Log structure matches Design-v1.md
- [ ] Authentication events logged (LOGIN, LOGOUT, MFA_SETUP, etc.)
- [ ] Tax CRUD events logged (TAX_WFH_CREATE, TAX_TRAVEL_UPDATE, etc.)
- [ ] File uploads logged (FILE_UPLOAD)
- [ ] Admin actions logged (USER_CREATE, MFA_RESET, etc.)
- [ ] GET /api/audit endpoint (admin-only, all logs)
- [ ] GET /api/audit/tax endpoint (user's own tax logs)
- [ ] Retention policy enforced (5 years for tax, 2 years for others)
- [ ] Integration tests for logging

---

#### IMP-010: File Upload Service

**Category:** Feature  
**Priority:** High

**Description:**
Implement file upload with validation, storage, and retrieval.

**Motivation:**
- Required for insurance PDFs, quotes, receipts, knowledge base photos
- Security requirement (validate file types and sizes)

**Impact:**
- Users can upload PDFs, images, documents
- Files stored in structured directories
- File metadata tracked in database

**Dependencies:**
- IMP-005 (Database schema - files table)
- IMP-008 (RBAC for file access)

**Risks:**
- Disk space exhaustion (20MB per file, 200MB per user limit)
- File type validation bypass

**Acceptance Criteria:**
- [x] POST /api/files/upload endpoint
- [x] GET /api/files/{id} endpoint (metadata)
- [x] GET /api/files/{id}/download endpoint (file download)
- [x] DELETE /api/files/{id} endpoint (permanent delete)
- [x] File validation: Max 20MB, allowed MIME types (PDF, JPG, PNG, GIF, WEBP, DOCX, XLSX, TXT, CSV)
- [x] Filename sanitization (path traversal, null bytes, length limits)
- [x] UUID-based filenames (prevent overwrites)
- [x] Files stored in /uploads/{category}/{uuid}_{filename}
- [x] Docker volume mounted for uploads/ (already configured in docker-compose.yml)
- [x] File metadata stored in files table
- [x] User storage quota management (200MB per user)
- [x] Unit tests for file service (11 tests)
- [x] Integration tests for file API (10 tests)
- [x] Audit logging for file operations (upload/download/delete)

**Status:** ✅ **COMPLETED** (2026-02-12)
- 21 tests passing
- File service with validation, quota, and permissions
- API endpoints for upload, download, delete, list
- Storage quota endpoint
- Integrated with audit logging

---

#### IMP-011: Frontend - Authentication UI

**Category:** Feature  
**Priority:** High

**Description:**
Create login form, MFA setup flow, and protected route wrapper.

**Motivation:**
- Users need UI to authenticate
- MFA must be user-friendly (QR code setup)

**Impact:**
- Users can log in via web interface
- MFA setup guided workflow
- Protected pages redirect to login

**Dependencies:**
- IMP-006 (Auth endpoints)
- IMP-007 (MFA endpoints)
- IMP-004 (Frontend structure)

**Risks:**
- UX confusion during MFA setup

**Acceptance Criteria:**
- [ ] Login form component created
- [ ] MFA setup flow created (show QR, verify TOTP)
- [ ] MFA verification prompt during login
- [ ] "Remember this device" checkbox
- [ ] Protected route wrapper (redirects if not authenticated)
- [ ] Auth context provider (React Context)
- [ ] Logout functionality
- [ ] Unit tests for auth components

---

#### IMP-012: Frontend - Admin Panel (User Management)

**Category:** Feature  
**Priority:** Medium

**Description:**
Create admin panel for user CRUD and MFA reset.

**Motivation:**
- Admin needs UI to manage users
- Admin needs ability to reset users' MFA if lost

**Impact:**
- Admin can create, view, edit users
- Admin can reset MFA for locked-out users

**Dependencies:**
- IMP-006 (Auth endpoints)
- IMP-008 (RBAC)
- IMP-011 (Frontend auth)

**Risks:**
- None (admin-only feature)

**Acceptance Criteria:**
- [ ] POST /api/admin/users endpoint (create user)
- [ ] GET /api/admin/users endpoint (list users)
- [ ] GET /api/admin/users/{id} endpoint (view user)
- [ ] PUT /api/admin/users/{id} endpoint (update user)
- [ ] DELETE /api/admin/users/{id} endpoint (soft-delete)
- [ ] POST /api/admin/users/{id}/reset-mfa endpoint
- [ ] Admin panel UI created
- [ ] User list table with filters
- [ ] User create/edit form
- [ ] MFA reset button with confirmation
- [ ] Admin-only route protection

---

### SPRINT 2: TAX RECORDS MODULE

#### IMP-013: Database Schema - Tax Records

**Category:** Feature  
**Priority:** High

**Description:**
Create database tables for tax_wfh_entries and tax_travel_entries.

**Motivation:**
- Foundation for tax tracking
- ATO compliance critical
- Per-user isolation required

**Impact:**
- Tax data can be stored
- User ownership enforced at database level

**Dependencies:**
- IMP-005 (Users table)

**Risks:**
- None (straightforward schema)

**Acceptance Criteria:**
- [x] Alembic migration created for tax_wfh_entries
- [x] Alembic migration created for tax_travel_entries
- [x] user_id foreign key enforced
- [x] Unique constraint: (user_id, date) for WFH entries
- [x] Indexes created per Design-v1.md
- [x] Migration runs successfully

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-014: Tax Records - WFH Entry CRUD

**Category:** Feature  
**Priority:** High

**Description:**
Implement WFH entry creation, retrieval, update, and deletion with per-user isolation.

**Motivation:**
- Core tax tracking functionality
- ATO compliance requirement
- Users need to track WFH hours

**Impact:**
- Users can add daily WFH hours
- Users can view/edit/delete own entries
- All users can read others' entries (household transparency)

**Dependencies:**
- IMP-013 (Tax schema)
- IMP-008 (RBAC)
- IMP-009 (Audit logging)

**Risks:**
- RBAC bypass allowing users to edit others' records

**Acceptance Criteria:**
- [x] POST /api/tax/wfh endpoint (create entry)
- [x] GET /api/tax/wfh endpoint (list own entries)
- [x] GET /api/tax/wfh/{id} endpoint (view entry)
- [x] PUT /api/tax/wfh/{id} endpoint (update own entry)
- [x] DELETE /api/tax/wfh/{id} endpoint (delete own entry)
- [x] GET /api/tax/wfh/users/{user_id} endpoint (view other user's entries - read-only)
- [x] Per-user isolation enforced (cannot modify others' records)
- [x] Audit logging for all CRUD operations
- [x] Unit tests for WFH service (17 tests)
- [x] Integration tests for WFH endpoints (10 tests)

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-015: Tax Records - Work Travel CRUD

**Category:** Feature  
**Priority:** High

**Description:**
Implement work travel entry CRUD with per-user isolation.

**Motivation:**
- Core tax tracking functionality
- ATO logbook compliance

**Impact:**
- Users can track work-related vehicle travel
- Distance and purpose recorded

**Dependencies:**
- IMP-013 (Tax schema)
- IMP-008 (RBAC)
- IMP-009 (Audit logging)

**Risks:**
- None (similar to WFH)

**Acceptance Criteria:**
- [x] POST /api/tax/travel endpoint (create entry)
- [x] GET /api/tax/travel endpoint (list own entries)
- [x] GET /api/tax/travel/{id} endpoint (view entry)
- [x] PUT /api/tax/travel/{id} endpoint (update own entry)
- [x] DELETE /api/tax/travel/{id} endpoint (delete own entry)
- [x] GET /api/tax/travel/users/{user_id} endpoint (view other user's entries)
- [x] Per-user isolation enforced
- [x] Audit logging for all CRUD operations
- [x] Unit tests for travel service (15 tests)
- [x] Integration tests for travel endpoints (9 tests)

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-016: Tax Records - FY Summary and Calculations

**Category:** Feature  
**Priority:** High

**Description:**
Calculate financial year totals for WFH hours and travel kilometers.

**Motivation:**
- ATO reporting requirement
- Users need to see FY totals for tax lodgement

**Impact:**
- Users can view FY summary dashboard
- Deduction amounts calculated automatically

**Dependencies:**
- IMP-014 (WFH entries)
- IMP-015 (Travel entries)

**Risks:**
- Date range calculation errors (FY = July 1 - June 30)

**Acceptance Criteria:**
- [x] GET /api/tax/wfh/summary endpoint (FY totals)
- [x] GET /api/tax/travel/summary endpoint (FY totals)
- [x] Calculate total days, hours, deduction for WFH (@ $0.67/hour)
- [x] Calculate total trips, km, deduction for travel (user-defined rate)
- [x] Summary grouped by financial year (July-June)
- [x] Unit tests for FY calculations (3 tests)
- [x] Integration tests for summary endpoints (2 tests)

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-017: Tax Records - ATO Export

**Category:** Feature  
**Priority:** High

**Description:**
Export WFH and travel data in ATO-compliant format (CSV or plain text).

**Motivation:**
- ATO lodgement requirement
- Users need exportable records

**Impact:**
- Users can download ATO-compliant summary
- Records ready for tax lodgement

**Dependencies:**
- IMP-016 (FY summary)

**Risks:**
- Export format not matching ATO expectations (user validation required)

**Acceptance Criteria:**
- [x] GET /api/tax/wfh/export/fy/{fy_year}/csv endpoint
- [x] GET /api/tax/wfh/export/fy/{fy_year}/text endpoint
- [x] GET /api/tax/travel/export/fy/{fy_year}/csv endpoint
- [x] GET /api/tax/travel/export/fy/{fy_year}/text endpoint
- [x] Export format matches Design-v1.md examples
- [x] Export includes: FY year, totals, deduction, detailed log
- [x] Audit logging for export events
- [x] Integration tests for export (7 tests total)

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-018: Frontend - Tax Records UI (WFH)

**Category:** Feature
**Priority:** High

**Description:**
Create WFH entry form, list view, and calendar view.

**Motivation:**
- Users need intuitive UI to track WFH
- Quick-add widget for dashboard

**Impact:**
- Users can add WFH entries via web UI
- Calendar view shows which days were worked

**Dependencies:**
- IMP-014 (WFH endpoints) ✅
- IMP-011 (Frontend auth) - Deferred

**Risks:**
- Date picker UX on mobile

**Acceptance Criteria:**
- [ ] WFH entry form component
- [ ] WFH list view with edit/delete
- [ ] Calendar view (read-only, highlights WFH days)
- [ ] FY summary widget
- [ ] Quick-add form (for dashboard)
- [ ] Client-side validation (React Hook Form + Zod)
- [ ] Unit tests for WFH components

**Status:** Deferred - Backend complete, UI pending

---

#### IMP-019: Frontend - Tax Records UI (Work Travel)

**Category:** Feature  
**Priority:** High

**Description:**
Create work travel entry form and list view.

**Motivation:**
- Users need UI to track work travel

**Impact:**
- Users can log work trips via web UI

**Dependencies:**
- IMP-015 (Travel endpoints)
- IMP-011 (Frontend auth)

**Risks:**
- None

**Acceptance Criteria:**
- [ ] Travel entry form component
- [ ] Travel list view with edit/delete
- [ ] FY summary widget
- [ ] Quick-add form (for dashboard)
- [ ] Client-side validation
- [ ] Unit tests for travel components

**Status:** Deferred - Backend complete, UI pending

---

#### IMP-020: Frontend - Tax Export UI

**Category:** Feature  
**Priority:** Medium

**Description:**
Add export buttons to tax summary views.

**Motivation:**
- Users need easy access to ATO exports

**Impact:**
- Users can download ATO-compliant exports with one click

**Dependencies:**
- IMP-017 (Export endpoints)
- IMP-018 (Tax UI)

**Risks:**
- None

**Acceptance Criteria:**
- [ ] Export button on WFH summary page
- [ ] Export button on travel summary page
- [ ] Download triggered as CSV/text file
- [ ] Export includes correct FY data

**Status:** Deferred - Backend complete, UI pending

---

### SPRINT 3: FINANCIAL MANAGEMENT MODULE

#### IMP-021: Database Schema - Financial Management

**Category:** Feature
**Priority:** High

**Description:**
Create database tables for income sources, bank accounts, expense categories, expenses, and utilities.

**Motivation:**
- Foundation for budget planning and utility tracking
- Enable household financial management
- Support budget transfer calculations

**Impact:**
- Financial data can be stored with proper relationships
- Expense categories linked to bank accounts for transfer calculations
- Utility tracking with cost-per-unit calculations

**Dependencies:**
- IMP-005 (Users table)

**Risks:**
- None (straightforward schema)

**Acceptance Criteria:**
- [x] Alembic migration created for 5 financial tables
- [x] 4 enum types created (IncomeFrequency, ExpenseFrequency, AccountType, UtilityType)
- [x] Foreign key relationships established (category → account, expense → category, utility → file)
- [x] Cascade deletes configured properly
- [x] Indexes created for query optimization
- [x] Migration runs successfully

**Status:** Complete ✅ (2026-02-13)
**Migration:** `8d07792f10cc_add_financial_management_tables.py`

---

#### IMP-022: Income Sources CRUD

**Category:** Feature
**Priority:** High

**Description:**
Implement income source management with frequency support (daily/weekly/fortnightly/monthly/yearly).

**Motivation:**
- Required for budget calculations
- Support multiple income streams
- Enable accurate budget planning

**Impact:**
- Users can track all household income sources
- Frequencies support various pay schedules
- Budget calculations can normalize to any frequency

**Dependencies:**
- IMP-021 (Financial schema)
- IMP-008 (RBAC)

**Risks:**
- None

**Acceptance Criteria:**
- [x] POST /api/financial/income endpoint (create)
- [x] GET /api/financial/income endpoint (list with pagination)
- [x] GET /api/financial/income/{id} endpoint (view)
- [x] PUT /api/financial/income/{id} endpoint (update)
- [x] DELETE /api/financial/income/{id} endpoint (delete)
- [x] Validation: amount > 0
- [x] Permission enforcement (financial:write for modifications)
- [x] IncomeSourceService with all CRUD operations

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-023: Bank Accounts and Expense Categories CRUD

**Category:** Feature
**Priority:** High

**Description:**
Implement bank account management and expense categories with account linking.

**Motivation:**
- Foundation for budget transfer calculations
- Enable expense organization by account
- Support multiple account types (checking/savings/offset)

**Impact:**
- Users can manage multiple bank accounts
- Expense categories organize spending by account
- Budget calculator groups expenses by destination account

**Dependencies:**
- IMP-021 (Financial schema)
- IMP-008 (RBAC)

**Risks:**
- None

**Acceptance Criteria:**
- [x] Bank Accounts: 5 endpoints (POST, GET list, GET single, PUT, DELETE)
- [x] Expense Categories: 5 endpoints (POST, GET list, GET single, PUT, DELETE)
- [x] Category filtering by bank account
- [x] Prevent account deletion if categories exist
- [x] Prevent category deletion if expenses exist
- [x] Optional balance tracking per account
- [x] Color coding support for categories
- [x] BankAccountService and ExpenseCategoryService

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-024: Expenses CRUD

**Category:** Feature
**Priority:** High

**Description:**
Implement expense tracking with frequency support and category linking.

**Motivation:**
- Core budget planning functionality
- Track recurring expenses (bills, subscriptions)
- Enable budget transfer calculations

**Impact:**
- Users can track all recurring expenses
- Expenses linked to categories (and thus accounts)
- Budget calculator aggregates expenses by account

**Dependencies:**
- IMP-023 (Expense categories)

**Risks:**
- None

**Acceptance Criteria:**
- [x] POST /api/financial/expenses endpoint (create)
- [x] GET /api/financial/expenses endpoint (list with category filter)
- [x] GET /api/financial/expenses/{id} endpoint (view)
- [x] PUT /api/financial/expenses/{id} endpoint (update)
- [x] DELETE /api/financial/expenses/{id} endpoint (delete)
- [x] Validation: amount > 0, category exists
- [x] Frequency support (daily/weekly/fortnightly/monthly/yearly)
- [x] Optional notes field
- [x] ExpenseService with all CRUD operations

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-025: Budget Calculation Service

**Category:** Feature
**Priority:** High

**Description:**
Implement budget calculation algorithm with frequency normalization and transfer requirements.

**Motivation:**
- Core budget planner functionality
- Help users understand how much to transfer to each account
- Support various pay frequencies

**Impact:**
- Users can calculate budget for any pay frequency
- Transfers grouped by bank account
- Shows which expenses each transfer covers
- Calculates surplus/deficit

**Dependencies:**
- IMP-022 (Income sources)
- IMP-024 (Expenses)

**Risks:**
- Frequency conversion accuracy

**Acceptance Criteria:**
- [x] POST /api/financial/budget/calculate endpoint (with pay frequency parameter)
- [x] GET /api/financial/budget/summary endpoint (monthly summary)
- [x] Frequency normalization algorithm (all frequencies → monthly → target frequency)
- [x] Conversion factors: daily=30x, weekly=4.33x, fortnightly=2.17x, monthly=1x, yearly=0.0833x
- [x] Group expenses by bank account via categories
- [x] Calculate required transfer per account
- [x] List expenses covered by each transfer
- [x] Calculate total income, total expenses, surplus/deficit
- [x] BudgetService with calculation logic
- [x] Response includes account allocations for dashboard widget

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-026: Utilities Tracking and Statistics

**Category:** Feature
**Priority:** High

**Description:**
Implement utility cost tracking with usage monitoring and statistics aggregation.

**Motivation:**
- Track household utility costs over time
- Monitor usage trends (electricity, gas, water, internet, mobile)
- Enable cost analysis and optimization

**Impact:**
- Users can log utility bills with usage data
- Automatic cost-per-unit calculation
- Statistics show averages and totals by utility type
- Optional file attachment for bills

**Dependencies:**
- IMP-021 (Financial schema)
- IMP-010 (File upload for attachments)

**Risks:**
- None

**Acceptance Criteria:**
- [x] POST /api/financial/utilities endpoint (create with usage/cost)
- [x] GET /api/financial/utilities endpoint (list with type/date filters)
- [x] GET /api/financial/utilities/{id} endpoint (view)
- [x] PUT /api/financial/utilities/{id} endpoint (update)
- [x] DELETE /api/financial/utilities/{id} endpoint (delete)
- [x] GET /api/financial/utilities/stats/{type} endpoint (aggregated statistics)
- [x] Validation: usage > 0, cost > 0, end date > start date
- [x] Automatic cost_per_unit calculation (cost / usage)
- [x] Statistics: avg cost, total usage, total cost, entry count, date range
- [x] Support for 5 utility types (electricity, gas, water, internet, mobile)
- [x] Optional file attachment linking
- [x] UtilityService with all operations

**Status:** Complete ✅ (2026-02-13)

---

#### IMP-027: Frontend - Financial Management UI

**Category:** Feature
**Priority:** High

**Description:**
Create budget planner UI, utility tracking UI, and utility cost graphs.

**Motivation:**
- Users need visual interface for financial management
- Budget planner needs intuitive transfer calculation display
- Utility graphs show cost trends over time

**Impact:**
- Users can manage finances via web UI
- Budget calculator shows clear transfer instructions
- Graphs visualize utility cost patterns

**Dependencies:**
- IMP-022 through IMP-026 (All financial endpoints) ✅
- IMP-011 (Frontend auth) - Deferred

**Risks:**
- Chart.js/Recharts configuration complexity

**Acceptance Criteria:**
- [ ] Income sources management UI
- [ ] Bank accounts management UI
- [ ] Expense categories management UI
- [ ] Expenses management UI
- [ ] Budget calculator page (select frequency, view transfers)
- [ ] Budget summary widget (dashboard)
- [ ] Utilities entry form
- [ ] Utilities list view with filters
- [ ] Utility cost graphs (line charts by type)
- [ ] Client-side validation (React Hook Form + Zod)
- [ ] Unit tests for financial components

**Status:** Deferred - Backend complete, UI pending

---

### SPRINT 4+: ADDITIONAL MODULES (DEFERRED)

Additional modules (Assets & Documents, Projects, Knowledge Base, Meal Planner) are defined in PROJECT_STATUS.md Sprints 4-7 but not detailed here yet. These will be added to Improvements.md as Sprint 3 completes.

---

## Sequencing

### Sprint 0 (Foundation)
**Order:** IMP-001 → IMP-002 → IMP-003 → IMP-004  
**Rationale:** Infrastructure must be established before any code can be written. Backend and frontend structures can be created in parallel after Docker stack is ready.

### Sprint 1 (Core Platform Services)
**Order:**
1. IMP-005 (Database schema) - Foundation for all services
2. IMP-006 (Authentication) - Required before RBAC
3. IMP-007 (MFA) - Extends authentication
4. IMP-008 (RBAC) - Required before audit logging and file upload
5. IMP-009 (Audit logging) - Needed by all modules
6. IMP-010 (File upload) - Platform service
7. IMP-011 (Frontend auth UI) - Can run in parallel with backend
8. IMP-012 (Admin panel) - Last (depends on all backend services)

**Rationale:** Database → Auth → Security → Platform Services → UI

### Sprint 2 (Tax Records Module)
**Order:**
1. IMP-013 (Tax schema) - Foundation
2. IMP-014 (WFH CRUD) + IMP-015 (Travel CRUD) - Can run in parallel
3. IMP-016 (FY summary) - Depends on CRUD
4. IMP-017 (Export) - Depends on summary
5. IMP-018 (WFH UI) + IMP-019 (Travel UI) - Can run in parallel with backend
6. IMP-020 (Export UI) - Last

**Rationale:** Schema → CRUD → Calculations → Export → UI

---

## Risks & Mitigations

### Risk 1: Raspberry Pi Performance
**Severity:** Medium  
**Impact:** Slow page loads, poor UX  
**Mitigation:**
- Optimize queries with indexes (defined in schema)
- Implement pagination early
- Monitor performance during development
- Plan for VPS migration if needed

### Risk 2: Docker Memory Constraints
**Severity:** Medium  
**Impact:** Containers crash, database connection issues  
**Mitigation:**
- Configure container memory limits
- Monitor RAM usage during testing
- Optimize PostgreSQL configuration for limited RAM

### Risk 3: Security Vulnerabilities in Authentication
**Severity:** High  
**Impact:** Account takeover, data breach  
**Mitigation:**
- Follow OWASP best practices
- Code review for auth/RBAC logic
- Penetration testing before v1.0
- Audit logging catches suspicious activity

### Risk 4: RBAC Permission Bypass
**Severity:** Critical  
**Impact:** Users can access/modify others' tax records  
**Mitigation:**
- Comprehensive RBAC unit tests
- Integration tests for all protected endpoints
- Manual testing with multiple user accounts
- Audit logging catches unauthorized access

### Risk 5: MFA Secret Loss
**Severity:** High  
**Impact:** Users locked out of accounts  
**Mitigation:**
- Admin can reset MFA (IMP-012)
- Backup codes (planned for v1.1)
- Document secret backup procedure

### Risk 6: Data Loss (No Backups in v1)
**Severity:** High  
**Impact:** Tax records lost, ATO compliance violated  
**Mitigation:**
- Document manual backup procedure in README
- Educate admin on importance of backups
- Monitor disk space (planned for v1.1)

### Risk 7: Scope Creep
**Severity:** Medium  
**Impact:** Delayed v1.0 release  
**Mitigation:**
- Strict adherence to Design-v1.md
- Defer all nice-to-haves to FUTURE_PLANS.md
- User must approve any scope changes

---

## Resource Considerations

**Development Environment:**
- Local machine for development (not Raspberry Pi)
- Raspberry Pi for production deployment only
- Docker Desktop required (Windows/Mac)

**Time Estimates:**
- Sprint 0: 1-2 days (setup only)
- Sprint 1: 2-3 weeks (core platform services)
- Sprint 2: 2 weeks (tax module)
- Total to functional tax tracking: ~5 weeks

**Skills Required:**
- Python (FastAPI, SQLAlchemy, Alembic)
- React (hooks, forms, routing)
- PostgreSQL (schema design, migrations)
- Docker (compose, containers, volumes)
- Security (Argon2, JWT, TOTP, RBAC)

---

## Parallelization Opportunities

**Sprint 0:**
- IMP-003 (Backend structure) and IMP-004 (Frontend structure) can run in parallel after IMP-001 and IMP-002 are complete.

**Sprint 1:**
- IMP-011 (Frontend auth UI) can begin once IMP-006 (Auth endpoints) is complete, running in parallel with IMP-007-IMP-010.

**Sprint 2:**
- IMP-014 (WFH CRUD) and IMP-015 (Travel CRUD) can run in parallel.
- IMP-018 (WFH UI) and IMP-019 (Travel UI) can run in parallel once respective backend endpoints are complete.

---

## Notes

- This document covers Sprints 0-2 in detail.
- Additional modules (Financial, Assets, Projects, Knowledge, Meal Planner) will be added as Sprint 2 progresses.
- All improvements must align with Design-v1.md (locked).
- Any architectural changes require Design-v2.md approval.
- Improvements are not approved until user confirms.

---

**Last Updated:** 2026-02-13
**Next Review:** After Sprint 4 completion
