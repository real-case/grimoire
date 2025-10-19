# API Routes Contract: Grimoire UI

**Feature**: 002-grimoire-ui-implement
**Date**: 2025-10-18
**Base Path**: `/api` (Next.js API routes)

## Overview

This document defines the API contracts for Next.js API routes that serve the Grimoire UI. These routes act as:
1. **Proxy** to the FastAPI backend for word lookups
2. **Direct handlers** for vocabulary CRUD operations

## Authentication

**Current**: No authentication (demo/prototype mode)
**Future**: JWT/session token in `Authorization` header

---

## Endpoints

### 1. Word Lookup (Proxy to FastAPI)

**Purpose**: Fetch word information from the FastAPI backend

#### GET `/api/words/[word]`

**Description**: Retrieve comprehensive information about a word

**Parameters**:
- `word` (path): The word to look up (URL-encoded)

**Request Example**:
```http
GET /api/words/serendipity HTTP/1.1
Host: grimoire-ui.vercel.app
Accept: application/json
```

**Success Response** (200 OK):
```json
{
  "word": "serendipity",
  "phonetics": [
    {
      "text": "/ˌsɛr.ənˈdɪp.ə.ti/",
      "audio": "https://example.com/audio/serendipity.mp3",
      "sourceUrl": "https://example.com/source",
      "license": {
        "name": "CC BY-SA 4.0",
        "url": "https://creativecommons.org/licenses/by-sa/4.0"
      }
    }
  ],
  "meanings": [
    {
      "partOfSpeech": "noun",
      "definitions": [
        {
          "definition": "The faculty or phenomenon of finding valuable or agreeable things not sought for.",
          "example": "The discovery was a happy accident, a piece of pure serendipity.",
          "synonyms": ["luck", "chance", "fortuity"],
          "antonyms": []
        }
      ],
      "synonyms": ["luck", "fortune"],
      "antonyms": []
    }
  ],
  "license": {
    "name": "CC BY-SA 4.0",
    "url": "https://creativecommons.org/licenses/by-sa/4.0"
  },
  "sourceUrls": ["https://en.wiktionary.org/wiki/serendipity"],
  "difficulty": "advanced",
  "frequency": 2.3,
  "styleTags": ["formal", "literary"],
  "relatedWords": ["fortunate", "fortuitous", "lucky"],
  "etymology": "Coined by Horace Walpole in 1754..."
}
```

**Error Responses**:

- **404 Not Found** - Word does not exist:
```json
{
  "error": "Word not found",
  "code": "WORD_NOT_FOUND",
  "message": "We couldn't find that word. Please check your spelling and try again.",
  "retryable": false
}
```

- **400 Bad Request** - Invalid word format:
```json
{
  "error": "Invalid word format",
  "code": "INVALID_INPUT",
  "message": "Please enter a valid word (letters, hyphens, and apostrophes only).",
  "retryable": false
}
```

- **502 Bad Gateway** - FastAPI backend unavailable:
```json
{
  "error": "Service unavailable",
  "code": "API_UNAVAILABLE",
  "message": "The word lookup service is temporarily unavailable. Please try again in a moment.",
  "retryable": true
}
```

- **504 Gateway Timeout** - Request timed out:
```json
{
  "error": "Request timeout",
  "code": "TIMEOUT",
  "message": "The request took too long. Please try again.",
  "retryable": true
}
```

**Performance Target**: p95 < 3 seconds (includes FastAPI call)

---

### 2. List Vocabulary

**Purpose**: Retrieve user's saved vocabulary words

#### GET `/api/vocabulary`

**Description**: Get paginated list of saved vocabulary entries

**Query Parameters**:
- `page` (optional): Page number (default: 0)
- `limit` (optional): Items per page (default: 20, max: 100)
- `sortBy` (optional): `savedAt` | `lastModified` | `word` (default: `lastModified`)
- `order` (optional): `asc` | `desc` (default: `desc`)
- `search` (optional): Filter by word/tags/notes (partial match)
- `tags` (optional): Comma-separated tag filter (AND logic)

**Request Example**:
```http
GET /api/vocabulary?page=0&limit=20&sortBy=lastModified&order=desc&search=happy HTTP/1.1
Host: grimoire-ui.vercel.app
Accept: application/json
```

