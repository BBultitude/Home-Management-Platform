# UI_ISSUES.md

## Overview

This document tracks UI/UX-specific issues, design inconsistencies, accessibility concerns, and frontend bugs.

**Issue Priority:**
- 🔴 Critical (unusable, blocks user flow)
- 🟡 High (significant UX impact)
- 🟢 Medium (minor annoyance)
- 🔵 Low (polish, nice-to-have)
- ✅ Resolved

---

## Critical UI Issues

_None currently identified_

---

## High Priority UI Issues

_None currently - UI-AUTH-0 has been resolved_

---

### UI-AUTH-1: No Admin User Management Interface

**Priority:** 🟡 High
**Category:** Admin Features
**Affects:** Admin users
**Reported:** 2026-02-14
**Planned Fix:** Sprint 13 (Admin Panel)

**Description:**
- Backend endpoints exist for user management (POST/GET/PUT/DELETE /api/admin/users)
- No UI for admins to:
  - View list of users
  - Create new users
  - Edit existing users (change role, deactivate)
  - Reset user MFA if locked out
- Admin must use API directly (via curl/Postman) to manage users

**Backend Status:** ✅ Complete (endpoints exist in auth.py)

**Plan:**
- Create admin-only route `/admin/users`
- User list table with search/filter
- Create user form (username, email, password, full_name, role)
- Edit user modal
- Delete/deactivate confirmation dialog
- MFA reset button with confirmation

---

### UI-AUTH-2: No MFA Setup Interface

**Priority:** 🟡 High
**Category:** Security
**Affects:** All users
**Reported:** 2026-02-14
**Planned Fix:** Sprint 13 (User Settings)

**Description:**
- Backend MFA endpoints exist (setup, enable, disable, verify)
- No UI for users to:
  - Enable MFA (view QR code, verify TOTP)
  - Disable MFA (requires password confirmation)
  - View/manage trusted devices
  - Revoke trusted devices
- Users cannot enable MFA without API access

**Backend Status:** ✅ Complete (MFA endpoints exist)

**Plan:**
- Add "Security" section to user settings page
- MFA setup flow:
  1. Click "Enable MFA"
  2. Display QR code (from POST /api/auth/mfa/setup)
  3. Input 6-digit code to verify
  4. Show backup codes (future)
- MFA disable flow (require password)
- Trusted devices list with revoke buttons

---

### UI-AUTH-3: No User Profile/Settings Page

**Priority:** 🟡 High
**Category:** User Management
**Affects:** All users
**Reported:** 2026-02-14
**Planned Fix:** Sprint 13 (User Settings)

**Description:**
- Backend password change endpoint exists (POST /api/auth/change-password)
- No UI for users to:
  - Change their own password
  - View their profile information
  - Update email or full name (if allowed)
  - See account settings
- Current dashboard shows user info but no edit capability

**Backend Status:** ✅ Password change complete, profile edit may need endpoint

**Plan:**
- Create `/settings` or `/profile` route
- User profile form:
  - View username (read-only)
  - View/edit email
  - View/edit full name
  - View role (read-only)
- Change password form (current password + new password × 2)
- Link from dashboard header (user menu)

---

_Additional UI issues to be populated during development and user testing_

---

## Medium Priority UI Issues

_To be populated during development and user testing_

---

## Low Priority UI Issues

_To be populated during development and user testing_

---

## Accessibility Issues

### A11Y-1: WCAG 2.1 Compliance Not Yet Verified

**Priority:** 🟡 High  
**Category:** Accessibility  
**Affects:** All pages  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 9 (Testing)

**Description:**
- WCAG 2.1 Level AA compliance not yet verified
- Need to audit:
  - Color contrast ratios
  - Keyboard navigation
  - Screen reader compatibility
  - Focus indicators
  - ARIA labels

**Plan:**
- Sprint 9: Run accessibility audit tools (axe, Lighthouse)
- Fix any violations before v1.0 release

---

### A11Y-2: No Skip to Main Content Link

