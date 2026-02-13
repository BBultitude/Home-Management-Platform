# UI Architecture & Design System

**Version:** 1.0.0
**Status:** Planning Phase
**Last Updated:** 2026-02-13

---

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Design System](#design-system)
3. [Component Library](#component-library)
4. [Layout Structure](#layout-structure)
5. [Theme & Styling](#theme--styling)
6. [Navigation Architecture](#navigation-architecture)
7. [Page Structure](#page-structure)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Technology Stack

### Core Framework
- **React 18+** - Modern React with Hooks and Suspense
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and dev server

### Styling & Design
- **Tailwind CSS 3+** - Utility-first CSS framework
- **shadcn/ui** - High-quality, accessible component library built on Radix UI
- **Radix UI** - Unstyled, accessible primitives
- **Lucide React** - Modern icon library (consistent with shadcn/ui)

### State Management
- **TanStack Query (React Query)** - Server state management and caching
- **Zustand** - Lightweight client state management
- **React Hook Form** - Form state management and validation

### Routing & Navigation
- **React Router v6** - Client-side routing
- **TanStack Router** - Type-safe routing (alternative)

### Data Fetching
- **Axios** - HTTP client with interceptors
- **TanStack Query** - Data fetching, caching, and synchronization

### Utilities
- **date-fns** - Date manipulation
- **zod** - Schema validation
- **clsx** - Conditional className utility
- **tailwind-merge** - Merge Tailwind classes intelligently

### Development Tools
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Vitest** - Unit testing
- **Playwright** - E2E testing

---

## Design System

### Why shadcn/ui?

**Advantages:**
1. **Copy-Paste Components** - Own the code, no package lock-in
2. **Built on Radix UI** - Accessible by default (WCAG 2.1)
3. **Tailwind CSS** - Consistent with our choice
4. **Customizable** - Full control over styling
5. **Modern** - Follows latest React patterns
6. **Type-Safe** - Full TypeScript support
7. **Production-Ready** - Used by major companies

**Design Philosophy:**
- Composition over configuration
- Accessibility first
- Developer experience focused
- Minimal runtime overhead

### Core Design Principles

1. **Consistency** - Same components, same patterns everywhere
2. **Accessibility** - WCAG 2.1 AA compliance
3. **Responsiveness** - Mobile-first approach
4. **Performance** - Lazy loading, code splitting
5. **Maintainability** - Clear component hierarchy
6. **Scalability** - Easy to extend and customize

---

## Component Library

### Base Components (from shadcn/ui)

**Layout:**
- `Card` - Container for content sections
- `Separator` - Visual divider
- `AspectRatio` - Maintain aspect ratios
- `ScrollArea` - Custom scrollbars

**Navigation:**
- `NavigationMenu` - Main navigation
- `Breadcrumb` - Page hierarchy
- `Tabs` - Tabbed interfaces
- `Pagination` - List pagination

**Forms:**
- `Form` - Form wrapper with validation
- `Input` - Text input
- `Textarea` - Multi-line text
- `Select` - Dropdown selection
- `Checkbox` - Boolean input
- `RadioGroup` - Single choice from options
- `Switch` - Toggle switch
- `Slider` - Range input
- `DatePicker` - Date selection
- `Label` - Form labels

**Feedback:**
- `Alert` - Important messages
- `Toast` - Temporary notifications
- `Badge` - Status indicators
- `Progress` - Loading progress
- `Skeleton` - Loading placeholders
- `Spinner` - Loading indicator

**Overlay:**
- `Dialog` - Modal dialogs
- `Sheet` - Side panels
- `Popover` - Floating content
- `DropdownMenu` - Context menus
- `Tooltip` - Helpful hints
- `AlertDialog` - Confirmation dialogs

**Data Display:**
- `Table` - Data tables
- `Avatar` - User avatars
- `Calendar` - Date picker calendar
- `Command` - Command palette (search)
- `ContextMenu` - Right-click menus

**Buttons:**
- `Button` - Primary action buttons
- `IconButton` - Icon-only buttons
- `ButtonGroup` - Button collections

### Custom Application Components

**Dashboard:**
- `DashboardWidget` - Reusable widget container
- `StatCard` - Statistic display card
- `AlertCard` - Alert/warning display
- `QuickActionButton` - Dashboard shortcuts
- `NotificationItem` - Notification display
- `SearchBar` - Global search component

**Financial:**
- `BudgetChart` - Budget visualization
- `ExpenseTable` - Expense list
- `IncomeCard` - Income source display
- `CategoryBadge` - Expense category indicator
- `AmountInput` - Currency input field
- `FrequencySelector` - Frequency dropdown

**Tax:**
- `WFHEntryForm` - WFH entry creation
- `TravelEntryForm` - Travel entry creation
- `TaxSummaryCard` - FY summary display
- `ATOExportButton` - Export functionality

**Assets:**
- `PolicyCard` - Insurance policy display
- `DocumentCard` - Document display
- `RenewalAlert` - Renewal notification
- `FileUploadZone` - Drag-drop upload
- `TagInput` - Tag management

**Projects:**
- `PriorityItemCard` - Priority display with scoring
- `ProjectCard` - Project status display
- `QuoteComparison` - Quote comparison table
- `ScoreBadge` - Cost-benefit score display
- `StatusBadge` - Project status indicator

**Knowledge:**
- `ArticleCard` - Knowledge article display
- `ArticleTypeIcon` - Type indicator
- `SearchResults` - Search result list
- `PasswordField` - Encrypted password input

**Meals:**
- `RecipeCard` - Recipe display
- `IngredientList` - Ingredient display
- `WeekPlanCalendar` - Weekly meal view
- `ShoppingList` - Shopping list display
- `MealDaySelector` - Day selection

**Admin:**
- `UserTable` - User management table
- `RoleSelector` - Role assignment
- `MFAResetDialog` - MFA reset confirmation
- `AuditLogViewer` - Audit log display
- `StatsDashboard` - System statistics

---

## Layout Structure

### Application Shell

```
┌─────────────────────────────────────────────────────────┐
│ Header (TopNav + UserMenu + GlobalSearch)              │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│  Sidebar │  Main Content Area                          │
│  (Nav)   │  ┌────────────────────────────────────────┐ │
│          │  │ Breadcrumbs                            │ │
│          │  ├────────────────────────────────────────┤ │
│          │  │                                        │ │
│          │  │ Page Content                           │ │
│          │  │                                        │ │
│          │  │                                        │ │
│          │  │                                        │ │
│          │  └────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────┘
```

### Responsive Breakpoints

```css
/* Mobile First Approach */
sm: 640px   /* Small devices (phones) */
md: 768px   /* Medium devices (tablets) */
lg: 1024px  /* Large devices (laptops) */
xl: 1280px  /* Extra large (desktops) */
2xl: 1536px /* 2X large (large desktops) */
```

### Layout Components

**AppShell:**
- Sticky header (60px height)
- Collapsible sidebar (240px width, mobile drawer)
- Main content area (responsive width)
- Bottom padding for mobile navigation

**Sidebar:**
- Logo at top
- Navigation menu (collapsible sections)
- User info at bottom
- Collapse button (desktop)
- Drawer overlay (mobile)

**Header:**
- Logo/branding (left)
- Global search (center)
- Notifications icon (right)
- User menu dropdown (right)
- Mobile menu toggle (mobile only)

---

## Theme & Styling

### Color Palette

**Primary Colors:**
```css
/* Blue (Primary) - Trust, reliability */
primary: {
  50:  '#eff6ff',
  100: '#dbeafe',
  200: '#bfdbfe',
  300: '#93c5fd',
  400: '#60a5fa',
  500: '#3b82f6',  /* Main primary */
  600: '#2563eb',
  700: '#1d4ed8',
  800: '#1e40af',
  900: '#1e3a8a',
}

/* Slate (Neutral) - UI elements */
slate: {
  50:  '#f8fafc',
  100: '#f1f5f9',
  200: '#e2e8f0',
  300: '#cbd5e1',
  400: '#94a3b8',
  500: '#64748b',
  600: '#475569',
  700: '#334155',
  800: '#1e293b',
  900: '#0f172a',
}
```

**Semantic Colors:**
```css
/* Success (Green) */
success: '#10b981'

/* Warning (Amber) */
warning: '#f59e0b'

/* Error (Red) */
error: '#ef4444'

/* Info (Blue) */
info: '#3b82f6'
```

**Module Colors (Subtle Accents):**
```css
tax: '#8b5cf6'       /* Purple */
financial: '#10b981'  /* Green */
assets: '#f59e0b'     /* Amber */
projects: '#ec4899'   /* Pink */
knowledge: '#06b6d4'  /* Cyan */
meals: '#f97316'      /* Orange */
```

### Typography

**Font Family:**
```css
/* Primary (Sans-serif) */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Monospace (Code) */
font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

**Font Sizes:**
```css
xs:   0.75rem  /* 12px */
sm:   0.875rem /* 14px */
base: 1rem     /* 16px */
lg:   1.125rem /* 18px */
xl:   1.25rem  /* 20px */
2xl:  1.5rem   /* 24px */
3xl:  1.875rem /* 30px */
4xl:  2.25rem  /* 36px */
```

**Font Weights:**
```css
normal: 400
medium: 500
semibold: 600
bold: 700
```

### Spacing Scale

```css
/* Tailwind's default spacing scale (4px base) */
0:  0
1:  0.25rem  /* 4px */
2:  0.5rem   /* 8px */
3:  0.75rem  /* 12px */
4:  1rem     /* 16px */
5:  1.25rem  /* 20px */
6:  1.5rem   /* 24px */
8:  2rem     /* 32px */
10: 2.5rem   /* 40px */
12: 3rem     /* 48px */
```

### Border Radius

```css
none: 0
sm:   0.125rem /* 2px */
md:   0.375rem /* 6px */
lg:   0.5rem   /* 8px */
xl:   0.75rem  /* 12px */
2xl:  1rem     /* 16px */
full: 9999px
```

### Shadows

```css
sm:  '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
md:  '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
lg:  '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
xl:  '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
```

### Dark Mode Support

**Strategy:**
- System preference detection
- Manual toggle in user menu
- Persistent localStorage
- Class-based dark mode (`dark:` prefix)

**Dark Mode Colors:**
```css
dark:bg-slate-900    /* Background */
dark:bg-slate-800    /* Cards */
dark:text-slate-100  /* Text */
dark:border-slate-700 /* Borders */
```

---

## Navigation Architecture

### Main Navigation Structure

```
Dashboard
├── Overview
└── Quick Actions

Tax Records
├── Work From Home
├── Work Travel
└── FY Summary

Financial
├── Income Sources
├── Bank Accounts
├── Expense Categories
├── Expenses
├── Utilities
└── Budget Calculator

Assets & Documents
├── Insurance Policies
├── Documents
└── Alerts

Projects & Tasks
├── Priority Items
├── Projects
└── Quotes

Knowledge Base
├── All Articles
├── By Type
└── Search

Meal Planner
├── Recipes
├── This Week's Plan
└── Shopping List

Admin (Admin only)
├── Users
├── System Stats
└── Audit Logs

Settings
├── Profile
├── Security (MFA)
├── Preferences
└── Notifications
```

### Navigation States

- **Active** - Current page (highlighted)
- **Hover** - Interactive feedback
- **Disabled** - Insufficient permissions
- **Badge** - Notification counts
- **Expandable** - Nested navigation

---

## Page Structure

### Standard Page Layout

```tsx
<PageContainer>
  <PageHeader>
    <Breadcrumbs />
    <PageTitle />
    <PageActions /> {/* Primary action buttons */}
  </PageHeader>

  <PageContent>
    {/* Page-specific content */}
  </PageContent>
</PageContainer>
```

### Common Page Patterns

**List Page:**
- Search/filter bar at top
- Action buttons (Create New, Import, Export)
- Data table with sorting and pagination
- Empty state for no data

**Detail Page:**
- Back button in header
- Main content card
- Actions (Edit, Delete) in header
- Related items section
- Activity timeline (if applicable)

**Form Page:**
- Form in centered card (max-width)
- Field validation with error messages
- Cancel and Submit buttons
- Unsaved changes warning

**Dashboard Page:**
- Grid of widget cards
- Responsive layout (1-2-3 columns)
- Quick actions
- Recent activity

---

## Implementation Roadmap

### Phase 1: Foundation (Sprint 12)
**Duration:** 1 week

**Goals:**
- Set up React + Vite + TypeScript project
- Configure Tailwind CSS
- Install and configure shadcn/ui
- Create base layout components
- Implement authentication flow

**Deliverables:**
- Project scaffolding
- Login/MFA pages
- AppShell layout
- Navigation sidebar
- User menu

**Components:**
- Button, Input, Form, Card
- Dialog, Toast, Alert
- Layout (AppShell, Header, Sidebar)

### Phase 2: Dashboard & Core Features (Sprint 13)
**Duration:** 2 weeks

**Goals:**
- Implement dashboard with all widgets
- Global search functionality
- Notification system
- Profile settings

**Deliverables:**
- Dashboard page with 8 widgets
- Global search UI
- Notification center
- User profile page
- Settings pages

**Components:**
- DashboardWidget, StatCard
- SearchBar, SearchResults
- NotificationItem, NotificationList
- All base form components

### Phase 3: Tax Module UI (Sprint 14)
**Duration:** 1 week

**Goals:**
- WFH entry management
- Travel entry management
- FY summary display
- ATO export functionality

**Deliverables:**
- Tax dashboard
- WFH entry list and forms
- Travel entry list and forms
- Summary page
- Export dialogs

**Components:**
- TaxEntryForm, TaxEntryTable
- SummaryCard, ExportButton

### Phase 4: Financial Module UI (Sprint 15)
**Duration:** 2 weeks

**Goals:**
- Income and expense management
- Budget calculator
- Utility tracking
- Financial dashboard

**Deliverables:**
- Financial dashboard
- Income/expense CRUD
- Budget calculation view
- Utility tracking UI
- Charts and visualizations

**Components:**
- BudgetChart, ExpenseTable
- CategorySelector, AmountInput
- FrequencySelector

### Phase 5: Assets Module UI (Sprint 16)
**Duration:** 1 week

**Goals:**
- Insurance policy management
- Document storage
- Renewal alerts
- File uploads

**Deliverables:**
- Assets dashboard
- Policy list and forms
- Document list and forms
- Alert notifications
- File upload interface

**Components:**
- PolicyCard, DocumentCard
- RenewalAlert, FileUploadZone
- TagInput

### Phase 6: Projects Module UI (Sprint 17)
**Duration:** 1-2 weeks

**Goals:**
- Priority item management with scoring
- Project tracking
- Quote comparison

**Deliverables:**
- Projects dashboard
- Priority items list (sorted by score)
- Project Kanban board
- Quote comparison table
- Convert priority → project workflow

**Components:**
- PriorityItemCard, ScoreBadge
- ProjectCard, StatusBadge
- QuoteComparison

### Phase 7: Knowledge Base UI (Sprint 18)
**Duration:** 1 week

**Goals:**
- Article management
- Full-text search
- Type-specific forms
- Attachment handling

**Deliverables:**
- Knowledge base dashboard
- Article list and search
- Article type forms
- Password encryption UI
- Attachment management

**Components:**
- ArticleCard, ArticleTypeIcon
- SearchResults, PasswordField

### Phase 8: Meal Planner UI (Sprint 19)
**Duration:** 1 week

**Goals:**
- Recipe management
- Weekly meal planning
- Shopping list generation

**Deliverables:**
- Meal planner dashboard
- Recipe list and forms
- Week plan calendar
- Shopping list view
- Print-friendly layouts

**Components:**
- RecipeCard, IngredientList
- WeekPlanCalendar, ShoppingList
- MealDaySelector

### Phase 9: Admin Panel UI (Sprint 20)
**Duration:** 1 week

**Goals:**
- User management interface
- System statistics
- Audit log viewer

**Deliverables:**
- Admin dashboard
- User management table
- Role assignment UI
- MFA reset dialogs
- Audit log viewer
- System stats widgets

**Components:**
- UserTable, RoleSelector
- MFAResetDialog, AuditLogViewer
- StatsDashboard

### Phase 10: Polish & Optimization (Sprint 21)
**Duration:** 1-2 weeks

**Goals:**
- Responsive design refinement
- Performance optimization
- Accessibility audit
- Error handling
- Loading states

**Deliverables:**
- Mobile-optimized layouts
- Lazy loading implementation
- Error boundaries
- Loading skeletons
- A11y improvements
- Dark mode polish

---

## Design System Configuration

### Tailwind Config

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {...},
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Component Naming Convention

```
<ModuleName><ComponentType>
Examples:
- DashboardWidget
- TaxEntryForm
- ProjectCard
- UserTable
```

### File Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui base components
│   ├── layout/          # Layout components
│   ├── dashboard/       # Dashboard-specific
│   ├── tax/             # Tax module
│   ├── financial/       # Financial module
│   ├── assets/          # Assets module
│   ├── projects/        # Projects module
│   ├── knowledge/       # Knowledge module
│   ├── meals/           # Meals module
│   └── admin/           # Admin module
├── pages/               # Page components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities and helpers
├── services/            # API services
├── stores/              # Zustand stores
└── styles/              # Global styles
```

---

## Best Practices

### Component Development
1. **TypeScript** - Always use proper types
2. **Props Interface** - Define clear prop interfaces
3. **Composition** - Prefer composition over inheritance
4. **Hooks** - Use custom hooks for reusable logic
5. **Memoization** - Use React.memo for expensive components

### Styling
1. **Tailwind First** - Use Tailwind utilities
2. **Component Variants** - Use cva for variant management
3. **Consistent Spacing** - Use spacing scale
4. **Responsive** - Mobile-first approach
5. **Dark Mode** - Support from day one

### Performance
1. **Code Splitting** - Lazy load routes and modules
2. **Image Optimization** - Use modern formats
3. **Bundle Size** - Monitor and optimize
4. **Caching** - Use React Query for server state
5. **Memoization** - Prevent unnecessary re-renders

### Accessibility
1. **Semantic HTML** - Use proper elements
2. **ARIA Labels** - Add when needed
3. **Keyboard Navigation** - Full keyboard support
4. **Focus Management** - Visible focus indicators
5. **Screen Readers** - Test with screen readers

---

## Summary

**Design System:** shadcn/ui + Tailwind CSS
**Components:** 100+ components (30+ from shadcn/ui, 70+ custom)
**Implementation:** 10 sprints (12-21)
**Timeline:** ~12-14 weeks
**Total Pages:** ~40 pages across 9 modules

**Next Steps:**
1. Set up frontend project (Sprint 12)
2. Install shadcn/ui and dependencies
3. Create base layout components
4. Implement authentication UI
5. Begin dashboard implementation

---

**Status:** ✅ Ready for Implementation
**Last Updated:** 2026-02-13
