# KNOWN_ISSUES.md

## Overview

This document tracks known technical issues, limitations, and technical debt in the Home Management Platform.

**Issue Status Legend:**
- 🔴 Critical (blocks functionality, security risk)
- 🟡 High (significant impact, workaround available)
- 🟢 Medium (minor impact, cosmetic)
- 🔵 Low (nice-to-have, future enhancement)
- ✅ Resolved

---

## Critical Issues

_None currently identified_

---

## High Priority Issues

### Issue #1: Manual Backups Required (By Design)

**Status:** 🟢 Medium (Design Decision, Not a Bug)
**Category:** Data Safety / User Responsibility  
**Affects:** All modules  
**Reported:** 2025-02-01  
**Resolution:** This is by design for home use

**Description:**
- Backups are **manual** and at the **administrator's discretion**
- No automated backup functionality planned
- This is intentional for a home-use product
- Users must manually backup database and uploaded files
- Tax records require 5-year retention (ATO compliance)

**Impact:**
- Risk of data loss if Pi fails without backups
- ATO compliance potentially violated if data lost
- No point-in-time recovery

**User Responsibility:**
- Admin must establish their own backup routine
- Recommended: Weekly manual backups (database dump + file copy)
- Options: External HDD, OneDrive, Google Drive, NAS, etc.
- Admin decides frequency, retention, and storage location

**Backup Procedure (To Be Documented):**
```bash
# Database backup
docker exec homemanager_db pg_dump -U user homedb > backup_$(date +%Y%m%d).sql

# File uploads backup
cp -r /var/lib/docker/volumes/homemanager_uploads_data /backup/location/

# Or use rclone, rsync, or any preferred backup tool
```

**Rationale:**
- Home product, not enterprise
- Users have different preferences for backup (cloud, local, NAS)
- Automated backup adds complexity and external dependencies
- Admin has full control over their data

**Related:** README.md will document backup procedures and recommendations

---

### Issue #2: Account Deletion vs ATO Retention Requirements

**Status:** 🟡 High  
**Category:** Compliance / Data Retention  
**Affects:** Tax Records module, User Management  
**Reported:** 2025-02-01  
**Planned Fix:** v1 (documented limitation), proper fix in future version

**Description:**
- Current design: Admin can delete user accounts (hard delete)
- User preference: "If deleted account then data gone" (immediate deletion)
- ATO requirement: Tax records must be retained for 5 years
- **Conflict:** Hard delete violates ATO retention requirements

**Impact:**
- **Critical ATO compliance violation** if account deleted before 5-year retention expires
- Legal/audit risk for household users
- Potential penalties or audit issues

**Current Approach (v1):**
- Hard delete as requested by user
- **DOCUMENTED LIMITATION:** Users must not delete accounts until 5 years after last tax entry
- Admin warning before deletion: "This will delete all tax records. Ensure 5-year retention requirement is met."
- Responsibility on admin to enforce retention policy manually

**Better Approach (Future):**
- Soft-delete with anonymization (recommended)
- User account marked deleted, tax records preserved
- Automatic purge after 5 years + 1 day
- OR: Transfer tax records to "Archived User" account

**Action Required:**
- ✅ Confirmed: User accepts hard-delete with manual retention enforcement for v1
- ⚠️ Risk acknowledged: ATO compliance is user's responsibility
- 📝 Document in user guide: "Do not delete user accounts until 5 years after their last tax entry"
- 🔮 Future: Implement automated retention enforcement

**Related:** Design-v1.md - Data Retention section

---

## Medium Priority Issues

### Issue #3: No Password Recovery Mechanism

**Status:** 🟢 Medium  
**Category:** User Experience  
**Affects:** Authentication  
**Reported:** 2025-02-01  
**Planned Fix:** v1.1

**Description:**
- v1 does not include self-service password reset
- Requires SMTP configuration (out of scope for v1)
- If user forgets password, admin must reset manually

**Impact:**
- Minor inconvenience (household environment, admin available)
- Admin overhead for password resets

**Workaround:**
- Admin resets password via admin panel
- User sets new password on next login

