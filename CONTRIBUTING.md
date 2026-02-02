# CONTRIBUTING.md

## Overview

This document defines the development workflow, coding standards, and contribution guidelines for the Home Management Platform.

**Project Authority Model:**
- **User:** Final decision-maker for scope, features, architecture, priorities
- **Developer/AI:** Proposes options, executes within boundaries, asks for clarification when needed

---

## Development Workflow

### 1. Project Phases

The project follows a structured workflow defined in [INSTRUCTIONS.md](./INSTRUCTIONS.md):

**Current Phase:** Planning & Architecture (Sprint 0)

**Workflow Stages:**
1. ✅ Requirements Gathering
2. 🔄 Architecture Design (Design-v1.md - pending approval)
3. ⏳ Implementation (begins after design approval)
4. ⏳ Testing & QA
5. ⏳ Deployment

---

## Architecture Authority

### Design Documents (Design-vX.md)

**Rules:**
- Design-v1.md is the **source of truth** for architecture
- Once approved, Design-v1.md is **locked** (no modifications)
- All code must align with the approved design
- Redesigns require a new versioned document (Design-v2.md, Design-v3.md, etc.)
- Never overwrite historical design documents

**When to Create a New Design Version:**
- Major architectural changes
- Structural changes beyond scope of Improvements.md
- Security or compliance requirements mandate re-architecture
- System evolves beyond assumptions of current design

**Process:**
1. User requests redesign
2. Developer creates Design-v(X+1).md
3. User reviews and approves
4. Design-v(X+1).md becomes the active architecture
5. Previous versions remain as historical reference

---

## Code Implementation

### Implementation Principles

1. **Follow Design-v1.md exactly**
   - No architectural changes without approval
   - No unsolicited refactors
   - Ask for clarification when requirements are ambiguous

2. **Minimal, scoped changes**
   - Modify only requested files
   - No "while I'm here" changes
   - Keep diffs focused

3. **Security-first**
   - HTTP-only cookies for sessions
   - Argon2 password hashing
   - MFA secrets encrypted at rest
   - Input validation (Pydantic/Zod)
   - RBAC enforcement on all endpoints

4. **Maintainability**
   - Clear naming conventions
   - Minimal complexity
   - Self-documenting code
   - Comments for non-obvious logic

---

## Coding Standards

### Backend (Python/FastAPI)

**Style Guide:**
- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Use mypy for type checking

**Code Structure:**
```
backend/
  app/
    main.py              # FastAPI app entry point
    dependencies.py      # Dependency injection
    models/              # SQLAlchemy models
      user.py
      tax.py
      financial.py
      ...
    schemas/             # Pydantic schemas (request/response)
      user.py
      tax.py
      ...
    services/            # Business logic
      auth_service.py
      tax_service.py
      ...
    routers/             # API endpoints
      auth.py
      tax.py
      financial.py
      ...
    core/                # Core utilities
      config.py          # Configuration
      security.py        # Auth helpers
      rbac.py            # RBAC logic
    utils/               # Helper functions
      file_upload.py
      audit_log.py
  tests/
    unit/
    integration/
  alembic/               # Database migrations
  requirements.txt
```

**Naming Conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Example:**
```python
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.tax import WFHEntry
from app.schemas.tax import WFHEntryCreate, WFHEntryResponse
from app.services.tax_service import TaxService
from app.core.rbac import require_role

router = APIRouter(prefix="/api/tax/wfh", tags=["tax"])


@router.post("/", response_model=WFHEntryResponse, status_code=status.HTTP_201_CREATED)
@require_role("Editor", "Admin")
async def create_wfh_entry(
    entry: WFHEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WFHEntryResponse:
    """Create a new work-from-home entry for the current user."""
    service = TaxService(db)
    return service.create_wfh_entry(user_id=current_user.id, entry_data=entry)
```

**Database Queries:**
- Use SQLAlchemy ORM (no raw SQL unless necessary)
- Always use parameterized queries
- Optimize with indexes (defined in models)
- Use `db.query()` not `session.query()` (for consistency)

**Error Handling:**
```python
from fastapi import HTTPException, status

# Validation errors
if hours > 24:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Hours must be between 0 and 24"
    )

# Not found
if not entry:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"WFH entry {entry_id} not found"
    )

# Permission denied
if entry.user_id != current_user.id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cannot modify others' tax records"
    )
```

---

### Frontend (React/TypeScript)

**Style Guide:**
- Use ESLint + Prettier
- Prefer TypeScript over JavaScript (when feasible)
- Use functional components + hooks (no class components)

**Code Structure:**
```
frontend/
  src/
    main.tsx             # App entry point
    App.tsx              # Root component
    routes.tsx           # React Router config
    components/          # Reusable components
      ui/                # shadcn/ui components
      forms/
        LoginForm.tsx
        WFHEntryForm.tsx
      layouts/
        DashboardLayout.tsx
        AuthLayout.tsx
    pages/               # Page components
      Dashboard.tsx
      TaxRecords.tsx
      Financial.tsx
    hooks/               # Custom hooks
      useAuth.ts
      useWFHEntries.ts
    services/            # API clients
      api.ts             # Axios instance
      taxService.ts
      authService.ts
    utils/               # Helper functions
      formatters.ts
      validators.ts
    types/               # TypeScript types
      user.ts
      tax.ts
    styles/              # Global styles
      globals.css
```

