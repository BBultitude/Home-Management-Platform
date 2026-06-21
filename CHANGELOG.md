# CHANGELOG.md

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed
- **Vite 8 frontend build failures (2)**: PR #10 bumped Vite 7→8 which switched to
  rolldown as its bundler, introducing two breaking changes:
  (1) `manualChunks` object form no longer accepted — converted to function form
  `(id) => { ... }` in `vite.config.ts`;
  (2) `minify: 'esbuild'` fails as esbuild is no longer bundled with Vite 8 —
  changed to `minify: true` to use rolldown's built-in oxc minifier.
- **Docker secrets permission error on Pi**: Backend container crashed on startup with
  `PermissionError: [Errno 13] Permission denied: /run/secrets/db_password`. Docker
  secrets are bind-mounted with host file permissions (`0400 root:root`), making them
  unreadable by the non-root `appuser`. Fixed by adding a `docker-entrypoint.sh` that
  runs as root, widens secret permissions to `o+r`, then drops to `appuser` via `gosu`
  before exec-ing uvicorn. `gosu` added to `Dockerfile.prod` apt-get block.

---

### Planned for v1.1
- Email notifications (SMTP integration)
- Automated backups to cloud storage
- PWA support with offline capability
- Performance optimizations
- Cost-Benefit Decision module

---

## [0.5.1] - 2026-02-25

### 🐛 Bug Fixes & UX Improvements

Post-production fixes from user feedback.

### Fixed
- **Billing Days Off-By-One**: Utility billing period day count now inclusive on both ends
  (June 11–Sept 11 correctly shows 93 days, not 92)
- **nginx 403 on /assets route**: Removed `$uri/` directory check from SPA try_files fallback;
  React Router navigation to `/assets` page now works correctly on mobile
- **Mobile Dark Mode (Knowledge Base)**: Added `color-scheme: light only` to `:root` to prevent
  Android Chrome's forced dark mode from inverting card colours

### Added
- **Average Daily Usage — Utilities Tab**: New "Avg Daily" column in the utilities table showing
  per-entry daily consumption rate (e.g. `18.45 kWh/day`); rates entries show `—`
- **Average Daily Usage — Backend**: `avg_daily_usage` and `total_billing_days` fields added to
  utility stats API response (`GET /financial/utilities/stats/{type}`)
- **Admin MFA Reset UI**: "Reset MFA" button in admin user table (visible only when MFA is
  enabled); includes confirmation dialog and toast feedback; uses existing backend endpoint
  `POST /admin/users/{user_id}/reset-mfa`

### Changed
- **Dashboard Utility Widgets**: Electricity/Gas/Water now show avg daily usage as primary
  metric instead of total cost/usage; Rates shows avg bill cost as primary metric
- **Dashboard**: Removed budget summary card (income/expenses/surplus) — provided no actionable
  value at a glance

---

## [0.5.0] - 2026-02-15

### 🍽️ Sprint 21 - Meal Planner UI (Complete)

Complete frontend implementation of the Meal Planner module with recipe management, weekly planning, and auto-generated shopping lists.

### Added

#### Meal Planner Module (`/meals`)
- **RecipesTab**: Full CRUD for recipes with ingredients and cooking steps
  - Dynamic ingredient input with separate amount (number) and unit (dropdown) fields
  - 15 standard measurement units (g, kg, oz, lb, ml, L, tsp, tbsp, cup, whole, piece, clove, bunch, to taste)
  - View-only recipe dialog with Eye icon (read without editing)
  - Search functionality for recipes
  - Ingredient count badge on recipe cards
- **WeekPlanTab**: Weekly meal planning with 7 numbered meal slots
  - Maps to Monday-Sunday backend fields
  - Single current week plan (no historical data)
  - View recipe button on each meal slot
  - Smart createOrUpdate pattern (try update, fallback to create)
  - Clear individual meals or entire plan
- **ShoppingListTab**: Auto-generated consolidated shopping list
  - Smart ingredient combining with case-insensitive matching
  - Groups by (ingredient name, unit) and sums quantities
  - Shows which recipes use each ingredient
  - Download as text file
  - Removed print functionality (download only)
