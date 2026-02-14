# Frontend Development Sprint Plan

**Status:** Planning Complete - Ready for Sprint 13
**Date:** 2026-02-14
**Backend Status:** ✅ 151 endpoints complete across all modules

---

## Sprint Status Overview

| Sprint | Name | Status | Priority | Estimated Tasks |
|--------|------|--------|----------|-----------------|
| Sprint 12 | Frontend Foundation | ✅ Complete | - | 8 tasks |
| Sprint 13 | Core UI Infrastructure | 🎯 Current | High | 12 tasks |
| Sprint 14 | Dashboard & Widgets | ⏳ Planned | High | 10 tasks |
| Sprint 15 | Tax Management UI | ⏳ Planned | High | 8 tasks |
| Sprint 16 | Financial Management UI | ⏳ Planned | High | 12 tasks |
| Sprint 17 | Assets & Documents UI | ⏳ Planned | Medium | 10 tasks |
| Sprint 18 | Projects & Tasks UI | ⏳ Planned | Medium | 10 tasks |
| Sprint 19 | Knowledge Base UI | ⏳ Planned | Medium | 8 tasks |
| Sprint 20 | Meal Planner UI | ⏳ Planned | Low | 8 tasks |
| Sprint 21 | Polish & Testing | ⏳ Planned | High | 15 tasks |

---

## Sprint 12: Frontend Foundation ✅ COMPLETE

**Duration:** Initial setup
**Completed:** 2026-02-13

### Completed Tasks
- [x] React + TypeScript + Vite setup
- [x] Tailwind CSS configuration
- [x] shadcn/ui component library setup
- [x] Authentication pages (Login, MFA Verify)
- [x] Settings page (password change, MFA setup)
- [x] Admin user management page
- [x] Auth store with Zustand
- [x] API client with Axios
- [x] Protected routes
- [x] HTTP-only cookie authentication

### Documentation
See: [SPRINT_12_SUMMARY.md](./SPRINT_12_SUMMARY.md)

---

## Sprint 13: Core UI Infrastructure 🎯 CURRENT

**Priority:** 🔴 Critical
**Duration:** ~2-3 days
**Blocked By:** None
**Blocks:** All module sprints

### Sprint Goal
Build the foundational UI infrastructure that all modules will depend on: navigation, layout, loading states, error handling, and form validation.

### Tasks

#### 1. Navigation & Layout (NAV-1 - High Priority)
- [ ] Create AppShell layout component with sidebar
- [ ] Implement sidebar navigation with module groups
- [ ] Add collapsible sidebar for desktop
- [ ] Build hamburger menu for mobile
- [ ] Create breadcrumb component
- [ ] Add active route highlighting
- [ ] Implement user menu dropdown in header

**Files to Create:**
- `src/components/layout/AppShell.tsx`
- `src/components/layout/Sidebar.tsx`
- `src/components/layout/Header.tsx`
- `src/components/layout/Breadcrumbs.tsx`

**Navigation Structure:**
```
📊 Dashboard
💰 Financial
   ├─ Income Sources
   ├─ Bank Accounts
   ├─ Expenses
   ├─ Utilities
   └─ Budget Calculator
📄 Tax Records
   ├─ Work From Home
   └─ Travel Claims
🏠 Assets
   ├─ Insurance Policies
   └─ Documents
🔨 Projects
   ├─ Priority Items
   ├─ Active Projects
   └─ Quotes
📚 Knowledge Base
🍽️ Meal Planner
   ├─ Recipes
   └─ Week Plans
⚙️ Settings
👤 Admin (if admin)
```

#### 2. Loading States (LOAD-1 - High Priority)
- [ ] Create Spinner component
- [ ] Create Skeleton loader components (card, table, list)
- [ ] Create page-level loading wrapper
- [ ] Add loading states to buttons
- [ ] Create progress bar component (for file uploads)

