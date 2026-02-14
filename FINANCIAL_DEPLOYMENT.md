# Financial Module - Production Deployment Guide

## Issue Summary

The Financial Management tables require proper database initialization to work correctly. The database enum types (income_frequency, account_type, expense_frequency, utility_type) must be created with **lowercase values** to match the Python model definitions.

## What Was Fixed (Feb 14, 2026)

1. **Migration File Updated**: `backend/alembic/versions/8d07792f10cc_add_financial_management_tables.py`
   - Enum values are correctly defined as lowercase strings
   - Added 'rates' to utility_type enum

2. **Permissions Added**: `backend/app/api/dependencies.py`
   - Added `"financial:write"` permission for ADMIN and EDITOR roles
   - Added `"financial:read"` permission for all roles

3. **Models Updated**: `backend/app/models/utility.py`
   - Added `UtilityType.RATES` for council rates/land tax

## Production Deployment Requirements

### For Fresh Database (New Production Environment)

When deploying to a **new** production environment with an empty database:

```bash
# 1. Start the database container
docker compose -f docker-compose.prod.yml up -d db

# 2. Run Alembic migrations to create all tables
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 3. Start remaining services
docker compose -f docker-compose.prod.yml up -d
```

### For Existing Database (Current Development)

The current development database has been **manually fixed** with correct enum types. This fix is stored in the Docker volume:
- Volume: `home-management-platform_db_data`
- Location: `/var/lib/docker/volumes/home-management-platform_db_data`

**This volume must be backed up and persisted** for the data to survive container restarts.

### Database Backup (CRITICAL for Production)

```bash
# Backup current database (including the fixed enums)
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres postgres > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres postgres < backup_YYYYMMDD_HHMMSS.sql
```

## Verifying Database is Correct

Run this test to verify enums are created correctly:

```bash
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import SessionLocal
from app.services.income_source_service import IncomeSourceService
from app.models.income_source import IncomeFrequency
from decimal import Decimal

db = SessionLocal()
try:
    result = IncomeSourceService.create_income_source(
        db=db,
        source_name='Test',
        amount=Decimal('100'),
        frequency=IncomeFrequency.MONTHLY
    )
    print('✓ SUCCESS: Database enums are correct')
    db.delete(result)
    db.commit()
except Exception as e:
    print('✗ ERROR:', str(e))
    print('Run: docker compose -f docker-compose.prod.yml exec backend alembic upgrade head')
finally:
    db.close()
"
```

## Migration File Reference

The migration file defines enums correctly:

```python
# income_frequency
sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='income_frequency')

# account_type
sa.Enum('checking', 'savings', 'offset', name='account_type')

# expense_frequency
sa.Enum('daily', 'weekly', 'fortnightly', 'monthly', 'yearly', name='expense_frequency')

# utility_type
sa.Enum('electricity', 'gas', 'water', 'internet', 'mobile', 'rates', name='utility_type')
```

## Production Checklist

- [ ] Database volume is configured for persistence (outside container)
- [ ] Regular database backups are scheduled
- [ ] Alembic migrations run on initial deployment
- [ ] Test script confirms enum types are correct
- [ ] User roles have `financial:write` and `financial:read` permissions
- [ ] Database connection uses production credentials
- [ ] SSL/TLS enabled for database connections (if applicable)

## Troubleshooting

### Error: "invalid input value for enum income_frequency: 'MONTHLY'"

**Cause:** Database enum types were created with uppercase values instead of lowercase.

**Solution:** Drop and recreate financial tables (ONLY safe if no production data):

```bash
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS expenses CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS expense_categories CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS bank_accounts CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS income_sources CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS utilities CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS income_frequency CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS account_type CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS expense_frequency CASCADE'))
    conn.execute(text('DROP TYPE IF EXISTS utility_type CASCADE'))
    conn.commit()

# Then run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Permission Denied Errors (HTTP 500)

**Cause:** `financial:write` or `financial:read` permissions not in PERMISSION_MATRIX.

**Solution:** Verify `backend/app/api/dependencies.py` contains:

```python
# Financial Management (Active)
"financial:write": [UserRole.ADMIN, UserRole.EDITOR],
"financial:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
```

## Important Notes

1. **Never use SQLAlchemy's `create_all()` in production** - always use Alembic migrations
2. **Database volumes must be persistent** - configure volume mapping in docker-compose.prod.yml
3. **Backup before any schema changes** - especially before running migrations
4. **Test migrations in staging first** - verify enum creation works correctly

## Contact

If issues persist, check:
- Backend logs: `docker compose -f docker-compose.prod.yml logs backend --tail=100`
- Database connectivity: `docker compose -f docker-compose.prod.yml exec backend python -c "from app.db.database import engine; print(engine.url)"`
- Migration status: `docker compose -f docker-compose.prod.yml exec backend alembic current`
