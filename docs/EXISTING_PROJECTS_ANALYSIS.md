# Existing Projects Analysis & Porting Strategy

## Overview

Analysis of three existing projects for integration into the Home Management Platform:
1. **DockerMate** - Container management (complete reference)
2. **Meal-Planner** - Recipe management and shopping lists (Sprint 7)
3. **Cost-Benefit-Decision** - Priority scoring for repairs (Sprint 5)

**Analysis Date:** 2026-02-12
**Analyst:** Claude (AI Development Assistant)

---

## 1. DockerMate - Production-Ready Patterns

**Location:** `/home/bryan/VSCode/DockerMate/`
**Stack:** Python/Flask + SQLAlchemy + Alpine.js + SQLite
**Status:** Production-ready, extensively tested

### 🔐 Already Leveraged

✅ **Password Validation** - Adapted from `backend/auth/password_manager.py`
- Weak pattern detection (Password123, Admin2024, etc.)
- Sequential pattern detection (12345, qwerty)
- Repeated character detection (aaaa, 1111)
- Battle-tested through production use

### 🎯 High-Priority Patterns to Leverage

#### 1. Session Management with Token Hashing
**File:** `backend/auth/session_manager.py`

```python
# DON'T store tokens plain-text - hash them!
session_token = SessionManager.create_session(...)
# Returns: plain token (shown to user in cookie)
# Stores: SHA-256 hash in database
```

**Benefits:**
- Even if database compromised, tokens are useless
- Timing attack safe
- Automatic cleanup of expired sessions
- IP tracking for audit

**Action:** Implement for IMP-006 enhancement (token persistence)

---

#### 2. Exception Hierarchy
**File:** `backend/utils/exceptions.py`

```python
class HomeManagementException(Exception):
    """Base exception for all custom exceptions"""
    pass

class ResourceNotFoundError(HomeManagementException):
    """Resource not found (404)"""
    pass

class ValidationError(HomeManagementException):
    """Invalid input data (400)"""
    pass

class AuthenticationError(HomeManagementException):
    """Authentication failed (401)"""
    pass

class PermissionError(HomeManagementException):
    """Insufficient permissions (403)"""
    pass
```

**Action:** Create `backend/app/exceptions.py` for IMP-008

---

#### 3. Hardware Detection for Resource Tuning
**File:** `backend/utils/hardware_detector.py`

**Profiles:**
- RASPBERRY_PI: ≤4 cores, ≤8GB RAM → Conservative limits
- LOW_END: ≤4 cores, ≤16GB RAM → Moderate limits
- MEDIUM_SERVER: ≤16 cores, ≤64GB RAM → Standard limits
- HIGH_END: >32 cores, >128GB RAM → Aggressive tuning

**Use Cases:**
- Database connection pool sizing
- File upload concurrency
- Background job limits
- Cache sizes

**Action:** Create `backend/app/utils/hardware.py` for platform tuning

---

#### 4. Security Headers Implementation
**File:** `app.py` (lines 173-227)

```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; ..."
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

**Action:** Add to `backend/app/main.py` middleware

---

#### 5. Rate Limiting Patterns
**File:** `backend/extensions.py`

```python
from flask_limiter import Limiter
limiter = Limiter(key_func=get_remote_address)

# Shared limit across mutation operations
mutation_limit = limiter.shared_limit("30 per minute", scope="mutation_ops")

