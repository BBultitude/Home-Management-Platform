# Improvements.md

## Document Metadata

- **Date Updated:** 2026-02-02
- **Author:** Claude (AI Strategist)
- **Reviewed By:** Bryan Bultitude
- **Active Architecture Version:** Design-v1.md (Approved)

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
- [ ] docker-compose.yml created with app + db services
- [ ] Backend Dockerfile created
- [ ] Containers start successfully
- [ ] Database initializes with empty schema
- [ ] App container can connect to database
- [ ] Health checks configured

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
- [ ] secrets/ directory created with .gitignore entry
- [ ] db_password.txt generated (32 bytes random)
- [ ] jwt_secret.txt generated (32 bytes random)
- [ ] mfa_encryption_key.txt generated (32 bytes random)
- [ ] Docker secrets configured in docker-compose.yml
- [ ] README instructions for secret generation added

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
- [ ] backend/ directory structure created per CONTRIBUTING.md
- [ ] main.py with FastAPI app initialization
- [ ] dependencies.py for dependency injection
- [ ] requirements.txt with core dependencies (FastAPI, SQLAlchemy, etc.)
- [ ] alembic/ directory for migrations
- [ ] tests/ directory structure
- [ ] .env.example created

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
- [ ] Alembic migration created for users table
- [ ] Alembic migration created for trusted_devices table
- [ ] Alembic migration created for audit_logs table
- [ ] Alembic migration created for files table
- [ ] Indexes created per Design-v1.md data model
- [ ] Migration runs successfully
- [ ] Database inspection shows correct schema

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
- [ ] POST /api/auth/register endpoint (admin-only)
- [ ] POST /api/auth/login endpoint
- [ ] POST /api/auth/logout endpoint
- [ ] GET /api/auth/me endpoint (current user info)
- [ ] Argon2 password hashing implemented
- [ ] NIST password policy enforced (8 char min, no complexity)
- [ ] HTTP-only JWT cookies set on login
- [ ] Session expiry configured (1 hour)
- [ ] Unit tests for auth service
- [ ] Integration tests for auth endpoints

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
- [ ] POST /api/files/upload endpoint
- [ ] GET /api/files/{id} endpoint (download/view)
- [ ] DELETE /api/files/{id} endpoint (if not referenced)
- [ ] File validation: Max 20MB, allowed MIME types (PDF, JPG, PNG, DOCX)
- [ ] Filename sanitization
- [ ] UUID-based filenames (prevent overwrites)
- [ ] Files stored in /uploads/{category}/{uuid}_{filename}
- [ ] Docker volume mounted for uploads/
- [ ] File metadata stored in files table
- [ ] Unit tests for file validation
- [ ] Integration tests for upload/download

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
- [ ] Alembic migration created for tax_wfh_entries
- [ ] Alembic migration created for tax_travel_entries
- [ ] user_id foreign key enforced
- [ ] Unique constraint: (user_id, date) for WFH entries
- [ ] Indexes created per Design-v1.md
- [ ] Migration runs successfully

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
- [ ] POST /api/tax/wfh endpoint (create entry)
- [ ] GET /api/tax/wfh endpoint (list own entries)
- [ ] GET /api/tax/wfh/{id} endpoint (view entry)
- [ ] PUT /api/tax/wfh/{id} endpoint (update own entry)
- [ ] DELETE /api/tax/wfh/{id} endpoint (delete own entry)
- [ ] GET /api/tax/wfh/users/{user_id} endpoint (view other user's entries - read-only)
- [ ] Per-user isolation enforced (cannot modify others' records)
- [ ] Audit logging for all CRUD operations
- [ ] Unit tests for WFH service
- [ ] Integration tests for WFH endpoints

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
- [ ] POST /api/tax/travel endpoint (create entry)
- [ ] GET /api/tax/travel endpoint (list own entries)
- [ ] GET /api/tax/travel/{id} endpoint (view entry)
- [ ] PUT /api/tax/travel/{id} endpoint (update own entry)
- [ ] DELETE /api/tax/travel/{id} endpoint (delete own entry)
- [ ] GET /api/tax/travel/users/{user_id} endpoint (view other user's entries)
- [ ] Per-user isolation enforced
- [ ] Audit logging for all CRUD operations
- [ ] Unit tests for travel service
- [ ] Integration tests for travel endpoints

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
- [ ] GET /api/tax/wfh/summary endpoint (FY totals)
- [ ] GET /api/tax/travel/summary endpoint (FY totals)
- [ ] Calculate total days, hours, deduction for WFH (@ $0.67/hour)
- [ ] Calculate total trips, km, deduction for travel (user-defined rate)
- [ ] Summary grouped by financial year (July-June)
- [ ] Unit tests for FY calculations
- [ ] Integration tests for summary endpoints

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
- [ ] GET /api/tax/wfh/export endpoint (CSV or text)
- [ ] GET /api/tax/travel/export endpoint (CSV or text)
- [ ] Export format matches Design-v1.md examples
- [ ] Export includes: FY year, totals, deduction, detailed log
- [ ] Audit logging for export events
- [ ] Integration tests for export

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
- IMP-014 (WFH endpoints)
- IMP-011 (Frontend auth)

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

---

### SPRINT 3+: ADDITIONAL MODULES (DEFERRED)

Additional modules (Financial Management, Assets & Documents, Projects, Knowledge Base, Meal Planner) are defined in PROJECT_STATUS.md Sprints 3-7 but not detailed here yet. These will be added to Improvements.md as Sprint 2 nears completion.

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

**Last Updated:** 2026-02-02  
**Next Review:** After Sprint 1 completion