**Success Response** (200 OK):
```json
{
  "entries": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "word": "happiness",
      "savedAt": "2025-10-18T10:30:00Z",
      "lastModified": "2025-10-18T14:22:00Z",
      "hasCustomEdits": true,
      "preview": "A state of well-being and contentment. Custom note: Remember to practice gratitude...",
      "tags": ["emotions", "positive", "beginner"]
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "word": "happy",
      "savedAt": "2025-10-17T09:15:00Z",
      "lastModified": "2025-10-17T09:15:00Z",
      "hasCustomEdits": false,
      "preview": "Feeling or showing pleasure or contentment.",
      "tags": ["emotions", "adjective"]
    }
  ],
  "pagination": {
    "page": 0,
    "limit": 20,
    "total": 47,
    "totalPages": 3,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

**Error Responses**:

- **400 Bad Request** - Invalid query parameters:
```json
{
  "error": "Invalid query parameters",
  "code": "INVALID_QUERY",
  "message": "Invalid value for 'limit'. Must be between 1 and 100.",
  "retryable": false
}
```

- **500 Internal Server Error** - Database error:
```json
{
  "error": "Server error",
  "code": "INTERNAL_ERROR",
  "message": "Something went wrong. Please try again later.",
  "retryable": true
}
```

**Performance Target**: p95 < 500ms

---

### 3. Get Vocabulary Entry

**Purpose**: Retrieve full details of a saved vocabulary entry

#### GET `/api/vocabulary/[id]`

**Description**: Get complete vocabulary entry including original data and all custom edits

**Parameters**:
- `id` (path): Vocabulary entry UUID

**Request Example**:
```http
GET /api/vocabulary/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: grimoire-ui.vercel.app
Accept: application/json
```

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "word": "serendipity",
  "savedAt": "2025-10-18T10:30:00Z",
  "lastModified": "2025-10-18T14:22:00Z",
  "userId": null,
  "originalData": {
    "word": "serendipity",
    "phonetics": [...],
    "meanings": [...],
    "difficulty": "advanced",
    "frequency": 2.3
  },
  "customDefinition": "Lucky accidents that lead to good things",
  "customPronunciation": "ser-en-DIP-ih-tee",
  "customExamples": [
    "It was pure serendipity that I met my mentor at that conference.",
    "The greatest discoveries often result from serendipity."
  ],
  "customNotes": "Remember: coined by Horace Walpole. Use in formal writing.",
  "customSynonyms": ["luck", "fate", "destiny"],
  "customAntonyms": ["planning", "design"],
  "customTags": ["advanced", "formal", "favorite"],
  "editHistory": [
    {
      "timestamp": "2025-10-18T10:30:00Z",
      "field": "customDefinition",
      "action": "added"
    },
    {
      "timestamp": "2025-10-18T14:22:00Z",
      "field": "customNotes",
      "action": "modified"
    }
  ]
}
```

**Error Responses**:

- **404 Not Found** - Entry does not exist:
```json
{
  "error": "Entry not found",
  "code": "ENTRY_NOT_FOUND",
  "message": "This vocabulary entry does not exist or has been deleted.",
  "retryable": false
}
```

**Performance Target**: p95 < 200ms

---

### 4. Create Vocabulary Entry

**Purpose**: Save a new word to user's vocabulary

#### POST `/api/vocabulary`

**Description**: Create a new vocabulary entry

**Request Body**:
```json
{
  "word": "serendipity",
  "originalData": {
    "word": "serendipity",
    "phonetics": [...],
    "meanings": [...]
  },
  "customDefinition": "Lucky accidents that lead to good things",
  "customPronunciation": null,
  "customExamples": [],
  "customNotes": "Remember to use in formal contexts",
  "customSynonyms": ["luck"],
  "customAntonyms": [],
  "customTags": ["advanced", "formal"]
}
```

**Validation Rules**:
- `word`: Required, 1-100 chars, matches `/^[a-zA-Z'-]+$/`
- `originalData`: Required, valid JSON object
- All `custom*` fields: Optional, see data-model.md for max lengths

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "word": "serendipity",
  "savedAt": "2025-10-18T10:30:00Z",
  "lastModified": "2025-10-18T10:30:00Z",
  "message": "Word saved to your vocabulary!"
}
```

**Error Responses**:

- **400 Bad Request** - Validation error:
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "message": "Custom definition exceeds maximum length of 2000 characters.",
  "field": "customDefinition",
  "retryable": false
}
```

- **409 Conflict** - Duplicate word:
```json
{
  "error": "Duplicate entry",
  "code": "DUPLICATE_WORD",
  "message": "You've already saved this word to your vocabulary.",
  "existingId": "550e8400-e29b-41d4-a716-446655440000",
  "retryable": false
}
```

**Performance Target**: p95 < 300ms

---

### 5. Update Vocabulary Entry

**Purpose**: Edit an existing vocabulary entry

#### PUT `/api/vocabulary/[id]`

**Description**: Update custom fields of a vocabulary entry

**Parameters**:
- `id` (path): Vocabulary entry UUID