**Files to Create:**
- `src/components/ui/spinner.tsx`
- `src/components/ui/skeleton.tsx`
- `src/components/ui/progress.tsx`
- `src/components/common/PageLoader.tsx`

#### 3. Error Handling (ERR-1 - High Priority)
- [ ] Create error message mapping function
- [ ] Build ErrorBoundary component
- [ ] Create user-friendly error display component
- [ ] Add toast notification system (for success/error messages)
- [ ] Implement retry mechanism wrapper

**Files to Create:**
- `src/lib/errorMessages.ts`
- `src/components/common/ErrorBoundary.tsx`
- `src/components/ui/toast.tsx` (shadcn/ui)
- `src/components/ui/toaster.tsx`

#### 4. Form Validation (FORM-1 - High Priority)
- [ ] Set up React Hook Form defaults
- [ ] Create Zod validation schemas
- [ ] Build reusable form components (FormField, FormError, FormLabel)
- [ ] Add inline error display
- [ ] Create form submit handler wrapper

**Files to Create:**
- `src/lib/formSchemas.ts`
- `src/components/forms/FormField.tsx`
- `src/hooks/useForm.ts`

#### 5. Confirmation Dialogs (UX-3 - High Priority)
- [ ] Create confirmation dialog component
- [ ] Add delete confirmation dialog
- [ ] Add warning dialog (for tax record deletion with ATO notice)
- [ ] Create useConfirm hook

**Files to Create:**
- `src/components/ui/dialog.tsx` (shadcn/ui)
- `src/components/ui/alert-dialog.tsx` (shadcn/ui)
- `src/hooks/useConfirm.ts`

#### 6. Date Picker (COMP-1 - High Priority)
- [ ] Install and configure date picker (shadcn/ui date picker)
- [ ] Create date input wrapper component
- [ ] Add date range picker
- [ ] Financial year selector component

**Files to Create:**
- `src/components/ui/calendar.tsx` (shadcn/ui)
- `src/components/ui/popover.tsx` (shadcn/ui)
- `src/components/forms/DatePicker.tsx`
- `src/components/forms/FinancialYearPicker.tsx`

#### 7. Common Components
- [ ] Create EmptyState component
- [ ] Create DataTable component (reusable table with sorting, filtering)
- [ ] Create SearchInput component
- [ ] Create Tag/Badge component
- [ ] Create StatusBadge component

**Files to Create:**
- `src/components/common/EmptyState.tsx`
- `src/components/common/DataTable.tsx`
- `src/components/ui/input.tsx` (already exists, enhance)
- `src/components/ui/badge.tsx` (shadcn/ui)

### Acceptance Criteria
- [x] Navigation works on desktop and mobile
- [x] All routes show breadcrumbs
- [x] Loading states display during async operations
- [x] Error messages are user-friendly
- [x] Form validation shows inline errors
- [x] Delete actions require confirmation
- [x] Date picker works on mobile and desktop
- [x] Components are reusable across all modules

### Related Issues
- UI_ISSUES.md: NAV-1, LOAD-1, ERR-1, FORM-1, UX-3, COMP-1

---

## Sprint 14: Dashboard & Widgets

**Priority:** 🟡 High
**Duration:** ~2 days
**Blocked By:** Sprint 13 (navigation, loading states)
**Backend:** `/dashboard` endpoints (22 endpoints available)

### Sprint Goal
Transform the placeholder dashboard into a functional home page with real data widgets and quick actions.

### Tasks

#### 1. Dashboard Summary Widget
- [ ] Fetch dashboard summary from `/dashboard/summary`
- [ ] Display key stats (total users, notifications, etc.)
- [ ] Add refresh button

#### 2. Alerts Widget
- [ ] Fetch alerts from `/dashboard/widgets/alerts`
- [ ] Display insurance renewals (< 30 days)
- [ ] Display document expiries
- [ ] Display quote expiries
- [ ] Add dismiss functionality
- [ ] Link to relevant pages

