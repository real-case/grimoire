# Research: Word Information Service for EFL Learners

**Feature**: 001-an-ai-agent
**Date**: 2025-10-13
**Phase**: 0 - Research & Decision Making

## Overview

This document resolves all NEEDS CLARIFICATION items from the Technical Context and provides architectural decisions for implementing the word information service.

## Research Topics

### 1. Rate Limiting Strategy

**Question**: What rate limits should be applied to protect service availability?

**Decision**: Implement tiered rate limiting based on usage patterns

**Rationale**:
- EFL learning is typically interactive but not high-frequency (students look up words as they encounter them)
- Need to prevent abuse while allowing legitimate learning workflows
- Industry standard for free educational APIs is 100-1000 requests/hour per user

**Recommended Limits**:
- **Anonymous users (by IP)**: 100 requests per hour, 500 requests per day
- **Authenticated users** (future): 1000 requests per hour, 5000 requests per day
- **Burst limit**: 10 requests per minute to allow rapid lookup workflows
- **Global limit**: 10,000 requests per minute across all users

**Implementation**:
- Use FastAPI middleware with Redis-backed sliding window algorithm
- Library: `slowapi` (integrates with FastAPI and Redis)
- Return standard HTTP 429 (Too Many Requests) with Retry-After header

**Alternatives Considered**:
- Token bucket algorithm: More complex, unnecessary for this use case
- Fixed window: Less accurate, can allow double requests at window boundaries
- No rate limiting: Rejected due to constitutional requirement (Principle IV)

---

### 2. Data Source Licensing and Selection

**Question**: Which dictionaries/APIs are permissible for sourcing word information?

**Decision**: Multi-source strategy with Claude AI enrichment as primary, supplemented by open-source datasets

**Primary Data Sources**:

1. **Anthropic Claude API (Primary)**
   - **Usage**: AI-powered generation and enrichment of word information
   - **License**: Anthropic API Terms of Service (commercial use allowed)
   - **Coverage**: Comprehensive - can generate all required fields
   - **Pros**:
     - Single integration for all linguistic data
     - Natural, learner-appropriate language
     - Can generate context-specific examples
     - Handles edge cases gracefully
   - **Cons**:
     - API costs per request
     - Requires internet connectivity
     - Variable response time (mitigated by caching)
   - **Rationale**: Grimoire is explicitly described as "an AI agent" - Claude is the natural choice for comprehensive, learner-focused content

2. **WordNet 3.1 (Open Source - Supplementary)**
   - **Usage**: Synonym/antonym relationships, word families
   - **License**: WordNet License (freely redistributable, academic/commercial use allowed)
   - **URL**: https://wordnet.princeton.edu/
   - **Coverage**: 155,000+ English words with semantic relationships
   - **Pros**: Free, well-structured, excellent for semantic relationships
   - **Cons**: Definitions are technical, not learner-friendly
   - **Integration**: Use for synonym/antonym validation and enrichment

3. **CMU Pronouncing Dictionary (Open Source - Supplementary)**
   - **Usage**: Phonetic pronunciations (ARPABET notation, convertible to IPA)
   - **License**: Public domain
   - **URL**: http://www.speech.cs.cmu.edu/cgi-bin/cmudict
   - **Coverage**: 134,000+ North American English pronunciations
   - **Pros**: Free, accurate phonetics, well-maintained
   - **Cons**: ARPABET format requires conversion to IPA
   - **Integration**: Use for phonetic validation and IPA cross-reference

4. **CEFR-J Wordlist (Open Academic Data - Supplementary)**
   - **Usage**: Difficulty levels (A1-C2) for 10,000+ common English words
   - **License**: Creative Commons (academic research data)
   - **Source**: Tamagawa University CEFR-J project
   - **Coverage**: 10,000 headwords with CEFR levels
   - **Pros**: Specifically designed for EFL learners, well-researched
   - **Cons**: Limited to common vocabulary
   - **Integration**: Map difficulty levels for known words, Claude estimates for others

