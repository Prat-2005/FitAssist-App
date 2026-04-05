# Migration Fix - Database Configuration Issues Resolved

## Problem Identified
The initial migration setup failed because:
1. `alembic.ini` had placeholder database credentials (`user:password`)
2. `migrations/env.py` didn't load environment variables from `.env` file
3. Environment variable `DATABASE_URL` from `.env` was not being used

## Solution Implemented

### 1. Fixed `migrations/env.py`
- Added `load_dotenv()` to load `.env` file at startup
- Changed `.env` path to correct location: `Path(__file__).parent.parent / ".env"`
- Updated `run_migrations_online()` to read `DATABASE_URL` from environment
- Removed import of `engine` from `db.database` to avoid premature connection attempts

### 2. Key Changes Made
```python
# Before: Would try to read from alembic.ini placeholders
connectable = engine_from_config(config.get_section(...))

# After: Reads actual DATABASE_URL from .env
database_url = os.getenv("DATABASE_URL", "fallback_url")
connectable = create_eng(database_url, poolclass=pool.NullPool)
```

## Migration Status ✅

- **Migration ID**: 001
- **Status**: Applied (head)
- **Columns Added**: 
  - `days_per_week` (Integer, nullable)
  - `duration_minutes` (Integer, nullable)
- **Table**: `profiles`

### Verification
```bash
alembic current  # Shows: 001 (head)
alembic history  # Shows migration was applied
```

## Files Modified
- `backend/migrations/env.py` - Fixed environment variable loading
- `backend/alembic.ini` - Already configured (no changes needed)

## How It Works Now
1. Alembic starts
2. `env.py` loads environment variables from `.env` 
3. `DATABASE_URL=postgresql://postgres:Prat3103@localhost:5433/fitassist_db` is read
4. Connection is established with real credentials
5. Migration runs on the correct database

## Next Steps (Optional)
- Test that the app can still connect to the database
- Verify Profile model can now use `days_per_week` and `duration_minutes`
- If adding more schema changes, use: `alembic revision --autogenerate -m "Description"`

## Important Notes
- Migrations are tracked in `alembic_version` table
- To rollback: `alembic downgrade -1`
- Always test migrations in development first
- The migration is fully reversible