**Naming Conventions:**
- Components: `PascalCase.tsx`
- Hooks: `useCamelCase.ts`
- Utils: `camelCase.ts`
- Types: `PascalCase` (interfaces/types)

**Example Component:**
```typescript
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useWFHEntries } from "@/hooks/useWFHEntries";

const wfhSchema = z.object({
  date: z.date(),
  hours: z.number().min(0).max(24),
  notes: z.string().max(500).optional(),
});

type WFHFormData = z.infer<typeof wfhSchema>;

export function WFHEntryForm() {
  const { createEntry, isLoading } = useWFHEntries();
  const { register, handleSubmit, formState: { errors } } = useForm<WFHFormData>({
    resolver: zodResolver(wfhSchema),
  });

  const onSubmit = async (data: WFHFormData) => {
    await createEntry(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        type="date"
        {...register("date")}
        error={errors.date?.message}
      />
      <Input
        type="number"
        step="0.5"
        {...register("hours", { valueAsNumber: true })}
        error={errors.hours?.message}
        placeholder="Hours worked"
      />
      <Button type="submit" disabled={isLoading}>
        {isLoading ? "Saving..." : "Add Entry"}
      </Button>
    </form>
  );
}
```

**State Management:**
- Use React Context for global state (auth, theme)
- Use TanStack Query for server state (API data)
- Use local state (useState) for component-level state

**API Calls:**
```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  withCredentials: true, // Include cookies
});

// Interceptor for auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Testing Standards

### Backend Testing

**Unit Tests (pytest):**
```python
# tests/unit/test_tax_service.py
import pytest
from datetime import date
from app.services.tax_service import TaxService
from app.schemas.tax import WFHEntryCreate

def test_calculate_wfh_deduction():
    """Test WFH deduction calculation."""
    service = TaxService(db=None)  # Mock DB if needed
    
    # Test case: 8 hours @ $0.67/hour = $5.36
    deduction = service.calculate_wfh_deduction(hours=8.0)
    assert deduction == 5.36


def test_validate_wfh_entry():
    """Test WFH entry validation."""
    service = TaxService(db=None)
    
    # Valid entry
    entry = WFHEntryCreate(date=date.today(), hours=8.0)
    assert service.validate_wfh_entry(entry) is True
    
    # Invalid: future date
    entry = WFHEntryCreate(date=date(2030, 1, 1), hours=8.0)
    with pytest.raises(ValueError):
        service.validate_wfh_entry(entry)
```

**Integration Tests (pytest + TestClient):**
```python
# tests/integration/test_tax_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_wfh_entry(auth_token):
    """Test WFH entry creation via API."""
    response = client.post(
        "/api/tax/wfh",
        json={"date": "2024-01-15", "hours": 8.0, "notes": "Full day"},
        cookies={"session_token": auth_token}
    )
    assert response.status_code == 201
    assert response.json()["hours"] == 8.0


def test_cannot_modify_others_tax_records(auth_token_user2):
    """Test RBAC: users cannot modify others' tax records."""
    # Create entry as user1
    entry = client.post("/api/tax/wfh", json={...}, cookies={...}).json()
    
    # Try to update as user2
    response = client.put(
        f"/api/tax/wfh/{entry['id']}",
        json={"hours": 10.0},
        cookies={"session_token": auth_token_user2}
    )
    assert response.status_code == 403
```

**Coverage Target:** 70% minimum for v1

---

### Frontend Testing (Vitest)

**Component Tests:**
```typescript
// src/components/__tests__/WFHEntryForm.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WFHEntryForm } from "../WFHEntryForm";

test("renders WFH entry form", () => {
  render(<WFHEntryForm />);
  expect(screen.getByPlaceholderText("Hours worked")).toBeInTheDocument();
});

test("validates hours input", async () => {
  render(<WFHEntryForm />);
  
  const input = screen.getByPlaceholderText("Hours worked");
  fireEvent.change(input, { target: { value: "30" } });
  
  await waitFor(() => {
    expect(screen.getByText("Hours must be between 0 and 24")).toBeInTheDocument();
  });
});
```

---

## Git Workflow

### Branch Strategy

**Main Branches:**
- `main` - Production-ready code (after v1.0)
- `develop` - Integration branch (active development)

**Feature Branches:**
- `feature/sprint-X-task-Y` - Sprint-specific tasks
- Example: `feature/sprint-2-tax-wfh-crud`

**Hotfix Branches:**
- `hotfix/issue-description`

### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Add or update tests
- `chore` - Build, dependencies, tooling

**Examples:**
```
feat(tax): implement WFH entry CRUD endpoints