#### 3. Priority Items Widget
- [ ] Fetch from `/dashboard/widgets/priorities`
- [ ] Display top 5 priority items with scores
- [ ] Quick action: "Convert to Project"
- [ ] Link to projects page

#### 4. Active Projects Widget
- [ ] Fetch from `/dashboard/widgets/projects`
- [ ] Display projects in progress
- [ ] Show progress bars
- [ ] Link to project details

#### 5. Financial Summary Widget
- [ ] Fetch from `/dashboard/widgets/financial`
- [ ] Display net income (monthly)
- [ ] Show budget status
- [ ] Quick action: "View Budget"

#### 6. Tax Summary Widget
- [ ] Fetch from `/dashboard/widgets/tax`
- [ ] Display current FY totals (WFH hours, travel claims)
- [ ] Quick action: "Add WFH Entry"

#### 7. Notifications Widget
- [ ] Fetch from `/dashboard/widgets/notifications`
- [ ] Display unread notifications
- [ ] Mark as read functionality
- [ ] Pin/dismiss functionality

#### 8. Meal Planner Widget
- [ ] Fetch from `/dashboard/widgets/meals`
- [ ] Display current week plan
- [ ] Quick action: "View Shopping List"

#### 9. Global Search
- [ ] Implement global search bar (top of page)
- [ ] Use `/dashboard/search` endpoint
- [ ] Show autocomplete results
- [ ] Navigate to search results page

#### 10. Quick Actions
- [ ] Add floating action button (FAB) or quick action panel
- [ ] Common actions: Add WFH, Add Expense, Add Document
- [ ] Role-based action visibility

### Files to Create
- `src/pages/Dashboard.tsx` (replace existing)
- `src/components/dashboard/SummaryWidget.tsx`
- `src/components/dashboard/AlertsWidget.tsx`
- `src/components/dashboard/PrioritiesWidget.tsx`
- `src/components/dashboard/ProjectsWidget.tsx`
- `src/components/dashboard/FinancialWidget.tsx`
- `src/components/dashboard/TaxWidget.tsx`
- `src/components/dashboard/NotificationsWidget.tsx`
- `src/components/dashboard/MealsWidget.tsx`
- `src/components/dashboard/GlobalSearch.tsx`

### Acceptance Criteria
- [x] Dashboard loads all widgets within 2 seconds
- [x] Widgets show loading skeletons while fetching
- [x] Empty states display when no data
- [x] Quick actions work correctly
- [x] All links navigate to correct pages
- [x] Widgets refresh on data changes

---

## Sprint 15: Tax Management UI

**Priority:** 🟡 High
**Duration:** ~2 days
**Blocked By:** Sprint 13
**Backend:** `/tax` endpoints (14 endpoints available)

### Sprint Goal
Build the Tax Records module UI for tracking work-from-home hours and travel claims.

### Tasks

#### 1. Tax Module Layout
- [ ] Create tax records page layout
- [ ] Add tabs: WFH | Travel | Summary
- [ ] Implement financial year selector

#### 2. Work From Home (WFH) Tab
- [ ] Create WFH entry list (table with date, hours, deduction)
- [ ] Add WFH entry form (date picker, hours input)
- [ ] Edit WFH entry
- [ ] Delete WFH entry (with confirmation)
- [ ] Validation: date required, hours 0.5-24
- [ ] Display current FY total

#### 3. Work Travel Tab
- [ ] Create travel entry list (table with date, from, to, km, deduction)
- [ ] Add travel entry form (date, from, to, km, purpose, vehicle)
- [ ] Edit travel entry
- [ ] Delete travel entry (with confirmation + ATO retention warning)
- [ ] Validation: km > 0, purpose required
- [ ] Display current FY total

#### 4. Summary Tab
- [ ] Fetch `/tax/wfh/summary` and `/tax/travel/summary`
- [ ] Display FY totals by category
- [ ] Show ATO-formatted summary
- [ ] Export button (download ATO format CSV)
- [ ] Graph: Monthly trend (WFH hours, travel km)

