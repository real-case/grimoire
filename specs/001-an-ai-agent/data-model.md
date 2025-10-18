# Data Model: Word Information Service for EFL Learners

**Feature**: 001-an-ai-agent
**Date**: 2025-10-13
**Phase**: 1 - Design

## Overview

This data model supports comprehensive word information storage for EFL learners, including definitions, phonetics, grammatical information, learning metadata, and semantic relationships.

## Entity Relationship Diagram

```
┌─────────────────────┐
│       Word          │
├─────────────────────┤
│ id (PK)             │
│ word_text (unique)  │──┐
│ language            │  │
│ created_at          │  │
│ updated_at          │  │
│ last_enriched_at    │  │
└─────────────────────┘  │
         │               │
         │ 1             │
         │               │
         │ *             │
┌────────▼────────────┐  │
│    Definition       │  │
├─────────────────────┤  │
│ id (PK)             │  │
│ word_id (FK)        │  │
│ definition_text     │  │
│ part_of_speech      │  │
│ usage_context       │  │
│ order_index         │  │
└─────────────────────┘  │
         │               │
         │ 1             │
         │               │
         │ *             │
┌────────▼────────────┐  │
│   UsageExample      │  │
├─────────────────────┤  │
│ id (PK)             │  │
│ definition_id (FK)  │  │
│ example_text        │  │
│ context_type        │  │
│ order_index         │  │
└─────────────────────┘  │
                         │
         ┌───────────────┘
         │ 1
         │
         │ 1
┌────────▼────────────┐
│PhoneticRepresentation│
├─────────────────────┤
│ id (PK)             │
│ word_id (FK, unique)│
│ ipa_transcription   │
│ audio_url (nullable)│
└─────────────────────┘

         ┌───────────────┐
         │ 1             │
         │               │
         │ 1             │
┌────────▼────────────┐  │
│GrammaticalInformation│ │
├─────────────────────┤  │
│ id (PK)             │  │
│ word_id (FK, unique)│  │
│ part_of_speech      │  │
│ plural_form         │  │
│ verb_base           │  │
│ verb_past_simple    │  │
│ verb_past_participle│  │
│ verb_present_part   │  │
│ verb_third_person   │  │
│ adj_comparative     │  │
│ adj_superlative     │  │
│ irregular_forms_json│  │
└─────────────────────┘  │
                         │
         ┌───────────────┘
         │ 1
         │
         │ 1
┌────────▼────────────┐
│ LearningMetadata    │
├─────────────────────┤
│ id (PK)             │
│ word_id (FK, unique)│
│ difficulty_level    │
│ cefr_level          │
│ frequency_rank      │
│ frequency_band      │
│ style_tags (array)  │
└─────────────────────┘

         ┌───────────────┐
         │ 1             │
         │               │
         │ *             │
┌────────▼────────────┐  │
│   RelatedWord       │  │
├─────────────────────┤  │
│ id (PK)             │  │
│ source_word_id (FK) │  │
│ target_word_id (FK) │  │
│ relationship_type   │  │
│ usage_notes         │  │
│ strength            │  │
└─────────────────────┘  │
                         │
                         └─────────┐
                                   │
                                   │ (self-referencing)
                                   │
                                   └──────────────┐
                                                  │
                                          (target word)
```

## Entities

### Word

Primary entity representing an English word.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `word_text` (VARCHAR(100), UNIQUE, NOT NULL, INDEXED): The word itself (lowercase, normalized)
- `language` (VARCHAR(10), NOT NULL): Language code (default: "en")
- `created_at` (TIMESTAMP, NOT NULL): When the word was first added
- `updated_at` (TIMESTAMP, NOT NULL): Last update timestamp
- `last_enriched_at` (TIMESTAMP, NULLABLE): Last time AI enrichment was performed