**Planned Resolution:**
- v1.1: Email-based password reset (requires SMTP)
- OR: Continue admin-only reset (acceptable for 10 users)

---

### Issue #4: No Email Notifications

**Status:** 🟢 Medium  
**Category:** User Experience  
**Affects:** Notifications  
**Reported:** 2025-02-01  
**Planned Fix:** v1.2

**Description:**
- v1 only supports in-app notifications
- No email alerts for critical events (insurance expiry, backup failures)
- Users must check dashboard to see alerts

**Impact:**
- Users may miss important renewals or alerts
- Reduced proactive notification effectiveness

**Workaround:**
- Check dashboard regularly
- Pin urgent notifications

**Planned Resolution:**
- v1.2: SMTP integration for email notifications
- User-configurable notification preferences

---

### Issue #5: Limited Search Scope (Metadata Only)

**Status:** 🟢 Medium  
**Category:** Functionality  
**Affects:** Global Search  
**Reported:** 2025-02-01  
**Planned Fix:** v2.0

**Description:**
- v1 search only indexes metadata (titles, descriptions, structured fields)
- PDF contents are not searchable
- Users cannot search inside uploaded documents

**Impact:**
- Reduced search effectiveness for finding information in documents
- Users must manually open and search PDFs

**Workaround:**
- Use descriptive titles and tags for documents
- Manual search in PDF viewer

**Planned Resolution:**
- v2.0: PDF text extraction and indexing
- Requires OCR library (e.g., pdfplumber, PyPDF2)

---

## Low Priority Issues

### Issue #6: No Multi-Property Support

**Status:** 🔵 Low  
**Category:** Feature Limitation  
**Affects:** All modules  
**Reported:** 2025-02-01  
**Planned Fix:** v2.0+

**Description:**
- Current design assumes single household/property
- Users with multiple properties (rental, vacation) cannot separate data

**Impact:**
- Users with multiple properties must manage all in one system
- No isolation or separate budgets per property

**Workaround:**
- Use naming conventions (e.g., "Main House - Insurance", "Rental - Insurance")
- Use tags to differentiate

**Planned Resolution:**
- v2.0: Multi-property support with property selector

---

### Issue #7: No Dark Mode

**Status:** 🔵 Low  
**Category:** User Experience / Accessibility  
**Affects:** Frontend  
**Reported:** 2025-02-01  
**Planned Fix:** v1.2

**Description:**
- v1 only supports light theme
- No dark mode option

**Impact:**
- Reduced accessibility for users sensitive to bright screens
- Less comfortable for nighttime use

**Workaround:**
- Use browser extensions for dark mode (not ideal)

**Planned Resolution:**
- v1.2: Dark mode toggle with system preference detection

---

### Issue #8: No Bulk Operations

**Status:** 🔵 Low  
**Category:** User Experience  
**Affects:** All modules  
**Reported:** 2025-02-01  
**Planned Fix:** v1.2

**Description:**
- v1 does not support bulk delete, export, or tag operations
- Users must perform actions one item at a time

**Impact:**
- Time-consuming for large datasets
- Poor UX when cleaning up old data

**Workaround:**
- Perform operations individually

**Planned Resolution:**
- v1.2: Bulk select + bulk actions (delete, export, tag)

---

## Design Limitations (Intentional)

These are known limitations based on design decisions, not bugs.

### L1: Direct Database Access Between Modules

**Description:**
- Modules access each other's database tables directly (e.g., Budget reads Insurance table)
- No internal API layer between modules

**Rationale:**
- Simpler for v1
- Adequate for small scale
- Modules are in same codebase

**Trade-off:**
- Tighter coupling between modules
- Harder to extract modules into separate services later

**Future Consideration:**
- v2: Refactor to internal API layer if coupling becomes problematic

---

### L2: No Offline Support

**Description:**
- App requires internet connection to function
- No offline mode or service worker

**Rationale:**
- Out of scope for v1 (responsive web only)
- PWA features deferred

**Trade-off:**
- Cannot use app without internet
- Less useful on mobile when offline

**Future Consideration:**
- v2: PWA with limited offline capability

---

### L3: Session Timeout (1 Hour)