#### 5. ATO Compliance
- [ ] Add ATO retention warning to delete confirmations
- [ ] Display retention period (5 years from FY end)
- [ ] Show "Do not delete" warning for records < 5 years old

### Files to Create
- `src/pages/Tax/TaxRecords.tsx`
- `src/pages/Tax/WFHTab.tsx`
- `src/pages/Tax/TravelTab.tsx`
- `src/pages/Tax/SummaryTab.tsx`
- `src/components/tax/WFHForm.tsx`
- `src/components/tax/TravelForm.tsx`
- `src/services/taxService.ts`

### Acceptance Criteria
- [x] Users can add/edit/delete WFH and travel entries
- [x] FY totals calculate correctly
- [x] ATO warnings display before deletion
- [x] Export generates valid ATO format
- [x] Validation matches backend requirements
- [x] Loading states show during API calls

---

## Sprint 16: Financial Management UI

**Priority:** 🟡 High
**Duration:** ~3 days
**Blocked By:** Sprint 13
**Backend:** `/financial` endpoints (28 endpoints available)

### Sprint Goal
Build the Financial module UI for managing income, expenses, accounts, utilities, and budget calculator.

### Tasks

#### 1. Financial Module Layout
- [ ] Create financial page layout
- [ ] Add tabs: Income | Accounts | Expenses | Utilities | Budget

#### 2. Income Sources Tab
- [ ] List income sources (CRUD)
- [ ] Form: name, type (salary/business/investment/other), amount, frequency
- [ ] Display total income by frequency

#### 3. Bank Accounts Tab
- [ ] List bank accounts (CRUD)
- [ ] Form: account_name, institution, account_type, balance
- [ ] Display total balance across accounts

#### 4. Expense Categories Tab
- [ ] List expense categories (CRUD)
- [ ] Form: category_name, is_fixed
- [ ] Display fixed vs variable breakdown

#### 5. Expenses Tab
- [ ] List expenses (CRUD)
- [ ] Form: category, amount, frequency, description
- [ ] Filter by category, fixed/variable
- [ ] Display total expenses by frequency

#### 6. Utilities Tab
- [ ] List utilities (CRUD)
- [ ] Form: utility_type, provider, account_number, amount, billing_frequency
- [ ] Display total utilities by frequency
- [ ] Graph: Utility costs over time (if endpoint exists)

#### 7. Budget Calculator
- [ ] Fetch `/financial/budget/calculate?frequency=monthly`
- [ ] Display total income, total expenses, net income
- [ ] Show account transfer schedule
- [ ] Highlight surplus/deficit
- [ ] Frequency selector (weekly/fortnightly/monthly)

#### 8. Financial Summary
- [ ] Overview card: total income, expenses, net income
- [ ] Quick stats: number of accounts, categories, etc.
- [ ] Recent transactions (if available)

### Files to Create
- `src/pages/Financial/FinancialManagement.tsx`
- `src/pages/Financial/IncomeTab.tsx`
- `src/pages/Financial/AccountsTab.tsx`
- `src/pages/Financial/ExpensesTab.tsx`
- `src/pages/Financial/UtilitiesTab.tsx`
- `src/pages/Financial/BudgetTab.tsx`
- `src/components/financial/IncomeForm.tsx`
- `src/components/financial/AccountForm.tsx`
- `src/components/financial/ExpenseForm.tsx`
- `src/components/financial/UtilityForm.tsx`
- `src/components/financial/BudgetCalculator.tsx`
- `src/services/financialService.ts`

### Acceptance Criteria
- [x] All CRUD operations work for income, accounts, expenses, utilities
- [x] Budget calculator displays correctly for all frequencies
- [x] Transfer schedule shows account allocations
- [x] Forms validate input (amounts > 0, required fields)
- [x] Loading states and error handling work
- [x] Data persists correctly