# Usage:
@router.post("/auth/login")
@limiter.limit("5 per 15 minutes")
def login(): ...
```

**FastAPI Equivalent:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Action:** Implement for IMP-006 enhancement (login throttling)

---

### 📋 Medium-Priority Patterns

1. **Singleton Pattern** - `backend/utils/docker_client.py`
   - Pattern for external service connections
   - Automatic reconnection logic
   - Health checking

2. **Configuration Management** - `config.py`
   - Centralized settings with environment variables
   - Directory creation helpers
   - Duration parsing utilities

3. **Alpine.js Frontend Patterns** - `frontend/templates/`
   - Simple reactive UI without React overhead
   - Form handling with validation
   - Modal/overlay patterns

4. **Testing Patterns** - `tests/unit/`
   - Fixture-based setup/teardown
   - Comprehensive edge case coverage
   - Security-focused assertions

---

## 2. Meal-Planner - Port Required (Sprint 7)

**Location:** `/home/bryan/VSCode/Meal-Planner/`
**Stack:** Node.js/Express + JSON file storage + Missing frontend
**Status:** Incomplete - algorithms missing, frontend missing

### ⚠️ Critical Issue

**GitHub Issue #1:** "Shopping List Item Combining Failing"
- **Problem:** "Baby spinach 1 cup, 2 cups, 1 cup" not consolidated
- **Root Cause:** Ingredient consolidation algorithm NOT implemented
- **Impact:** Core feature broken/missing

### 📊 What Exists

**20 Default Recipes** - Complete, well-documented
**File:** `server.js` (lines 38-327)

```javascript
// Example recipe structure:
{
  name: "Chicken Fried Rice",
  steps: "1. Heat 1 tablespoon of oil...<br>2. Add diced chicken...",
  ingredients: [
    {name: "Chicken breast", quantity: "300 g"},
    {name: "Rice (cooked)", quantity: "3 cups"},
    {name: "Carrot", quantity: "1 medium"},
    {name: "Peas", quantity: "1 cup"},
    {name: "Eggs", quantity: "2"},
    {name: "Soy sauce", quantity: "2 tablespoons"},
    {name: "Olive oil", quantity: "As needed"}  // Pantry staple
  ]
}
```

**Recipes Inventory:**
- 20 recipes total
- 175 ingredient instances
- Diverse categories: chicken (7), pork (4), beef (4), salmon (2), vegetarian (3)

### ❌ What's Missing

1. **Ingredient Consolidation Algorithm**
   - Must combine: "1 cup" + "2 cups" + "1 cup" = "4 cups"
   - Handle mixed units: cups, grams, tablespoons, teaspoons
   - Special handling: "As needed", "To taste", "Optional"

2. **Measurement Conversion (Australian)**
   - Cup → Gram conversions vary by ingredient:
     - 1 cup rice ≠ 1 cup spinach (density difference)
     - Need ingredient-specific conversion tables
   - Metric system preference (README states "convert cups to grams")

3. **Shopping List Generation**
   - Aggregate ingredients across multiple meals
   - Convert to standard units
   - Mark pantry staples separately
   - Format for printing

4. **Frontend Code**
   - Server expects `index.html` at root - NOT IN REPO
   - All UI must be built from scratch
   - No React components to port

5. **Authentication**
   - Comment on line 392: "In production, this should verify admin PIN before saving"
   - NO auth on POST /api/data endpoint

### 🎯 Port Strategy for Sprint 7

#### Phase 1: Data Migration
```python
# Create SQLAlchemy models
class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    steps: Mapped[str] = mapped_column(Text)  # HTML formatting preserved
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[str] = mapped_column(String(255))  # "300 g", "1 cup"
    unit: Mapped[str | None] = mapped_column(String(50))  # Normalized: g, ml, cup
    canonical_amount: Mapped[float | None]  # For consolidation
```

**Migration Script:**
```python
# Read server.js DEFAULT_MEALS array (lines 38-327)
# Parse JavaScript to extract 20 recipes
# Insert into PostgreSQL with proper normalization
```

#### Phase 2: Implement Missing Algorithms

**1. Quantity Parser**
```python
def parse_quantity(quantity_str: str) -> tuple[float, str]:
    """
    Parse "300 g" → (300.0, "g")
    Parse "1 cup" → (1.0, "cup")
    Parse "As needed" → (None, "as_needed")
    Parse "To taste" → (None, "to_taste")
    Parse "2 tablespoons" → (2.0, "tbsp")
    """
    # Regex patterns for each format
    # Special case handling
    # Unit normalization