- **mealPlannerService.ts**: TypeScript API wrapper for meal planner operations

#### Ingredient Data Model Restructure
- Split `quantity` string into structured fields:
  - `quantity_amount`: Decimal (numeric value)
  - `quantity_unit`: MeasurementUnit enum (standardized unit)
- Database migration (`d8f42a1b9c3e_update_ingredients_quantity_structure`)
  - Adds `quantity_amount` and `quantity_unit` columns
  - Migrates existing data with default values
  - Drops old `quantity` column
- Updated shopping list consolidation algorithm:
  - Groups ingredients by lowercase name and unit
  - Sums amounts for matching groups
  - Formats as "300 g" instead of "300g, 100g"
  - Handles pantry staples as "As needed"

### Fixed
- datetime.timedelta import bug in week_plan.py model
- Recipe update 500 error (API endpoints now use quantity_amount/quantity_unit)
- Ingredient combining case sensitivity (Chicken vs chicken now combine)
- Week plan 404 error handling on delete then save (expected behavior)

### Changed
- Simplified week plan to current week only (no date pickers)
- Updated meal planner schemas and services for new ingredient structure
- Ingredient form layout: 5 cols name, 2 cols amount, 4 cols unit, 1 col delete
- All dialogs use solid white backgrounds for consistency

### Permissions
- Added `meals:write` and `meals:read` to RBAC system

---

## [0.4.0] - 2026-02-15

### 📝 Documentation & Status Update

Updated project documentation to accurately reflect completion status:
- Backend: 100% complete (all modules implemented)
- Frontend: ~90% complete (Meal Planner UI pending)
- All 15 completed sprints properly documented

---

## [0.3.0] - 2026-02-15

### 🎨 Sprint 20 - Knowledge Base + File Upload Integration

Complete implementation of the Household Knowledge Base module with 8 article types and file upload integration across Assets and Projects modules.

### Added

#### File Upload System
- **FileUploadInput Component**: Reusable drag-and-drop file upload component
  - Client-side validation (20MB per file, allowed MIME types: PDF, PNG, JPG, GIF, WEBP, TXT, CSV, XLSX)
  - Upload progress indicator
  - File preview with download/delete functionality
  - Categories: INSURANCE, QUOTE, UTILITY, KNOWLEDGE, TAX, PROJECT, ASSET, OTHER
  - Integrates with backend /api/v1/files endpoints
- **fileService.ts**: TypeScript API wrapper for file operations
  - upload(), get(), download(), delete(), list(), getQuota()
  - Storage quota enforcement (200MB total, 20MB per file)

#### Knowledge Base Module (`/knowledge`)
- **KnowledgeBase.tsx**: Main page with unified article view
  - Full-text search using PostgreSQL ts_rank with 300ms debounce
  - Filter by article type and tags
  - Article cards with type icons, tags, and attachment counts
  - Create/Edit/Delete article functionality
- **ArticleForm.tsx**: Dynamic type-specific forms for 8 article types
- **knowledgeService.ts**: TypeScript API wrapper for knowledge base operations

#### Knowledge Article Types
1. **Measurement**: Room dimensions, window sizes, measurements
   - Fields: location, measurement_type, value, unit, date_measured, notes
2. **Paint**: Colors, finishes, coverage information
   - Fields: room_area, surface_type, brand, product_line, color_name, color_code, finish, retailer
3. **TechDevice**: Routers, modems, smart devices with credentials
   - Fields: device_type, brand_model, location, IP, MAC, WiFi SSID/password, admin credentials
   - **Backend encrypts passwords using Fernet**
4. **StorageLocation**: Garage organization, item storage tracking
   - Fields: storage_area, items_stored (array), category, last_updated
5. **Vehicle**: Cars, motorcycles, bicycles with maintenance tracking
   - Fields: make, model, year, VIN, registration, service_history, next_service
   - **Links to insurance policies**
6. **EmergencyContact**: Important contacts and service providers
   - Fields: name, relationship_role, phones, email, category, when_to_call
   - **Pin to dashboard flag for quick access**
7. **Appliance**: Home appliances with warranty and service tracking
   - Fields: appliance_type, brand, model, serial, warranty, service_history, energy_rating
