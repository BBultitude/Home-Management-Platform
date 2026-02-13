# PROJECT_STATUS.md

## Project Information

**Project Name:** Home Management Platform
**Current Version:** v0.1.0 (Pre-release / Development)
**Active Design Document:** Design-v1.md (Approved)
**Project Phase:** Development - Sprint 1
**Started:** 2025-02-01
**Target v1.0 Release:** TBD

## ⚠️ Existing Codebases Available for Porting

Two modules have existing implementations that will be ported during later sprints:

1. **Cost-Benefit Decision** (Sprint 5): https://github.com/BBultitude/Cost-Benefit-Decision
   - Node.js/Express + JSON → Port to Python/FastAPI + PostgreSQL

2. **Meal Planner** (Sprint 7): https://github.com/BBultitude/Meal-Planner
   - Node.js/Express + JSON → Port to Python/FastAPI + PostgreSQL

---

## Version History

| Version | Date | Status | Design Doc | Notes |
|---------|------|--------|------------|-------|
| v0.1.0 | 2025-02-01 | In Progress | Design-v1.md (Draft) | Initial architecture definition |

---

## Current Sprint: Sprint 4 - Assets & Documents Module

**Sprint Goal:** Implement insurance vault and document storage
**Sprint Duration:** TBD
**Sprint Status:** ⚪ Not Started

### Previous Sprints
- **Sprint 0:** Foundation & Planning - 🟢 Completed (2026-02-02)
- **Sprint 1:** Core Platform Services - 🟢 Completed (2026-02-02 to 2026-02-12)
- **Sprint 2:** Tax Records Module (Backend) - 🟢 Completed (2026-02-13)
- **Sprint 3:** Financial Management Module (Backend) - 🟢 Completed (2026-02-13)

### Sprint Tasks

| Task ID | Task | Status | Assignee | Priority | Blockers | Completed |
|---------|------|--------|----------|----------|----------|-----------|
| S0-T1 | Review and approve Design-v1.md | 🟢 Completed | User | High | None | 2026-02-02 |
| S0-T2 | Set up development environment | 🟢 Completed | Developer | High | S0-T1 | 2026-02-11 |
| S0-T3 | Initialize Git repository | 🟢 Completed | Developer | High | S0-T1 | 2026-02-02 |
| S0-T4 | Set up Docker Compose stack (skeleton) | 🟢 Completed | Developer | High | S0-T2 | 2026-02-11 |
| S0-T5 | Generate secrets (DB, JWT, MFA key) | 🟢 Completed | Developer | High | S0-T4 | 2026-02-11 |
| S0-T6 | Configure Cloudflare Tunnel | ⚪ Not Started | User/Developer | Medium | S0-T4 | - |

**Legend:**
- ⚪ Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔴 Blocked
- 🔵 Deferred

---

## Upcoming Sprints (Tentative)

### Sprint 1 - Core Platform Services ✅

**Sprint Goal:** Implement authentication, RBAC, and file upload services
**Duration:** 11 days (2026-02-02 to 2026-02-12)
**Status:** 🟢 **COMPLETED**

**Key Deliverables:**
- ✅ User registration and login (password + MFA)
- ✅ Session management (HTTP-only cookies)
- ✅ RBAC implementation (Admin, Editor, Reader)
- ✅ File upload service with validation
- ✅ Database schema for users, trusted devices, files, audit logs
- ✅ Comprehensive audit logging

**Backend Tasks:**
- [x] IMP-005: Database schema (users, trusted_devices, files, audit_logs)
- [x] IMP-006: User authentication service and endpoints
- [x] IMP-007: MFA implementation (PyOTP + Fernet encryption)
- [x] IMP-007: Trusted device functionality
- [x] IMP-008: RBAC with permission matrix (30+ permissions)
- [x] IMP-009: Audit logging service (40+ event types, 5-year retention for tax/auth)
- [x] IMP-010: File upload service (validation, quota management, UUID-based storage)
- [x] Database migrations (Alembic)
- [x] Comprehensive test coverage:
  - 186 tests passing
  - 88% code coverage
  - 100% coverage on auth, MFA, and audit services

**Frontend Tasks:**
- [ ] DEFERRED: Set up React project structure (moved to Sprint 1.5)
- [ ] DEFERRED: Create login/MFA forms (moved to Sprint 1.5)
- [ ] DEFERRED: Create protected route wrapper (moved to Sprint 1.5)

**Notes:**
- Frontend deferred to allow backend stabilization first
- File service adapted to existing File model (no soft delete)
- All acceptance criteria met for backend services

---

### Sprint 2 - Tax Records Module ✅

**Sprint Goal:** Implement per-user tax tracking (WFH + Work Travel)
**Duration:** 1 day (2026-02-13)
**Status:** 🟢 **COMPLETED** (Backend only)

