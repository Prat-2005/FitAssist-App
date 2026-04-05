# FitAssist Backend Deployment Guide

## Migration Integration with Backend Code

### Why Migrations Matter
The `backend-updation` commit added new columns to the `Profile` model:
- `days_per_week` (Integer, nullable)
- `duration_minutes` (Integer, nullable)

These columns exist in the ORM model but NOT in existing databases. Using only `Base.metadata.create_all()` won't alter existing tables.

### Deployment Checklist

#### 1. Pre-Deployment (Dev/Staging)
- [ ] Pull latest code with migrations
- [ ] Ensure `DATABASE_URL` environment variable is set
- [ ] Back up production database
- [ ] Test migrations in staging environment:
  ```bash
  cd backend
  alembic upgrade head
  ```
- [ ] Verify new columns appear: `SELECT * FROM profiles LIMIT 1;`

#### 2. Production Deployment
- [ ] Apply migrations to production database FIRST:
  ```bash
  cd backend
  alembic upgrade head
  ```
- [ ] Verify migration status: `alembic current`
- [ ] Deploy new application code
- [ ] Restart application servers
- [ ] Monitor logs for any errors

#### 3. Rollback Procedure (if needed)
- [ ] Revert application deployment
- [ ] If schema changes caused issues:
  ```bash
  alembic downgrade -1
  ```

### Environment Setup

Create `.env` in project root:
```bash
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/fitassist_db
```

### Initial Database Setup

For new installations:
```bash
cd backend
# Create base tables (still needed for first table creation)
python -c "from db.database import init_db; init_db()"
# Then apply all migrations
alembic upgrade head
```

### Monitoring

Check migration status anytime:
```bash
cd backend
alembic current        # Current revision
alembic history        # All applied migrations
alembic history -v     # Verbose history
```

### Common Issues

**Issue**: Database connection fails
- **Fix**: Verify DATABASE_URL and PostgreSQL is running

**Issue**: Migration table doesn't exist
- **Fix**: Ensure at least one table exists, then run migrations

**Issue**: Column already exists error
- **Fix**: Check if migration was already applied: `alembic current`

## Configuration Files

### alembic.ini
- Specifies migration folder location
- Database connection URL (use environment variable)
- Migration naming and versioning

### migrations/env.py
- Imports all ORM models
- Configures target metadata
- Sets up both online and offline migration modes

### Backend Models
- Changes to models in `backend/models/` require corresponding migrations
- Always update both model files AND create migrations

## Next Steps

After deploying code with new schema:
1. Monitor application logs
2. Verify Profile queries work correctly
3. Update application code to use new fields (days_per_week, duration_minutes)
4. Add tests for new profile fields