8. **Vendor**: Contractors and service providers with ratings
   - Fields: business_name, service_type, contact info, rating (1-5 stars), cost_range, review

### Enhanced

#### Assets Module
- **DocumentsTab**: Replaced file_id placeholder with FileUploadInput component
  - Required file upload for all documents
  - Download/delete functionality in table view
- **InsurancePoliciesTab**: Added optional policy document upload
  - Store insurance policy PDFs for reference

#### Projects Module
- **QuotesTab**: Added optional quote document upload
  - Upload contractor quote PDFs for comparison
  - Display in quote comparison table

### Technical Details
- **UI Components**: Added Checkbox component from @radix-ui/react-checkbox
- **Type Safety**: All services use TypeScript type-only imports with verbatimModuleSyntax
- **Toast Notifications**: Migrated from custom useToast to sonner throughout
- **Validation**: Client-side and server-side validation for all article types
- **Search**: Real-time full-text search with PostgreSQL tsvector
- **File Attachments**: Many-to-many relationship between articles and files

### Fixed
- Type errors in InsurancePoliciesTab and QuotesTab document_id handling
- Import statements using type-only imports for better type safety
- NodeJS.Timeout replaced with ReturnType<typeof setTimeout> for compatibility

---

## [1.0.0] - 2026-02-13

### 🎉 Initial Production Release

First production-ready release of the Home Management Platform with complete backend API implementation.

### Added

#### Core Platform Services (Sprint 1)
- User authentication with username/password
- Multi-factor authentication (MFA) with TOTP (PyOTP)
- Role-based access control (RBAC): Admin, Editor, Reader roles
- 30+ granular permissions across modules
- Session management with HTTP-only secure cookies
- Trusted device tracking with device fingerprinting
- Comprehensive audit logging (40+ event types, 5-year retention for tax/auth)
- File upload service with validation (10MB limit, mime type validation)
- UUID-based file storage
- Database migrations with Alembic

#### Tax Records Module (Sprint 2)
- Work From Home (WFH) entry tracking
- Work Travel expense tracking with distance calculation
- Financial Year summary (July 1 - June 30)
- ATO-compliant export formats (CSV and text)
- Per-user data isolation
- 14 API endpoints (7 WFH, 7 Travel)

#### Financial Management Module (Sprint 3)
- Income source management with 5 frequency types
- Bank account management (checking, savings, offset types)
- Expense category management with bank account linking
- Expense tracking with frequency support
- Budget calculation with frequency normalization
- Utility cost tracking (electricity, gas, water, internet)
- Utility statistics aggregation
- 28 API endpoints

#### Assets & Documents Module (Sprint 4)
- Insurance policy management (10 policy types)
- Document storage and categorization (9 document types)
- Renewal alerts (30-day and 7-day thresholds)
- Expiry tracking for documents
- File upload integration
- Tag-based organization (ARRAY type)
- Search functionality
- 18 API endpoints

#### Projects & Tasks Module (Sprint 5)
- Priority item tracking with cost-benefit scoring algorithm
- Automated benefit_score = severity + frequency (2-10)
- Automated cost_score = log10(cost) + 1 (1-5)
- Net score calculation for prioritization
- Convert priority item to project workflow
- Project management with 5-status lifecycle
- Quote tracking with contractor details
- Quote comparison and selection
- Quote expiry notifications
- 21 API endpoints

#### Household Knowledge Base (Sprint 6)
- Structured knowledge articles with 8 types
- Flexible JSONB schemas for type-specific data
- Full-text search with PostgreSQL TSVECTOR/GIN indexes
- Password encryption for TechDevice articles (Fernet)
- File attachment support via junction table
- Tag-based organization
- Search indexing with to_tsvector
- 10 API endpoints

#### Meal Planner Module (Sprint 7)
- Recipe management with HTML-formatted steps
- Ingredient management with sort ordering
- Weekly meal planning (Monday-Sunday)
- Shopping list generation with ingredient consolidation
- Pantry staples detection ("As needed" marking)
- Australian measurement conversions (cups, tbsp, tsp)
- Quantity summing for same-unit ingredients
- Recipe search by name or ingredient
- Current week plan retrieval
- 13 API endpoints

