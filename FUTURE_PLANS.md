# FUTURE_PLANS.md

## Overview

This document outlines planned features, enhancements, and long-term vision for the Home Management Platform beyond v1.0.

**Timeframe Categories:**
- **v1.1 (3-6 months post-v1.0):** High-priority improvements
- **v1.2 (6-9 months post-v1.0):** Medium-priority enhancements
- **v2.0 (9-18 months post-v1.0):** Major features and redesigns
- **Long-term (18+ months):** Strategic opportunities

**Priority Levels:**
- 🔴 High - Critical for usability or compliance
- 🟡 Medium - Significant value, nice to have
- 🟢 Low - Polish, convenience

---

## v1.1 - Essential Improvements (3-6 Months Post-v1.0)

### 1. Budget Year Configurability

**Priority:** 🟡 Medium  
**Category:** Financial Management  
**Effort:** 1 week

**Description:**
- Allow users to configure budget year type:
  - Calendar year (Jan-Dec) - v1 default
  - Financial year (July-June) - Australian FY
- Global setting (applies to all users)
- Affects budget planning, projections, and reporting
- Tax module continues to use FY (not configurable)

**Why:**
- Some households prefer budgeting by financial year
- Aligns with how some people plan their finances
- User requested feature

**Implementation:**
- Add `budget_year_type` setting to system configuration
- Enum: `CALENDAR_YEAR`, `FINANCIAL_YEAR`
- Update budget calculations to respect setting
- Update date pickers and period selectors
- Migration: Default to `CALENDAR_YEAR` for existing users

**Tasks:**
- [ ] Add budget_year_type to SystemSettings model
- [ ] Update budget calculation logic
- [ ] Update UI date ranges
- [ ] Add admin setting toggle
- [ ] Test both modes thoroughly
- [ ] Document in user guide

---

### 2. System Monitoring and Alerting

**Priority:** 🔴 High  
**Category:** Operations  
**Effort:** 1-2 weeks

**Description:**
- Monitor critical system metrics:
  - Disk space (alert at 80% full)
  - Docker container health
  - Database connection pool
  - Memory/CPU usage
- In-app alerts for critical events
- Optional email alerts (if SMTP configured)

**Why:**
- Prevent disk space exhaustion (breaks database)
- Early warning for system issues
- Improve reliability

**Implementation:**
- Simple monitoring script (Python)
- Check metrics every 15 minutes (cron)
- Create in-app notifications for issues
- Optional: Send email alerts (if SMTP configured)

**Tasks:**
- [ ] Write monitoring script
- [ ] Configure cron job
- [ ] Integrate with notifications system
- [ ] Add admin dashboard widget for system health

---

### 3. Password Recovery

**Priority:** 🟡 Medium  
**Category:** User Management  
**Effort:** 1 week

**Description:**
- Email-based password reset (if SMTP configured)
- OR admin-assisted reset (fallback)
- Reset token expires after 1 hour
- User must set new password

**Why:**
- Reduces admin overhead
- Improves UX (users can self-serve)

**Implementation:**
- Option 1: Email-based (requires SMTP)
  - User requests reset → Email sent with token link
  - User clicks link → Sets new password
- Option 2: Admin-assisted (no SMTP required)
  - User contacts admin → Admin generates reset link
  - Admin provides link to user (via secure channel)

**Decision:** Start with admin-assisted, add email-based later if SMTP configured

**Tasks:**
- [ ] Implement password reset token generation
- [ ] Add reset UI (set new password)
- [ ] Admin panel: Generate reset link for user
- [ ] (Optional) Email-based reset flow

---

### 5. Performance Optimizations

**Priority:** 🟡 Medium  
**Category:** Performance  
**Effort:** 1-2 weeks

**Description:**
- Database query optimization (EXPLAIN ANALYZE review)
- Add indexes for frequently queried columns
- Implement Redis caching for dashboard widgets
- Optimize large list views (pagination, virtual scrolling)

**Why:**
- Improve page load times (especially dashboard)
- Better experience as data grows
- Ensure Pi can handle 10 concurrent users

