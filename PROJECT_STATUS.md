# PROJECT_STATUS.md

## Project Information

**Project Name:** Home Management Platform  
**Current Version:** v0.1.0 (Pre-release / Development)  
**Active Design Document:** Design-v1.md (Draft - Pending Approval)  
**Project Phase:** Planning & Architecture  
**Started:** 2025-02-01  
**Target v1.0 Release:** TBD (After Design-v1.md approval)

---

## Version History

| Version | Date | Status | Design Doc | Notes |
|---------|------|--------|------------|-------|
| v0.1.0 | 2025-02-01 | In Progress | Design-v1.md (Draft) | Initial architecture definition |

---

## Current Sprint: Sprint 0 - Foundation & Planning

**Sprint Goal:** Complete architecture design and establish project foundation  
**Sprint Duration:** TBD  
**Sprint Status:** 🟡 In Progress

### Sprint Tasks

| Task ID | Task | Status | Assignee | Priority | Blockers |
|---------|------|--------|----------|----------|----------|
| S0-T1 | Review and approve Design-v1.md | 🟡 In Progress | User | High | None |
| S0-T2 | Set up development environment | ⚪ Not Started | Developer | High | S0-T1 |
| S0-T3 | Initialize Git repository | ⚪ Not Started | Developer | High | S0-T1 |
| S0-T4 | Set up Docker Compose stack (skeleton) | ⚪ Not Started | Developer | High | S0-T2 |
| S0-T5 | Generate secrets (DB, JWT, MFA key) | ⚪ Not Started | Developer | High | S0-T4 |
| S0-T6 | Configure Cloudflare Tunnel | ⚪ Not Started | User/Developer | Medium | S0-T4 |

**Legend:**
- ⚪ Not Started
- 🟡 In Progress
- 🟢 Completed
- 🔴 Blocked
- 🔵 Deferred

---

## Upcoming Sprints (Tentative)

### Sprint 1 - Core Platform Services

**Sprint Goal:** Implement authentication, RBAC, and file upload services  
**Estimated Duration:** 2-3 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- User registration and login (password + MFA)
- Session management (HTTP-only cookies)
- RBAC implementation (Admin, Editor, Reader)
- File upload service with validation
- Database schema for users, trusted devices, files
- Basic audit logging

**Tasks:**
- [ ] Set up FastAPI project structure
- [ ] Configure PostgreSQL connection
- [ ] Implement user model and authentication (FastAPI-Users)
- [ ] Implement MFA (PyOTP + encrypted secrets)
- [ ] Implement trusted device functionality
- [ ] Implement RBAC decorators and permissions
- [ ] Implement file upload endpoint with validation
- [ ] Create database migrations (Alembic)
- [ ] Write unit tests for authentication and RBAC
- [ ] Set up React project structure
- [ ] Create login/MFA forms
- [ ] Create protected route wrapper (auth check)

---

### Sprint 2 - Tax Records Module

**Sprint Goal:** Implement per-user tax tracking (WFH + Work Travel)  
**Estimated Duration:** 2 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- WFH entry CRUD (with per-user isolation)
- Work Travel entry CRUD (with per-user isolation)
- Tax summary calculations (FY totals)
- ATO-compliant export (CSV/PDF)
- Calendar view (read-only) for WFH entries
- Quick-add widgets for dashboard

**Tasks:**
- [ ] Create tax_wfh_entries and tax_travel_entries tables
- [ ] Implement WFH API endpoints (CRUD + summary)
- [ ] Implement Work Travel API endpoints (CRUD + summary)
- [ ] Implement per-user isolation checks (RBAC)
- [ ] Implement export functionality (CSV format)
- [ ] Create WFH entry form (React)
- [ ] Create Work Travel entry form (React)
- [ ] Create tax summary view (FY totals)
- [ ] Create calendar view component
- [ ] Write integration tests for tax endpoints
- [ ] Implement audit logging for tax operations

---

### Sprint 3 - Financial Management Module

**Sprint Goal:** Implement budget planner and utility cost tracking  
**Estimated Duration:** 2-3 weeks  
**Status:** ⚪ Not Started

**Key Deliverables:**
- Household members and income sources management
- Bank accounts and expense categories management
- Budget calculation logic (transfer requirements)
- Utility cost entry and tracking
- Utility cost graphs (Chart.js/Recharts)
- Budget summary for dashboard

**Tasks:**
- [ ] Create financial module database schema
- [ ] Implement household members CRUD
- [ ] Implement income sources CRUD
- [ ] Implement bank accounts CRUD
- [ ] Implement expense categories CRUD
- [ ] Implement budget calculation algorithm
- [ ] Implement utility entries CRUD
- [ ] Implement utility graph data aggregation
- [ ] Create budget planner UI
- [ ] Create utility tracking UI
- [ ] Create utility cost graphs (Recharts)
- [ ] Write unit tests for budget calculations
- [ ] Integration with Insurance module (read renewal costs)

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

**Last Updated:** 2025-02-01  
**Next Review:** After Design-v1.md approval