**Description:**
- Sessions expire after 1 hour of inactivity
- User must re-login (but trusted devices skip MFA)

**Rationale:**
- Security best practice
- Balance between security and convenience

**Trade-off:**
- Inconvenient for long sessions
- Users may need to re-authenticate frequently

**Configuration:**
- Adjustable in environment variables if needed
- Trusted devices reduce friction (30-day remember)

---

## Technical Debt

### TD1: No Comprehensive Error Handling in v1

**Priority:** Medium  
**Affects:** All modules  
**Description:**
- Basic try/catch error handling in v1
- No centralized error logging or monitoring
- Errors logged to console only

**Plan:**
- v1.1: Centralized error handler with structured logging
- v2: Integrate with external monitoring (Sentry, CloudWatch)

---

### TD2: No Database Connection Pooling

**Priority:** Low  
**Affects:** Performance  
**Description:**
- v1 uses default SQLAlchemy connection handling
- No PgBouncer or advanced pooling

**Plan:**
- Monitor connection usage in production
- Add PgBouncer if connection limits reached

---

### TD3: No Rate Limiting (API-Level)

**Priority:** Low  
**Affects:** Security / Performance  
**Description:**
- v1 only has login throttling (10 attempts/min)
- No general API rate limiting per user

**Plan:**
- v1.1: Add per-user API rate limits (100 requests/min) if needed
- Rely on Cloudflare WAF for now

---

## Security Considerations

### SEC1: Database Not Encrypted at Rest

**Priority:** Medium  
**Affects:** Data Security  
**Description:**
- PostgreSQL database is not encrypted at rest in v1
- Relies on OS-level encryption (if configured)

**Mitigation:**
- Ensure Raspberry Pi OS has full-disk encryption enabled
- OR: Encrypt PostgreSQL data directory with LUKS

**Plan:**
- v2: Implement PostgreSQL Transparent Data Encryption (TDE) or similar

---

### SEC2: No CAPTCHA on Login

**Priority:** Low  
**Affects:** Brute Force Protection  
**Description:**
- No CAPTCHA to prevent automated login attempts
- Relies on throttling + geo-blocking

**Mitigation:**
- Login throttling (10 attempts/min)
- Cloudflare WAF blocks automated attacks
- Geo-blocking (Oceania/Australia only)

**Plan:**
- Monitor for brute force attempts
- Add CAPTCHA in v1.1 if needed

---

### SEC3: No 2FA Backup Codes

**Priority:** Low  
**Affects:** Account Recovery  
**Description:**
- No backup codes for MFA
- If user loses authenticator app, admin must reset MFA

**Mitigation:**
- Admin can reset MFA via admin panel
- Household environment (admin accessible)

**Plan:**
- v1.1: Generate backup codes during MFA setup

---

## Performance Considerations

### PERF1: No Query Optimization in v1

**Priority:** Medium  
**Affects:** Dashboard, Search  
**Description:**
- v1 uses basic queries without optimization
- No EXPLAIN ANALYZE review
- May slow down as data grows

**Mitigation:**
- Database indexes on commonly queried columns
- Pagination for large datasets

**Plan:**
- Sprint 9: Performance testing and query optimization
- Add indexes as needed

---

### PERF2: No Caching

**Priority:** Low  
**Affects:** Performance  
**Description:**
- No Redis or caching layer
- Dashboard widgets query database on every load

**Mitigation:**
- Acceptable for 10 users
- PostgreSQL is fast enough for small datasets

**Plan:**
- v1.1: Add Redis caching for dashboard widgets (5-min TTL)

---

## Issue Workflow

**Reporting New Issues:**
1. Add to this document under appropriate section
2. Assign severity and status
3. Link to FUTURE_PLANS.md if future fix planned
4. Link to UI_ISSUES.md if UI-specific

**Resolving Issues:**
1. Update status to ✅ Resolved
2. Add resolution date and version
3. Move to "Resolved Issues" section
4. Update CHANGELOG.md

---

## Resolved Issues

_None yet - this is a new project_

---

**Last Updated:** 2025-02-01  
**Next Review:** After each sprint