**Implementation:**
- Run EXPLAIN ANALYZE on slow queries
- Add indexes (user_id, date, timestamps, foreign keys)
- Redis cache with 5-minute TTL for dashboard data
- Lazy loading for large lists

**Tasks:**
- [ ] Performance audit (identify slow queries)
- [ ] Add database indexes
- [ ] Set up Redis container
- [ ] Implement caching for dashboard widgets
- [ ] Test with realistic data volume (1000+ records)

---

### 6. MFA Backup Codes

**Priority:** 🟢 Low  
**Category:** User Management / UX  
**Effort:** 3 days

**Description:**
- Generate 10 backup codes during MFA setup
- User can download/print codes
- Each code can be used once
- Admin can regenerate codes if lost

**Why:**
- Prevent lockout if user loses authenticator app
- Reduce admin overhead for MFA resets

**Implementation:**
- Generate 10 random codes (cryptographically secure)
- Store hashed codes in database
- Provide download as text file
- Verify code during login (if MFA code fails)
- Mark code as used after successful login

**Tasks:**
- [ ] Generate backup codes during MFA setup
- [ ] Store hashed codes in database
- [ ] Add backup code verification to login flow
- [ ] UI to download/print backup codes
- [ ] Admin panel: Regenerate backup codes

---

## v1.2 - UX Enhancements (6-9 Months Post-v1.0)

### 1. Email Notifications (SMTP Integration)

**Priority:** 🟡 Medium  
**Category:** Notifications  
**Effort:** 1 week

**Description:**
- SMTP integration for email notifications
- Email alerts for:
  - Insurance renewals (30 days, 7 days before)
  - Quote expiry
  - Backup failures
  - System issues (disk space, errors)
- User-configurable notification preferences

