# Data Model: Monorepo Conversion

**Feature**: 003-convert-to-monorepo
**Date**: 2025-10-19

## Note

This feature is an **infrastructure/tooling change** that does not introduce new data models or modify existing ones.

## Existing Data Models (Unchanged)

The following data models from the Grimoire project remain **unchanged** after monorepo conversion:

### API (Python/SQLAlchemy)
- **Word**: Definition, phonetics, usage examples, grammar, etc.
- **User** (if applicable): User accounts and preferences
- **Vocabulary**: User's saved words
- Database schema managed via Alembic migrations

### UI (TypeScript/Prisma)
- **Vocabulary**: User's saved words (Prisma ORM)
- Database schema managed via Prisma migrations

## Impact Assessment

- ✅ **No schema changes**: Database tables, columns, and relationships remain identical
- ✅ **No migration required**: Alembic and Prisma migrations continue working
- ✅ **File locations**: Model files move from `/src/models/` to `/apps/api/src/models/` but content unchanged
- ✅ **Import paths**: Python imports remain relative within the app (no changes needed)

## Validation

After monorepo migration, verify:
- [ ] Alembic migrations run successfully: `nx run api:migrate`
- [ ] Prisma migrations run successfully: `nx run ui:prisma-migrate`
- [ ] Database connections work: Test API and UI against existing database
- [ ] No schema drift: Compare pre and post-migration schemas

---

**Data model analysis**: N/A - Infrastructure change only
**Ready for implementation**: ✅ Yes (no data model work required)
