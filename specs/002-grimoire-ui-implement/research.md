# Research & Technical Decisions: Grimoire UI

**Feature**: 002-grimoire-ui-implement
**Date**: 2025-10-18
**Status**: Complete

## Overview

This document resolves technical unknowns identified during planning and establishes best practices for the Next.js + FastAPI integration.

## Research Items

### 1. Database Choice for Vocabulary Storage

**Decision**: PostgreSQL with Prisma ORM

**Rationale**:
- **PostgreSQL chosen because**:
  - Already used by FastAPI backend (feature 001), so infrastructure exists
  - Can run as separate database instance (different schema/database name) while sharing infrastructure
  - Excellent TypeScript/Node.js support via multiple drivers
  - ACID compliance ensures data integrity for user vocabulary
  - JSON column support for flexible metadata storage

- **Prisma ORM chosen because**:
  - Best-in-class TypeScript integration with automatic type generation
  - Built-in migration system for schema evolution
  - Works seamlessly with Next.js API routes
  - Excellent developer experience with Prisma Studio for data inspection
  - Connection pooling and query optimization built-in

**Alternatives Considered**:
- **SQLite**: Simple but not ideal for concurrent users in production deployment
- **MongoDB**: Flexible schema but overkill for simple CRUD operations; adds complexity
- **Supabase**: Great features but adds external dependency; prefer self-hosted for consistency with backend

**Implementation Notes**:
- Create separate database `grimoire_vocabulary` alongside existing `grimoire_words` (or similar)
- Use Prisma schema in `grimoire-ui/prisma/schema.prisma`
- Connection string via environment variable `VOCABULARY_DATABASE_URL`

---

### 2. Client-Side Data Fetching Strategy

**Decision**: Native Next.js fetch with caching + React hooks for state management

**Rationale**:
- **Next.js native fetch** (App Router):
  - Built-in request deduplication prevents redundant API calls
  - Automatic caching with `cache` and `revalidate` options
  - Works seamlessly with Server Components and Server Actions
  - No additional dependencies, reducing bundle size
  - Aligned with Next.js 14+ best practices

- **Custom React hooks** for client-side interactions:
  - `useWordLookup` - manages search state, loading, errors
  - `useVocabulary` - manages saved words list and CRUD operations
  - Lightweight, no external state management library needed for this scope

**Alternatives Considered**:
- **React Query (TanStack Query)**: Excellent library but adds 13KB gzipped; overkill for simple CRUD operations
- **SWR**: Lighter than React Query (5KB) but still unnecessary given Next.js built-in caching
- **Zustand/Redux**: State management overkill for feature scope; local state + fetch caching sufficient

**Implementation Notes**:
- Use Server Components for initial page load (vocabulary list)
- Use client-side fetch for interactive word lookup
- Implement optimistic updates for save/edit operations
- Cache word lookups in memory with TTL (5 minutes) to avoid redundant API calls

---

### 3. API Response Type Generation

**Decision**: Manual TypeScript types + runtime validation with Zod

**Rationale**:
- **Manual types** for FastAPI responses:
  - FastAPI backend (feature 001) already has Pydantic schemas
  - Will extract and translate to TypeScript manually (one-time effort)
  - Keeps UI decoupled from backend tooling
  - Allows UI-specific type augmentations (e.g., edit state tracking)

- **Zod for runtime validation**:
  - Validates API responses at runtime (type safety beyond compile time)
  - Prevents crashes from unexpected API changes
  - Provides clear error messages for debugging
  - Lightweight (9KB gzipped)
  - Can generate TypeScript types from schemas (single source of truth)

**Alternatives Considered**:
- **OpenAPI code generation**: FastAPI generates OpenAPI specs, but adds build complexity and tight coupling
- **tRPC**: Requires backend adoption; not feasible for existing FastAPI
- **GraphQL**: Complete overkill for simple REST API integration

**Implementation Notes**:
- Define Zod schemas in `grimoire-ui/src/types/word.ts`
- Use `z.infer<typeof schema>` to derive TypeScript types
- Wrap fetch calls with Zod validation: `wordSchema.parse(await response.json())`
- Create separate types for API responses vs. UI state (e.g., `WordData` vs. `EditableWord`)

---

### 4. Form State Management for Editable Fields

**Decision**: React Hook Form with controlled inputs

**Rationale**:
- **React Hook Form**:
  - Minimal re-renders (uncontrolled by default, but works with controlled)
  - Built-in validation support
  - Small bundle size (9KB gzipped)
  - Excellent TypeScript support
  - Plays well with Headless UI components
  - Handles complex nested fields (definitions array, examples, etc.)

- **Controlled inputs** for editable fields:
  - Provides instant visual feedback for unsaved changes
  - Easier to implement "edited field highlighting" (FR-010)
  - Simpler dirty state tracking for "unsaved changes" warning (FR-009)