**Relationships**:
- Has many `Definition` (1:many)
- Has one `PhoneticRepresentation` (1:1)
- Has one `GrammaticalInformation` (1:1)
- Has one `LearningMetadata` (1:1)
- Has many `RelatedWord` as source (1:many)
- Has many `RelatedWord` as target (1:many)

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `word_text`
- INDEX on `language`
- INDEX on `created_at` (for sorting/pagination)

**Validation Rules**:
- `word_text` must be lowercase
- `word_text` must match pattern: `^[a-z]+(-[a-z]+)*$` (letters and hyphens only)
- `language` must be valid ISO 639-1 code

**Notes**:
- `word_text` is normalized to lowercase for consistent lookups
- Hyphenated words (e.g., "well-being") are supported
- Apostrophes stripped during normalization (user searches "don't" → stored as "dont")

---

### Definition

Represents a single meaning/definition of a word.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `word_id` (UUID, FK → Word.id, NOT NULL, INDEXED): Parent word
- `definition_text` (TEXT, NOT NULL): Clear, learner-appropriate definition
- `part_of_speech` (VARCHAR(20), NOT NULL): noun, verb, adjective, adverb, etc.
- `usage_context` (VARCHAR(50), NULLABLE): Context where this definition applies (e.g., "informal", "technical", "archaic")
- `order_index` (INTEGER, NOT NULL): Display order (1, 2, 3...)

**Relationships**:
- Belongs to `Word` (many:1)
- Has many `UsageExample` (1:many)
- Has many `RelatedWord` (for definition-specific synonyms/antonyms)

**Indexes**:
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `word_id`
- COMPOSITE INDEX on `(word_id, order_index)` for sorted retrieval

**Validation Rules**:
- `definition_text` must be 10-500 characters
- `part_of_speech` must be in predefined list: ["noun", "verb", "adjective", "adverb", "pronoun", "preposition", "conjunction", "interjection", "determiner", "modal"]
- `order_index` must be positive integer

**Notes**:
- Words with multiple meanings have multiple Definition entries
- `order_index` determines display order (most common meaning first)

---

### UsageExample

Example sentences demonstrating word usage.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `definition_id` (UUID, FK → Definition.id, NOT NULL, INDEXED): Parent definition
- `example_text` (TEXT, NOT NULL): Example sentence
- `context_type` (VARCHAR(30), NULLABLE): Context category (e.g., "academic", "casual", "business")
- `order_index` (INTEGER, NOT NULL): Display order

**Relationships**:
- Belongs to `Definition` (many:1)

**Indexes**:
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `definition_id`
- COMPOSITE INDEX on `(definition_id, order_index)`

**Validation Rules**:
- `example_text` must be 5-300 characters
- `example_text` must contain the target word (case-insensitive)
- 3-5 examples per definition (enforced at application level)

---

### PhoneticRepresentation

Pronunciation information for a word.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `word_id` (UUID, FK → Word.id, UNIQUE, NOT NULL): Parent word (one-to-one)
- `ipa_transcription` (VARCHAR(200), NOT NULL): IPA phonetic transcription
- `audio_url` (VARCHAR(500), NULLABLE): URL to pronunciation audio (future feature)

**Relationships**:
- Belongs to `Word` (1:1)

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `word_id`

**Validation Rules**:
- `ipa_transcription` must use valid IPA characters
- `ipa_transcription` enclosed in forward slashes: `/ˈwɜːrd/`

**Notes**:
- IPA is the international standard for phonetic transcription
- CMU Dictionary ARPABET notation will be converted to IPA during enrichment
- British and American pronunciations may differ (store primary variant)

---

### GrammaticalInformation