**Priority:** 🟢 Medium  
**Category:** Accessibility  
**Affects:** All pages  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 7 (Dashboard)

**Description:**
- No "Skip to main content" link for keyboard/screen reader users
- Users must tab through entire navigation to reach content

**Plan:**
- Add skip link in global layout component
- Ensure focus moves to main content when activated

---

## Mobile Responsiveness Issues

### MOB-1: Dashboard Layout Not Yet Optimized for Mobile

**Priority:** 🟡 High  
**Category:** Mobile Responsiveness  
**Affects:** Dashboard  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 7 (Dashboard)

**Description:**
- Dashboard widget layout TBD
- Need to ensure:
  - Widgets stack vertically on mobile
  - Touch targets are 44x44px minimum
  - Graphs are legible on small screens
  - Quick-action buttons are accessible

**Plan:**
- Sprint 7: Implement mobile-first responsive design
- Test on multiple screen sizes (iPhone, Android, tablet)

---

### MOB-2: Tables May Be Difficult to Use on Mobile

**Priority:** 🟢 Medium  
**Category:** Mobile Responsiveness  
**Affects:** Budget, Projects, Quotes, Knowledge Base  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 7+

**Description:**
- Wide tables (e.g., Budget transfer schedule, Quote comparison) may not fit on mobile
- Need responsive table strategy:
  - Horizontal scrolling
  - Card view on mobile
  - OR collapsible columns

**Plan:**
- Implement card view alternative for mobile
- Allow users to toggle between table and card view

---

## Form Validation Issues

### FORM-1: Client-Side Validation Not Yet Implemented

**Priority:** 🟡 High  
**Category:** Form Validation  
**Affects:** All forms  
**Reported:** 2025-02-01  
**Planned Fix:** During module implementation

**Description:**
- Client-side validation needed for better UX
- Backend validation exists (Pydantic), but client should validate before submission
- Need to show inline errors

**Plan:**
- Use React Hook Form + Zod for client-side validation
- Display errors inline (red text below field)
- Disable submit button until form is valid

---

### FORM-2: No Autosave for Long Forms

**Priority:** 🔵 Low  
**Category:** Form UX  
**Affects:** Knowledge Base, Project forms  
**Reported:** 2025-02-01  
**Planned Fix:** v1.2

**Description:**
- No autosave for long forms (e.g., Knowledge article creation)
- User may lose work if browser crashes or navigates away

**Plan:**
- v1.2: Implement autosave to localStorage
- Warn user before navigating away from unsaved form

---

## Data Visualization Issues

### VIZ-1: Graph Colors Not Yet Defined

**Priority:** 🟢 Medium  
**Category:** Data Visualization  
**Affects:** Utility Graphs, Dashboard  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 3 (Financial Module)

**Description:**
- Need to define consistent color palette for graphs
- Ensure colors are:
  - Colorblind-friendly
  - High contrast
  - Consistent across modules

**Plan:**
- Define color palette in Tailwind config
- Use palette for all graphs (Recharts)

---

### VIZ-2: No Empty State Graphics for Graphs

**Priority:** 🔵 Low  
**Category:** Data Visualization  
**Affects:** Utility Graphs, Dashboard  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 7 (Dashboard)

**Description:**
- When no data exists, graphs show empty chart
- Need helpful empty state:
  - "No data yet. Add your first utility entry to see trends."
  - Link to add entry

**Plan:**
- Create empty state component for graphs
- Include helpful message and action button

---

## Navigation Issues

### NAV-1: Navigation Structure Not Yet Finalized

**Priority:** 🟡 High  
**Category:** Navigation  
**Affects:** All pages  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 7 (Dashboard)

**Description:**
- Top-level navigation structure TBD
- Need to decide:
  - Sidebar vs top nav
  - Module organization
  - Mobile menu (hamburger vs bottom tabs)

**Plan:**
- Sprint 7: Implement sidebar navigation (desktop) + hamburger menu (mobile)
- Group modules logically:
  - Dashboard
  - Financial
  - Assets
  - Projects
  - Knowledge
  - Tax (My Records)
  - Admin (if admin)