**Alternatives Considered**:
- **Formik**: Heavier (13KB), older architecture, more re-renders
- **Native React state**: Works but verbose and error-prone for complex forms with validation
- **Uncontrolled forms**: Lighter but harder to implement edit highlighting

**Implementation Notes**:
- Use `useForm` hook with default values from API response
- Track `formState.isDirty` to show unsaved changes warning
- Track `formState.dirtyFields` to highlight edited fields (FR-010)
- Implement "discard changes" to reset form to original API values

---

### 5. Error Handling Strategy

**Decision**: Three-tier error handling with user-friendly messages

**Rationale**:
Aligned with FR-007 (clear error messages) and US-4 (error handling), implement:

1. **Input Validation** (client-side):
   - Zod schemas for immediate feedback on invalid input
   - Prevent empty/invalid submissions (FR-012)
   - Show inline validation errors

2. **Network/API Errors** (Next.js API routes):
   - Catch and classify errors: 404 (not found), 500 (server error), timeout, network failure
   - Return standardized error response: `{ error: string, code: string, retryable: boolean }`
   - Map technical errors to user-friendly messages

3. **UI Error Boundaries**:
   - React Error Boundaries for unexpected component crashes
   - Fallback UI with "something went wrong" message
   - Error logging for debugging (console in dev, service in production)

**Error Message Examples**:
- `WORD_NOT_FOUND`: "We couldn't find that word. Please check your spelling and try again."
- `API_UNAVAILABLE`: "The word lookup service is temporarily unavailable. Please try again in a moment."
- `NETWORK_ERROR`: "Network connection lost. Please check your internet connection and try again."
- `DUPLICATE_WORD`: "You've already saved this word to your vocabulary."

**Implementation Notes**:
- Create error utility in `lib/errors.ts` with error code mapping
- Use toast notifications (Headless UI) for transient errors
- Inline error display for form validation
- Retry logic for transient network errors (max 3 attempts with exponential backoff)

---

### 6. Testing Strategy

**Decision**: Three-layer testing approach

**Rationale**:

1. **Unit Tests (Jest + React Testing Library)**:
   - Component testing: `WordDisplay`, `EditableField`, `VocabularyList`
   - Hook testing: `useWordLookup`, `useVocabulary`
   - Utility testing: validation, error handling, API client
   - Target: 80% code coverage

2. **Integration Tests (Jest + MSW)**:
   - Mock Service Worker intercepts API calls
   - Test full user flows: lookup → edit → save
   - Test error scenarios: network failures, API errors, validation failures
   - Test edge cases from spec (partial data, duplicate saves, etc.)

3. **E2E Tests (Playwright)**:
   - Critical path: word lookup and save
   - Real browser testing across Chrome, Firefox, Safari
   - Visual regression testing for UI consistency
   - Run in CI/CD pipeline before deployment

**Alternatives Considered**:
- **Cypress**: Popular but Playwright has better TypeScript support and faster execution
- **Testing Library alone**: Good but insufficient without E2E coverage
- **No E2E**: Risky given user-facing application with complex flows

**Implementation Notes**:
- MSW handlers in `tests/mocks/handlers.ts`
- Shared test fixtures in `tests/fixtures/`
- Playwright config for parallel execution and retries
- Run unit/integration tests on every commit, E2E on PR merge

---

### 7. Deployment Strategy

**Decision**: Vercel for Next.js UI, existing infrastructure for FastAPI

**Rationale**:
- **Vercel for UI**:
  - Native Next.js support (created by Vercel)
  - Automatic preview deployments for PRs
  - Edge network for fast global delivery
  - Free tier sufficient for MVP
  - Easy environment variable management
  - Built-in analytics and performance monitoring

- **Separate PostgreSQL for vocabulary**:
  - Can use Vercel Postgres (free tier: 60h compute, 256MB storage)
  - Or connect to existing PostgreSQL server with separate database
  - Prisma works with both options

- **CORS Configuration**:
  - FastAPI backend must allow requests from Vercel domain
  - Set `ALLOWED_ORIGINS` environment variable in FastAPI
  - Use Next.js rewrites for seamless proxying

**Alternatives Considered**:
- **Self-hosted**: More control but requires infrastructure management, SSL certs, scaling
- **Netlify**: Good alternative but Vercel has tighter Next.js integration
- **AWS/GCP**: Overkill for MVP, higher operational complexity

**Implementation Notes**:
- `next.config.js` with environment variables for FastAPI URL
- Vercel environment variables: `FASTAPI_URL`, `VOCABULARY_DATABASE_URL`, `API_SECRET_KEY`
- FastAPI CORS update (if not already configured): add Vercel domain to allowed origins
- Document deployment process in quickstart.md

---

### 8. Authentication & User Management

**Decision**: Defer authentication to future feature

**Rationale**:
- **Current scope**: Single-user or demo mode
  - No authentication/authorization in feature spec
  - No multi-user requirements mentioned
  - Vocabulary storage can be user-agnostic initially (all saved words in one pool)

