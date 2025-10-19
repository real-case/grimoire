# Quickstart Guide: Grimoire UI

**Feature**: 002-grimoire-ui-implement
**Last Updated**: 2025-10-18

## Overview

This guide walks through setting up and running the Grimoire UI - a Next.js web application for looking up words, editing their information, and building a personal vocabulary collection.

**Prerequisites**:
- Node.js 18+ and Yarn installed
- PostgreSQL 14+ running (for vocabulary storage)
- FastAPI backend running (feature 001-an-ai-agent)
- Basic familiarity with terminal/command line

---

## Quick Start (5 minutes)

```bash
# 1. Navigate to project root
cd /path/to/grimoire

# 2. Set up the UI project
cd grimoire-ui
yarn install

# 3. Set up the database
cp .env.example .env.local
# Edit .env.local with your database connection string

# 4. Run database migrations
yarn prisma migrate dev

# 5. Start the development server
yarn dev

# 6. Open browser
open http://localhost:3000
```

---

## Detailed Setup

### 1. Install Dependencies

```bash
cd grimoire-ui
yarn install
```

This installs:
- Next.js 14+ (App Router)
- React 18+
- Tailwind CSS 3.x
- Headless UI components
- Prisma ORM
- Zod validation
- React Hook Form
- TypeScript 5.x

**Expected output**: `✨ Done in X.XXs`

---

### 2. Database Setup

#### Option A: New PostgreSQL Database

```bash
# Create a new database for vocabulary storage
createdb grimoire_vocabulary

# Or using psql
psql -U postgres
CREATE DATABASE grimoire_vocabulary;
\q
```

#### Option B: Use Existing PostgreSQL Server

Create a new database within your existing PostgreSQL instance:

```sql
CREATE DATABASE grimoire_vocabulary
  WITH OWNER = your_user
  ENCODING = 'UTF8';
```

---

### 3. Environment Configuration

Create `.env.local` file in `grimoire-ui/`:

```bash
# grimoire-ui/.env.local

# Database connection for vocabulary storage
VOCABULARY_DATABASE_URL="postgresql://user:password@localhost:5432/grimoire_vocabulary"

# FastAPI backend URL (from feature 001)
FASTAPI_URL="http://localhost:8000"

# Optional: API secret key (for future auth)
# API_SECRET_KEY="your-secret-key-here"

# Next.js environment
NODE_ENV=development
```

**Security Note**: Never commit `.env.local` to git. It's already in `.gitignore`.

---

### 4. Database Migration

```bash
# Generate Prisma client from schema
yarn prisma generate

# Run migrations to create tables
yarn prisma migrate dev --name init

# Optional: Open Prisma Studio to inspect database
yarn prisma studio
```

**Expected output**:
```
✔ Generated Prisma Client
✔ Applied 1 migration
```

**Verify database**:
```bash
psql grimoire_vocabulary -c "\dt"
```

Should show `vocabulary_entries` table.

---

### 5. Verify FastAPI Backend

Ensure the FastAPI backend (feature 001) is running:

```bash
# In a separate terminal
cd /path/to/grimoire/src
uvicorn api.main:app --reload

# Test the API
curl http://localhost:8000/api/words/hello
```

Should return word information JSON.

---

### 6. Start Development Server

```bash
cd grimoire-ui
yarn dev
```

**Expected output**:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

**Verify**:
- Navigate to http://localhost:3000
- You should see the word lookup interface
- Try looking up a word (e.g., "hello")
- Results should display within 3 seconds

---

## Project Structure Tour

```
grimoire-ui/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (word lookup)
│   │   ├── vocabulary/        # Saved vocabulary list
│   │   └── api/               # API routes (proxy + CRUD)
│   │
│   ├── components/            # React components
│   │   ├── ui/               # Base UI components
│   │   ├── WordLookupForm.tsx
│   │   ├── WordDisplay.tsx
│   │   ├── EditableField.tsx
│   │   └── VocabularyList.tsx
│   │
│   ├── lib/                   # Utilities
│   │   ├── api-client.ts     # Fetch wrapper
│   │   ├── db.ts             # Prisma client
│   │   └── validation.ts     # Input validation
│   │
│   ├── types/                # TypeScript types
│   │   ├── word.ts           # Word data types
│   │   └── vocabulary.ts     # Vocabulary types
│   │
│   └── hooks/                # Custom React hooks
│       ├── useWordLookup.ts
│       └── useVocabulary.ts
│
├── prisma/
│   └── schema.prisma         # Database schema
│
├── tests/                    # Test suites
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## Development Workflow

### Running Tests

```bash
# Unit + integration tests
yarn test

# Watch mode
yarn test:watch

# E2E tests (Playwright)
yarn test:e2e

# Coverage report
yarn test:coverage
```

### Type Checking

```bash
# Run TypeScript compiler
yarn type-check

# Watch mode
yarn type-check:watch
```

### Linting & Formatting

```bash
# Lint
yarn lint

# Format code
yarn format

# Fix auto-fixable issues
yarn lint:fix
```

### Database Management

```bash
# Create a new migration
yarn prisma migrate dev --name add_field

# Reset database (⚠️ deletes all data)
yarn prisma migrate reset

# Generate Prisma client after schema changes
yarn prisma generate

