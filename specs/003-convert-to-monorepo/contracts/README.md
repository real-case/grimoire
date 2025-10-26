# API Contracts: Monorepo Conversion

**Feature**: 003-convert-to-monorepo
**Date**: 2025-10-19

## Note

This feature is an **infrastructure/tooling change** that does not introduce new API contracts or modify existing API endpoints.

## Existing API Contracts (Unchanged)

The Grimoire API contracts remain **unchanged** after monorepo conversion:

### FastAPI Endpoints
- `GET /api/v1/words/{word}` - Word lookup
- `POST /api/v1/vocabulary` - Save word to vocabulary
- `GET /api/v1/vocabulary` - List saved vocabulary
- `DELETE /api/v1/vocabulary/{word_id}` - Delete saved word

All endpoints, request/response schemas, and OpenAPI documentation remain identical.

### UI API Routes (Next.js)
- `/api/vocabulary/*` - Next.js API routes for vocabulary management
- `/api/lookup/*` - Word lookup proxy to FastAPI backend

## Impact Assessment

- ✅ **No endpoint changes**: All URLs, methods, and schemas unchanged
- ✅ **No contract updates**: OpenAPI spec (if exists) remains valid
- ✅ **CORS configuration**: May need path updates if using absolute URLs
- ✅ **Environment variables**: API URLs in UI config may need review

## Validation

After monorepo migration, verify:
- [ ] API documentation still generates: `nx run api:docs` (if available)
- [ ] All endpoints respond correctly: Run integration tests
- [ ] UI can communicate with API: Test full word lookup flow
- [ ] CORS allows UI origin: Check browser console for CORS errors

---

**API contract analysis**: N/A - Infrastructure change only
**Ready for implementation**: ✅ Yes (no contract work required)