**Why:**
- Proactive alerts (users don't need to check dashboard)
- Critical for renewals and backup failures

**Implementation:**
- Configure SMTP (Gmail, Outlook, or custom server)
- Email templates (HTML + plain text)
- User preferences: Enable/disable per notification type
- Queue emails (Celery + Redis for background processing)

**Tasks:**
- [ ] SMTP configuration (environment variables)
- [ ] Email templates (HTML + plain text)
- [ ] Notification preferences UI
- [ ] Background email queue (Celery)
- [ ] Test with multiple email providers

---

### 2. PWA Support (Offline Capability, Installable)

**Priority:** 🟡 Medium  
**Category:** Mobile / UX  
**Effort:** 2 weeks

**Description:**
- Progressive Web App (PWA) with service worker
- Installable on mobile (Add to Home Screen)
- Limited offline capability:
  - View cached data (dashboard, tax summary)
  - Queue actions for sync when online
- Push notifications (optional, future)

**Why:**
- Better mobile experience (feels like native app)
- Offline access to critical data
- No app store required

**Implementation:**
- Workbox for service worker
- Cache dashboard data, static assets
- Offline fallback page
- Sync queued actions when online (background sync)
- Manifest file for installability

**Tasks:**
- [ ] Configure service worker (Workbox)
- [ ] Define caching strategy (dashboard, static assets)
- [ ] Implement offline fallback
- [ ] Add manifest file
- [ ] Test on iOS and Android
- [ ] (Optional) Push notifications

---

### 3. Dark Mode

**Priority:** 🟢 Low  
**Category:** Accessibility / UX  
**Effort:** 3 days

**Description:**
- Dark mode toggle
- Respect system preference (prefers-color-scheme)
- Persist user preference (localStorage)
- WCAG AA contrast in both modes

**Why:**
- Accessibility (reduces eye strain)
- Popular user preference
- Better for nighttime use

**Implementation:**
- Tailwind CSS dark mode (class-based)
- Toggle in settings or navbar
- Save preference to localStorage
- Detect system preference on first visit

**Tasks:**
- [ ] Configure Tailwind dark mode
- [ ] Design dark color palette
- [ ] Add toggle UI
- [ ] Persist preference
- [ ] Test WCAG contrast

---

### 4. Bulk Operations

**Priority:** 🟢 Low  
**Category:** UX  
**Effort:** 1 week

**Description:**
- Bulk select items (checkbox list)
- Bulk actions:
  - Delete (with confirmation)
  - Export to CSV
  - Tag (for Knowledge Base)
  - Mark as read (for notifications)

**Why:**
- Time-saving for large datasets
- Better UX when cleaning up old data

**Implementation:**
- Checkbox in list views
- Select all / Select none
- Bulk action dropdown
- Confirmation dialog for destructive actions

**Tasks:**
- [ ] Add bulk select UI (checkboxes)
- [ ] Implement bulk delete (with confirmation)
- [ ] Implement bulk export (CSV)
- [ ] Implement bulk tagging (Knowledge Base)
- [ ] Test with large datasets

---

### 5. Drag-and-Drop File Upload

**Priority:** 🟢 Low  
**Category:** UX  
**Effort:** 2 days

**Description:**
- Drag-and-drop zone for file uploads
- Visual feedback (highlight on drag over)
- Multiple file upload support

**Why:**
- More intuitive than clicking "Choose file"
- Faster for uploading multiple files

**Implementation:**
- React Dropzone or custom implementation
- Visual feedback (border highlight, cursor change)
- Support multiple files at once

**Tasks:**
- [ ] Implement drag-and-drop component
- [ ] Add visual feedback
- [ ] Test on desktop and mobile (mobile uses native file picker)

---

### 6. Breadcrumb Navigation

**Priority:** 🟢 Low  
**Category:** Navigation  
**Effort:** 2 days

**Description:**
- Breadcrumbs for nested pages
- Example: Dashboard > Projects > Project Detail > Quote Detail
- Clickable links to parent pages

**Why:**
- Helps users understand their location in hierarchy
- Quick navigation to parent pages

**Implementation:**
- Breadcrumb component (React Router)
- Auto-generate from route structure
- Show on detail pages and nested views

**Tasks:**
- [ ] Create breadcrumb component
- [ ] Integrate with React Router
- [ ] Add to detail pages

---

## v2.0 - Major Features (9-18 Months Post-v1.0)

**Note:** Meal Planner and Cost-Benefit Decision Tracker modules are now part of v1.0 (originally planned for v2.0).

### 1. Receipt Scanning (OCR for Tax Receipts)

**Priority:** 🟡 Medium  
**Category:** Tax Module Enhancement  
**Effort:** 2-3 weeks

**Description:**
- Upload receipt photo (mobile or desktop)
- OCR to extract:
  - Date
  - Merchant
  - Amount
  - Category (suggested)
- Auto-populate tax entry
- Store receipt image as attachment

**Why:**
- Faster data entry (no manual typing)
- Better record keeping (receipt image attached)
- Mobile-friendly workflow

**Implementation:**
- OCR library: Tesseract or Google Vision API
- Pre-processing: Image enhancement (contrast, rotation correction)
- Field extraction: Date, merchant, amount regex
- UI: Upload → Preview extracted data → Confirm/edit → Save

**Tasks:**
- [ ] Integrate OCR library (Tesseract or Vision API)
- [ ] Implement image pre-processing
- [ ] Implement field extraction
- [ ] Add receipt upload UI
- [ ] Test with variety of receipts (stores, restaurants, gas)

---

### 4. Calendar Integration (Google Calendar)

**Priority:** 🟢 Low  
**Category:** Integration  
**Effort:** 2 weeks

**Description:**
- Sync insurance renewals to Google Calendar
- Sync vehicle registration to Google Calendar
- Sync project milestones to Google Calendar
- Two-way sync (optional, future)

**Why:**
- Users already use calendars
- Proactive reminders via calendar notifications

**Implementation:**
- Google Calendar API
- OAuth 2.0 authentication
- Create events for renewals (30 days before)
- Optional: Update events if renewal date changes

**Tasks:**
- [ ] Set up Google Calendar API
- [ ] Implement OAuth flow
- [ ] Sync renewals to calendar
- [ ] Sync vehicle registrations to calendar
- [ ] (Optional) Two-way sync

---

### 5. Investment Tracking

**Priority:** 🟢 Low  
**Category:** New Module  
**Effort:** 3-4 weeks

**Description:**
- Track investment portfolio (stocks, bonds, ETFs)
- Track contributions and withdrawals
- Track performance (gains/losses)
- Basic graphs (portfolio value over time)
- Integration with tax module (capital gains)

**Why:**
- Natural extension of financial management
- Helps with tax reporting (capital gains)

**Features:**
- Manual entry of holdings (ticker, quantity, purchase price)
- Track dividends and distributions
- Performance graphs (portfolio value, gains/losses)
- Export to CSV for tax lodgement

**Tasks:**
- [ ] Design database schema (investments, transactions)
- [ ] Implement investment CRUD
- [ ] Implement performance calculations
- [ ] Implement graphs (portfolio value, asset allocation)
- [ ] Integrate with tax module (capital gains tracking)

---

### 6. Multi-Property Support

**Priority:** 🟢 Low  
**Category:** Architecture Enhancement  
**Effort:** 4-5 weeks (significant)

**Description:**
- Support multiple properties (main home, rental, vacation)
- Property selector (dropdown or tabs)
- Separate budgets, insurance, projects per property
- Consolidated view (all properties)

**Why:**
- Users with multiple properties need separate tracking
- Rental property requires separate financials

**Implementation:**
- Add `property_id` to all relevant tables
- Property selector in UI
- Filter data by selected property
- Consolidated dashboard (all properties)

**Tasks:**
- [ ] Design schema changes (add property_id)
- [ ] Implement property CRUD (create, edit, delete)
- [ ] Add property selector to UI
- [ ] Update all modules to filter by property
- [ ] Implement consolidated view
- [ ] Migrate existing data to "Main Home" property

---

### 7. PDF Content Search (Full-Text)

**Priority:** 🟢 Low  
**Category:** Search Enhancement  
**Effort:** 2 weeks

**Description:**
- Extract text from uploaded PDFs
- Index PDF contents for search
- Search inside PDFs (not just metadata)
- Highlight search results in PDF viewer

**Why:**
- Find information inside documents
- Better search experience

**Implementation:**
- PDF text extraction: PyPDF2, pdfplumber, or Tika
- Index in PostgreSQL (same search_vector as metadata)
- Search across metadata + PDF contents
- Highlight results in PDF viewer (react-pdf)

**Tasks:**
- [ ] Integrate PDF text extraction library
- [ ] Extract text on upload (background job)
- [ ] Index PDF contents (PostgreSQL FTS)
- [ ] Update search to include PDF contents
- [ ] Highlight search results in PDF viewer

---

### 8. Mobile Native Apps (iOS/Android)

**Priority:** 🟢 Low  
**Category:** Mobile  
**Effort:** 8-12 weeks (significant)

**Description:**
- Native iOS and Android apps
- Offline-first architecture
- Push notifications (renewals, alerts)
- Camera integration (receipt scanning)

**Why:**
- Better mobile experience than PWA
- Native features (camera, notifications)

**Implementation:**
- React Native or Flutter
- Shared codebase with web (where possible)
- Offline storage (SQLite or Realm)
- Sync to backend when online

**Tasks:**
- [ ] Choose framework (React Native vs Flutter)
- [ ] Set up project structure
- [ ] Implement core modules (tax, financial, dashboard)
- [ ] Implement offline storage and sync
- [ ] Implement camera integration
- [ ] Implement push notifications
- [ ] Test on iOS and Android devices
- [ ] Publish to App Store and Google Play

---

## Long-Term Ideas (18+ Months)

### 1. Microservices Architecture (If Needed)

**Priority:** 🟢 Low  
**Category:** Architecture  
**Effort:** Significant (months)

**Description:**
- Break monolith into microservices:
  - Auth service
  - Tax service
  - Financial service
  - Asset service
  - Knowledge service
- Internal APIs between services
- Easier to scale and maintain

**Why:**
- Better scalability (scale services independently)
- Easier to add new modules
- Better separation of concerns

**Trade-offs:**
- More complex deployment
- Higher overhead (network calls)
- Not needed for 10 users

**Decision:** Only if project grows beyond household scale

---

### 2. Advanced Monitoring (Prometheus + Grafana)

**Priority:** 🟢 Low  
**Category:** Operations  
**Effort:** 1-2 weeks

**Description:**
- Prometheus for metrics collection
- Grafana for visualization
- Metrics:
  - Request rate, error rate, latency
  - Database connections, query times
  - Memory, CPU usage
  - Custom business metrics (active users, tax entries per week)

**Why:**
- Better observability
- Identify performance bottlenecks
- Proactive issue detection

**Implementation:**
- Prometheus container
- Grafana container
- FastAPI metrics exporter
- Pre-built dashboards (Grafana)

---

### 3. Voice Assistant Integration (Alexa/Google Home)

**Priority:** 🟢 Low  
**Category:** Integration  
**Effort:** 2-3 weeks

**Description:**
- Voice commands for common tasks:
  - "Add 8 hours WFH today"
  - "What's my WFH total this year?"
  - "When does my car insurance renew?"
- Integration with Alexa Skills or Google Actions

**Why:**
- Convenient for hands-free data entry
- Natural language interaction

**Implementation:**
- Alexa Skill or Google Action
- API integration with backend
- Voice intent parsing
- Response formatting (natural language)

---

### 4. API for Third-Party Integrations

**Priority:** 🟢 Low  
**Category:** Integration  
**Effort:** 2 weeks

**Description:**
- Public API (OAuth 2.0)
- Allow third-party apps to integrate
- Use cases:
  - Home automation (Home Assistant integration)
  - Custom dashboards
  - Mobile apps by third parties

**Why:**
- Extend platform capabilities
- Community contributions

**Implementation:**
- OAuth 2.0 provider
- API documentation (OpenAPI)
- Rate limiting
- Webhooks (for real-time updates)

---

## Community Contributions (If Open Sourced)

If the project is open sourced in the future, consider:

**Good First Issues:**
- Dark mode
- Additional article types for Knowledge Base
- Additional graphs for utility tracking
- New export formats (Excel, JSON)

**Advanced Contributions:**
- OCR for receipts
- Calendar integrations
- Voice assistant skills
- Mobile apps

**Documentation Contributions:**
- User guides
- Video tutorials
- Deployment guides (different platforms)

---

## User Feedback Integration

As users interact with v1.0, collect feedback on:

**Feature Requests:**
- What features are most requested?
- What pain points exist?

**Usability Issues:**
- What workflows are confusing?
- What takes too long?

**Performance Issues:**
- What pages are slow?
- What queries need optimization?

**Prioritization:**
- Use feedback to inform v1.1, v1.2 priorities
- Defer nice-to-haves to long-term roadmap

---

## Technology Evolution

**Monitor and evaluate:**
- New frontend frameworks (Svelte 5, Next.js 15)
- New backend frameworks (Rust-based alternatives?)
- New database features (PostgreSQL 17+)
- New deployment platforms (Kubernetes, serverless)

**Decision criteria:**
- Does it solve a real problem?
- Is it stable and mature?
- Is the migration effort justified?

---

## Strategic Opportunities

**Potential future directions:**

1. **Multi-Tenant SaaS:**
   - Host for multiple households (paid service)
   - Subscription model
   - Managed backups, support

2. **Integration Marketplace:**
   - Third-party integrations (plugins)
   - Payment processing
   - Community ecosystem

3. **AI-Powered Features:**
   - Budget recommendations (ML-based)
   - Predictive renewals
   - Smart categorization (receipts, documents)
   - Natural language queries ("What did I spend on electricity last summer?")

---

**Last Updated:** 2025-02-01  
**Next Review:** After v1.0 release, then quarterly
