-- Seed script for word "brave"
-- This creates a complete word entry with definitions, phonetics, and learning metadata

BEGIN;

-- Insert the word
INSERT INTO words (id, word_text, language, created_at, updated_at, last_enriched_at)
VALUES (
    'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
    'brave',
    'en',
    NOW(),
    NOW(),
    NOW()
)
ON CONFLICT (word_text) DO NOTHING;

-- Insert definitions
INSERT INTO definitions (id, word_id, definition_text, part_of_speech, order_index, created_at, updated_at)
VALUES
    (
        'aaaaaaaa-bbbb-cccc-dddd-222222222221'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'Ready to face and endure danger or pain; showing courage.',
        'adjective',
        1,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-222222222222'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'To endure or face unpleasant conditions or behavior without showing fear.',
        'verb',
        2,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-222222222223'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'A Native American warrior.',
        'noun',
        3,
        NOW(),
        NOW()
    )
ON CONFLICT DO NOTHING;

-- Insert usage examples
INSERT INTO usage_examples (id, definition_id, example_text, context_type, order_index, created_at, updated_at)
VALUES
    (
        'aaaaaaaa-bbbb-cccc-dddd-333333333331'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-222222222221'::uuid,
        'She made a brave attempt to smile.',
        'general',
        1,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-333333333332'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-222222222221'::uuid,
        'The brave soldiers fought for their country.',
        'general',
        2,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-333333333333'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-222222222222'::uuid,
        'We had to brave the cold weather.',
        'general',
        1,
        NOW(),
        NOW()
    )
ON CONFLICT DO NOTHING;

-- Insert phonetic representations
INSERT INTO phonetic_representations (id, word_id, ipa_transcription, audio_url, created_at, updated_at)
VALUES (
    'aaaaaaaa-bbbb-cccc-dddd-444444444441'::uuid,
    'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
    '/breɪv/',
    NULL,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;

-- Insert learning metadata
INSERT INTO learning_metadata (
    id, word_id, difficulty_level, frequency_rank,
    style_tags, created_at, updated_at
)
VALUES (
    'aaaaaaaa-bbbb-cccc-dddd-555555555551'::uuid,
    'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
    'B1',
    2500,
    ARRAY['general', 'positive']::varchar[],
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;

-- Insert related words (synonyms)
INSERT INTO words (id, word_text, language, created_at, updated_at)
VALUES
    ('aaaaaaaa-bbbb-cccc-dddd-111111111112'::uuid, 'courageous', 'en', NOW(), NOW()),
    ('aaaaaaaa-bbbb-cccc-dddd-111111111113'::uuid, 'fearless', 'en', NOW(), NOW()),
    ('aaaaaaaa-bbbb-cccc-dddd-111111111114'::uuid, 'bold', 'en', NOW(), NOW())
ON CONFLICT (word_text) DO NOTHING;

INSERT INTO related_words (id, source_word_id, target_word_id, relationship_type, strength, created_at, updated_at)
VALUES
    (
        'aaaaaaaa-bbbb-cccc-dddd-666666666661'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111112'::uuid,
        'synonym',
        0.9,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-666666666662'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111113'::uuid,
        'synonym',
        0.85,
        NOW(),
        NOW()
    ),
    (
        'aaaaaaaa-bbbb-cccc-dddd-666666666663'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111111'::uuid,
        'aaaaaaaa-bbbb-cccc-dddd-111111111114'::uuid,
        'synonym',
        0.8,
        NOW(),
        NOW()
    )
ON CONFLICT DO NOTHING;

COMMIT;