#### Dashboard & Global Features (Sprint 8)
- Dashboard data aggregation with 8 widgets
- Alerts widget (insurance renewals, document expiries, quote expiries)
- Priorities widget (top 10 by net_score)
- Projects widget (status counts, active projects list)
- Meal plan widget (current week with meals)
- Financial widget (monthly expenses, utilities, upcoming premiums)
- Tax summary widget (current FY deductions)
- Notifications widget (recent + unread count)
- Quick stats widget (header counts across all modules)
- Notifications system (5 types, 7 categories)
- Automatic notification generation for renewals/expiries
- Global search across 6 modules (recipes, knowledge, projects, priorities, assets, financial)
- PostgreSQL FTS for knowledge articles
- Quick search for autocomplete
- Relevance scoring (exact match, starts with, contains)
- 22 API endpoints

#### Admin Panel & User Management (Sprint 9)
- User management (list, get, update, delete)
- Role management with protection against last admin removal
- User activation/deactivation
- MFA reset functionality (generates new secret and QR code)
- System statistics (users, security, activity)
- Per-user activity statistics
- Enhanced audit log queries (by user, module, action)
- Protection against self-modification
- 14 API endpoints

### Testing & Documentation (Sprint 10)
- 47 new test cases for Sprints 8-9
- Notification service tests (16 tests)
- Admin service tests (22 tests)
- Dashboard service tests (9 tests)
- Comprehensive API Guide (151 endpoints documented)
- Deployment Guide (Docker Compose + manual installation)
- Database Schema Reference (22 tables)
- Security best practices documentation
- Backup/restore procedures
- Troubleshooting guide

### Security
- JWT-based session authentication with configurable expiry
- MFA with TOTP (RFC 6238 compliant)
- Fernet encryption for sensitive data (MFA secrets, passwords)
- Password strength validation (12-128 chars, complexity requirements)
- HTTP-only secure cookies with SameSite=Strict
- CSRF protection via SameSite cookies
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS prevention (Pydantic input validation)
- Comprehensive audit logging for all actions
- Permission-based authorization for all endpoints
- Secure file upload validation (mime type, size, extension)
- Protection against common attacks (OWASP Top 10)

### Database
- PostgreSQL 14+ with advanced features
- 22 tables across 9 modules
- UUID primary keys (gen_random_uuid)
- JSONB for flexible schemas
- ARRAY types for tags
- TSVECTOR for full-text search
- GIN indexes for JSONB and TSVECTOR
- B-tree indexes for foreign keys and common queries
- Composite indexes for optimized filtering
- Foreign key constraints with CASCADE/SET NULL
- Check constraints for data validation
- Unique constraints for business rules
- Alembic migrations for version control
- Migration history tracking

### API Endpoints
- **Total:** 151 endpoints across 10 modules
- **Authentication:** 6 endpoints
- **Tax Records:** 14 endpoints
- **Financial:** 28 endpoints
- **Assets & Documents:** 18 endpoints
- **Projects & Tasks:** 21 endpoints
- **Knowledge Base:** 10 endpoints
- **Meal Planner:** 13 endpoints
- **Dashboard:** 22 endpoints
- **Admin:** 14 endpoints
- **Audit Logs:** 5 endpoints

### Documentation
- API Guide with usage examples
- Deployment Guide (Docker + manual)
- Database Schema Reference
- Interactive Swagger UI at `/docs`
- ReDoc UI at `/redoc`
- OpenAPI 3.0 specification
- Security best practices
- Permission matrix
- Error handling guide
- Backup/restore procedures
- Troubleshooting guide
- Configuration reference

### Deployment
- Docker Compose configuration
- Multi-stage Dockerfile for optimization
- Systemd service files
- Nginx reverse proxy configuration
- SSL/TLS setup with Let's Encrypt
- Cloudflare Tunnel support
- Automated database backups
- Log rotation with journald
- Environment variable management
- Production-ready settings
- Health check endpoints

### Performance
- Database indexes for common queries
- Pagination for large result sets
- Efficient aggregation queries for dashboard
- Query optimization for search
- Connection pooling with SQLAlchemy
- Lazy loading for relationships
- Selective eager loading where needed

