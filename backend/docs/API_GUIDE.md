# Home Management Platform - API Guide

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1` (Development)
**Documentation:** `http://localhost:8000/docs` (Swagger UI)

## Table of Contents

1. [Authentication](#authentication)
2. [Permissions & RBAC](#permissions--rbac)
3. [API Modules](#api-modules)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Testing with Swagger](#testing-with-swagger)

---

## Authentication

### Session-Based Authentication

The API uses **HTTP-only cookie-based sessions** with JWT tokens for security.

#### Login Flow

1. **POST /auth/login** - Authenticate with username/password
2. **POST /auth/verify-mfa** - Verify MFA code (if enabled)
3. Subsequent requests automatically include session cookie

**Example Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  },
  "requires_mfa": true,
  "message": "Login successful. Please verify MFA code."
}
```

#### MFA Verification (if required)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-mfa" \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

#### Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -b cookies.txt
```

---

## Permissions & RBAC

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Full system access | All permissions |
| **Editor** | Can create and modify data | Read + Write permissions (excludes admin operations) |
| **Reader** | Read-only access | Read-only permissions |

### Permission Matrix

| Module | Read | Write | Admin |
|--------|------|-------|-------|
| Auth | All | Admin only | Admin only |
| Tax | Authenticated users | Editor+ | Admin only |
| Financial | Authenticated users | Editor+ | Admin only |
| Assets | Authenticated users | Editor+ | Admin only |
| Projects | Authenticated users | Editor+ | Admin only |
| Knowledge | Authenticated users | Editor+ | Admin only |
| Meals | Authenticated users | Editor+ | Admin only |
| Dashboard | Authenticated users | N/A | Admin only (notifications) |
| Admin | Admin only | Admin only | Admin only |

### Permission Patterns

- `module:read` - Read access to module
- `module:write` - Write access to module
- `module:admin` - Admin access to module

**Example:** To create a recipe, user needs `meals:write` permission.

---

## API Modules

### 1. Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user (admin only) | Admin |
| POST | `/auth/login` | Login with credentials | No |
| POST | `/auth/verify-mfa` | Verify MFA code | Partial |
| POST | `/auth/logout` | Logout current session | Yes |
| GET | `/auth/me` | Get current user info | Yes |
| POST | `/auth/change-password` | Change password | Yes |

### 2. Tax Records (`/tax`)

#### Work From Home (WFH)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/tax/wfh` | Create WFH entry | tax:write |
| GET | `/tax/wfh` | List WFH entries | Authenticated |
| GET | `/tax/wfh/{id}` | Get WFH entry | Authenticated |
| PUT | `/tax/wfh/{id}` | Update WFH entry | tax:write |
| DELETE | `/tax/wfh/{id}` | Delete WFH entry | tax:write |
| GET | `/tax/wfh/summary` | Get FY summary | Authenticated |
| GET | `/tax/wfh/export` | Export ATO format | Authenticated |

#### Work Travel

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/tax/travel` | Create travel entry | tax:write |
| GET | `/tax/travel` | List travel entries | Authenticated |
| GET | `/tax/travel/{id}` | Get travel entry | Authenticated |
| PUT | `/tax/travel/{id}` | Update travel entry | tax:write |
| DELETE | `/tax/travel/{id}` | Delete travel entry | tax:write |
| GET | `/tax/travel/summary` | Get FY summary | Authenticated |
| GET | `/tax/travel/export` | Export ATO format | Authenticated |

**Example: Create WFH Entry**
```bash
curl -X POST "http://localhost:8000/api/v1/tax/wfh" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "date": "2026-02-13",
    "hours_worked": 8.0
  }'
```

### 3. Financial Management (`/financial`)

#### Income Sources (5 endpoints)
#### Bank Accounts (5 endpoints)
#### Expense Categories (5 endpoints)
#### Expenses (5 endpoints)
#### Utilities (6 endpoints)
#### Budget Calculation (2 endpoints)

**Total: 28 endpoints**

**Example: Calculate Budget**
```bash
curl -X GET "http://localhost:8000/api/v1/financial/budget/calculate?frequency=monthly" \
  -b cookies.txt
```

**Response:**
```json
{
  "frequency": "monthly",
  "total_income": 5000.00,
  "total_expenses": 3500.00,
  "net_income": 1500.00,
  "accounts": [...],
  "transfers_needed": [...]
}
```

### 4. Assets & Documents (`/assets`)

#### Insurance Policies (8 endpoints)
- CRUD operations
- Renewal alerts
- Cost summary

#### Documents (10 endpoints)
- CRUD operations
- File upload integration
- Expiry alerts
- Search

**Total: 18 endpoints**

**Example: Get Renewal Alerts**
```bash
curl -X GET "http://localhost:8000/api/v1/assets/insurance/renewal-alerts?days_threshold=30" \
  -b cookies.txt
```

### 5. Projects & Tasks (`/projects`)

#### Priority Items (7 endpoints)
- Cost-benefit scoring
- Convert to project

#### Projects (7 endpoints)
- Status workflow
- Cost tracking

#### Quotes (7 endpoints)
- Quote comparison
- Expiry tracking

**Total: 21 endpoints**

**Example: Create Priority Item**
```bash
curl -X POST "http://localhost:8000/api/v1/projects/priorities" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Fix Roof Leak",
    "description": "Water damage in bedroom",
    "severity": 5,
    "frequency": 4,
    "estimated_cost": 2500.00
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Fix Roof Leak",
  "benefit_score": 9,
  "cost_score": 4,
  "net_score": 5,
  "status": "identified"
}
```

### 6. Knowledge Base (`/knowledge`)

#### Articles (7 endpoints)
- 8 article types with flexible JSONB schemas
- Full-text search
- Password encryption for TechDevice articles

#### Attachments (3 endpoints)
- Link files to articles

**Total: 10 endpoints**

**Example: Search Knowledge**
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"query": "wifi password"}'
```

