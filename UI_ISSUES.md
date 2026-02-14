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

_None currently - All auth UI tasks completed_

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

### ✅ UI-AUTH-1: Admin User Management Interface

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** Admin Features
**Affects:** Admin users

**Issue:**
No UI existed for admins to manage users (view, create, edit, delete). Admins had to use API directly.

**Solution:**
Created complete admin user management interface at `/admin/users` with:
- User list table showing all users with role, email, MFA status
- Create new user form with validation (username, email, password, full_name, role)
- Edit user functionality (update role, email, full name)
- Delete user with confirmation dialog
- MFA reset capability for locked-out users
- Proper error handling for Pydantic validation errors
- Admin-only access control

**Files Created:**
- `frontend/src/pages/AdminUsers.tsx` - Complete admin user management UI
- Added route in `frontend/src/App.tsx` for `/admin/users`
- Added "Admin Panel" button in Dashboard header for admin users

**Result:**
- ✅ Admins can view all users
- ✅ Create new users with proper validation
- ✅ Edit user roles and information
- ✅ Delete users (with retention warnings)
- ✅ Reset MFA for locked-out users
- ✅ Proper error display for validation failures

---

### ✅ UI-AUTH-2: MFA Setup Interface

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** Security / MFA
**Affects:** All users

**Issue:**
No UI for users to enable/disable MFA or verify TOTP codes during login. Backend endpoints existed but were inaccessible to regular users.

**Solution:**
Implemented complete MFA workflow:

**MFA Setup (Settings Page):**
1. "Enable MFA" button in security section
2. QR code generation and display
3. 6-digit verification code input
4. MFA enable/disable toggle with confirmation
5. Visual MFA status indicator

**MFA Login Verification:**
1. Created `/mfa` route with MFAVerify page
2. 6-digit code input with auto-formatting
3. Bearer token authentication flow
4. Trusted device checkbox (disabled - backend TODO documented in KNOWN_ISSUES.md)
5. Proper error handling and user feedback

**Files Created/Modified:**
- `frontend/src/pages/Settings.tsx` - Added MFA setup UI
- `frontend/src/pages/MFAVerify.tsx` - MFA login verification page
- `frontend/src/stores/authStore.ts` - Added mfaToken handling
- `KNOWN_ISSUES.md` - Documented MFA-001: Trusted device feature not implemented

**Result:**
- ✅ Users can enable MFA from settings
- ✅ QR code displays for authenticator app setup
- ✅ MFA verification required on login
- ✅ Proper error messages for invalid codes
- ✅ MFA status visible in user profile
- ✅ Graceful handling of missing backend feature (trusted devices)

---

### ✅ UI-AUTH-3: User Profile/Settings Page

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** User Management
**Affects:** All users

**Issue:**
No UI for users to view their profile or change their password. Dashboard showed user info but was read-only.

**Solution:**
Created comprehensive Settings page at `/settings` with:

**User Profile Section:**
- Display username (read-only)
- Display email
- Display full name
- Display role
- Display MFA status

**Password Change Section:**
- Current password input
- New password input with NIST validation (12-128 chars, complexity requirements)
- Confirm password input
- Real-time validation matching backend requirements:
  - Length 12-128 characters
  - Upper/lowercase/digit requirements
  - No weak patterns (password123, admin2024, etc.)
  - No sequential patterns (12345, qwerty)
  - No repeated characters (aaaa, 1111)
- Proper error display for Pydantic validation
- Auto-logout after successful password change

**Security Section:**
- MFA setup and management (see UI-AUTH-2)

**Files Created:**
- `frontend/src/pages/Settings.tsx` - Complete user settings page
- Added route in `frontend/src/App.tsx` for `/settings`
- Added "Settings" button in Dashboard header

**Result:**
- ✅ Users can view their profile information
- ✅ Change password with NIST-compliant validation
- ✅ Enable/disable MFA
- ✅ Clear error messages for validation failures
- ✅ Secure flow (logout after password change)

---

### ✅ UI-TAX-1: Tax Module Modal Dialog Transparency Issue

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** UI Components / Dialogs
**Affects:** Tax module (WFH and Travel entry modals)

**Issue:**
When adding an entry in the Tax module, the modal dialog appeared as just outlines with a transparent/grey background. The modal content was hard to read because it lacked a solid white background, and the background page text was visible through the modal.

**Root Cause:**
The DialogContent component in `dialog.tsx` had `bg-white` in the className, but it wasn't being applied consistently or was being overridden. The component needed more explicit background styling to ensure it displays as a solid white modal.

**Solution:**
Updated the DialogContent component to include:
- `bg-white dark:bg-white` for explicit white background in both light and dark modes
- `border-border` for consistent border styling
- Ensures modal has solid white background with properly greyed overlay

**Files Modified:**
- `frontend/src/components/ui/dialog.tsx` - Enhanced background styling for DialogContent

**Result:**
- ✅ Modal dialogs now display with solid white background
- ✅ Grey overlay properly dims background content
- ✅ Modal content is clearly readable
- ✅ Consistent styling across all dialog instances

---

### ✅ UI-TAX-2: Tax Summary API 422 Error - Invalid Parameters

**Status:** Resolved
**Resolved Date:** 2026-02-14
**Category:** API Integration / Tax Module
**Affects:** Tax module Summary tab

**Issue:**
When navigating to the Tax Summary tab, toast error appeared: "entry_id: Input should be a valid integer, unable to parse string as an integer" with console errors showing 422 (Unprocessable Entity) for:
- `/api/v1/tax/wfh/summary?financial_year=2025`
- `/api/v1/tax/travel/summary?financial_year=2025`

**Root Cause:**
Mismatch between frontend and backend API parameter types:
- **Backend endpoints** expect: `/summary/fy/{fy_year}` - with `fy_year` as a PATH parameter
- **Frontend was sending**: `/summary?financial_year=2025` - as a QUERY parameter
- Backend received unexpected query parameter and failed validation

**Solution:**
Updated taxService.ts to match backend API endpoint structure:
1. **WFH Summary**: Changed from `/tax/wfh/summary?financial_year=X` to `/tax/wfh/summary/fy/{year}`
2. **WFH Export**: Changed from `/tax/wfh/export?financial_year=X` to `/tax/wfh/export/fy/{year}/csv`
3. **Travel Summary**: Changed from `/tax/travel/summary?financial_year=X` to `/tax/travel/summary/fy/{year}`
4. **Travel Export**: Changed from `/tax/travel/export?financial_year=X` to `/tax/travel/export/fy/{year}/csv`

**Files Modified:**
- `frontend/src/services/taxService.ts` - Fixed API endpoints for summary and export calls

**Result:**
- ✅ Summary tab loads without errors
- ✅ WFH and Travel summaries display correctly
- ✅ Export functionality works for both WFH and Travel
- ✅ Proper API parameter handling matching backend expectations

---

**Last Updated:** 2026-02-14
**Next Review:** After Sprint 16 (Financial Management UI), then Sprint 9 (Testing)