---

### NAV-2: No Breadcrumbs for Deep Navigation

**Priority:** 🔵 Low  
**Category:** Navigation  
**Affects:** Detail pages  
**Reported:** 2025-02-01  
**Planned Fix:** v1.1

**Description:**
- No breadcrumbs for nested pages (e.g., Project → Quote Detail)
- Users may not know where they are in hierarchy

**Plan:**
- v1.1: Add breadcrumb component for detail pages

---

## Loading & Performance Issues

### LOAD-1: No Loading Indicators

**Priority:** 🟡 High  
**Category:** Loading States  
**Affects:** All async operations  
**Reported:** 2025-02-01  
**Planned Fix:** During module implementation

**Description:**
- Need loading states for:
  - Page loads
  - Form submissions
  - API calls
  - File uploads

**Plan:**
- Implement loading spinner component
- Show inline loading for buttons ("Saving...")
- Show page-level skeleton loaders for initial loads

---

### LOAD-2: No Progress Indicator for File Uploads

**Priority:** 🟢 Medium  
**Category:** Loading States  
**Affects:** File upload  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 1 (Platform Services)

**Description:**
- File upload should show progress bar
- Especially for larger PDFs (up to 10MB)

**Plan:**
- Implement progress bar for file uploads
- Show percentage and file size

---

## Error Handling Issues

### ERR-1: No User-Friendly Error Messages

**Priority:** 🟡 High  
**Category:** Error Handling  
**Affects:** All forms and API calls  
**Reported:** 2025-02-01  
**Planned Fix:** During module implementation

**Description:**
- Backend errors may not be user-friendly
- Need to translate technical errors to plain language
- Example: "400 Bad Request" → "Please check your input and try again"

**Plan:**
- Create error message mapping
- Show friendly errors in UI
- Log technical details for debugging

---

### ERR-2: No Retry Mechanism for Failed Requests

**Priority:** 🔵 Low  
**Category:** Error Handling  
**Affects:** All API calls  
**Reported:** 2025-02-01  
**Planned Fix:** v1.1

**Description:**
- If API request fails (network issue), user must retry manually
- No automatic retry

**Plan:**
- v1.1: Implement retry logic with exponential backoff (using TanStack Query)

---

## Component-Specific Issues

### COMP-1: Date Picker Not Yet Selected

**Priority:** 🟡 High  
**Category:** Component Selection  
**Affects:** All date inputs  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 2 (Tax Module)

**Description:**
- Need to choose date picker component
- Options: shadcn/ui date picker, react-datepicker, native input

**Plan:**
- Sprint 2: Select and implement date picker
- Ensure mobile-friendly (native keyboard on mobile)

---

### COMP-2: File Viewer Not Yet Implemented

**Priority:** 🟢 Medium  
**Category:** Component Implementation  
**Affects:** Insurance, Documents, Projects  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 4 (Assets Module)

**Description:**
- Need in-app PDF viewer
- OR link to download/open in browser

**Plan:**
- Sprint 4: Implement PDF viewer (react-pdf or browser native)
- Allow download as fallback

---

## Design Consistency Issues

### DES-1: Design System Not Yet Defined

**Priority:** 🟡 High  
**Category:** Design System  
**Affects:** All components  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 1 (Platform Services)

**Description:**
- Need to define:
  - Color palette
  - Typography scale
  - Spacing system
  - Component patterns
  - Button styles
  - Form styles

**Plan:**
- Sprint 1: Configure Tailwind with custom theme
- Use shadcn/ui for consistent component library

---

### DES-2: No Icon Library Selected

**Priority:** 🟢 Medium  
**Category:** Design System  
**Affects:** All icons  
**Reported:** 2025-02-01  
**Planned Fix:** Sprint 1 (Platform Services)

**Description:**
- Need to choose icon library
- Options: Heroicons, Lucide, Feather Icons