**Key Deliverables:**
- ✅ WFH entry CRUD (with per-user isolation)
- ✅ Work Travel entry CRUD (with per-user isolation)
- ✅ Tax summary calculations (FY totals)
- ✅ ATO-compliant export (CSV/Text)
- 🔵 Calendar view (deferred - UI pending)
- 🔵 Quick-add widgets (deferred - UI pending)

**Backend Tasks:**
- [x] IMP-013: Database schema (tax_wfh_entries, tax_travel_entries)
- [x] IMP-014: WFH API endpoints (7 endpoints: CRUD + summary + export)
- [x] IMP-015: Work Travel API endpoints (7 endpoints: CRUD + summary + export)
- [x] IMP-016: FY summary calculations (July 1 - June 30)
- [x] IMP-017: ATO export functionality (CSV + text formats)
- [x] Per-user isolation enforced (RBAC)
- [x] Audit logging for all tax operations
- [x] Comprehensive test coverage:
  - 57 tax module tests passing (100%)
  - WFH: 17 service + 14 API tests
  - Travel: 15 service + 13 API tests

**Frontend Tasks:**
- [ ] IMP-018: WFH entry UI (DEFERRED)
- [ ] IMP-019: Travel entry UI (DEFERRED)
- [ ] IMP-020: Export UI buttons (DEFERRED)

**Notes:**
- Backend fully functional and tested
- All API endpoints ready for UI integration
- UI deferred - will be built when frontend structure is ready
- Can test via FastAPI Swagger UI at `/docs`

---

### Sprint 3 - Financial Management Module ✅

**Sprint Goal:** Implement budget planner and utility cost tracking
**Duration:** 1 day (2026-02-13)
**Status:** 🟢 **COMPLETED** (Backend only)

**Key Deliverables:**
- ✅ Income sources CRUD with frequency management
- ✅ Bank accounts CRUD (checking/savings/offset)
- ✅ Expense categories CRUD (linked to accounts)
- ✅ Expenses CRUD with frequency tracking
- ✅ Budget calculation algorithm (frequency normalization, transfer requirements)
- ✅ Utility cost entry and tracking
- ✅ Utility statistics aggregation
- 🔵 Budget planner UI (deferred)
- 🔵 Utility tracking UI (deferred)
- 🔵 Utility cost graphs (deferred)

**Backend Tasks:**
- [x] Database schema (5 tables: income_sources, bank_accounts, expense_categories, expenses, utilities)
- [x] Income sources API (5 endpoints: CRUD)
- [x] Bank accounts API (5 endpoints: CRUD)
- [x] Expense categories API (5 endpoints: CRUD with bank account filtering)
- [x] Expenses API (5 endpoints: CRUD with category filtering)
- [x] Budget calculation service (frequency normalization: daily/weekly/fortnightly/monthly/yearly)
- [x] Budget calculation API (2 endpoints: calculate by frequency, monthly summary)
- [x] Utilities API (6 endpoints: CRUD + statistics aggregation)
- [x] Per-user permission enforcement (financial:read, financial:write)
- [x] Services: IncomeSourceService, BankAccountService, ExpenseCategoryService, ExpenseService, BudgetService, UtilityService

**Frontend Tasks:**
- [ ] Budget planner UI (DEFERRED)
- [ ] Utility tracking UI (DEFERRED)
- [ ] Utility cost graphs (DEFERRED)

**Notes:**
- Backend fully functional with 23 financial endpoints
- Budget calculation supports all pay frequencies (daily through yearly)
- Automatic cost-per-unit calculation for utilities
- Utility stats include avg cost, total usage, aggregation by type
- UI deferred - will be built when frontend structure is ready
- Can test via FastAPI Swagger UI at `/docs`

---

### Sprint 4 - Assets & Documents Module

**Sprint Goal:** Implement insurance vault and document storage  
**Estimated Duration:** 2 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Insurance policy CRUD with renewal tracking
- Document storage and categorization
- File upload integration
- Renewal alerts (30 days, 7 days)
- Document viewer

**Tasks:**
- [ ] Create insurance_policies and documents tables
- [ ] Implement insurance policy CRUD
- [ ] Implement documents CRUD
- [ ] Implement renewal alert logic
- [ ] Create insurance policy form (React)
- [ ] Create document upload form (React)
- [ ] Create document viewer component
- [ ] Create renewal alerts widget (dashboard)
- [ ] Write integration tests for assets endpoints

---

### Sprint 5 - Projects & Tasks Module (with Repair Prioritization)

