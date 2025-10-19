# Data Model: Grimoire UI

**Feature**: 002-grimoire-ui-implement
**Date**: 2025-10-18
**Database**: PostgreSQL (separate instance: `grimoire_vocabulary`)
**ORM**: Prisma

## Overview

This document defines the data models for the Grimoire UI feature. The feature uses two data sources:

1. **Read-only**: Word information from FastAPI backend (feature 001) - not defined here
2. **Read/Write**: User vocabulary storage - defined below

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│         VocabularyEntry             │
├─────────────────────────────────────┤
│ id: String (UUID)                   │
│ word: String (indexed)              │
│ savedAt: DateTime                   │
│ lastModified: DateTime              │
│ userId: String? (nullable, future)  │
│                                     │
│ // Original API data (immutable)   │
│ originalData: JSON                  │
│                                     │
│ // User edits (mutable)            │
│ customDefinition: String?           │
│ customPronunciation: String?        │
│ customExamples: String[]?           │
│ customNotes: String?                │
│ customSynonyms: String[]?           │
│ customAntonyms: String[]?           │
│ customTags: String[]?               │
│                                     │
│ // Metadata                        │
│ editHistory: EditRecord[]           │
└─────────────────────────────────────┘
```

## Entities

### VocabularyEntry

Represents a word saved by a user to their personal vocabulary collection.

**Purpose**: Store user-customized word entries with both original API data and user edits.

**Lifecycle**:
1. Created when user saves a word from lookup results
2. Updated when user edits any field
3. Deleted when user removes word from vocabulary
4. Queried when displaying saved vocabulary list

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key, auto-generated | Unique identifier for vocabulary entry |
| `word` | String | Required, indexed, lowercase | The word itself (normalized to lowercase for duplicate detection) |
| `savedAt` | DateTime | Required, default: now() | Timestamp when word was first saved |
| `lastModified` | DateTime | Required, auto-update | Timestamp of last edit |
| `userId` | String | Nullable, indexed, foreign key (future) | Owner of this vocabulary entry (null = public/demo mode) |
| `originalData` | JSON | Required | Complete original response from word API (immutable snapshot) |
| `customDefinition` | Text | Nullable | User's custom/simplified definition (overrides original) |
| `customPronunciation` | String | Nullable | User's pronunciation notes |
| `customExamples` | String[] | Nullable | User's custom usage examples |
| `customNotes` | Text | Nullable | User's personal notes about the word |
| `customSynonyms` | String[] | Nullable | User-added synonyms |
| `customAntonyms` | String[] | Nullable | User-added antonyms |
| `customTags` | String[] | Nullable | User-defined tags for categorization (e.g., "advanced", "business", "slang") |
| `editHistory` | JSON | Required, default: [] | Array of edit records (timestamp + field changed) |

**Indexes**:
- Primary: `id`
- Unique: `(word, userId)` - prevents duplicate words per user
- Index: `userId` - for querying user's vocabulary
- Index: `savedAt` - for sorting by save date
- Index: `lastModified` - for sorting by edit date

**Validation Rules**:
- `word`: 1-100 characters, alphanumeric + hyphens/apostrophes, required
- `customDefinition`: max 2000 characters
- `customPronunciation`: max 200 characters
- `customExamples`: max 10 items, each max 500 characters
- `customNotes`: max 5000 characters
- `customSynonyms/Antonyms`: max 20 items each, each max 50 characters
- `customTags`: max 20 items, each max 30 characters
- `originalData`: must be valid JSON, required on creation

**State Transitions**:
```
[NEW] --save--> [SAVED] --edit--> [MODIFIED] --edit--> [MODIFIED]
                   |                    |
                   +-------delete-------+
                            |
                          [DELETED]