```

**2. Unit Conversion Table**
```python
UNIT_CONVERSIONS = {
    # Volume
    "cup": {"ml": 250},
    "tablespoon": {"ml": 15, "tbsp": 1},
    "teaspoon": {"ml": 5, "tsp": 1},

    # Weight (ingredient-specific)
    "rice": {"cup_to_g": 185},
    "spinach": {"cup_to_g": 30},  # Loose packed
    "cheese": {"cup_to_g": 110},  # Grated
    # ... more ingredients
}

def convert_unit(amount: float, from_unit: str, to_unit: str, ingredient: str = None):
    """Convert between units, ingredient-aware for density"""
    # Lookup conversion factor
    # Apply conversion
    # Return (new_amount, new_unit)
```

**3. Ingredient Consolidation**
```python
def consolidate_ingredients(recipes: List[Recipe]) -> List[ShoppingListItem]:
    """
    Solve Issue #1: Combine "1 cup + 2 cups + 1 cup = 4 cups"
    """
    ingredient_map = defaultdict(lambda: {"amount": 0, "unit": None})

    for recipe in recipes:
        for ingredient in recipe.ingredients:
            amount, unit = parse_quantity(ingredient.quantity)

            # Special handling
            if unit in ("as_needed", "to_taste", "optional"):
                ingredient_map[ingredient.name]["pantry_staple"] = True
                continue

            # Normalize unit (cups → grams if possible)
            if unit == "cup" and ingredient.name.lower() in UNIT_CONVERSIONS:
                amount, unit = convert_unit(amount, "cup", "g", ingredient.name)

            # Consolidate
            if ingredient_map[ingredient.name]["unit"] == unit:
                ingredient_map[ingredient.name]["amount"] += amount
            else:
                # Unit mismatch - needs manual handling or conversion
                pass

    return format_shopping_list(ingredient_map)
```

#### Phase 3: API Endpoints

```python
# Recipe CRUD
POST   /api/recipes                    # Create recipe (admin)
GET    /api/recipes                    # List all recipes
GET    /api/recipes/{id}               # Get recipe details
PUT    /api/recipes/{id}               # Update recipe (admin)
DELETE /api/recipes/{id}               # Delete recipe (admin)

# Meal Planning
POST   /api/meal-plans                 # Create weekly plan
GET    /api/meal-plans/{week_start}    # Get plan for week
PUT    /api/meal-plans/{week_start}    # Update weekly plan
DELETE /api/meal-plans/{week_start}    # Clear weekly plan

# Shopping List
GET    /api/meal-plans/{week_start}/shopping-list  # Generate from week plan
POST   /api/shopping-lists             # Save custom list
GET    /api/shopping-lists/{id}        # Retrieve saved list
```

#### Phase 4: React Frontend

**Components to Build:**
```
<MealPlannerPage>
  <Tabs>
    <WeekPlannerTab>
      <DaySelector day="Monday">
        <RecipeDropdown recipes={allRecipes} />
      </DaySelector>
      ...
    </WeekPlannerTab>

    <RecipesTab>
      <RecipeGrid recipes={allRecipes}>
        <RecipeCard recipe={recipe}>
          <PrintButton />
        </RecipeCard>
      </RecipeGrid>
    </RecipesTab>

    <ManageMealsTab authenticated={isAdmin}>
      <RecipeForm onSubmit={createRecipe} />
      <RecipeList editable={true} />
    </ManageMealsTab>
  </Tabs>

  <ShoppingList items={consolidatedIngredients}>
    <PrintButton />
    <ExportButton format="pdf" />
  </ShoppingList>