5. **English Word Frequency List (Open Data - Supplementary)**
   - **Source**: Google Books Ngram corpus or COCA (Corpus of Contemporary American English)
   - **License**: Research data (freely available)
   - **Usage**: Word frequency rankings for learning prioritization
   - **Coverage**: Millions of words with frequency data
   - **Integration**: Assign frequency bands (top 1k, 5k, 10k, etc.)

**Data Flow Architecture**:
```
User Request → Cache Check → [Hit: Return cached data]
                           ↓ [Miss]
                    Word Repository Check
                           ↓
                [Exists: Return from DB] [Not exists: Enrich & Store]
                           ↓
                Claude AI Enrichment Service
                    ↓
            Generate comprehensive word info
            (definitions, examples, grammar)
                    ↓
            Validate/Enrich with open sources
            (WordNet for synonyms, CMU for phonetics,
             CEFR-J for difficulty, frequency lists)
                    ↓
            Store in PostgreSQL → Cache in Redis → Return
```

**Cost Management**:
- Cache all enriched words indefinitely (Redis + PostgreSQL)
- Only call Claude API for new words or periodic updates
- Batch-enrich common 10,000 words during initial setup
- Estimated cost: $0.01-0.05 per new word enrichment (amortized over all queries)

**Attribution**:
- Document all data sources in API responses (optional metadata field)
- Include attribution in quickstart.md and documentation
- Comply with all license requirements

**Alternatives Considered**:
- **Proprietary APIs** (Merriam-Webster, Oxford): Expensive, restrictive licenses, not learner-focused
- **Wikipedia/Wiktionary scraping**: Terms of service violations, unreliable data quality
- **Pre-built EFL datasets**: Limited coverage, static data, no examples

---

### 3. Data Source Integration Architecture

**Question**: How should data sources be integrated to maintain extensibility?

**Decision**: Adapter pattern with service layer abstraction

**Architecture**:

```python
# Abstract base adapter
class DataSourceAdapter(ABC):
    @abstractmethod
    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """Fetch raw word data from source"""
        pass

    @abstractmethod
    def supports_field(self, field: str) -> bool:
        """Check if adapter provides a specific field"""
        pass

# Concrete adapters
class ClaudeEnrichmentAdapter(DataSourceAdapter):
    """Primary: AI-powered comprehensive enrichment"""
    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        # Call Anthropic API with structured prompt
        pass

class WordNetAdapter(DataSourceAdapter):
    """Supplementary: Synonyms, antonyms, relationships"""
    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        # Query local WordNet database
        pass

class CMUPhoneticAdapter(DataSourceAdapter):
    """Supplementary: Phonetic pronunciations"""
    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        # Query CMU dictionary, convert ARPABET to IPA
        pass

# Orchestration service
class EnrichmentService:
    def __init__(self):
        self.adapters = [
            ClaudeEnrichmentAdapter(),
            WordNetAdapter(),
            CMUPhoneticAdapter(),
        ]

    async def enrich_word(self, word: str) -> WordData:
        """
        1. Call Claude for comprehensive data (primary)
        2. Validate/supplement with open sources
        3. Merge results into complete WordData
        """
        pass
```

**Benefits**:
- New data sources can be added without changing core logic
- Each adapter is independently testable
- Can prioritize sources (Claude primary, others supplementary)
- Easy to add caching at adapter level
- Supports fallback strategies if primary source fails

**Configuration** (in .env):
```
# Data Sources
ANTHROPIC_API_KEY=sk-...
ENABLE_WORDNET=true
ENABLE_CMU_DICT=true
ENABLE_CEFR_LEVELS=true

# Enrichment Strategy
PRIMARY_SOURCE=claude
FALLBACK_SOURCES=wordnet,cmu
REQUIRE_ALL_FIELDS=false
```

**Error Handling**:
- If Claude API fails: Return partial data from supplementary sources + flag incomplete
- If supplementary sources fail: Log warning, continue with Claude data only
- Comply with constitution Principle III (explicit indication of missing data)

---