Grammatical metadata and word forms.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `word_id` (UUID, FK → Word.id, UNIQUE, NOT NULL): Parent word (one-to-one)
- `part_of_speech` (VARCHAR(20), NULLABLE): Primary part of speech (if unambiguous)
- `plural_form` (VARCHAR(100), NULLABLE): Plural form for nouns (e.g., "children" for "child")
- `verb_base` (VARCHAR(100), NULLABLE): Base form (infinitive)
- `verb_past_simple` (VARCHAR(100), NULLABLE): Past simple tense
- `verb_past_participle` (VARCHAR(100), NULLABLE): Past participle
- `verb_present_participle` (VARCHAR(100), NULLABLE): Present participle (-ing form)
- `verb_third_person` (VARCHAR(100), NULLABLE): 3rd person singular present
- `adj_comparative` (VARCHAR(100), NULLABLE): Comparative form (e.g., "better")
- `adj_superlative` (VARCHAR(100), NULLABLE): Superlative form (e.g., "best")
- `irregular_forms_json` (JSONB, NULLABLE): Additional irregular forms as key-value pairs

**Relationships**:
- Belongs to `Word` (1:1)

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `word_id`

**Validation Rules**:
- At least one field (besides `id` and `word_id`) must be non-null
- Verb forms: if any verb field is populated, `verb_base` must be populated
- Adjective forms: if comparative/superlative provided, must be consistent

**Notes**:
- Only populate fields relevant to the word's part of speech
- Irregular forms are especially important for learners
- Regular forms (e.g., "walk" → "walked") can be omitted if they follow standard rules

---

### LearningMetadata

Learning-specific metadata for EFL students.

**Fields**:
- `id` (UUID, PK): Unique identifier
- `word_id` (UUID, FK → Word.id, UNIQUE, NOT NULL): Parent word (one-to-one)
- `difficulty_level` (VARCHAR(10), NULLABLE): CEFR level (A1, A2, B1, B2, C1, C2)
- `cefr_level` (VARCHAR(5), NULLABLE): Specific CEFR level (same as difficulty_level, for clarity)
- `frequency_rank` (INTEGER, NULLABLE): Word rank by frequency (1 = most common)
- `frequency_band` (VARCHAR(20), NULLABLE): Band label (e.g., "top-1000", "top-5000", "rare")
- `style_tags` (TEXT[], NULLABLE): Array of style tags (e.g., ["formal", "technical"], ["informal", "slang"])

**Relationships**:
- Belongs to `Word` (1:1)

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `word_id`
- INDEX on `frequency_rank` (for sorting by difficulty)
- INDEX on `difficulty_level` (for filtering)

**Validation Rules**:
- `difficulty_level` must be one of: A1, A2, B1, B2, C1, C2, or null
- `frequency_rank` must be positive integer
- `frequency_band` must be one of: "top-100", "top-1000", "top-5000", "top-10000", "rare", "very-rare"
- `style_tags` values must be from predefined list: ["formal", "informal", "technical", "archaic", "slang", "literary", "regional", "offensive"]

**Notes**:
- CEFR (Common European Framework of Reference) is the standard for EFL proficiency
- Frequency data helps learners prioritize essential vocabulary
- Style tags help learners use words in appropriate contexts

---

### RelatedWord

Semantic relationships between words (synonyms, antonyms, derivatives).

**Fields**:
- `id` (UUID, PK): Unique identifier
- `source_word_id` (UUID, FK → Word.id, NOT NULL, INDEXED): Source word
- `target_word_id` (UUID, FK → Word.id, NOT NULL, INDEXED): Related word
- `relationship_type` (VARCHAR(30), NOT NULL): Type of relationship
- `usage_notes` (TEXT, NULLABLE): Explanation of subtle differences in usage
- `strength` (FLOAT, NULLABLE): Relationship strength (0.0-1.0, for synonyms)

**Relationships**:
- Belongs to `Word` as source (many:1)
- Belongs to `Word` as target (many:1)

**Indexes**:
- PRIMARY KEY on `id`
- FOREIGN KEY INDEX on `source_word_id`
- FOREIGN KEY INDEX on `target_word_id`
- COMPOSITE INDEX on `(source_word_id, relationship_type)` for efficient queries
- UNIQUE INDEX on `(source_word_id, target_word_id, relationship_type)` to prevent duplicates