```

---

### EditRecord (embedded in editHistory)

Tracks changes made to vocabulary entries for audit and potential undo functionality.

**Purpose**: Provide edit history for user reference and debugging.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | DateTime | When the edit was made |
| `field` | String | Which field was edited (e.g., "customDefinition", "customNotes") |
| `action` | String | "added", "modified", "deleted" |

**Example**:
```json
{
  "editHistory": [
    {
      "timestamp": "2025-10-18T10:30:00Z",
      "field": "customDefinition",
      "action": "modified"
    },
    {
      "timestamp": "2025-10-18T10:32:00Z",
      "field": "customNotes",
      "action": "added"
    }
  ]
}
```

---

## Prisma Schema

```prisma
// grimoire-ui/prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("VOCABULARY_DATABASE_URL")
}

model VocabularyEntry {
  id                    String   @id @default(uuid())
  word                  String   // Normalized to lowercase
  savedAt               DateTime @default(now())
  lastModified          DateTime @updatedAt
  userId                String?  // Nullable for now, required when auth added

  // Original API data (immutable)
  originalData          Json     // Complete word info from API

  // User customizations (all nullable)
  customDefinition      String?  @db.Text
  customPronunciation   String?  @db.VarChar(200)
  customExamples        String[] // Array of strings
  customNotes           String?  @db.Text
  customSynonyms        String[] // Array of strings
  customAntonyms        String[] // Array of strings
  customTags            String[] // Array of strings

  // Edit tracking
  editHistory           Json     @default("[]") // Array of EditRecord objects

  // Indexes and constraints
  @@unique([word, userId]) // One word per user
  @@index([userId])        // Query by user
  @@index([savedAt])       // Sort by save date
  @@index([lastModified])  // Sort by edit date
  @@map("vocabulary_entries")
}
```

---

## API Response Types (from FastAPI backend)

These types represent the data structure returned by the existing word lookup API (feature 001). They are defined here for reference but are not stored in our database.

### WordData (from GET /api/words/{word})

```typescript
// grimoire-ui/src/types/word.ts

interface WordData {
  word: string;
  phonetics: Phonetic[];
  meanings: Meaning[];
  license?: License;
  sourceUrls?: string[];
}

interface Phonetic {
  text?: string;        // IPA pronunciation
  audio?: string;       // URL to audio file
  sourceUrl?: string;
  license?: License;
}

interface Meaning {
  partOfSpeech: string; // "noun", "verb", "adjective", etc.
  definitions: Definition[];
  synonyms?: string[];
  antonyms?: string[];
}

interface Definition {
  definition: string;
  example?: string;
  synonyms?: string[];
  antonyms?: string[];
}

interface License {
  name: string;
  url: string;
}

// Extended type with additional metadata (from our AI agent)
interface EnhancedWordData extends WordData {
  difficulty?: "beginner" | "intermediate" | "advanced" | "expert";
  frequency?: number;        // Usage frequency score
  styleTags?: string[];      // "formal", "informal", "slang", "archaic", etc.
  relatedWords?: string[];   // Semantically related words
  etymology?: string;        // Word origin and history
}
```

---

## UI State Types

These types represent the state of data in the UI, combining API data with user edits.

### EditableWord

```typescript
// grimoire-ui/src/types/vocabulary.ts

interface EditableWord {
  // Metadata
  id?: string;              // Present if saved, undefined if new
  word: string;
  savedAt?: Date;
  lastModified?: Date;

  // Original API data (read-only reference)
  originalData: EnhancedWordData;

  // Current display values (may be original or edited)
  displayDefinition: string;
  displayPronunciation?: string;
  displayExamples: string[];
  displayNotes?: string;
  displaySynonyms: string[];
  displayAntonyms: string[];
  displayTags: string[];

  // Edit tracking
  editedFields: Set<string>;    // Which fields have been modified
  isDirty: boolean;             // Has any field been edited?

  // UI state
  isLoading?: boolean;
  error?: string;
}
```

### VocabularyListItem

```typescript
// grimoire-ui/src/types/vocabulary.ts