# Open Prisma Studio (GUI for database)
yarn prisma studio
```

---

## Common Tasks

### 1. Look Up a Word

1. Navigate to http://localhost:3000
2. Enter a word in the search box
3. Click "Search" or press Enter
4. View word information (definitions, pronunciation, examples, etc.)

### 2. Edit Word Information

1. After looking up a word, click on any editable field
2. Modify the content
3. Notice that edited fields are highlighted
4. Click "Save to Vocabulary" to persist changes

### 3. Save to Vocabulary

1. Look up a word
2. Optionally edit fields
3. Click "Save to Vocabulary" button
4. See confirmation message
5. Word is now in your vocabulary collection

### 4. View Saved Vocabulary

1. Navigate to http://localhost:3000/vocabulary
2. See list of all saved words
3. Sort by: Last Modified, Save Date, or Word
4. Search by word, tags, or notes
5. Click a word to view/edit full details

### 5. Delete from Vocabulary

1. Go to vocabulary list or word detail page
2. Click "Delete" or trash icon
3. Confirm deletion
4. Word removed from your collection (original API data unaffected)

---

## Troubleshooting

### Issue: "Cannot connect to database"

**Solution**:
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env.local
cat .env.local | grep VOCABULARY_DATABASE_URL

# Test connection manually
psql $VOCABULARY_DATABASE_URL -c "SELECT 1"
```

---

### Issue: "FastAPI backend unavailable"

**Solution**:
```bash
# Check FastAPI is running
curl http://localhost:8000/health

# Start FastAPI if needed
cd ../src
uvicorn api.main:app --reload

# Check FASTAPI_URL in .env.local
cat .env.local | grep FASTAPI_URL
```

---

### Issue: "Word not found" for valid words

**Possible causes**:
1. FastAPI backend database is empty
2. Network issue between Next.js and FastAPI
3. CORS not configured properly

**Solution**:
```bash
# Test FastAPI directly
curl http://localhost:8000/api/words/test

# Check Next.js API route
curl http://localhost:3000/api/words/test

# Check browser console for CORS errors
# If CORS issue, add Next.js URL to FastAPI allowed origins
```

---

### Issue: Port 3000 already in use

**Solution**:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
yarn dev -p 3001
```

---

### Issue: Prisma client out of sync

**Error**: `@prisma/client did not initialize yet`

**Solution**:
```bash
# Regenerate Prisma client
yarn prisma generate

# Restart dev server
yarn dev
```

---

## Configuration Options

### Tailwind Configuration

Edit `tailwind.config.ts` to customize:
- Colors
- Fonts
- Spacing
- Breakpoints

### Next.js Configuration

Edit `next.config.js` to customize:
- Redirects/rewrites
- Image domains
- Environment variables
- Bundle analysis

### TypeScript Configuration

Edit `tsconfig.json` to customize:
- Strict mode settings
- Path aliases
- Module resolution

---

## Performance Optimization

### 1. Bundle Analysis

```bash
# Analyze bundle size
ANALYZE=true yarn build
```

### 2. Caching Strategy

**Word lookups**: Cached for 5 minutes (reduce FastAPI load)
**Vocabulary list**: No cache (always fresh)

To adjust cache duration, edit `src/app/api/words/[word]/route.ts`:

```typescript
export const revalidate = 300; // seconds
```

### 3. Database Indexes

Indexes are already defined in Prisma schema for:
- User vocabulary queries
- Word duplicate detection
- Sorting by date

Monitor slow queries with:
```bash
yarn prisma studio
# View query performance in Studio
```

---

## Deployment

### Development Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
cd grimoire-ui
vercel

# Set environment variables in Vercel dashboard:
# - VOCABULARY_DATABASE_URL (use Vercel Postgres or external DB)
# - FASTAPI_URL (production FastAPI URL)
```

### Production Deployment

1. **Database**: Set up production PostgreSQL (Vercel Postgres, Railway, Supabase, etc.)
2. **Environment Variables**: Configure in Vercel dashboard
3. **CORS**: Add Vercel domain to FastAPI allowed origins
4. **Deploy**:

```bash
vercel --prod
```

**Post-deployment**:
- Test word lookup functionality
- Verify vocabulary CRUD operations
- Check response times (should meet performance targets)
- Monitor error logs

---

## Next Steps

After setup, proceed to:

1. **Implementation**: Use `/speckit.tasks` to generate implementation tasks
2. **Testing**: Write tests following `tests/` structure
3. **Customization**: Modify UI components in `src/components/`
4. **Feature Extensions**: Add new fields, tags, or vocabulary features

---

## Useful Commands Reference

| Command | Description |
|---------|-------------|
| `yarn dev` | Start development server |
| `yarn build` | Build for production |
| `yarn start` | Start production server |
| `yarn test` | Run tests |
| `yarn lint` | Lint code |
| `yarn format` | Format code |
| `yarn type-check` | TypeScript check |
| `yarn prisma studio` | Open database GUI |
| `yarn prisma migrate dev` | Create/apply migration |
| `yarn prisma generate` | Generate Prisma client |

---

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Headless UI Documentation](https://headlessui.com/)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/api-routes.md)

---

## Getting Help

**Issues**:
- Check [Troubleshooting](#troubleshooting) section
- Review feature spec and contracts
- Check browser console and terminal for error messages

**Questions**:
- Refer to [spec.md](./spec.md) for requirements
- Refer to [data-model.md](./data-model.md) for database schema
- Refer to [contracts/](./contracts/) for API definitions

---

**Quickstart Status**: ✅ COMPLETE - Ready for development