**Validation Rules**:
- `source_word_id` ≠ `target_word_id` (word cannot relate to itself)
- `relationship_type` must be one of: "synonym", "antonym", "derivative", "compound", "hypernym", "hyponym", "related"
- `strength` must be between 0.0 and 1.0 (if provided)

**Relationship Types**:
- **synonym**: Words with similar meanings (e.g., "happy" ↔ "joyful")
- **antonym**: Words with opposite meanings (e.g., "hot" ↔ "cold")
- **derivative**: Morphologically related (e.g., "happy" → "happiness")
- **compound**: Compound word relationship (e.g., "book" → "bookshelf")
- **hypernym**: More general term (e.g., "dog" → "animal")
- **hyponym**: More specific term (e.g., "animal" → "dog")
- **related**: General semantic relation

**Notes**:
- Relationships are directional (source → target)
- Synonym relationships should be bidirectional (created in both directions)
- `usage_notes` help learners understand when to use one synonym over another

---

## Database Schema (PostgreSQL)

### Table: words

```sql
CREATE TABLE words (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word_text VARCHAR(100) NOT NULL UNIQUE,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_enriched_at TIMESTAMP
);

CREATE INDEX idx_words_word_text ON words(word_text);
CREATE INDEX idx_words_language ON words(language);
CREATE INDEX idx_words_created_at ON words(created_at);
```

### Table: definitions

```sql
CREATE TABLE definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word_id UUID NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    definition_text TEXT NOT NULL,
    part_of_speech VARCHAR(20) NOT NULL,
    usage_context VARCHAR(50),
    order_index INTEGER NOT NULL,
    CONSTRAINT check_order_index_positive CHECK (order_index > 0)
);

CREATE INDEX idx_definitions_word_id ON definitions(word_id);
CREATE INDEX idx_definitions_word_order ON definitions(word_id, order_index);
```

### Table: usage_examples

```sql
CREATE TABLE usage_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    definition_id UUID NOT NULL REFERENCES definitions(id) ON DELETE CASCADE,
    example_text TEXT NOT NULL,
    context_type VARCHAR(30),
    order_index INTEGER NOT NULL,
    CONSTRAINT check_order_index_positive CHECK (order_index > 0)
);

CREATE INDEX idx_usage_examples_definition_id ON usage_examples(definition_id);
CREATE INDEX idx_usage_examples_definition_order ON usage_examples(definition_id, order_index);
```

### Table: phonetic_representations

```sql
CREATE TABLE phonetic_representations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word_id UUID NOT NULL UNIQUE REFERENCES words(id) ON DELETE CASCADE,
    ipa_transcription VARCHAR(200) NOT NULL,
    audio_url VARCHAR(500)
);

CREATE UNIQUE INDEX idx_phonetic_word_id ON phonetic_representations(word_id);
```

### Table: grammatical_information

```sql
CREATE TABLE grammatical_information (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word_id UUID NOT NULL UNIQUE REFERENCES words(id) ON DELETE CASCADE,
    part_of_speech VARCHAR(20),
    plural_form VARCHAR(100),
    verb_base VARCHAR(100),
    verb_past_simple VARCHAR(100),
    verb_past_participle VARCHAR(100),
    verb_present_participle VARCHAR(100),
    verb_third_person VARCHAR(100),
    adj_comparative VARCHAR(100),
    adj_superlative VARCHAR(100),
    irregular_forms_json JSONB
);

CREATE UNIQUE INDEX idx_grammatical_word_id ON grammatical_information(word_id);
```

### Table: learning_metadata

```sql
CREATE TABLE learning_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word_id UUID NOT NULL UNIQUE REFERENCES words(id) ON DELETE CASCADE,
    difficulty_level VARCHAR(10),
    cefr_level VARCHAR(5),
    frequency_rank INTEGER,
    frequency_band VARCHAR(20),
    style_tags TEXT[],
    CONSTRAINT check_frequency_rank_positive CHECK (frequency_rank IS NULL OR frequency_rank > 0),
    CONSTRAINT check_cefr_level CHECK (cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2') OR cefr_level IS NULL)
);

CREATE UNIQUE INDEX idx_learning_metadata_word_id ON learning_metadata(word_id);
CREATE INDEX idx_learning_metadata_frequency_rank ON learning_metadata(frequency_rank);
CREATE INDEX idx_learning_metadata_difficulty_level ON learning_metadata(difficulty_level);
```