---

## Sprint 17: Assets & Documents UI

**Priority:** 🟢 Medium
**Duration:** ~2 days
**Blocked By:** Sprint 13
**Backend:** `/assets` endpoints (18 endpoints available)

### Sprint Goal
Build the Assets module UI for managing insurance policies and important documents.

### Tasks

#### 1. Assets Module Layout
- [ ] Create assets page layout
- [ ] Add tabs: Insurance | Documents

#### 2. Insurance Policies Tab
- [ ] List insurance policies (CRUD)
- [ ] Form: policy_number, type, provider, coverage_amount, premium, frequency, start/end date
- [ ] Display renewal alerts (< 30 days)
- [ ] Cost summary by type
- [ ] Filter by type, provider

#### 3. Documents Tab
- [ ] List documents (CRUD)
- [ ] Form: title, document_type, description, tags, expiry_date, file upload
- [ ] File upload integration (use existing file upload endpoint)
- [ ] Display expiry alerts (< 30 days)
- [ ] Search documents by title, tags, type
- [ ] Download/view document

#### 4. Alerts
- [ ] Fetch `/assets/insurance/renewal-alerts?days_threshold=30`
- [ ] Fetch `/assets/documents/expiry-alerts?days_threshold=30`
- [ ] Display alerts widget on assets page
- [ ] Link alerts to edit forms

#### 5. File Viewer
- [ ] Implement PDF viewer component (react-pdf or browser native)
- [ ] Download button for all file types
- [ ] Thumbnail preview (if possible)

### Files to Create
- `src/pages/Assets/AssetsManagement.tsx`
- `src/pages/Assets/InsuranceTab.tsx`
- `src/pages/Assets/DocumentsTab.tsx`
- `src/components/assets/InsuranceForm.tsx`
- `src/components/assets/DocumentForm.tsx`
- `src/components/assets/FileUpload.tsx`
- `src/components/assets/FileViewer.tsx`
- `src/services/assetsService.ts`

### Acceptance Criteria
- [x] Insurance and document CRUD works
- [x] File upload shows progress bar
- [x] Renewal/expiry alerts display correctly
- [x] Documents are searchable
- [x] PDF viewer works in-browser
- [x] Download functionality works

---

## Sprint 18: Projects & Tasks UI

**Priority:** 🟢 Medium
**Duration:** ~2-3 days
**Blocked By:** Sprint 13
**Backend:** `/projects` endpoints (21 endpoints available)

### Sprint Goal
Build the Projects module UI for tracking priority items, projects, and quotes.

### Tasks

#### 1. Projects Module Layout
- [ ] Create projects page layout
- [ ] Add tabs: Priorities | Projects | Quotes

#### 2. Priority Items Tab
- [ ] List priority items (CRUD)
- [ ] Form: name, description, severity, frequency, estimated_cost
- [ ] Display calculated scores (benefit, cost, net)
- [ ] Sort by net score
- [ ] Convert to project button
- [ ] Status filter (identified/researching/quoted/in_project)

#### 3. Projects Tab
- [ ] List projects (CRUD)
- [ ] Form: name, description, priority_score, actual_cost, start_date, end_date, status
- [ ] Display status workflow (planning/in_progress/on_hold/completed/cancelled)
- [ ] Cost tracking (estimated vs actual)
- [ ] Link to related quotes

#### 4. Quotes Tab
- [ ] List quotes (CRUD)
- [ ] Form: project, vendor_name, vendor_contact, quoted_amount, quote_date, expiry_date, notes, status
- [ ] Quote comparison table (for same project)
- [ ] Expiry alerts (< 7 days)
- [ ] Status filter (pending/accepted/rejected/expired)

#### 5. Project Dashboard
- [ ] Overview: active projects, pending quotes
- [ ] Total cost tracking
- [ ] Project timeline (Gantt chart or simple timeline)