### Known Limitations
- Frontend UI not implemented (backend-first approach)
- No automated task scheduling (cron/Celery not configured)
- No email notifications (SMTP not configured)
- No real-time updates (WebSocket not implemented)
- Single-household deployment (no multi-tenancy)
- No mobile app (API-only)
- No PWA/offline support

### Technical Stack
- **Python:** 3.11+
- **Framework:** FastAPI 0.109+
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** PyJWT, PyOTP, Cryptography
- **Validation:** Pydantic v2
- **Testing:** Pytest
- **Server:** Uvicorn
- **Documentation:** OpenAPI/Swagger

### Statistics
- **Lines of Code:** ~15,000 (backend)
- **Test Files:** 17 (14 from Sprint 1-2, 3 new)
- **Test Cases:** 233+ (186 from Sprint 1-2, 47 new)
- **Code Coverage:** 88% (Sprint 1-2 modules)
- **Database Tables:** 22
- **Migrations:** 10
- **Documentation Pages:** 6
- **API Endpoints:** 151

---

## [1.0.0-dev] - 2025-02-01

### Added
- Initial project setup
- Architecture documentation (Design-v1.md)
- Project tracking (PROJECT_STATUS.md)
- Issue tracking (KNOWN_ISSUES.md, UI_ISSUES.md)
- Documentation (README.md, CONTRIBUTING.md, FUTURE_PLANS.md)

### Architecture
- Modular plugin architecture designed
- Five core modules defined:
  - Financial Management (Budget, Utilities, Forecasting)
  - Assets & Documents (Insurance, Quotes)
  - Projects & Tasks (Project tracking)
  - Household Knowledge (Structured articles)
  - Tax Records & Compliance (WFH, Travel logbook)
- Platform services layer specified
- Security architecture defined (MFA, RBAC, HTTP-only cookies)

### Technology Stack
- Backend: Python 3.11 + FastAPI
- Frontend: React 18 + Tailwind CSS
- Database: PostgreSQL 16
- Containers: Docker Compose
- Security: PyOTP, Argon2, Fernet encryption

---

## Release Notes Template (For Future Releases)

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features added to the project

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future releases

### Removed
- Features removed from the project

### Fixed
- Bug fixes