- **Future extensibility**:
  - Add user ID foreign key to vocabulary table when auth implemented
  - Use Next.js middleware for auth checks
  - Consider NextAuth.js or Clerk for auth provider

- **Immediate approach**:
  - All vocabulary words accessible to anyone (demo/prototype mode)
  - Add "User Management" dependency note in plan.md
  - Design schema with optional `userId` field (nullable initially, required later)

**Implementation Notes**:
- Add TODO comment in schema: `// TODO: Add userId when authentication implemented`
- Document auth deferral in quickstart.md
- Ensure no PII stored in vocabulary entries (words are not personal data)

---

## Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend Framework | Next.js | 14.x | App Router, Server Components, built-in optimizations |
| UI Library | React | 18.x | Next.js dependency, industry standard |
| Styling | Tailwind CSS | 3.x | Utility-first, fast development, small bundle |
| Components | Headless UI | 2.x | Accessible, unstyled primitives for custom styling |
| Language | TypeScript | 5.x | Type safety, better DX, catch errors at compile time |
| Database | PostgreSQL | 14+ | Existing infrastructure, reliable, feature-rich |
| ORM | Prisma | 5.x | Best TypeScript support, migrations, type generation |
| Validation | Zod | 3.x | Runtime type checking, schema validation, small size |
| Forms | React Hook Form | 7.x | Performance, validation, small bundle |
| Testing (Unit) | Jest + RTL | Latest | Standard React testing, good ecosystem |
| Testing (E2E) | Playwright | Latest | Cross-browser, fast, TypeScript-first |
| API Mocking | MSW | Latest | Service worker-based, realistic API mocking |
| Package Manager | Yarn | 1.x | User specified, faster than npm, good caching |
| Deployment | Vercel | N/A | Optimal Next.js hosting, preview deploys, analytics |

---

## Best Practices Checklist

### Next.js App Router
- ✅ Use Server Components by default, Client Components only when needed (interactivity, hooks)
- ✅ Leverage API routes for backend proxy (keeps secrets server-side)
- ✅ Use `loading.tsx` and `error.tsx` for loading/error states
- ✅ Implement proper metadata for SEO (`metadata` export in pages)
- ✅ Use Next.js Image component for optimized images

### TypeScript
- ✅ Strict mode enabled (`strict: true` in tsconfig.json)
- ✅ No `any` types; use `unknown` and type guards if needed
- ✅ Zod schemas as single source of truth for runtime types
- ✅ Export types from dedicated `types/` directory

### Performance
- ✅ Bundle size monitoring (aim for <200KB initial load)
- ✅ Code splitting via dynamic imports for heavy components
- ✅ Optimize images (WebP format, proper sizing)
- ✅ Implement proper caching headers for API routes
- ✅ Use React.memo for expensive components (only if profiling shows benefit)

### Accessibility
- ✅ Semantic HTML elements
- ✅ Proper ARIA labels for interactive elements
- ✅ Keyboard navigation support (Headless UI provides this)
- ✅ Focus management for modal dialogs
- ✅ Color contrast ratios meet WCAG AA standards (use Tailwind's default palette)

### Error Handling
- ✅ User-friendly error messages (never expose stack traces to users)
- ✅ Proper error logging for debugging
- ✅ Retry logic for transient failures
- ✅ Graceful degradation when API unavailable

### Security
- ✅ API keys never exposed to browser (use Next.js API routes)
- ✅ Input validation on both client and server
- ✅ Sanitize user-generated content before display (React handles this by default)
- ✅ HTTPS only (enforced by Vercel)
- ✅ CORS properly configured

---

## Open Questions & Future Work

### Resolved in This Phase
- ✅ Database choice: PostgreSQL with Prisma
- ✅ Data fetching: Next.js native fetch + custom hooks
- ✅ Type safety: Manual types + Zod validation
- ✅ Forms: React Hook Form
- ✅ Testing: Jest/RTL + Playwright
- ✅ Deployment: Vercel

### Deferred to Implementation
- Authentication/user management (design schema with future auth in mind)
- Internationalization (i18n) - not in scope, but Next.js supports it
- Offline support (PWA) - not required, but can add later
- Real-time collaboration - not in scope
- Advanced search/filtering - may add in vocabulary list view

### Dependencies on Backend (Feature 001)
- Need to confirm exact API endpoint URL for word lookup
- Need to confirm API response schema (will inspect during implementation)
- Need to confirm CORS configuration (will update if needed)
- Need to confirm rate limiting (if any) to handle in UI

---

## References

- [Next.js 14 Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Headless UI Documentation](https://headlessui.com/)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Zod Documentation](https://zod.dev/)
- [React Hook Form Documentation](https://react-hook-form.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Next.js on Vercel Best Practices](https://vercel.com/docs/frameworks/nextjs)

---

**Phase 0 Status**: ✅ COMPLETE - All technical unknowns resolved, ready for Phase 1 (Design & Contracts)
