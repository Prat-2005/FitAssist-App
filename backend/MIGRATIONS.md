# Database Migrations Guide

This directory contains Alembic database migrations for FitAssist. Migrations manage schema changes in a version-controlled, reversible way.

## Quick Start

### Before First Run (Initial Setup)
Ensure your `.env` file contains:
```
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/fitassist_db
```

### Applying Migrations

**Apply all pending migrations:**
```bash
cd backend
alembic upgrade head
```

**Apply a specific migration:**
```bash
alembic upgrade <revision_id>
```

**Check migration status:**
```bash
alembic current
alembic history
```

### Reverting Migrations

**Downgrade one migration:**
```bash
alembic downgrade -1
```

**Downgrade to a specific revision:**
```bash
alembic downgrade <revision_id>
```

**Downgrade to initial state:**
```bash
alembic downgrade base
```

## Creating New Migrations

### Automatic Migration (Recommended)
When you modify ORM models:

1. Make changes to files in `backend/models/`
2. Generate migration automatically:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Descriptive message"
   ```
3. Review the generated file in `versions/`
4. Test locally: `alembic upgrade head`
5. Commit to git

### Manual Migration
For complex changes or when autogenerate doesn't capture everything:

```bash
alembic revision -m "Descriptive message"
```

Then edit the generated file in `versions/` to define `upgrade()` and `downgrade()` functions.

## Important Migration Rules

1. **Always include downgrade()** - Every migration must be reversible
2. **Test both ways** - Run `upgrade` and `downgrade` locally
3. **Order matters** - Migrations run sequentially by revision ID
4. **Data safety** - Back up production database before running migrations
5. **Deployment order** - Apply migrations BEFORE deploying new code that uses new schema

## Pending Migrations

### Migration 001: Add Profile Workout Preferences
- **Status**: Created, not yet applied
- **Changes**: 
  - Adds `days_per_week` (Integer, nullable) column to `profiles` table
  - Adds `duration_minutes` (Integer, nullable) column to `profiles` table
- **Reason**: Profile model updated to support user workout scheduling preferences
- **Application**: 
  ```bash
  alembic upgrade 001
  ```

## Database Schema Documentation

See `backend/db/database.py` and `backend/models/` for current schema definitions.

## Troubleshooting

**Connection Error**: Verify DATABASE_URL in `.env` and that PostgreSQL is running
**Migration Not Found**: Check migration name in `alembic history`
**Duplicate Revision IDs**: Delete conflicting migration file and recreate
**Alembic Lock**: Delete `alembic_version` row from database if migration gets stuck

## References
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
