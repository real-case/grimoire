# Quickstart Guide: Grimoire Word Information API

**Feature**: 001-an-ai-agent
**Version**: 1.0.0
**Last Updated**: 2025-10-13

## Overview

Grimoire is a comprehensive word information API designed for English as a Foreign Language (EFL) learners. It provides definitions, phonetic transcriptions (IPA), usage examples, grammatical information, synonyms/antonyms, difficulty levels (CEFR), and frequency data.

### Key Features

- 📚 Comprehensive word definitions (learner-appropriate language)
- 🗣️ IPA phonetic transcriptions for pronunciation
- 📝 3-5 natural usage examples per definition
- ✏️ Complete grammatical information (plurals, verb forms, etc.)
- 🔗 Related words (synonyms, antonyms, word families)
- 📊 CEFR difficulty levels (A1-C2) and frequency rankings
- ⚡ Fast response times (<500ms cached, <2000ms non-cached)
- 🤖 AI-powered enrichment via Claude

---

## Prerequisites

### Required Software

- **Python 3.12+** (tested with 3.12)
- **PostgreSQL 14+** (for persistent storage)
- **Redis 7+** (for caching)
- **Docker & Docker Compose** (recommended for local development)

### API Keys

- **Anthropic API Key**: Required for AI-powered word enrichment
  - Sign up at: https://console.anthropic.com/
  - Cost: ~$0.01-0.05 per new word enrichment

---

## Quick Start (Docker)

The fastest way to get started is using Docker Compose:

### 1. Clone and Setup

```bash
git clone <repository-url>
cd grimoire

# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Start Services

```bash
# Start PostgreSQL, Redis, and the API
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# (Optional) Load common 10,000 words
docker-compose exec api python scripts/load_common_words.py
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Lookup a word
curl http://localhost:8000/api/v1/words/serendipity | jq

# Expected response:
# {
#   "word": "serendipity",
#   "phonetic": {
#     "ipa": "/ˌserənˈdɪpɪti/"
#   },
#   "definitions": [
#     {
#       "part_of_speech": "noun",
#       "definition": "The occurrence and development of events by chance...",
#       "examples": ["Meeting her was pure serendipity.", ...]
#     }
#   ],
#   "learning_metadata": {
#     "difficulty_level": "C1",
#     "frequency_rank": 12453,
#     "frequency_band": "top-10000"
#   },
#   ...
# }
```

### 5. View API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```bash
# Create database
createdb grimoire

# Create user (optional)
psql -c "CREATE USER grimoire_user WITH PASSWORD 'your_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE grimoire TO grimoire_user;"
```

### 3. Setup Redis

```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### 4. Configure Environment

```bash
# Copy and edit .env
cp .env.example .env

# Required environment variables:
cat << EOF > .env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://grimoire_user:your_password@localhost/grimoire

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Data Sources
ENABLE_WORDNET=true
ENABLE_CMU_DICT=true
ENABLE_CEFR_LEVELS=true

# Rate Limiting
RATE_LIMIT_ANON_HOURLY=100
RATE_LIMIT_ANON_BURST=10

# Logging & Monitoring (optional)
SENTRY_DSN=  # Add if using Sentry
EOF
```

### 5. Run Migrations

```bash
# Initialize Alembic (first time only)
alembic upgrade head
```

### 6. Start the API

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## API Usage Examples

### Basic Word Lookup

```bash
curl http://localhost:8000/api/v1/words/cat
```

**Response**:
```json
{
  "word": "cat",
  "language": "en",
  "phonetic": {
    "ipa": "/kæt/",
    "audio_url": null
  },
  "definitions": [
    {
      "part_of_speech": "noun",
      "definition": "A small furry animal with whiskers, claws, and a tail, commonly kept as a pet.",
      "usage_context": null,
      "examples": [
        "My cat loves to sleep in the sun.",
        "The cat caught a mouse in the garden.",
        "She adopted a stray cat from the shelter."
      ]
    }
  ],
  "grammatical_info": {
    "part_of_speech": "noun",
    "plural_form": "cats",
    "verb_forms": null,
    "adjective_forms": null
  },
  "learning_metadata": {
    "difficulty_level": "A1",
    "cefr_level": "A1",
    "frequency_rank": 1245,
    "frequency_band": "top-5000",
    "style_tags": []
  },
  "related_words": [
    {
      "word": "kitten",
      "relationship": "related",
      "usage_notes": "A young cat"
    },
    {
      "word": "feline",
      "relationship": "synonym",
      "usage_notes": "More formal term"
    }
  ],
  "data_completeness": {
    "missing_fields": [],
    "completeness_percentage": 100
  }
}
```

### Word with Multiple Meanings

```bash
curl http://localhost:8000/api/v1/words/run
```

Returns multiple definitions with different parts of speech and contexts.

### Exclude Related Words

```bash
curl "http://localhost:8000/api/v1/words/serendipity?include_related=false"
```

### Exclude Usage Examples

```bash
curl "http://localhost:8000/api/v1/words/serendipity?include_examples=false"
```

---

## Common Tasks

### Adding New Words

Words are automatically enriched on first lookup. To pre-load common words:

```bash
# Load top 10,000 English words
python scripts/load_common_words.py --count 10000

# This will:
# 1. Read word frequency list
# 2. Batch enrich via Claude API
# 3. Supplement with WordNet, CMU Dict, CEFR-J
# 4. Store in PostgreSQL
# 5. Cache in Redis

# Estimated time: 2-4 hours
# Estimated cost: $100-500 (one-time)
```

### Monitoring Cache Performance

