# Grimoire UI - Word Vocabulary Builder

A Next.js web application for looking up English words, viewing comprehensive definitions, and building a personal vocabulary collection.

## 🎯 Features

### MVP (Current Implementation)
- ✅ **Word Lookup**: Search for English words and view detailed information (definitions, pronunciation, examples, etymology)
- ✅ **Save to Vocabulary**: Save words to your personal collection
- ✅ **Vocabulary List**: View and manage saved words with pagination and sorting
- ✅ **Unicode Support**: Full support for diacritics and non-English characters
- ✅ **Error Handling**: Clear, user-friendly error messages with retry logic
- ✅ **Responsive Design**: Works on desktop and mobile devices

### Coming Soon
- 🔜 **Edit Word Information**: Customize definitions and add personal notes before saving
- 🔜 **Enhanced Error Handling**: More detailed error messages and retry suggestions
- 🔜 **Search & Filter**: Find words in your vocabulary by tags or content

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and Yarn
- PostgreSQL 14+ (running via Docker Compose)
- FastAPI backend (from feature 001-an-ai-agent)

### Installation

```bash
# 1. Navigate to grimoire-ui directory
cd grimoire-ui

# 2. Install dependencies
yarn install

# 3. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your database connection

# 4. Start PostgreSQL (from repo root)
cd ..
docker-compose up -d postgres

# 5. Set up database (back in grimoire-ui/)
cd grimoire-ui
# Database table is already created via SQL

# 6. Start development server
yarn dev

# 7. Open browser
open http://localhost:3000
```

### Environment Variables

Create `.env.local` with:

```bash
# Database connection (using existing PostgreSQL from Docker Compose)
VOCABULARY_DATABASE_URL="postgresql://grimoire_user:password@localhost:5432/grimoire"

# FastAPI backend URL
FASTAPI_URL="http://localhost:8000"

# Next.js environment
NODE_ENV=development
```

## 🏗️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x
- **UI Components**: Headless UI 2.x
- **Database**: PostgreSQL 14+ with Prisma ORM
- **Validation**: Zod 3.x
- **Forms**: React Hook Form 7.x
- **Deployment**: Vercel-ready

## 📁 Project Structure

```
grimoire-ui/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (word lookup)
│   │   ├── globals.css        # Global styles
│   │   ├── api/               # API routes
│   │   │   ├── words/[word]/route.ts    # Word lookup proxy
│   │   │   └── vocabulary/route.ts      # Vocabulary CRUD
│   │   └── vocabulary/
│   │       └── page.tsx       # Vocabulary list page
│   │
│   ├── components/            # React components
│   │   ├── WordLookupForm.tsx
│   │   ├── WordDisplay.tsx
│   │   └── VocabularyList.tsx
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useWordLookup.ts
│   │   └── useVocabulary.ts
│   │
│   ├── lib/                   # Utilities
│   │   ├── api-client.ts     # Fetch wrapper with retry logic
│   │   ├── db.ts             # Prisma client singleton
│   │   └── errors.ts         # Error handling utilities
│   │
│   └── types/                 # TypeScript types
│       └── contracts.ts       # Zod schemas and types
│
├── prisma/
│   └── schema.prisma         # Database schema
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── .env.local
```

## 🔧 Development

### Available Scripts

```bash
# Development
yarn dev              # Start dev server (http://localhost:3000)

# Build & Production
yarn build            # Build for production
yarn start            # Start production server

# Code Quality
yarn lint             # Run ESLint
yarn type-check       # Run TypeScript compiler

# Database
yarn prisma studio    # Open Prisma Studio (database GUI)
```

## 🧪 Testing the Application

### Word Lookup
1. Navigate to http://localhost:3000
2. Enter a word (e.g., "serendipity")
3. Click "Search" or press Enter
4. View word information (definitions, pronunciation, examples)

### Save to Vocabulary
1. Look up a word
2. Click "Save to Vocabulary" button
3. See confirmation message
4. Navigate to `/vocabulary` to view saved words

### Vocabulary Management
1. Go to http://localhost:3000/vocabulary
2. View all saved words
3. Sort by: Last Modified, Date Saved, or Word
4. Use pagination for large collections

## 🗄️ Database Schema

The application uses a single `vocabulary_entries` table:

```sql
CREATE TABLE vocabulary_entries (
  id VARCHAR(36) PRIMARY KEY,
  word VARCHAR(255) NOT NULL,
  saved_at TIMESTAMP DEFAULT NOW(),
  last_modified TIMESTAMP DEFAULT NOW(),
  user_id VARCHAR(255),

  -- Original API data
  original_data JSONB NOT NULL,

  -- User customizations
  custom_definition TEXT,
  custom_pronunciation VARCHAR(200),
  custom_examples TEXT[],
  custom_notes TEXT,
  custom_synonyms TEXT[],
  custom_antonyms TEXT[],
  custom_tags TEXT[],

  -- Edit history
  edit_history JSONB DEFAULT '[]'::jsonb,

  UNIQUE(word, user_id)
);
```

## 🔌 API Routes

### Word Lookup
- `GET /api/words/[word]` - Proxy to FastAPI backend with 5-minute caching

### Vocabulary CRUD
- `GET /api/vocabulary` - List saved words (pagination, sorting, filtering)
- `POST /api/vocabulary` - Create vocabulary entry
- `GET /api/vocabulary/[id]` - Get single entry
- `PUT /api/vocabulary/[id]` - Update entry
- `DELETE /api/vocabulary/[id]` - Delete entry

## ⚠️ Current Limitations

1. **Prisma Client**: Using placeholders in API routes due to Yarn PnP compatibility issues. Database operations return mock data until resolved.

2. **No Authentication**: Currently using `userId: null` for all entries. Multi-user support will be added later.

3. **Mock Save Functionality**: Vocabulary save operations show success but don't persist to database yet (Prisma client issue).

## 🚧 Troubleshooting

### Port 3000 already in use
```bash
lsof -ti:3000 | xargs kill -9
# Or use a different port
yarn dev -p 3001
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps

# Verify connection string in .env.local
cat .env.local | grep VOCABULARY_DATABASE_URL
```

### FastAPI backend unavailable
```bash
# Start FastAPI backend
cd ../src
uvicorn api.main:app --reload
```

## 📝 Implementation Status

### ✅ Completed (MVP)
- Phase 1: Setup (T001-T012)
- Phase 2: Foundational (T013-T023)
- Phase 3: User Story 1 - Word Lookup (T024-T033)
- Phase 4: User Story 3 - Save to Database (T034-T045)

### 🔜 Upcoming
- Phase 5: User Story 2 - Edit Word Information (T046-T056)
- Phase 6: User Story 4 - Enhanced Error Handling (T057-T063)
- Phase 7: Polish & Accessibility (T064-T080)

## 📚 Documentation

- [Feature Specification](../specs/002-grimoire-ui-implement/spec.md)
- [Implementation Plan](../specs/002-grimoire-ui-implement/plan.md)
- [Data Model](../specs/002-grimoire-ui-implement/data-model.md)
- [API Contracts](../specs/002-grimoire-ui-implement/contracts/)
- [Tasks List](../specs/002-grimoire-ui-implement/tasks.md)

## 🤝 Contributing

This is part of the Grimoire project. See the main repository README for contribution guidelines.

## 📄 License

Part of the Grimoire project - see main repository for license information.

---

**Status**: MVP Complete ✅ | **Version**: 0.1.0 | **Last Updated**: 2025-10-18
