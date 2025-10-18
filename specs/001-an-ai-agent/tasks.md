# Tasks: Word Information Service for EFL Learners

**Input**: Design documents from `/specs/001-an-ai-agent/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are optional for this feature. Tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure needed by all user stories

- [x] T001 Create project directory structure per implementation plan (src/, tests/, alembic/, etc.)
- [x] T002 [P] Create pyproject.toml with project metadata (name: grimoire, version: 1.0.0, Python 3.12+)
- [x] T003 [P] Create requirements.txt with all dependencies from plan.md (FastAPI, Anthropic, SQLAlchemy, Redis, etc.)
- [x] T004 [P] Create .env.example with all required environment variables (DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, rate limits)
- [x] T005 [P] Create docker-compose.yml with PostgreSQL and Redis services for local development
- [x] T006 [P] Create Dockerfile for production deployment with Python 3.12 base image
- [x] T007 [P] Configure ruff for linting in pyproject.toml
- [x] T008 [P] Configure black for formatting in pyproject.toml
- [x] T009 [P] Configure mypy for type checking in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 [P] Implement core configuration in src/core/config.py using Pydantic BaseSettings (DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, rate limits)
- [x] T011 [P] Implement logging setup in src/core/logging.py using loguru with JSON formatting
- [x] T012 Implement async database session management in src/core/database.py (create_async_engine, async_session_maker, get_db dependency)
- [x] T013 Implement Redis connection and cache utilities in src/core/cache.py (async Redis client, get_redis dependency, cache key builders)
- [x] T014 Initialize Alembic for database migrations (alembic init alembic, configure alembic.ini with async PostgreSQL)
- [x] T015 Create base SQLAlchemy model with common fields in src/models/__init__.py (id, created_at, updated_at, Base class)
- [x] T016 [P] Implement Word model in src/models/word.py (id, word_text unique index, language, timestamps, last_enriched_at)
- [x] T017 [P] Implement Definition model in src/models/definition.py (id, word_id FK, definition_text, part_of_speech, usage_context, order_index)
- [x] T018 [P] Implement UsageExample model in src/models/usage_example.py (id, definition_id FK, example_text, context_type, order_index)
- [x] T019 [P] Implement PhoneticRepresentation model in src/models/phonetic.py (id, word_id FK unique, ipa_transcription, audio_url nullable)
- [x] T020 [P] Implement GrammaticalInformation model in src/models/grammar.py (id, word_id FK unique, plural_form, verb forms, adjective forms, irregular_forms_json JSONB)
- [x] T021 [P] Implement LearningMetadata model in src/models/learning_metadata.py (id, word_id FK unique, difficulty_level, cefr_level, frequency_rank, frequency_band, style_tags array)
- [x] T022 [P] Implement RelatedWord model in src/models/related_word.py (id, source_word_id FK, target_word_id FK, relationship_type, usage_notes, strength, unique constraint)
- [x] T023 Create initial database migration in alembic/versions/ (autogenerate from all models, include all indexes and constraints)
- [x] T024 Implement WordRepository in src/repositories/word_repository.py (get_by_word_text, create_word_with_all_relations, update_word async methods)
- [x] T025 Implement abstract DataSourceAdapter in src/services/data_source_adapter.py (fetch_word_data, supports_field abstract methods)
- [x] T026 Implement CacheService in src/services/cache_service.py (get_cached_word, set_cached_word with TTL strategy, invalidate_word_cache)
- [x] T027 [P] Create Pydantic request schemas in src/api/v1/models/requests.py (WordLookupRequest with query parameters)
- [x] T028 [P] Create Pydantic response schemas in src/api/v1/models/responses.py (WordResponse, PhoneticSchema, DefinitionSchema, GrammaticalInfoSchema, LearningMetadataSchema, RelatedWordSchema, DataCompletenessSchema, ErrorResponse)
- [x] T029 Implement rate limiting middleware in src/api/middleware/rate_limit.py (slowapi integration, Redis-backed sliding window, 100 req/hr anon, 10 req/min burst)
- [x] T030 Implement error handling middleware in src/api/middleware/error_handlers.py (global exception handlers, standardized error responses with error codes)
- [x] T031 [P] Implement CORS middleware configuration in src/api/middleware/cors.py (allow origins, methods, headers for web clients)
- [x] T032 Create FastAPI application in src/main.py (app initialization, middleware registration, lifespan events for DB/Redis connections)
- [x] T033 Implement health check endpoint in src/api/v1/endpoints/health.py (GET /health, check database, Redis, and AI service connectivity)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Word Lookup (Priority: P1) 🎯 MVP

**Goal**: Provide immediate, comprehensive word information (definition, phonetics, usage examples, grammatical information)

**Independent Test**: Query "serendipity" and verify response includes definition, IPA phonetics, usage examples, and grammatical information

### Implementation for User Story 1

- [x] T034 [P] [US1] Implement ClaudeEnrichmentAdapter in src/services/claude_enrichment_adapter.py (fetch_word_data via Anthropic API, structured prompt for definitions/phonetics/grammar/examples, supports_field for all fields)
- [x] T035 [P] [US1] Implement WordNetAdapter in src/services/wordnet_adapter.py (fetch_word_data from local WordNet, supports_field for synonyms/antonyms)
- [x] T036 [P] [US1] Implement CMUPhoneticAdapter in src/services/cmu_phonetic_adapter.py (fetch_word_data from CMU dict, convert ARPABET to IPA, supports_field for phonetics)
- [x] T037 [US1] Implement EnrichmentService in src/services/enrichment_service.py (enrich_word orchestrates all adapters, merges data from Claude + WordNet + CMU, validates completeness)
- [x] T038 [US1] Implement WordService core logic in src/services/word_service.py (lookup_word checks cache → DB → enrichment, create_word_from_enrichment, calculate_data_completeness)
- [x] T039 [US1] Implement GET /api/v1/words/{word} endpoint in src/api/v1/endpoints/words.py (route handler, call word_service.lookup_word, return WordResponse, handle 404/400/500 errors)
- [x] T040 [US1] Add word normalization logic in src/api/v1/endpoints/words.py (lowercase conversion, strip whitespace, validate pattern ^[a-z]+(-[a-z]+)*$)
- [x] T041 [US1] Add cache status header in src/api/v1/endpoints/words.py (X-Cache-Status: HIT/MISS based on cache service result)
- [x] T042 [US1] Add rate limit headers in src/api/v1/endpoints/words.py (X-RateLimit-Remaining, X-RateLimit-Reset from rate limit middleware)
- [x] T043 [US1] Implement word not found error handling in src/api/v1/endpoints/words.py (404 response with WordNotFoundResponse, include spelling suggestions if available)

**Checkpoint**: At this point, User Story 1 should be fully functional - students can query words and receive comprehensive information

---

## Phase 4: User Story 2 - Contextual Learning with Examples (Priority: P2)

**Goal**: Provide 3-5 natural usage examples in different contexts to help learners understand nuances

**Independent Test**: Query "ubiquitous" and verify multiple natural usage examples are provided showing the word in different contexts

### Implementation for User Story 2

- [x] T044 [US2] Enhance ClaudeEnrichmentAdapter in src/services/claude_enrichment_adapter.py (improve prompt to generate 3-5 context-specific examples: academic, casual, business)
- [x] T045 [US2] Implement example context detection in src/services/enrichment_service.py (classify examples into context types: academic, casual, business, technical)
- [x] T046 [US2] Add example filtering in src/services/word_service.py (respect include_examples query parameter, filter examples based on request)
- [x] T047 [US2] Update WordResponse schema in src/api/v1/models/responses.py (ensure examples array is properly populated for all definitions)
- [x] T048 [US2] Add query parameter include_examples to GET /api/v1/words/{word} in src/api/v1/endpoints/words.py (default=true, boolean)
- [x] T049 [US2] Implement example quality validation in src/services/enrichment_service.py (verify each example contains the target word, 5-300 chars, natural language)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - learners get comprehensive info with rich examples

---

## Phase 5: User Story 3 - Vocabulary Expansion with Synonyms and Related Words (Priority: P3)

**Goal**: Provide synonyms, antonyms, and related words with usage notes to help learners expand vocabulary

**Independent Test**: Query "happy" and verify synonyms (joyful, content, pleased), antonyms (sad, unhappy, miserable), and related words (happiness, happily) are provided with context

### Implementation for User Story 3

- [x] T050 [US3] Enhance WordNetAdapter in src/services/wordnet_adapter.py (fetch full synonym sets, antonym sets, and hypernyms/hyponyms from WordNet)
- [x] T051 [US3] Enhance ClaudeEnrichmentAdapter in src/services/claude_enrichment_adapter.py (generate usage notes explaining subtle differences between synonyms, identify derivative words)
- [x] T052 [US3] Implement related words merging in src/services/enrichment_service.py (combine WordNet relationships with Claude-generated usage notes, calculate relationship strength)
- [x] T053 [US3] Implement related words storage in src/services/word_service.py (create RelatedWord entries in database, handle bidirectional synonyms - deferred for background processing)
- [x] T054 [US3] Add query parameter include_related to GET /api/v1/words/{word} in src/api/v1/endpoints/words.py (default=true, boolean)
- [x] T055 [US3] Add related words filtering in src/services/word_service.py (respect include_related query parameter, filter related words based on request)
- [x] T056 [US3] Implement related words retrieval in src/repositories/word_repository.py (get_related_words async method with relationship type filtering)

**Checkpoint**: All three user stories (US1, US2, US3) should now be independently functional - learners get comprehensive info with examples and related words

---

## Phase 6: User Story 4 - Proficiency-Appropriate Content (Priority: P4)

**Goal**: Provide CEFR difficulty levels and frequency information to help learners prioritize vocabulary

**Independent Test**: Query "cat" (beginner) and "photosynthesis" (advanced) and verify difficulty levels are clearly indicated

### Implementation for User Story 4

- [x] T057 [P] [US4] Implement CEFRAdapter in src/services/cefr_adapter.py (load CEFR-J wordlist, fetch_word_data returns difficulty level A1-C2, supports_field for difficulty)
- [x] T058 [P] [US4] Implement FrequencyAdapter in src/services/frequency_adapter.py (load word frequency list, fetch_word_data returns frequency rank and band, supports_field for frequency)
- [x] T059 [US4] Integrate CEFR and frequency adapters in src/services/enrichment_service.py (call CEFR adapter for known words, Claude estimates for unknown words, add frequency data)
- [x] T060 [US4] Implement difficulty level estimation in src/services/enrichment_service.py (estimate CEFR from frequency when CEFR adapter doesn't have data, fallback strategy)
- [x] T061 [US4] Implement frequency band calculation in src/services/frequency_adapter.py (map frequency rank to bands: top-100, top-1000, top-5000, top-10000, rare, very-rare)
- [x] T062 [US4] Update LearningMetadata storage in src/services/word_service.py (save difficulty_level, cefr_level, frequency_rank, frequency_band to database)
- [x] T063 [US4] Ensure LearningMetadata is included in WordResponse in src/api/v1/endpoints/words.py (validate difficulty and frequency data is present in all responses)

**Checkpoint**: User Stories 1-4 are functional - learners can prioritize vocabulary based on difficulty and frequency

---

## Phase 7: User Story 5 - Grammatical Guidance (Priority: P5)

**Goal**: Provide complete grammatical information including irregular forms, verb conjugations, and comparative/superlative forms

**Independent Test**: Query "child" and verify irregular plural "children" is shown, or query "swim" and verify conjugations (swim-swam-swum) are provided

### Implementation for User Story 5

- [x] T064 [US5] Enhance ClaudeEnrichmentAdapter in src/services/claude_enrichment_adapter.py (improve prompt to generate complete grammatical information: plurals, verb forms, adjective forms, irregular forms)
- [x] T065 [US5] Implement grammatical form validation in src/services/enrichment_service.py (validate verb forms are consistent, plurals are correct, adjective forms follow rules)
- [x] T066 [US5] Implement irregular form detection in src/services/enrichment_service.py (detect irregular plurals, irregular verb forms, irregular comparatives/superlatives, store in irregular_forms_json)
- [x] T067 [US5] Update GrammaticalInformation storage in src/services/word_service.py (save all grammatical forms to database, handle JSONB for irregular forms)
- [x] T068 [US5] Ensure GrammaticalInformation is included in WordResponse in src/api/v1/endpoints/words.py (validate grammatical data is present and complete)
- [x] T069 [US5] Implement part-of-speech specific grammar rules in src/services/enrichment_service.py (populate verb fields for verbs, plural for nouns, comparative/superlative for adjectives)

**Checkpoint**: All five user stories (US1-US5) are fully functional - comprehensive word information with all grammatical guidance

---

## Phase 8: Edge Cases & Error Handling

**Purpose**: Handle edge cases and error scenarios identified in spec.md

- [x] T070 [P] Implement spelling suggestion algorithm in src/services/spelling_service.py (Levenshtein distance, suggest close matches within edit distance 2)
- [x] T071 Integrate spelling suggestions in src/services/word_service.py (when word not found, call spelling_service.suggest_similar_words, return top 3 suggestions)
- [x] T072 Implement 404 error response with suggestions in src/api/v1/endpoints/words.py (WordNotFoundResponse with suggestions array)
- [x] T073 Implement multiple definition handling in src/services/enrichment_service.py (clearly separate homographs with distinct definitions, order by commonality)
- [x] T074 Implement archaic/obscure word handling in src/services/enrichment_service.py (add style tags: archaic, rare, obsolete, technical based on Claude analysis)
- [x] T075 Implement proper noun detection in src/services/enrichment_service.py (detect proper nouns, add style tag, include basic context if available)
- [x] T076 Implement missing field indicator in src/services/word_service.py (calculate data_completeness.missing_fields, set completeness_percentage)
- [x] T077 Implement input validation in src/api/v1/endpoints/words.py (validate word pattern, max length 100, reject empty input with 400 error)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T078 [P] Create .gitignore with Python, virtual env, IDE, and secrets exclusions
- [x] T079 [P] Create README.md with project overview, setup instructions, and API documentation link
- [x] T080 [P] Update quickstart.md validation script (verify all examples in quickstart.md work correctly)
- [x] T081 Add comprehensive logging in src/services/word_service.py (log lookup requests, cache hits/misses, enrichment duration, errors)
- [x] T082 Add performance monitoring in src/services/enrichment_service.py (track Claude API response times, adapter call durations)
- [x] T083 Add Sentry integration in src/core/logging.py (capture exceptions, track performance, set environment tags)
- [x] T084 [P] Configure Prometheus metrics in src/api/middleware/metrics.py (request count, response time, cache hit ratio, error rate)
- [x] T085 Implement request ID tracing in src/api/middleware/request_id.py (generate unique request ID, add to logs and error responses)
- [x] T086 Add API documentation in src/main.py (configure OpenAPI metadata, title, description, version, contact info)
- [x] T087 Implement database connection pooling in src/core/database.py (configure pool_size=20, max_overflow=10, pool_pre_ping=True)
- [x] T088 Implement Redis connection pooling in src/core/cache.py (configure min_size=10, max_size=50)
- [x] T089 Create database seed script in scripts/load_common_words.py (batch load top 10,000 words, parallelize enrichment, handle errors)
- [x] T090 Create database backup script in scripts/backup_database.sh (pg_dump with compression, upload to cloud storage)
- [ ] T091 Create deployment documentation in docs/deployment.md (Railway, Fly.io, DigitalOcean deployment guides)
- [ ] T092 Add OpenAPI validation in src/api/v1/endpoints/words.py (verify responses match contracts/openapi.yaml schema)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Builds on US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Builds on US1 but independently testable
  - User Story 4 (P4): Can start after Foundational - Builds on US1 but independently testable
  - User Story 5 (P5): Can start after Foundational - Builds on US1 but independently testable
- **Edge Cases (Phase 8)**: Depends on US1 completion - Enhances core functionality
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: FOUNDATIONAL - All other stories build on basic word lookup
- **User Story 2 (P2)**: Extends US1 with richer examples - independently testable
- **User Story 3 (P3)**: Extends US1 with related words - independently testable
- **User Story 4 (P4)**: Extends US1 with difficulty/frequency - independently testable
- **User Story 5 (P5)**: Extends US1 with grammatical forms - independently testable

### Within Each User Story

- Models before services (T016-T022 before T024-T026)
- Services before endpoints (T034-T038 before T039-T043)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T009)
- All Model tasks in Foundational marked [P] can run in parallel (T016-T022, T027-T028, T031)
- Adapter implementations within a story marked [P] can run in parallel (T034-T036, T057-T058)
- Different user stories can be worked on in parallel by different team members once Foundational is complete

---

## Parallel Example: Foundational Phase

```bash
# Launch all model definitions together:
Task: "Implement Word model in src/models/word.py"
Task: "Implement Definition model in src/models/definition.py"
Task: "Implement UsageExample model in src/models/usage_example.py"
Task: "Implement PhoneticRepresentation model in src/models/phonetic.py"
Task: "Implement GrammaticalInformation model in src/models/grammar.py"
Task: "Implement LearningMetadata model in src/models/learning_metadata.py"
Task: "Implement RelatedWord model in src/models/related_word.py"