### Table: related_words

```sql
CREATE TABLE related_words (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_word_id UUID NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    target_word_id UUID NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    relationship_type VARCHAR(30) NOT NULL,
    usage_notes TEXT,
    strength FLOAT,
    CONSTRAINT check_no_self_relation CHECK (source_word_id != target_word_id),
    CONSTRAINT check_strength_range CHECK (strength IS NULL OR (strength >= 0.0 AND strength <= 1.0)),
    CONSTRAINT check_relationship_type CHECK (relationship_type IN ('synonym', 'antonym', 'derivative', 'compound', 'hypernym', 'hyponym', 'related'))
);

CREATE INDEX idx_related_words_source ON related_words(source_word_id);
CREATE INDEX idx_related_words_target ON related_words(target_word_id);
CREATE INDEX idx_related_words_source_type ON related_words(source_word_id, relationship_type);
CREATE UNIQUE INDEX idx_related_words_unique ON related_words(source_word_id, target_word_id, relationship_type);
```

---

## Data Migration Strategy

### Initial Data Load

1. **Common Vocabulary (Top 10,000 words)**:
   - Load word list from frequency corpus
   - Batch enrich via Claude API (parallelized)
   - Supplement with WordNet, CMU Dict, CEFR-J data
   - Estimated time: 2-4 hours
   - Estimated cost: $100-500 (one-time)

2. **On-Demand Enrichment**:
   - New words enriched when first queried
   - Cached indefinitely after enrichment
   - Background job for periodic re-enrichment (quarterly)

### Schema Evolution

- Use Alembic for all schema changes
- Backward compatible migrations preferred
- Non-nullable fields added as nullable first, then backfilled, then made non-nullable

---

## Performance Considerations

### Query Optimization

**Most Common Query** (word lookup):
```sql
SELECT w.*,
       json_agg(DISTINCT d.*) as definitions,
       json_agg(DISTINCT ue.*) as usage_examples,
       pr.*,
       gi.*,
       lm.*,
       json_agg(DISTINCT rw.*) as related_words
FROM words w
LEFT JOIN definitions d ON d.word_id = w.id
LEFT JOIN usage_examples ue ON ue.definition_id = d.id
LEFT JOIN phonetic_representations pr ON pr.word_id = w.id
LEFT JOIN grammatical_information gi ON gi.word_id = w.id
LEFT JOIN learning_metadata lm ON lm.word_id = w.id
LEFT JOIN related_words rw ON rw.source_word_id = w.id
WHERE w.word_text = ?
GROUP BY w.id, pr.id, gi.id, lm.id;
```

**Optimization Strategy**:
- Use SQLAlchemy `selectinload()` to avoid N+1 queries
- Cache full word response in Redis (serialized JSON)
- Index on `word_text` ensures O(log n) lookup

### Estimated Storage

- **Per word entry**: ~5-10 KB (with all relationships)
- **10,000 words**: ~50-100 MB
- **100,000 words**: ~500 MB - 1 GB
- PostgreSQL can easily handle millions of words

---

## Compliance with Constitution

### Principle II: Data Quality & Accuracy ✅
- IPA standards enforced in `phonetic_representations`
- Data sources documented and traceable
- Validation constraints ensure completeness

### Principle III: Response Completeness ✅
- All required fields represented in entities
- Nullable fields allow explicit null responses
- Relationships ensure comprehensive data retrieval

### Principle V: Extensibility ✅
- Schema supports adding new fields via migrations
- JSONB `irregular_forms_json` allows flexible grammar data
- Relationship pattern extensible to new semantic relations

**Data model ready for API contract generation** ✅