</MealPlannerPage>
```

### 📌 Key Decisions for Sprint 7

1. **Unit Conversion Strategy**
   - Option A: Build comprehensive conversion tables
   - Option B: Keep units as-is, warn user of mixed units
   - **Recommendation:** Option A with fallback to B for unknown ingredients

2. **Pantry Staple Handling**
   - Items like "Olive oil: As needed" appear 15+ times
   - **Recommendation:** Mark as "Always in pantry" instead of quantities

3. **Default Recipes**
   - Original has 20 recipes pre-loaded
   - Design doc says "start with empty database"
   - **Recommendation:** Offer as optional seed data (admin can bulk import)

4. **Frontend Framework**
   - React + Tailwind (match Home Management Platform style)
   - Reuse DockerMate's dark theme color palette

---

## 3. Cost-Benefit-Decision - Port Required (Sprint 5)

**Location:** `/home/bryan/VSCode/Cost-Benefit-Decision/`
**Stack:** Python/FastAPI + SQLite + Vanilla JavaScript
**Status:** Feature-complete, production-ready

### ✅ Strengths

1. **Already FastAPI** - Minimal porting effort!
2. **Clean algorithm** - Easy to understand and maintain
3. **Simple UI** - Intuitive, responsive design
4. **Well-tested** - Edge cases covered

### 🧮 Core Algorithm (EXCELLENT)

**File:** `backend/main.py` (lines 62-69)

```python
def compute_scores(cost: float, severity: int, frequency: int) -> tuple[int, int, int]:
    # Benefit = how important is this issue?
    benefit = severity + frequency  # Range: 2-10

    # Cost score = logarithmic normalization
    # $10 → 2, $100 → 3, $1000 → 4
    if cost <= 0:
        cost_score = 1
    else:
        cost_score = max(1, int(round(math.log10(cost))) + 1)

    # Net score = ROI indicator
    # Positive = good ROI (high impact, lower cost)
    # Negative = expensive relative to benefit
    net = benefit - cost_score

    return benefit, cost_score, net
```

**Algorithm Insights:**
- **Logarithmic cost** brilliant for diverse budgets ($10 fix vs $10k project)
- **Simple inputs** (1-5 scales) match human intuition
- **Clear output** (net score) enables prioritization
- **No weighting** treats severity and frequency equally

**Example Calculations:**

| Item | Cost | Severity | Frequency | Benefit | Cost Score | Net Score | Priority |
|------|------|----------|-----------|---------|------------|-----------|----------|
| Leaky faucet | $50 | 2 | 5 | 7 | 2 | **+5** | High ✅ |
| Roof replacement | $15000 | 5 | 1 | 6 | 5 | **+1** | Medium |
| Cosmetic paint | $500 | 1 | 1 | 2 | 3 | **-1** | Low ❌ |
| Security system | $2000 | 5 | 5 | 10 | 4 | **+6** | Critical ✅✅ |

### 🎯 Port Strategy for Sprint 5

#### Phase 1: Database Schema Extension

**Current Schema (SQLite):**
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    description TEXT,
    cost REAL,
    severity INTEGER,
    frequency INTEGER,
    benefit_score INTEGER,
    cost_score INTEGER,
    net_score INTEGER,
    created_at INTEGER
)
```

**Enhanced Schema (PostgreSQL):**
```python
class PriorityItem(Base):
    __tablename__ = "priority_items"

    # Existing fields
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    cost: Mapped[float]  # Estimated cost
    severity: Mapped[int]  # 1-5 scale
    frequency: Mapped[int]  # 1-5 scale

    # Calculated scores (denormalized for query performance)
    benefit_score: Mapped[int]
    cost_score: Mapped[int]
    net_score: Mapped[int]

    # NEW FIELDS for Home Management Platform
    status: Mapped[str] = mapped_column(
        Enum("pending", "in_progress", "completed", "rejected", "on_hold")
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    category: Mapped[str | None] = mapped_column(String(50))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    # Tracking
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    completed_at: Mapped[datetime | None]

    # Additional metadata
    notes: Mapped[str | None] = mapped_column(Text)
    actual_cost: Mapped[float | None]  # Track budget variance
    estimated_duration: Mapped[int | None]  # Hours
    tags: Mapped[list[str]] = mapped_column(JSON)  # ["plumbing", "urgent"]
```

