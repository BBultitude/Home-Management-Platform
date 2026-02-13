# Database Schema Reference

**Database:** PostgreSQL 14+
**ORM:** SQLAlchemy 2.0
**Migrations:** Alembic

---

## Schema Overview

The Home Management Platform uses **22 tables** across **9 modules**:

1. **Core** (3 tables): users, trusted_devices, audit_logs
2. **Files** (1 table): files
3. **Tax** (2 tables): tax_wfh_entries, tax_travel_entries
4. **Financial** (5 tables): income_sources, bank_accounts, expense_categories, expenses, utilities
5. **Assets** (2 tables): insurance_policies, documents
6. **Projects** (3 tables): priority_items, projects, quotes
7. **Knowledge** (2 tables): knowledge_articles, knowledge_attachments
8. **Meals** (3 tables): recipes, ingredients, week_plans
9. **Dashboard** (1 table): notifications

---

## Table Details

### Core Module

#### users
- **Primary Key:** id (UUID)
- **Unique:** username, email
- **Indexes:** username, email
- **Fields:** username, email, password_hash, full_name, role (enum), is_active, mfa_enabled, mfa_secret, created_at, updated_at, last_login

#### trusted_devices
- **Primary Key:** id (UUID)
- **Foreign Keys:** user_id → users.id
- **Indexes:** user_id, fingerprint
- **Fields:** user_id, device_name, fingerprint, ip_address, user_agent, last_used, expires_at, created_at

#### audit_logs
- **Primary Key:** id (UUID)
- **Foreign Keys:** user_id → users.id (nullable)
- **Indexes:** user_id, action, module, created_at
- **Fields:** user_id, action (enum), module (enum), details, metadata (JSONB), severity (enum), created_at

### Files Module

#### files
- **Primary Key:** id (UUID)
- **Indexes:** category, uploaded_by, created_at
- **Fields:** filename, original_filename, mime_type, size_bytes, category (enum), file_path, uploaded_by, created_at, updated_at

### Tax Module

#### tax_wfh_entries
- **Primary Key:** id (UUID)
- **Indexes:** date
- **Fields:** date, hours_worked, created_at, updated_at

#### tax_travel_entries
- **Primary Key:** id (UUID)
- **Indexes:** date
- **Fields:** date, from_location, to_location, distance_km, purpose, created_at, updated_at

### Financial Module

#### income_sources
- **Primary Key:** id (UUID)
- **Fields:** name, description, amount, frequency (enum), is_primary, created_at, updated_at

#### bank_accounts
- **Primary Key:** id (UUID)
- **Fields:** name, account_type (enum), current_balance, interest_rate, created_at, updated_at

#### expense_categories
- **Primary Key:** id (UUID)
- **Foreign Keys:** bank_account_id → bank_accounts.id
- **Indexes:** bank_account_id
- **Fields:** name, description, budgeted_amount, bank_account_id, created_at, updated_at

#### expenses
- **Primary Key:** id (UUID)
- **Foreign Keys:** category_id → expense_categories.id
- **Indexes:** category_id, expense_date
- **Fields:** category_id, description, amount, expense_date, frequency (enum), created_at, updated_at

#### utilities
- **Primary Key:** id (UUID)
- **Indexes:** utility_type, bill_date
- **Fields:** utility_type (enum), provider, bill_date, usage_amount, usage_unit, total_cost, cost_per_unit, created_at, updated_at

### Assets Module

#### insurance_policies
- **Primary Key:** id (UUID)
- **Indexes:** renewal_date, policy_type
- **Fields:** policy_name, policy_type (enum), provider, policy_number, premium_amount, premium_frequency (enum), renewal_date, coverage_details, created_at, updated_at

#### documents
- **Primary Key:** id (UUID)
- **Foreign Keys:** file_id → files.id (nullable)
- **Indexes:** document_type, expiry_date
- **Fields:** title, description, document_type (enum), file_id, expiry_date, tags (ARRAY), created_at, updated_at

### Projects Module

#### priority_items
- **Primary Key:** id (UUID)
- **Foreign Keys:** project_id → projects.id (nullable)
- **Indexes:** status, net_score, project_id
- **Fields:** name, description, severity, frequency, estimated_cost, benefit_score, cost_score, net_score, status (enum), project_id, created_at, updated_at

#### projects
- **Primary Key:** id (UUID)
- **Foreign Keys:** originating_priority_id → priority_items.id (nullable)
- **Indexes:** status, originating_priority_id
- **Fields:** name, description, status (enum), estimated_cost, actual_cost, completion_percentage, notes, originating_priority_id, created_at, updated_at

#### quotes
- **Primary Key:** id (UUID)
- **Foreign Keys:** project_id → projects.id (nullable)
- **Indexes:** project_id, expires_at
- **Fields:** project_id, contractor_name, contractor_email, contractor_phone, amount, notes, expires_at, is_selected, created_at, updated_at

### Knowledge Module