interface VocabularyListItem {
  id: string;
  word: string;
  savedAt: Date;
  lastModified: Date;
  hasCustomEdits: boolean;      // Computed: true if any custom* field is non-null
  preview: string;              // First 100 chars of definition for list display
  tags: string[];               // Custom tags for filtering
}
```

---

## Data Access Patterns

### Common Queries

1. **Get user's vocabulary list** (with pagination and sorting):
```typescript
await prisma.vocabularyEntry.findMany({
  where: { userId: userId ?? null },
  orderBy: { lastModified: 'desc' },
  skip: page * pageSize,
  take: pageSize,
  select: {
    id: true,
    word: true,
    savedAt: true,
    lastModified: true,
    customDefinition: true,
    customTags: true,
    originalData: true,
  }
});
```

2. **Check if word already exists**:
```typescript
const existing = await prisma.vocabularyEntry.findUnique({
  where: {
    word_userId: {
      word: word.toLowerCase(),
      userId: userId ?? null,
    }
  }
});
```

3. **Save new vocabulary entry**:
```typescript
await prisma.vocabularyEntry.create({
  data: {
    word: word.toLowerCase(),
    userId: userId ?? null,
    originalData: apiResponse,
    customDefinition: customDef,
    // ... other custom fields
    editHistory: customDef ? [{
      timestamp: new Date(),
      field: 'customDefinition',
      action: 'added'
    }] : [],
  }
});
```

4. **Update existing entry**:
```typescript
await prisma.vocabularyEntry.update({
  where: { id: entryId },
  data: {
    customNotes: newNotes,
    editHistory: {
      push: {
        timestamp: new Date(),
        field: 'customNotes',
        action: 'modified'
      }
    }
  }
});
```

5. **Delete entry**:
```typescript
await prisma.vocabularyEntry.delete({
  where: { id: entryId }
});
```

6. **Search vocabulary** (by word or tags):
```typescript
await prisma.vocabularyEntry.findMany({
  where: {
    userId: userId ?? null,
    OR: [
      { word: { contains: searchQuery.toLowerCase() } },
      { customTags: { has: searchQuery } },
      { customNotes: { contains: searchQuery } }
    ]
  }
});
```

---

## Schema Evolution Considerations

### Future Auth Integration

When authentication is added:
1. Make `userId` required (remove nullable)
2. Add foreign key constraint to User table
3. Add index on userId (already present)
4. Migration: assign existing entries to default user or mark as public

### Additional Features

Potential future fields to add:
- `reviewSchedule`: For spaced repetition learning
- `masteryLevel`: Track user's confidence with word
- `quizHistory`: Record quiz performance
- `lastReviewed`: Timestamp for study tracking
- `favorite`: Boolean for marking important words
- `collection`: String for grouping words into themed collections

---

## Validation Rules Summary

| Field | Min | Max | Pattern | Required |
|-------|-----|-----|---------|----------|
| word | 1 | 100 | `^[a-zA-Z'-]+$` | Yes |
| customDefinition | 0 | 2000 | Any | No |
| customPronunciation | 0 | 200 | Any | No |
| customExamples | 0 items | 10 items | Each max 500 chars | No |
| customNotes | 0 | 5000 | Any | No |
| customSynonyms | 0 items | 20 items | Each max 50 chars | No |
| customAntonyms | 0 items | 20 items | Each max 50 chars | No |
| customTags | 0 items | 20 items | Each max 30 chars, `^[a-z0-9-]+$` | No |

---

## Performance Considerations

### Indexing Strategy
- Primary key (id): UUID for distributed system compatibility
- Unique constraint (word, userId): Fast duplicate detection
- Index on userId: Fast user vocabulary queries
- Index on savedAt/lastModified: Fast sorting

### Query Optimization
- Use `select` to limit returned fields in list views
- Implement cursor-based pagination for large vocabulary lists
- Consider adding full-text search index if search becomes slow (>1000 entries)

### Storage Estimates
- Average entry size: ~2-5 KB (originalData) + 0.5-2 KB (custom fields) = 2.5-7 KB
- 1000 words per user: 2.5-7 MB per user
- 10,000 users: 25-70 GB total (well within PostgreSQL limits)

---

**Phase 1 Data Model Status**: ✅ COMPLETE