**Sprint Goal:** Implement repair prioritization, project planning, and quote tracking  
**Estimated Duration:** 2-3 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Priority items CRUD with cost-benefit scoring
- Convert priority item → Create project workflow
- Project CRUD with status workflow
- Quote CRUD with contractor details
- Quote comparison view
- Quote expiry alerts
- Project document linking

**Tasks:**
- [ ] Create priority_items table (with scoring columns)
- [ ] Create projects table (with priority_item_id FK)
- [ ] Create quotes table
- [ ] Implement priority items CRUD API
- [ ] Implement cost-benefit scoring algorithm (port from existing code)
- [ ] Implement "Convert to Project" API endpoint
- [ ] Implement project CRUD API
- [ ] Implement quote CRUD API
- [ ] Implement status workflow logic
- [ ] Create priority items list view (sorted by net_score) (React)
- [ ] Create priority item form (React)
- [ ] Create "Convert to Project" button/modal (React)
- [ ] Create project form and status selector (React)
- [ ] Create quote form (React)
- [ ] Create quote comparison table (React)
- [ ] Create project detail view with linked quotes and originating priority item
- [ ] Write integration tests for priority items, projects, and quotes endpoints

**Integration Note:** This sprint combines the ported Cost-Benefit Decision Tracker with project management for unified workflow.

---

### Sprint 6 - Household Knowledge Base

**Sprint Goal:** Implement structured knowledge articles  
**Estimated Duration:** 2-3 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Knowledge article CRUD for all 8 types
- Template-based data entry forms
- Full-text search (PostgreSQL FTS)
- Article type schemas and validation
- Article list/grid views with filters

**Tasks:**
- [ ] Create knowledge_articles table (JSONB schema)
- [ ] Define schemas for all 8 article types
- [ ] Implement knowledge article CRUD
- [ ] Implement template-based form generator
- [ ] Implement full-text search
- [ ] Create knowledge article entry forms (React)
- [ ] Create article list/grid view with filters
- [ ] Create article type selector
- [ ] Implement password encryption for TechDevice articles
- [ ] Write unit tests for schema validation
- [ ] Write integration tests for knowledge endpoints

---

### Sprint 7 - Meal Planner Module

**Sprint Goal:** Port meal planner and implement recipe management with shopping list generation  
**Estimated Duration:** 2-3 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Recipe CRUD (no pre-loaded recipes, starts empty)
- Ingredient management
- Weekly meal planning
- Shopping list generation with consolidation
- Australian measurement conversions

**Tasks:**
- [ ] Create recipes table
- [ ] Create ingredients table
- [ ] Create week_plans table
- [ ] Implement recipe CRUD API
- [ ] Implement ingredient CRUD API
- [ ] Implement week plan CRUD API
- [ ] Port shopping list generation algorithm (consolidation + conversions)
- [ ] Implement Australian measurement conversion logic
- [ ] Create recipe list view (React)
- [ ] Create recipe form (with ingredients editor) (React)
- [ ] Create weekly meal planner calendar (React)
- [ ] Create shopping list generator view (React)
- [ ] Create print-friendly recipe/shopping list views
- [ ] Write unit tests for consolidation algorithm
- [ ] Write integration tests for meal planner endpoints

**Porting Note:** Ported from Node.js/Express + JSON → Python/FastAPI + PostgreSQL + React

---

### Sprint 8 - Dashboard & Global Features

**Sprint Goal:** Implement unified dashboard and global search  
**Estimated Duration:** 2 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Dashboard with all widgets (including priorities and meal planner)
- Global search across modules
- In-app notifications
- Quick-action shortcuts
- Mobile-responsive layout

**Tasks:**
- [ ] Implement dashboard data aggregation endpoints
- [ ] Implement global search (PostgreSQL FTS)
- [ ] Implement notifications system
- [ ] Create dashboard page with widgets (React)
- [ ] Create repair/upgrade priorities widget
- [ ] Create meal planner widget
- [ ] Create global search component
- [ ] Create notification widget
- [ ] Create quick-action buttons
- [ ] Optimize dashboard for mobile
- [ ] Write integration tests for dashboard
- [ ] Write integration tests for search

---

### Sprint 8 - Admin Panel & User Management

**Sprint Goal:** Implement admin user management interface  
**Estimated Duration:** 1 week  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Admin panel UI
- User management (create, update, delete, MFA reset)
- Audit log viewer (admin-only)
- System settings (future placeholder)

**Tasks:**
- [ ] Implement admin user management endpoints
- [ ] Implement audit log query endpoints
- [ ] Create admin panel layout (React)
- [ ] Create user management table and forms
- [ ] Create audit log viewer
- [ ] Implement MFA reset functionality
- [ ] Write integration tests for admin endpoints

---

### Sprint 9 - Testing, Documentation & Deployment