#### knowledge_articles
- **Primary Key:** id (UUID)
- **Indexes:** article_type, search_vector (GIN)
- **Fields:** title, description, article_type (enum), data (JSONB), tags (ARRAY), search_vector (TSVECTOR), created_at, updated_at

#### knowledge_attachments
- **Primary Key:** id (UUID)
- **Foreign Keys:** article_id → knowledge_articles.id, file_id → files.id
- **Indexes:** article_id, file_id
- **Fields:** article_id, file_id

### Meals Module

#### recipes
- **Primary Key:** id (UUID)
- **Indexes:** name
- **Fields:** name, steps, created_at, updated_at

#### ingredients
- **Primary Key:** id (UUID)
- **Foreign Keys:** recipe_id → recipes.id (CASCADE)
- **Indexes:** recipe_id, name
- **Fields:** recipe_id, name, quantity, sort_order

#### week_plans
- **Primary Key:** id (UUID)
- **Foreign Keys:** monday_meal_id...sunday_meal_id → recipes.id (SET NULL)
- **Unique:** week_starting
- **Indexes:** week_starting
- **Fields:** week_starting, monday_meal_id, tuesday_meal_id, wednesday_meal_id, thursday_meal_id, friday_meal_id, saturday_meal_id, sunday_meal_id, created_at, updated_at

### Dashboard Module

#### notifications
- **Primary Key:** id (UUID)
- **Indexes:** user_id, is_read, created_at, (user_id, is_read) composite
- **Fields:** user_id, type (enum), category (enum), title, message, action_url, action_label, is_read, is_dismissed, created_at, read_at

---

## Enums

### UserRole
- admin
- editor
- reader

### FileCategory
- tax_document
- insurance_policy
- document
- knowledge_attachment
- general

### PolicyType
- home, car, health, life, pet, travel, contents, landlord, income_protection, other

### PremiumFrequency
- monthly, quarterly, yearly

### DocumentType
- contract, receipt, warranty, manual, certificate, legal, medical, financial, other

### PriorityStatus
- identified, converted

### ProjectStatus
- planned, approved, in_progress, completed, cancelled

### UtilityType
- electricity, gas, water, internet

### ArticleType
- measurement, paint, tech_device, storage_location, vehicle, emergency_contact, appliance, vendor

### NotificationType
- info, warning, error, success, reminder

### NotificationCategory
- system, tax, financial, assets, projects, knowledge, meals

---

## Relationships

### One-to-Many
- users → audit_logs
- users → trusted_devices
- users → notifications
- bank_accounts → expense_categories
- expense_categories → expenses
- projects → quotes
- recipes → ingredients
- knowledge_articles → knowledge_attachments

### Many-to-One with Nullable
- expenses → category (optional)
- documents → file (optional)
- priority_items → project (optional)
- projects → priority_item (optional)
- quotes → project (optional)

### Circular References
- priority_items ↔ projects (originating_priority_id and project_id)

### Array Relationships
- week_plans → recipes (7 foreign keys for each day)

---

## Constraints

### Check Constraints
- priority_items: severity BETWEEN 1 AND 5
- priority_items: frequency BETWEEN 1 AND 5
- knowledge_articles: article_type IN (enum values)

### Unique Constraints
- users.username
- users.email
- week_plans.week_starting

### Foreign Key Actions
- CASCADE: ingredients.recipe_id
- SET NULL: week_plans meal IDs, quotes.project_id
- RESTRICT (default): most other relationships

---

## Indexes

### Performance Indexes
- audit_logs: (user_id, created_at) - for user activity queries
- notifications: (user_id, is_read) - for unread count
- knowledge_articles: search_vector (GIN) - for full-text search
- All foreign keys have indexes

### Search Indexes
- recipes.name
- ingredients.name
- documents.document_type
- insurance_policies.renewal_date

---

## Special Features

### JSONB Fields
- audit_logs.metadata - Flexible event data
- knowledge_articles.data - Type-specific structured data

### ARRAY Fields
- documents.tags - String array for categorization
- knowledge_articles.tags - String array for search

### TSVECTOR
- knowledge_articles.search_vector - Full-text search index

### Timestamps
All tables have:
- created_at (auto-set on insert)
- updated_at (auto-set on update, where applicable)

---

## Migration Strategy

### Alembic Revisions

Migrations are in `alembic/versions/` in chronological order:
1. Initial schema (users, auth, files, audit)
2. Tax tables
3. Financial tables
4. Assets tables
5. Projects tables
6. Knowledge tables
7. Meal planner tables
8. Notifications table

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## Backup Recommendations

### What to Backup
- Database (full dump)
- File uploads (./uploads directory)
- Environment variables (.env file)
- Migration history (alembic/versions/)

### Backup Frequency
- Database: Daily
- Files: Daily
- Config: On change

### Retention
- Daily backups: 30 days
- Weekly backups: 3 months
- Monthly backups: 1 year

---

**For schema diagrams and ER diagrams, use tools like:**
- pgAdmin 4 (built-in ERD tool)
- DBeaver (database visualization)
- SchemaSpy (automatic documentation generation)
