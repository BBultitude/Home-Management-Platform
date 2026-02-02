# CHANGELOG.md

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned for v1.0.0
- Initial release with core functionality
- See PROJECT_STATUS.md for detailed sprint plan

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