## Technology Best Practices

### FastAPI Best Practices

**Research Summary**:

1. **Async/Await**: Use async route handlers for I/O-bound operations (database, cache, external APIs)
2. **Dependency Injection**: Use FastAPI's `Depends()` for database sessions, auth, configuration
3. **Pydantic Models**: Strict request/response validation with Pydantic v2
4. **Error Handling**: Custom exception handlers for consistent error responses
5. **Versioning**: Route prefix `/api/v1/` for future versioning
6. **Documentation**: Auto-generated OpenAPI (Swagger) at `/docs` and ReDoc at `/redoc`
7. **Middleware**: CORS, rate limiting, request logging, error tracking (Sentry)
8. **Testing**: Use `TestClient` for sync testing, `httpx.AsyncClient` for async

**Recommended Structure** (implemented in Project Structure):
- Separate Pydantic schemas (`api/v1/models/`) from SQLAlchemy models (`models/`)
- Business logic in services (`services/`), data access in repositories (`repositories/`)
- Configuration via `pydantic-settings` (type-safe environment variables)

### PostgreSQL + SQLAlchemy Async Best Practices

**Research Summary**:

1. **Async Engine**: Use `create_async_engine` with `asyncpg` driver
2. **Session Management**: AsyncSession with async context managers
3. **Connection Pooling**: Configure pool size (min 5, max 20 for this scale)
4. **Indexes**:
   - B-tree index on `word.word_text` (primary lookup)
   - GIN index on `definition.definition_text` for full-text search (future feature)
   - Foreign key indexes on all relationship columns
5. **Migrations**: Alembic with `alembic revision --autogenerate` for schema changes
6. **Query Optimization**:
   - Use eager loading (`selectinload`, `joinedload`) to avoid N+1 queries
   - Limit result sets for relationships
7. **Transactions**: Use async transaction context for multi-table operations

**Example**:
```python
# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Route with dependency injection
@router.get("/words/{word}")
async def get_word(
    word: str,
    db: AsyncSession = Depends(get_db)
):
    return await word_service.lookup_word(word, db)
```

### Redis Caching Best Practices

**Research Summary**:

1. **Key Naming**: Prefix with namespace (e.g., `grimoire:word:{word}`)
2. **Serialization**: Use JSON for complex objects, msgpack for performance
3. **TTL Strategy**:
   - Common words (top 5000): No expiration (cache indefinitely)
   - Less common words: 30-day TTL
   - Failed lookups: 1-hour TTL to prevent repeated failed API calls
4. **Cache Invalidation**: Explicit invalidation when data is updated
5. **Connection Pooling**: Use connection pool (min 10, max 50)
6. **Fallback**: Graceful degradation if Redis unavailable (slower, but still functional)

**Cache Key Strategy**:
```
grimoire:word:{word_text}                 # Full word data
grimoire:word:{word_text}:definitions     # Just definitions
grimoire:word:{word_text}:frequency       # Frequency rank
grimoire:rate_limit:{ip}:{window}         # Rate limiting counters
```

---

## Decision Summary

| Topic | Decision | Status |
|-------|----------|--------|
| Rate Limiting | 100 req/hour (anon), 10 req/min burst, slowapi + Redis | ✅ RESOLVED |
| Data Sources | Claude (primary) + WordNet + CMU + CEFR-J + frequency lists | ✅ RESOLVED |
| Architecture | Adapter pattern with service layer orchestration | ✅ RESOLVED |
| Primary API | Anthropic Claude for AI-powered enrichment | ✅ RESOLVED |
| Caching Strategy | Redis with tiered TTL (indefinite for common words) | ✅ RESOLVED |
| Phonetics | CMU Dict + Claude, convert ARPABET to IPA | ✅ RESOLVED |
| Difficulty Levels | CEFR-J for common words, Claude estimates for others | ✅ RESOLVED |

**All NEEDS CLARIFICATION items resolved ✅**

**Next Phase**: Phase 1 - Design (data-model.md, contracts/, quickstart.md)