### Files to Create
- `src/pages/Projects/ProjectsManagement.tsx`
- `src/pages/Projects/PrioritiesTab.tsx`
- `src/pages/Projects/ProjectsTab.tsx`
- `src/pages/Projects/QuotesTab.tsx`
- `src/components/projects/PriorityForm.tsx`
- `src/components/projects/ProjectForm.tsx`
- `src/components/projects/QuoteForm.tsx`
- `src/components/projects/QuoteComparison.tsx`
- `src/services/projectsService.ts`

### Acceptance Criteria
- [x] Priority scoring works correctly
- [x] Convert to project creates project from priority
- [x] Quote comparison shows side-by-side
- [x] Project status workflow is intuitive
- [x] Cost tracking displays correctly
- [x] Expiry alerts work

---

## Sprint 19: Knowledge Base UI

**Priority:** 🟢 Medium
**Duration:** ~2 days
**Blocked By:** Sprint 13
**Backend:** `/knowledge` endpoints (10 endpoints available)

### Sprint Goal
Build the Knowledge Base module UI for storing household reference information.

### Tasks

#### 1. Knowledge Base Layout
- [ ] Create knowledge base page layout
- [ ] Article type selector/filter
- [ ] Search bar

#### 2. Article List
- [ ] Display articles (all types)
- [ ] Filter by article_type
- [ ] Search articles (full-text search endpoint)
- [ ] Display article cards with type icon

#### 3. Article Types & Forms
- [ ] Measurement: item_name, measurement_value, measurement_unit, location, date_recorded
- [ ] PaintColor: room_name, color_name, brand, color_code, finish_type, purchase_location
- [ ] TechDevice: device_name, device_type, model, serial_number, purchase_date, warranty_expiry, login_username, encrypted_password
- [ ] KeyLocation: key_name, location_description, quantity, key_type, notes
- [ ] Instruction: item_name, instruction_type, instruction_text, pdf_attachment, web_link
- [ ] Warranty: item_name, purchase_date, warranty_period_months, warranty_expiry, retailer, receipt_attachment
- [ ] Subscription: service_name, provider, cost, billing_frequency, renewal_date, login_username, encrypted_password
- [ ] General: title, content, category, tags

#### 4. Article Detail View
- [ ] Display article with type-specific layout
- [ ] Edit/delete buttons
- [ ] Attachments section (if applicable)
- [ ] Password decryption (for TechDevice, Subscription)

#### 5. Search & Filter
- [ ] Full-text search using `/knowledge/search`
- [ ] Filter by article_type
- [ ] Sort by date created/updated

### Files to Create
- `src/pages/Knowledge/KnowledgeBase.tsx`
- `src/components/knowledge/ArticleCard.tsx`
- `src/components/knowledge/ArticleDetail.tsx`
- `src/components/knowledge/ArticleForm.tsx` (dynamic based on type)
- `src/components/knowledge/SearchBar.tsx`
- `src/services/knowledgeService.ts`

### Acceptance Criteria
- [x] All 8 article types can be created/edited/deleted
- [x] Search finds articles correctly
- [x] Password fields are encrypted (backend handles this)
- [x] Attachments can be linked to articles
- [x] Type-specific forms show correct fields

---

## Sprint 20: Meal Planner UI

**Priority:** 🔵 Low
**Duration:** ~2 days
**Blocked By:** Sprint 13
**Backend:** `/meals` endpoints (13 endpoints available)

### Sprint Goal
Build the Meal Planner module UI for managing recipes and weekly meal plans.

### Tasks

#### 1. Meal Planner Layout
- [ ] Create meal planner page layout
- [ ] Add tabs: Recipes | Week Plans

#### 2. Recipes Tab
- [ ] List recipes (CRUD)
- [ ] Form: recipe_name, servings, prep_time, cook_time, instructions, ingredients (array)
- [ ] Ingredient management (add/remove rows)
- [ ] Search recipes by name or ingredient