### Security
- Security improvements or vulnerability fixes
```

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes, major redesigns
- **MINOR** (x.Y.0): New features, backward-compatible
- **PATCH** (x.y.Z): Bug fixes, backward-compatible

**Examples:**
- `1.0.0` → `1.1.0`: Added email notifications (new feature)
- `1.1.0` → `1.1.1`: Fixed tax calculation bug (bug fix)
- `1.9.0` → `2.0.0`: Redesigned architecture (breaking changes)

---

## Future Releases (Planned)

See [FUTURE_PLANS.md](./FUTURE_PLANS.md) for detailed roadmap.

### v1.1 (Planned Q2 2025)
- Email notifications
- Automated backups (OneDrive sync)
- Bulk actions (multi-select)
- Dashboard widget caching
- Dark mode support
- Keyboard shortcuts

### v1.2 (Planned Q3 2025)
- Soft-delete with anonymization (ATO compliance)
- Automated tax data purge (5-year retention)
- MFA backup codes
- Tablet-optimized UI
- Pre-filled tax PDF forms
- Budget rollover feature

### v2.0 (Planned Q4 2025+)
- PWA with offline support
- Custom knowledge article types
- Google Calendar integration
- Internal API layer (module decoupling)
- Advanced analytics
- IP-based access restrictions

---

## Changelog Guidelines

### When to Update

Update CHANGELOG.md for:
- Every release (major, minor, patch)
- Significant features (even before release)
- Security fixes (immediately)
- Breaking changes (with migration guide)

### What to Include

**Good:**
- Clear description of change
- Why it matters to users
- Breaking changes highlighted
- Migration instructions (if needed)

**Example Entry:**

```markdown
### Added
- **Email Notifications**: Users can now receive email alerts for insurance renewals and project updates. Configure SMTP settings in Settings → Notifications. (#245)

### Fixed
- **Tax Calculation Bug**: Fixed incorrect FY total when entries span midnight. All historical calculations recalculated automatically on upgrade. (#312)

### Security
- **MFA Bypass Vulnerability**: Patched critical vulnerability allowing MFA bypass via session manipulation. All users required to re-authenticate. **Upgrade immediately.** (CVE-2025-XXXX)

### Changed
- **BREAKING**: Tax export API endpoint changed from `/tax/export` to `/tax/wfh/export` and `/tax/travel/export` for clarity. Update any scripts. (#289)
  - **Migration**: Update API calls before upgrading
  - **Timeline**: Old endpoint deprecated in v1.1, removed in v2.0
```

---

## Release Checklist

Before tagging a new release:

- [ ] All planned features implemented
- [ ] All tests passing
- [ ] Security review completed
- [ ] Documentation updated (README, Design-vX.md)
- [ ] CHANGELOG.md updated with all changes
- [ ] Version bumped in all relevant files
- [ ] Migration guide written (if breaking changes)
- [ ] Release notes drafted
- [ ] User acceptance testing completed

---

## Git Tags

**Creating a Release Tag:**

```bash
# Tag format: vX.Y.Z
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"

# Push tag
git push origin v1.0.0

# Verify tag
git tag -l
git show v1.0.0
```

**Tag Message Template:**

```
Release vX.Y.Z: [Short description]

Highlights:
- Feature 1
- Feature 2
- Important fix

Full changelog: https://github.com/org/repo/blob/main/CHANGELOG.md#XYZ

Breaking changes: [Yes/No]
Security fixes: [Yes/No]
```

---

## Deprecated Features Log

Track features being phased out:

| Feature | Deprecated In | Reason | Removed In | Alternative |
|---------|---------------|--------|------------|-------------|
| - | - | - | - | - |

**Example:**
| Feature | Deprecated In | Reason | Removed In | Alternative |
|---------|---------------|--------|------------|-------------|
| Old budget API `/budget/summary` | v1.1 | Replaced by module-specific endpoints | v2.0 | Use `/financial/budget/summary` |

---

## Security Advisories

Track security fixes:

| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| - | - | - | - | - |

**Example:**
| CVE | Severity | Affected Versions | Fixed In | Description |
|-----|----------|-------------------|----------|-------------|
| CVE-2025-0001 | Critical | v1.0.0 - v1.0.5 | v1.0.6 | MFA bypass via session manipulation |

---

## Migration Guides

For breaking changes, provide migration guides:

### Upgrading from v1.0.x to v1.1.0

**Breaking Changes:**
1. Tax export endpoint split into WFH and Travel endpoints

**Migration Steps:**

```bash
# 1. Backup database
docker exec home_mgmt_db pg_dump -U home_mgmt_user home_mgmt > backup.sql

# 2. Stop containers
docker-compose down

# 3. Pull new version
git pull origin main

# 4. Update containers
docker-compose pull
docker-compose up -d

# 5. Run migrations
docker exec home_mgmt_app alembic upgrade head

# 6. Update API calls (if using programmatically)
# Old: GET /api/v1/tax/export?type=wfh
# New: GET /api/v1/tax/wfh/export
```

**API Changes:**

| Old Endpoint | New Endpoint | Notes |
|-------------|--------------|-------|
| `/tax/export` | `/tax/wfh/export` | WFH data only |
| `/tax/export` | `/tax/travel/export` | Travel data only |

**Database Changes:**
- No schema changes requiring manual intervention
- All migrations handled automatically

**Configuration Changes:**
- New environment variable: `EMAIL_NOTIFICATIONS_ENABLED` (default: false)
- Add SMTP settings if enabling email notifications

---

## Contributors

We recognize all contributors to this project:

### v1.0.0
- [Your Name] - Initial architecture and implementation

### v1.1.0
- [Contributors list]

---

## Links

- [Repository](https://github.com/org/repo)
- [Issue Tracker](https://github.com/org/repo/issues)
- [Discussions](https://github.com/org/repo/discussions)
- [Security Policy](./SECURITY.md) (future)

---

**Last Updated:** 2025-02-01

---
## Sprint Summary Archive

### Sprint 12 - Frontend Foundation (2026-02-13)
Completed initial React + TypeScript + Tailwind CSS setup with shadcn/ui components.