### 7. Meal Planner (`/meals`)

#### Recipes (5 endpoints)
- CRUD with ingredients
- Search by name/ingredient

#### Week Plans (7 endpoints)
- Weekly meal planning
- Current week view
- Shopping list generation

**Total: 13 endpoints**

**Example: Generate Shopping List**
```bash
curl -X GET "http://localhost:8000/api/v1/meals/week-plans/{plan_id}/shopping-list" \
  -b cookies.txt
```

**Response:**
```json
{
  "week_starting": "2026-02-10",
  "items": [
    {
      "ingredient": "chicken breast",
      "quantity": "800 g",
      "recipe_names": ["Chicken Stir Fry", "Grilled Chicken"]
    },
    {
      "ingredient": "salt",
      "quantity": "As needed",
      "recipe_names": ["All recipes"]
    }
  ],
  "total_items": 15
}
```

### 8. Dashboard (`/dashboard`)

#### Dashboard Widgets (8 endpoints)
- Complete summary
- Individual widgets (alerts, priorities, projects, meals, financial, tax, notifications, stats)

#### Notifications (10 endpoints)
- CRUD operations
- Mark as read/unread
- Dismiss functionality
- Auto-generation (admin)

#### Global Search (2 endpoints)
- Cross-module search
- Quick search for autocomplete

**Total: 20 endpoints**

**Example: Get Dashboard Summary**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/summary" \
  -b cookies.txt
```

**Example: Global Search**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/search?q=roof&modules=projects,knowledge" \
  -b cookies.txt
```

### 9. Admin (`/admin`)

#### User Management (7 endpoints)
- List/get/update/delete users
- Role management
- Activate/deactivate
- MFA reset

#### System Statistics (2 endpoints)
- System-wide stats
- User-specific stats

#### Enhanced Audit Logs (3 endpoints)
- By user, module, or action

#### Backup (1 endpoint)
- `GET /admin/backup/download` — streams a ZIP archive containing a `pg_dump` SQL file and all uploaded files; logs a `BACKUP_DOWNLOAD` audit event at WARNING severity

**Total: 13 endpoints**

**Example: List Users**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users?role=editor&is_active=true" \
  -b cookies.txt
```

**Example: Update User Role**
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/{user_id}/role" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"role": "editor"}'
```

### 10. Audit Logs (`/audit`)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/audit` | Get all audit logs (with filters) | Admin |
| GET | `/audit/tax` | Get user's tax audit logs | Authenticated |
| GET | `/admin/audit/users/{id}` | Get user's all logs | Admin |
| GET | `/admin/audit/modules/{module}` | Get logs by module | Admin |
| GET | `/admin/audit/actions/{action}` | Get logs by action | Admin |

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Not authenticated |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

**Validation Error Example:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Consider implementing for production:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Testing with Swagger

### Access Swagger UI

Navigate to: `http://localhost:8000/docs`

### Interactive Testing

1. Click "Authorize" button
2. Login via `/auth/login` endpoint
3. Copy session cookie from browser DevTools
4. Use "Try it out" on any endpoint
5. View request/response details

### Swagger Features

- **Interactive documentation** - Test endpoints directly
- **Schema validation** - See request/response schemas
- **Authentication** - Login and test authenticated endpoints
- **Code generation** - Generate client code in multiple languages

---

## API Summary Statistics

| Module | Endpoints | Authentication | RBAC |
|--------|-----------|----------------|------|
| Authentication | 6 | Partial | Yes |
| Tax Records | 14 | Yes | Yes |
| Financial | 28 | Yes | Yes |
| Assets & Documents | 18 | Yes | Yes |
| Projects & Tasks | 21 | Yes | Yes |
| Knowledge Base | 10 | Yes | Yes |
| Meal Planner | 13 | Yes | Yes |
| Dashboard | 22 | Yes | Partial |
| Admin | 14 | Yes | Admin only |
| Audit Logs | 5 | Yes | Mixed |
| **Total** | **151 endpoints** | - | - |

---

## Best Practices

1. **Always authenticate** - Include session cookie in all requests
2. **Handle errors** - Check status codes and error messages
3. **Use pagination** - Limit large result sets with limit/offset
4. **Validate input** - Check Swagger schemas before requests
5. **Check permissions** - Verify user has required role/permission
6. **Log out properly** - Call `/auth/logout` when done
7. **Use HTTPS** - Always use HTTPS in production
8. **Rotate secrets** - Regularly update JWT secrets and encryption keys

---

## Next Steps

- Review [Deployment Guide](./DEPLOYMENT_GUIDE.md) for production setup
- Check [Database Schema](./DATABASE_SCHEMA.md) for data models
- See [Permission Matrix](./PERMISSIONS.md) for detailed RBAC rules
- Read [Security Guide](../PASSWORD_SECURITY.md) for security best practices

---

**Last Updated:** 2026-02-13
**API Version:** 1.0.0