#### 3. Week Plans Tab
- [ ] List week plans (CRUD)
- [ ] Form: week_starting (Monday), meal assignments (day + meal_type)
- [ ] Calendar view (7 days × 3 meals)
- [ ] Drag-and-drop recipes to days (optional enhancement)
- [ ] Current week view (fetch `/meals/week-plans/current`)

#### 4. Shopping List
- [ ] Generate shopping list for week plan
- [ ] Display grouped ingredients with quantities
- [ ] Print/export functionality

#### 5. Recipe Detail
- [ ] Display recipe with ingredients and instructions
- [ ] Servings calculator (scale ingredients)
- [ ] Print recipe

### Files to Create
- `src/pages/Meals/MealPlanner.tsx`
- `src/pages/Meals/RecipesTab.tsx`
- `src/pages/Meals/WeekPlansTab.tsx`
- `src/components/meals/RecipeForm.tsx`
- `src/components/meals/WeekPlanForm.tsx`
- `src/components/meals/ShoppingList.tsx`
- `src/components/meals/RecipeCard.tsx`
- `src/services/mealsService.ts`

### Acceptance Criteria
- [x] Recipes can be created with multiple ingredients
- [x] Week plans assign recipes to days/meals
- [x] Shopping list aggregates ingredients correctly
- [x] Search finds recipes by ingredient
- [x] Current week view displays correctly

---

## Sprint 21: Polish & Testing

**Priority:** 🟡 High
**Duration:** ~3 days
**Blocked By:** Sprints 13-20

### Sprint Goal
Polish the UI, ensure accessibility, mobile responsiveness, and comprehensive testing.

### Tasks

#### 1. Accessibility (A11Y-1 - High Priority)
- [ ] Run Lighthouse accessibility audit
- [ ] Run axe DevTools audit
- [ ] Fix color contrast issues (WCAG AA)
- [ ] Add skip-to-content link
- [ ] Verify keyboard navigation (all forms, all pages)
- [ ] Add ARIA labels where needed
- [ ] Test with screen reader (NVDA or VoiceOver)

#### 2. Mobile Responsiveness (MOB-1 - High Priority)
- [ ] Test all pages on mobile (iPhone, Android)
- [ ] Ensure tables are responsive (card view or horizontal scroll)
- [ ] Verify touch targets are 44×44px minimum
- [ ] Test hamburger menu
- [ ] Optimize dashboard for mobile
- [ ] Test forms on mobile

#### 3. Design Consistency
- [ ] Review all color usage (consistent with design system)
- [ ] Ensure typography is consistent
- [ ] Standardize spacing/padding
- [ ] Verify button styles are consistent
- [ ] Check card/modal consistency

#### 4. Performance Optimization
- [ ] Implement pagination for large lists
- [ ] Add query optimization (TanStack Query caching)
- [ ] Lazy load routes (React.lazy)
- [ ] Optimize bundle size (check with Vite build analyzer)
- [ ] Add image optimization (if applicable)

#### 5. Error States & Edge Cases
- [ ] Test all empty states
- [ ] Test network error scenarios
- [ ] Test validation edge cases
- [ ] Test with slow network (throttling)
- [ ] Test with no data scenarios

#### 6. User Testing
- [ ] Test with admin user
- [ ] Test with editor user
- [ ] Test with reader user
- [ ] Verify role-based access works correctly
- [ ] Test logout/session expiry

#### 7. Documentation
- [ ] Update README with UI screenshots
- [ ] Document component usage
- [ ] Create user guide (basic usage)
- [ ] Update KNOWN_ISSUES.md
- [ ] Update UI_ISSUES.md (mark resolved)

#### 8. Final Checks
- [ ] All console errors/warnings resolved
- [ ] All TODOs addressed or documented
- [ ] Build passes without errors
- [ ] Lighthouse score > 90 (Performance, Accessibility, Best Practices)