**Plan:**
- Sprint 1: Select icon library (recommend Lucide for shadcn/ui compatibility)

---

## Future UX Enhancements

### UX-1: No Drag-and-Drop for File Upload

**Priority:** 🔵 Low  
**Category:** UX Enhancement  
**Affects:** File upload  
**Reported:** 2025-02-01  
**Planned Fix:** v1.2

**Description:**
- File upload requires clicking "Choose file" button
- Drag-and-drop is more intuitive

**Plan:**
- v1.2: Add drag-and-drop zone for file uploads

---

### UX-2: No Keyboard Shortcuts

**Priority:** 🔵 Low  
**Category:** UX Enhancement  
**Affects:** All pages  
**Reported:** 2025-02-01  
**Planned Fix:** v2.0

**Description:**
- No keyboard shortcuts for common actions
- Example: "Ctrl+K" for search, "N" for new entry

**Plan:**
- v2.0: Implement keyboard shortcut system

---

### UX-3: No Confirmation Dialogs for Delete Actions

**Priority:** 🟡 High  
**Category:** UX Safety  
**Affects:** All delete actions  
**Reported:** 2025-02-01  
**Planned Fix:** During module implementation

**Description:**
- Need confirmation dialogs before deleting data
- Especially for tax records (5-year retention)

**Plan:**
- Implement confirmation modal component
- Use for all delete actions
- Show warning for tax record deletions ("This will be retained for 5 years per ATO requirements")

---

## Testing & QA Notes

**UI Testing Checklist (Sprint 9):**
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on multiple devices (desktop, tablet, mobile)
- [ ] Test keyboard navigation (all forms, all pages)
- [ ] Test screen reader compatibility (NVDA, VoiceOver)
- [ ] Test color contrast (WCAG AA)
- [ ] Test touch targets (44x44px minimum)
- [ ] Test form validation (client-side + server-side)
- [ ] Test loading states (slow network simulation)
- [ ] Test error states (network errors, validation errors)
- [ ] Test empty states (no data scenarios)

---

## Issue Workflow

**Reporting New UI Issues:**
1. Add to appropriate section based on priority
2. Include:
   - Description
   - Affected components/pages
   - Planned fix (sprint or version)
3. Link to KNOWN_ISSUES.md if related to backend

**Resolving UI Issues:**
1. Update status to ✅ Resolved
2. Add resolution date and sprint
3. Move to "Resolved UI Issues" section
4. Update CHANGELOG.md

---

## Resolved UI Issues

### ✅ UI-AUTH-0: Login Error Not Displayed on Failed Authentication

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** Authentication / Error Handling
**Affects:** Login page

**Issue:**
When entering incorrect credentials, the login page would redirect/refresh without showing an error message to the user.

**Root Cause:**
Axios response interceptor was catching ALL 401 errors (including failed login attempts) and executing `window.location.href = '/'`, causing a full page reload that cleared the error state before it could be displayed.

**Solution:**
1. Updated Axios interceptor to exclude `/auth/login` endpoint from automatic 401 redirects
2. Enhanced Alert component destructive variant styling (prominent red background)
3. Fixed authStore to explicitly manage `isAuthenticated` state on login success/failure
4. Added `onRehydrateStorage` to correctly set `isAuthenticated` when hydrating from localStorage

**Files Modified:**
- `frontend/src/lib/api.ts` - Fixed 401 interceptor to exclude login endpoint
- `frontend/src/stores/authStore.ts` - Explicit `isAuthenticated` management
- `frontend/src/components/ui/alert.tsx` - Enhanced destructive variant styling
- `frontend/src/pages/Login.tsx` - Already had proper error handling, no changes needed

**Result:**
- ✅ Failed login displays prominent red error message
- ✅ Error persists without flickering or navigation
- ✅ Successful login redirects to dashboard correctly
- ✅ Logout clears session properly (both frontend and backend)

---

**Last Updated:** 2026-02-14
**Next Review:** After Sprint 13 (Admin & User Management UI), then Sprint 9 (Testing)