# Then launch all Pydantic schemas together:
Task: "Create Pydantic request schemas in src/api/v1/models/requests.py"
Task: "Create Pydantic response schemas in src/api/v1/models/responses.py"
```

---

## Parallel Example: User Story 1

```bash
# Launch all adapters for User Story 1 together:
Task: "Implement ClaudeEnrichmentAdapter in src/services/claude_enrichment_adapter.py"
Task: "Implement WordNetAdapter in src/services/wordnet_adapter.py"
Task: "Implement CMUPhoneticAdapter in src/services/cmu_phonetic_adapter.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T033) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T034-T043)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add Edge Cases → Test independently → Deploy/Demo
8. Add Polish → Final deployment
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done (T033 complete):
   - Developer A: User Story 1 (T034-T043)
   - Developer B: User Story 4 (T057-T063) - can start in parallel since it uses separate adapters
   - Developer C: User Story 5 (T064-T069) - enhances Claude adapter independently
3. Stories complete and integrate independently
4. User Stories 2 & 3 can proceed once US1 is complete

---

## Task Count Summary

**Total Tasks**: 92

**Phase Breakdown**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 24 tasks (CRITICAL - blocks all stories)
- Phase 3 (User Story 1 - P1): 10 tasks (MVP)
- Phase 4 (User Story 2 - P2): 6 tasks
- Phase 5 (User Story 3 - P3): 7 tasks
- Phase 6 (User Story 4 - P4): 7 tasks
- Phase 7 (User Story 5 - P5): 6 tasks
- Phase 8 (Edge Cases): 8 tasks
- Phase 9 (Polish): 15 tasks

**Parallel Opportunities**: 31 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Recommended first delivery):
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 24 tasks
- Phase 3 (User Story 1): 10 tasks
- **Total MVP**: 43 tasks

**Independent Test Criteria**:
- US1: Query "serendipity" → comprehensive word info returned
- US2: Query "ubiquitous" → multiple context-specific examples returned
- US3: Query "happy" → synonyms, antonyms, related words returned
- US4: Query "cat" and "photosynthesis" → difficulty levels clearly indicated
- US5: Query "child" and "swim" → grammatical forms shown correctly

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are optional for this feature - focus is on implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Constitution compliance: All tasks align with API-First Design, Data Quality, Response Completeness, Performance, and Extensibility principles