**Request Body** (all fields optional, only include fields to update):
```json
{
  "customDefinition": "Updated definition",
  "customNotes": "Added more context",
  "customTags": ["advanced", "formal", "favorite"]
}
```

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "lastModified": "2025-10-18T15:45:00Z",
  "message": "Changes saved successfully!"
}
```

**Error Responses**:

- **404 Not Found** - Entry does not exist
- **400 Bad Request** - Validation error
- **422 Unprocessable Entity** - Cannot modify originalData:
```json
{
  "error": "Invalid operation",
  "code": "IMMUTABLE_FIELD",
  "message": "The originalData field cannot be modified. Create a new entry instead.",
  "retryable": false
}
```

**Performance Target**: p95 < 250ms

---

### 6. Delete Vocabulary Entry

**Purpose**: Remove a word from user's vocabulary

#### DELETE `/api/vocabulary/[id]`

**Description**: Delete a vocabulary entry

**Parameters**:
- `id` (path): Vocabulary entry UUID

**Request Example**:
```http
DELETE /api/vocabulary/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: grimoire-ui.vercel.app
```

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Word removed from your vocabulary."
}
```

**Error Responses**:

- **404 Not Found** - Entry does not exist (idempotent - returns success)

**Performance Target**: p95 < 200ms

---

## Error Response Schema

All error responses follow this standard format:

```typescript
interface ErrorResponse {
  error: string;           // Short error description
  code: string;            // Machine-readable error code
  message: string;         // User-friendly error message
  field?: string;          // Field name for validation errors
  retryable: boolean;      // Whether client should retry
  details?: unknown;       // Optional additional context
}
```

### Error Codes

| Code | HTTP Status | Description | Retryable |
|------|-------------|-------------|-----------|
| `WORD_NOT_FOUND` | 404 | Word does not exist in API | No |
| `ENTRY_NOT_FOUND` | 404 | Vocabulary entry does not exist | No |
| `DUPLICATE_WORD` | 409 | Word already in vocabulary | No |
| `INVALID_INPUT` | 400 | Invalid word format or query params | No |
| `VALIDATION_ERROR` | 400 | Field validation failed | No |
| `IMMUTABLE_FIELD` | 422 | Attempt to modify read-only field | No |
| `API_UNAVAILABLE` | 502 | FastAPI backend down | Yes |
| `TIMEOUT` | 504 | Request exceeded time limit | Yes |
| `INTERNAL_ERROR` | 500 | Unexpected server error | Yes |
| `NETWORK_ERROR` | 0 | Client-side network failure | Yes |

---

## Rate Limiting

**Current**: None (demo mode)

**Future**:
- Authenticated users: 1000 requests/hour
- Vocabulary operations: 100 creates/hour, 500 reads/hour
- Word lookups: 200 requests/hour (proxied to FastAPI rate limits)

**Rate Limit Headers** (future):
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1634567890
```

---

## CORS Configuration

**Allowed Origins**:
- Development: `http://localhost:3000`
- Production: `https://grimoire-ui.vercel.app`

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

---

## Caching Strategy

### Word Lookups (`/api/words/[word]`)
- **Server-side**: Cache FastAPI responses for 5 minutes
- **Client-side**: `Cache-Control: public, max-age=300, stale-while-revalidate=60`

### Vocabulary List (`/api/vocabulary`)
- **Server-side**: No caching (always fresh)
- **Client-side**: `Cache-Control: no-cache` (revalidate on every request)

### Vocabulary Entry (`/api/vocabulary/[id]`)
- **Server-side**: No caching
- **Client-side**: `Cache-Control: no-cache`

---

## TypeScript Types

```typescript
// Request/Response types for API routes

// Word lookup
export type WordLookupResponse = EnhancedWordData | ErrorResponse;

// Vocabulary list
export interface VocabularyListRequest {
  page?: number;
  limit?: number;
  sortBy?: 'savedAt' | 'lastModified' | 'word';
  order?: 'asc' | 'desc';
  search?: string;
  tags?: string;
}

export interface VocabularyListResponse {
  entries: VocabularyListItem[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// Create/Update vocabulary
export interface CreateVocabularyRequest {
  word: string;
  originalData: EnhancedWordData;
  customDefinition?: string;
  customPronunciation?: string;
  customExamples?: string[];
  customNotes?: string;
  customSynonyms?: string[];
  customAntonyms?: string[];
  customTags?: string[];
}

export interface UpdateVocabularyRequest {
  customDefinition?: string;
  customPronunciation?: string;
  customExamples?: string[];
  customNotes?: string;
  customSynonyms?: string[];
  customAntonyms?: string[];
  customTags?: string[];
}

export interface VocabularyMutationResponse {
  id: string;
  word?: string;
  savedAt?: string;
  lastModified: string;
  message: string;
}

// Error response
export interface ErrorResponse {
  error: string;
  code: string;
  message: string;
  field?: string;
  retryable: boolean;
  details?: unknown;
}
```

---

## Testing Requirements

### Contract Tests
- Verify request/response schemas match this specification
- Test all error scenarios and status codes
- Validate error response format consistency

### Integration Tests
- Test FastAPI proxy with mocked backend
- Test vocabulary CRUD operations with test database
- Test pagination, sorting, filtering logic
- Test duplicate detection
- Test validation rules

### Performance Tests
- Verify p95 response times under load
- Test concurrent vocabulary operations
- Stress test pagination with large datasets

---

**Contract Status**: ✅ COMPLETE - Ready for implementation