**Sprint Goal:** Comprehensive testing, documentation, and deployment preparation  
**Estimated Duration:** 2 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- 70%+ unit test coverage
- Integration tests for all endpoints
- User documentation (setup, usage guides)
- Deployment scripts and instructions
- Performance testing and optimization

**Tasks:**
- [ ] Achieve 70% unit test coverage
- [ ] Write integration tests for all modules
- [ ] Write user setup guide
- [ ] Write user guide for each module
- [ ] Create deployment scripts (Docker Compose)
- [ ] Test deployment on Raspberry Pi
- [ ] Performance testing (load testing, query optimization)
- [ ] Security audit (basic penetration testing)
- [ ] Create admin onboarding checklist
- [ ] Final QA pass

---

### Sprint 10 - v1.0 Release Preparation

**Sprint Goal:** Final polish and v1.0 release  
**Estimated Duration:** 1 week  
**Status:** ⚪ Not Started

**Key Deliverables:**
- v1.0 release candidate
- Release notes
- Migration guide (if applicable)
- Production deployment

**Tasks:**
- [ ] Final bug fixes
- [ ] Update CHANGELOG.md
- [ ] Create release notes
- [ ] Tag v1.0 release in Git
- [ ] Deploy to production (Raspberry Pi)
- [ ] Post-deployment verification
- [ ] User training session

---

## Backlog (Post-v1.0)

See FUTURE_PLANS.md for detailed roadmap.

**High-Priority Items for v1.1:**
- Automated backups (OneDrive sync)
- Monitoring and alerting (disk space, errors)
- CSV import for tax data and insurance policies
- Password recovery (admin-assisted or email-based)
- Performance optimizations (caching, query optimization)

**Medium-Priority Items for v1.2+:**
- Email notifications (SMTP integration)
- PWA support (offline capability, installable)
- Data export/import (full backup/restore)
- Advanced search filters
- Bulk operations (delete, export)

**Long-Term Items for v2.0+:**
- Receipt scanning (OCR)
- Calendar integration (Google Calendar)
- Investment tracking
- Mobile native apps

**Note:** Meal Planner and repair prioritization (cost-benefit) are now in v1.0 (originally planned for v2.0).

---

## Milestones

| Milestone | Target Date | Status | Completion Criteria |
|-----------|-------------|--------|---------------------|
| Design Approval | TBD | 🟡 In Progress | Design-v1.md approved by user |
| Foundation Complete | TBD | ⚪ Not Started | Docker stack running, DB initialized |
| Core Platform Services | TBD | ⚪ Not Started | Auth, RBAC, file upload working |
| Tax Module Complete | TBD | ⚪ Not Started | WFH and Travel tracking functional |
| All Modules Implemented | TBD | ⚪ Not Started | All 6 modules functional |
| Dashboard Complete | TBD | ⚪ Not Started | Dashboard showing all widgets |
| Testing Complete | TBD | ⚪ Not Started | 70% coverage, all integration tests pass |
| v1.0 Released | TBD | ⚪ Not Started | Deployed to production, users trained |

---

## Risks & Blockers

### Active Risks

| Risk | Severity | Impact | Mitigation | Status |
|------|----------|--------|------------|--------|
| Design not approved | High | Delays all development | Iterate on design based on feedback | 🟡 Active |
| Raspberry Pi performance | Medium | Poor UX, slowdowns | Optimize queries, implement caching | ⚪ Monitoring |
| Scope creep | Medium | Delayed v1.0 | Strict adherence to v1 scope, defer to FUTURE_PLANS | ⚪ Monitoring |

### Resolved Risks

_None yet_

---

## Dependencies

### External Dependencies
- Cloudflare Tunnel (for public access)
- Raspberry Pi availability and configuration
- User availability for testing and feedback

### Internal Dependencies
- Design-v1.md approval (blocks all development)
- Core platform services (blocks all modules)
- Database schema (blocks module implementation)

---

## Team & Responsibilities

**User:**
- Product owner / decision maker
- Design approval
- Testing and feedback
- Cloudflare configuration
- Production deployment oversight

**AI/Developer:**
- Architecture and design
- Implementation
- Testing (unit, integration)
- Documentation
- Deployment scripting

---

## Communication & Reporting

**Status Updates:** Weekly (or as needed)  
**Sprint Reviews:** After each sprint  
**Blockers:** Raised immediately  
**Design Changes:** Require user approval  

---

## Notes

- Sprint numbers are tentative and may be adjusted based on progress and feedback
- Task estimates will be refined as sprints begin
- New issues will be tracked in KNOWN_ISSUES.md as they arise
- UI-specific issues will be tracked in UI_ISSUES.md

---

**Last Updated:** 2026-02-13
**Next Review:** After Sprint 4 completion