#### Phase 2: "Convert to Project" Workflow

**Design Doc Requirement (DESIGN-v1.md):**
> "Priority items can be 'converted to project' which creates a project record and links the priority item via project.priority_item_id"

**Implementation:**
```python
@router.post("/priority-items/{id}/convert-to-project")
def convert_to_project(
    id: int,
    project_data: ProjectConversionData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Convert priority item → Create project

    1. Get priority item
    2. Create project with:
       - Name from priority item description
       - Budget from priority item cost
       - Priority from net_score
       - Link back to priority item
    3. Update priority item status → "converted"
    4. Return new project
    """
    priority_item = db.query(PriorityItem).filter_by(id=id).first()

    project = Project(
        name=project_data.name or priority_item.description,
        description=priority_item.notes or "",
        status="planning",
        budget=priority_item.cost,
        priority_item_id=priority_item.id,  # Link back
        created_by=current_user.id
    )

    priority_item.status = "converted"
    priority_item.project_id = project.id

    db.add(project)
    db.commit()

    return ProjectOut.model_validate(project)
```

#### Phase 3: UI Integration

**React Components:**
```tsx
<PriorityItemsList>
  <PriorityItemCard item={item}>
    <ScoreDisplay benefit={item.benefit_score} cost={item.cost_score} net={item.net_score} />
    <ActionButtons>
      <ConvertToProjectButton onClick={() => convertToProject(item.id)} />
      <MarkCompleteButton onClick={() => markComplete(item.id)} />
      <DeleteButton onClick={() => deleteItem(item.id)} />
    </ActionButtons>
  </PriorityItemCard>
</PriorityItemsList>

<PriorityItemForm onSubmit={createPriorityItem}>
  <TextInput label="Description" />
  <NumberInput label="Cost ($)" min={0} />
  <RangeInput label="Severity (1-5)" min={1} max={5} />
  <RangeInput label="Frequency (1-5)" min={1} max={5} />
  <CategorySelect categories={["plumbing", "electrical", "cosmetic", ...]} />
</PriorityItemForm>

<HelpModal>
  <h2>How Scoring Works</h2>
  <p>Benefit = Severity + Frequency</p>
  <p>Cost Score = log10(cost) + 1</p>
  <p>Net Score = Benefit - Cost Score</p>
  <p>Higher net scores = better ROI</p>
</HelpModal>
```

**Reuse Existing CSS:**
- Dark theme from `frontend/styles.css`
- Grid layout pattern (2-column: form + list)
- Table styling for priority list
- Help modal pattern

#### Phase 4: Algorithm Enhancements

**Option 1: Add Time Decay (Aging Boost)**
```python
def compute_scores_with_aging(cost, severity, frequency, created_at):
    benefit = severity + frequency
    cost_score = max(1, int(round(math.log10(cost))) + 1)

    # Boost older items (increases urgency over time)
    age_days = (datetime.utcnow() - created_at).days
    age_boost = min(1.5, 1.0 + (age_days / 365))  # Cap at +50%

    net = (benefit - cost_score) * age_boost
    return benefit, cost_score, net
```

**Option 2: Multiplicative Benefit**
```python
benefit = severity * frequency  # Range: 1-25
# Emphasizes items that are BOTH severe AND frequent
# Example: severity=5, frequency=5 → 25 (vs additive: 10)
```

**Recommendation:** Keep additive model, optionally add aging boost as filter

---

## 4. Cross-Project Learnings

### Common Patterns Across All 3 Projects

1. **FastAPI/Flask Backend** - All use Python web frameworks
2. **SQLite/JSON Persistence** - Simple file-based storage
3. **Dark Theme UI** - Consistent dark color palette
4. **Admin-Only Mutations** - Non-public write operations
5. **Single-Container Deployment** - Docker with Nginx