### Acceptance Criteria
- [x] WCAG 2.1 Level AA compliance verified
- [x] Mobile responsive on all pages
- [x] Lighthouse score > 90
- [x] All roles tested
- [x] No critical bugs
- [x] Documentation complete

---

## Priority Matrix

### High Priority (Must Have for v1.0)
1. ✅ Sprint 12: Foundation
2. 🎯 Sprint 13: Core UI Infrastructure
3. Sprint 14: Dashboard & Widgets
4. Sprint 15: Tax Management UI
5. Sprint 16: Financial Management UI
6. Sprint 21: Polish & Testing

### Medium Priority (Should Have for v1.0)
7. Sprint 17: Assets & Documents UI
8. Sprint 18: Projects & Tasks UI
9. Sprint 19: Knowledge Base UI

### Low Priority (Nice to Have for v1.0, Can Defer to v1.1)
10. Sprint 20: Meal Planner UI

---

## Dependencies & Blockers

**Sprint 13 blocks all other sprints** - Must complete first

### Critical Path
```
Sprint 13 (Core Infrastructure)
    ↓
Sprint 14 (Dashboard) ← High Priority
    ↓
Sprint 15 (Tax) ← High Priority
    ↓
Sprint 16 (Financial) ← High Priority
    ↓
Sprint 17, 18, 19, 20 (Modules) ← Can be parallel
    ↓
Sprint 21 (Polish & Testing)
```

---

## Backend Integration Notes

### Available Endpoints by Module
- **Authentication:** 6 endpoints ✅
- **Tax Records:** 14 endpoints ✅
- **Financial:** 28 endpoints ✅
- **Assets & Documents:** 18 endpoints ✅
- **Projects & Tasks:** 21 endpoints ✅
- **Knowledge Base:** 10 endpoints ✅
- **Meal Planner:** 13 endpoints ✅
- **Dashboard:** 22 endpoints ✅
- **Admin:** 14 endpoints ✅
- **Audit Logs:** 5 endpoints ✅

**Total:** 151 endpoints ready for integration

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- API Guide: `backend/docs/API_GUIDE.md`

---

## Estimated Timeline

Assuming full-time development:

| Sprint | Duration | Cumulative |
|--------|----------|------------|
| Sprint 12 | Complete | - |
| Sprint 13 | 2-3 days | 2-3 days |
| Sprint 14 | 2 days | 4-5 days |
| Sprint 15 | 2 days | 6-7 days |
| Sprint 16 | 3 days | 9-10 days |
| Sprint 17 | 2 days | 11-12 days |
| Sprint 18 | 2-3 days | 13-15 days |
| Sprint 19 | 2 days | 15-17 days |
| Sprint 20 | 2 days | 17-19 days |
| Sprint 21 | 3 days | 20-22 days |

**Total Estimated: 20-22 working days (4-5 weeks)**

---

## Success Metrics

### Sprint 13 Success
- [x] Navigation works on all devices
- [x] Loading states implemented
- [x] Error handling is user-friendly
- [x] Forms validate correctly

### Overall v1.0 Success
- [x] All high-priority modules complete
- [x] WCAG AA compliance
- [x] Mobile responsive
- [x] No critical bugs
- [x] Lighthouse score > 90
- [x] User can complete all primary workflows

---

## Next Steps

**Immediate Action:** Begin Sprint 13 - Core UI Infrastructure

**Start with:**
1. AppShell layout component
2. Sidebar navigation
3. Loading spinner component
4. Error boundary

**Files to Create First:**
- `src/components/layout/AppShell.tsx`
- `src/components/layout/Sidebar.tsx`
- `src/components/ui/spinner.tsx`
- `src/components/common/ErrorBoundary.tsx`

---

**Last Updated:** 2026-02-14
**Current Sprint:** Sprint 13 (Core UI Infrastructure)
**Next Review:** After Sprint 13 completion