```bash
# Redis CLI
redis-cli

# Check cache stats
INFO stats

# View cached words
KEYS grimoire:word:*

# Check specific word cache
GET grimoire:word:serendipity
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with output
pytest -v -s
```

---

## Performance Tuning

### Database Optimization

```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM words WHERE word_text = 'serendipity';

-- Vacuum database (run periodically)
VACUUM ANALYZE;
```

### Redis Cache Tuning

```bash
# In redis.conf or via docker-compose environment:

# Memory limit
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (optional, cache can be rebuilt)
save ""  # Disable persistence for pure cache use

# Connection pool settings (in .env)
REDIS_POOL_MIN_SIZE=10
REDIS_POOL_MAX_SIZE=50
```

### Application Performance

```bash
# Monitor request times
# Check X-Cache-Status header
curl -I http://localhost:8000/api/v1/words/cat

# Response headers:
# X-Cache-Status: HIT  (or MISS for first lookup)
# X-RateLimit-Remaining: 99
# X-RateLimit-Reset: 1697200000
```

---

## Data Sources

### Primary Source

**Anthropic Claude API**:
- AI-powered comprehensive word enrichment
- Generates definitions, examples, grammatical information
- License: Anthropic API Terms of Service
- Attribution: Not required in API responses

### Supplementary Sources

**WordNet 3.1** (Open Source):
- Synonym/antonym relationships, word families
- License: WordNet License (freely redistributable)
- URL: https://wordnet.princeton.edu/
- Attribution: "Data from WordNet 3.1 (Princeton University)"

**CMU Pronouncing Dictionary** (Public Domain):
- Phonetic pronunciations (ARPABET → IPA conversion)
- URL: http://www.speech.cs.cmu.edu/cgi-bin/cmudict
- Attribution: "Phonetic data from CMU Pronouncing Dictionary"

**CEFR-J Wordlist** (Open Academic Data):
- Difficulty levels for 10,000+ common words
- Source: Tamagawa University CEFR-J project
- License: Creative Commons (academic research data)
- Attribution: "Difficulty levels from CEFR-J Wordlist (Tamagawa University)"

**English Word Frequency List**:
- Frequency rankings from Google Books Ngram / COCA
- License: Research data (freely available)
- Attribution: "Frequency data from [source name]"

### Attribution

All data sources are properly attributed in documentation. API responses may optionally include attribution metadata.

---

## Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs -f api

# Common issues:
# 1. Port 8000 already in use
lsof -i :8000  # Kill process or change port

# 2. Database connection failed
# Verify DATABASE_URL in .env
# Check PostgreSQL is running: pg_isready

# 3. Redis connection failed
# Check Redis is running: redis-cli ping
```

### Slow Word Lookups

```bash
# 1. Check if Redis is running
redis-cli ping

# 2. Verify cache is being used
curl -I http://localhost:8000/api/v1/words/cat
# Look for: X-Cache-Status: HIT

# 3. Check database indexes
psql grimoire -c "\d words"

# 4. Monitor Claude API response time
# Check logs for "Enrichment duration"
```

### Rate Limit Issues

```bash
# Check current rate limit settings
grep RATE_LIMIT .env

# Adjust in .env:
RATE_LIMIT_ANON_HOURLY=1000  # Increase if needed
RATE_LIMIT_ANON_BURST=20

# Restart API
docker-compose restart api
```

### Database Migration Errors

```bash
# Check current migration version
alembic current

# View pending migrations
alembic heads

# Force to specific version (careful!)
alembic stamp head

# Reset and reapply (development only!)
alembic downgrade base
alembic upgrade head
```

---

## Architecture Overview

```
┌─────────────┐
│   Client    │
│  (Browser,  │
│  Mobile App)│
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│        FastAPI Application           │
│  ┌────────────────────────────────┐  │
│  │  API Layer (v1/endpoints/)     │  │
│  │  - Rate limiting middleware    │  │
│  │  - Request validation          │  │
│  └──────────────┬─────────────────┘  │
│                 ▼                     │
│  ┌────────────────────────────────┐  │
│  │  Service Layer                 │  │
│  │  - WordService (business logic)│  │
│  │  - EnrichmentService (AI)      │  │
│  │  - CacheService                │  │
│  └──────────────┬─────────────────┘  │
│                 ▼                     │
│  ┌────────────────────────────────┐  │
│  │  Repository Layer              │  │
│  │  - WordRepository (data access)│  │
│  └──────────────┬─────────────────┘  │
└─────────────────┼────────────────────┘
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
┌─────────────┐       ┌─────────────┐
│ PostgreSQL  │       │    Redis    │
│  (Storage)  │       │   (Cache)   │
└─────────────┘       └─────────────┘
       │
       ▼
┌─────────────────────────────┐
│   External Data Sources     │
│  - Anthropic Claude API     │
│  - WordNet (local)          │
│  - CMU Dictionary (local)   │
│  - CEFR-J (local)           │
└─────────────────────────────┘
```

---

## Next Steps

1. **Read the full API specification**: See `contracts/openapi.yaml`
2. **Review the data model**: See `data-model.md`
3. **Explore implementation tasks**: Run `/speckit.tasks` to generate implementation tasks
4. **Set up monitoring**: Configure Sentry for error tracking, Prometheus for metrics
5. **Deploy to production**: See deployment guides for Railway/Fly.io/DigitalOcean

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: `specs/001-an-ai-agent/contracts/openapi.yaml`
- **Data Model**: `specs/001-an-ai-agent/data-model.md`
- **Research Decisions**: `specs/001-an-ai-agent/research.md`
- **Implementation Plan**: `specs/001-an-ai-agent/plan.md`

---

**Last Updated**: 2025-10-13
**Grimoire Version**: 1.0.0
**API Version**: v1