- Add POST, GET, PUT, DELETE endpoints
- Implement per-user isolation
- Add audit logging for all operations

Closes #S2-T1

---

fix(auth): prevent login throttling bypass

Users could bypass throttling by changing IP.
Now throttling uses username+IP combination.

Fixes #ISSUE-123
```

### Pull Request Process

> **Note:** PR process will be established once development begins. For now, direct commits to `develop` are acceptable during Sprint 0.

1. Create feature branch from `develop`
2. Implement feature following Design-v1.md
3. Write tests (unit + integration)
4. Ensure all tests pass
5. Update documentation if needed
6. Create PR to `develop`
7. Code review (if applicable)
8. Merge to `develop`

---

## Database Migrations

### Alembic Workflow

**Create Migration:**
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add tax_wfh_entries table"

# Review generated migration in alembic/versions/
# Edit if needed (auto-generate isn't perfect)

# Apply migration
alembic upgrade head
```

**Rollback Migration:**
```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

**Migration Best Practices:**
- Always review auto-generated migrations
- Test migrations on local database before committing
- Include both `upgrade()` and `downgrade()` functions
- Add indexes in the migration, not just in models
- Consider data migrations separately (if needed)

---

## Code Review Checklist

**Security:**
- [ ] No hardcoded secrets or credentials
- [ ] Input validation present (Pydantic/Zod)
- [ ] RBAC checks on protected endpoints
- [ ] HTTP-only cookies for sessions
- [ ] Parameterized database queries (no SQL injection)

**Functionality:**
- [ ] Code aligns with Design-v1.md
- [ ] Handles edge cases (null, empty, invalid input)
- [ ] Error messages are user-friendly
- [ ] Audit logging for tax operations

**Testing:**
- [ ] Unit tests cover critical logic
- [ ] Integration tests cover API endpoints
- [ ] Tests pass locally

**Code Quality:**
- [ ] Follows coding standards (Black, ESLint)
- [ ] Clear variable/function names
- [ ] No unnecessary complexity
- [ ] Comments for non-obvious logic

**Documentation:**
- [ ] API endpoint documented (docstring)
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Known issues documented (if applicable)

---

## Issue Tracking

### Issue Categories

**Technical Issues:**
- Track in [KNOWN_ISSUES.md](./KNOWN_ISSUES.md)
- Use priority labels (Critical, High, Medium, Low)

**UI/UX Issues:**
- Track in [UI_ISSUES.md](./UI_ISSUES.md)
- Include screenshots/mockups when possible

**Sprint Tasks:**
- Track in [PROJECT_STATUS.md](./PROJECT_STATUS.md)
- Update status as tasks progress

### Reporting Issues

**Template:**
```markdown
### Issue #X: Brief Description

**Priority:** 🟡 High
**Category:** Security / Performance / UX / etc.
**Affects:** Module name
**Reported:** YYYY-MM-DD

**Description:**
- Detailed description
- Steps to reproduce (if applicable)

**Impact:**
- What breaks or degrades

**Mitigation/Workaround:**
- Temporary solution (if available)

**Planned Fix:**
- Sprint or version
```

---

## Documentation Updates

### When to Update Documentation

**Design-v1.md:**
- Never (locked after approval)
- Create Design-v2.md for redesigns

**PROJECT_STATUS.md:**
- After each sprint
- When tasks change status
- When new sprints are planned

**KNOWN_ISSUES.md:**
- When new issues discovered
- When issues resolved

**CHANGELOG.md:**
- After each release (v1.0, v1.1, etc.)

**README.md:**
- When project status changes
- When installation instructions change

---

## Release Process

> **Note:** Release process will be finalized before v1.0. This is a preliminary outline.

**Pre-Release Checklist:**
1. All sprint tasks completed
2. 70%+ test coverage achieved
3. Security audit completed (basic)
4. Performance testing completed
5. Documentation updated
6. CHANGELOG.md updated

**Release Steps:**
1. Create release branch: `release/vX.Y.Z`
2. Update version numbers (package.json, pyproject.toml, etc.)
3. Update CHANGELOG.md
4. Tag release: `git tag vX.Y.Z`
5. Merge to `main`
6. Deploy to production
7. Create GitHub release (if public repo)

---

## Questions & Clarifications

**When in doubt:**
- Review Design-v1.md
- Check KNOWN_ISSUES.md for existing issues
- Ask the user for clarification (never assume)

**Scope creep:**
- If a request exceeds v1 scope, defer to FUTURE_PLANS.md
- Suggest alternatives that align with current design
- Get user approval before expanding scope

---

## Contact & Communication

**User:** Final decision-maker, provide feedback and approvals  
**Developer/AI:** Propose solutions, implement approved designs  

**Communication Channels:**
- Sprint reviews (after each sprint)
- Design approvals (before implementation)
- Issue reports (as needed)

---

**Last Updated:** 2025-02-01  
**Next Review:** After Design-v1.md approval