### Unified Architecture for Home Management Platform

```
┌─────────────────────────────────────────────────────────────┐
│                  Home Management Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Backend: Python/FastAPI + PostgreSQL + SQLAlchemy          │
│  - Auth: DockerMate session + password patterns ✅           │
│  - Projects: Cost-Benefit algorithm + workflow              │
│  - Meal Planner: Recipe management + consolidation          │
│  - Tax Records: ATO-compliant tracking                      │
│  - Files: Upload service with validation                    │
│  - Audit: 5-year retention for tax/auth                     │
│                                                               │
│  Frontend: React + Tailwind CSS                             │
│  - Dark theme (DockerMate color palette)                    │
│  - Component library (reusable across modules)              │
│  - State management (React Context + React Query)           │
│  - Responsive design (mobile-friendly)                      │
│                                                               │
│  Deployment: Docker Compose                                 │
│  - Multi-container (app, db, nginx)                         │
│  - DockerMate network patterns                              │
│  - Health checks + monitoring                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Priorities

### Immediate (Sprint 1-2)
- [x] Password validation from DockerMate ✅ **DONE**
- [ ] Exception hierarchy from DockerMate
- [ ] Security headers from DockerMate
- [ ] Rate limiting from DockerMate
- [ ] Hardware detection from DockerMate

### Sprint 5 (Projects Module)
- [ ] Port Cost-Benefit algorithm
- [ ] Create priority_items table
- [ ] Implement "Convert to Project" workflow
- [ ] Build React UI for priority items
- [ ] Add project management CRUD

### Sprint 7 (Meal Planner Module)
- [ ] Fix Issue #1: Ingredient consolidation algorithm
- [ ] Build measurement conversion tables
- [ ] Create recipe database schema
- [ ] Migrate 20 default recipes
- [ ] Build React meal planner UI
- [ ] Implement shopping list generation

---

## 6. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Meal Planner Issue #1** (consolidation broken) | High | Implement from scratch with comprehensive tests |
| **Missing frontend** (Meal Planner) | Medium | Budget extra time for UI development |
| **Unit conversion complexity** | Medium | Start with basic conversions, expand iteratively |
| **Algorithm porting** (Cost-Benefit) | Low | Already Python/FastAPI, minimal work |
| **Auth integration** | Low | Patterns established in DockerMate |

---

## 7. Code Reuse Checklist

### From DockerMate
- [x] Password validation logic ✅
- [ ] Session manager (token hashing)
- [ ] Exception hierarchy
- [ ] Security headers
- [ ] Rate limiting
- [ ] Hardware detection
- [ ] Configuration management
- [ ] Testing patterns

### From Cost-Benefit-Decision
- [ ] Priority scoring algorithm
- [ ] Pydantic schemas (ItemIn/ItemOut)
- [ ] FastAPI endpoint patterns
- [ ] CSS dark theme
- [ ] Form layouts
- [ ] Table components

### From Meal-Planner
- [ ] 20 default recipes (data only)
- [ ] Recipe data structure
- [ ] Ingredient format
- [ ] Server.js API patterns (adapt to FastAPI)

---

## 8. Documentation References

**DockerMate:**
- Design docs: `DESIGN-v1.md`, `DESIGN-v2.md`
- Deployment: `DOCKER_COMPOSE_GUIDE.md`
- Auth code: `backend/auth/`
- Tests: `tests/unit/`

**Meal-Planner:**
- README: Feature overview, measurement types
- Server: `server.js` (recipes + API)
- Issue #1: Consolidation bug

**Cost-Benefit-Decision:**
- Algorithm: `backend/main.py`
- UI: `frontend/app.js`, `frontend/index.html`
- Docker: `Dockerfile`, `nginx/nginx.conf`

---

**Last Updated:** 2026-02-12
**Next Review:** After Sprint 5 and Sprint 7 completion
**Maintained By:** Development Team

