"""Initial schema with all word models

Revision ID: ea8a5178aa8b
Revises: 
Create Date: 2025-10-13 09:26:39.302757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea8a5178aa8b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create words table
    op.create_table(
        'words',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('word_text', sa.String(length=100), nullable=False),
        sa.Column('language', sa.String(length=10), server_default='en', nullable=False),
        sa.Column('last_enriched_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint("word_text ~ '^[a-z]+(-[a-z]+)*$'", name='check_word_text_pattern'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_text')
    )
    op.create_index('idx_words_language', 'words', ['language'])
    op.create_index('idx_words_created_at', 'words', ['created_at'])
    op.create_index(op.f('ix_words_word_text'), 'words', ['word_text'], unique=True)

    # Create definitions table
    op.create_table(
        'definitions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('word_id', sa.UUID(), nullable=False),
        sa.Column('definition_text', sa.Text(), nullable=False),
        sa.Column('part_of_speech', sa.String(length=20), nullable=False),
        sa.Column('usage_context', sa.String(length=50), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.CheckConstraint('order_index > 0', name='check_order_index_positive'),
        sa.CheckConstraint("part_of_speech IN ('noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'determiner', 'modal')", name='check_part_of_speech_valid'),
        sa.CheckConstraint('length(definition_text) >= 10 AND length(definition_text) <= 500', name='check_definition_text_length'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_definitions_word_id', 'definitions', ['word_id'])
    op.create_index('idx_definitions_word_order', 'definitions', ['word_id', 'order_index'])

    # Create usage_examples table
    op.create_table(
        'usage_examples',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('definition_id', sa.UUID(), nullable=False),
        sa.Column('example_text', sa.Text(), nullable=False),
        sa.Column('context_type', sa.String(length=30), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.CheckConstraint('order_index > 0', name='check_order_index_positive'),
        sa.CheckConstraint('length(example_text) >= 5 AND length(example_text) <= 300', name='check_example_text_length'),
        sa.ForeignKeyConstraint(['definition_id'], ['definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usage_examples_definition_id', 'usage_examples', ['definition_id'])
    op.create_index('idx_usage_examples_definition_order', 'usage_examples', ['definition_id', 'order_index'])

    # Create phonetic_representations table
    op.create_table(
        'phonetic_representations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('word_id', sa.UUID(), nullable=False),
        sa.Column('ipa_transcription', sa.String(length=200), nullable=False),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_id')
    )
    op.create_index('idx_phonetic_word_id', 'phonetic_representations', ['word_id'], unique=True)

    # Create grammatical_information table
    op.create_table(
        'grammatical_information',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('word_id', sa.UUID(), nullable=False),
        sa.Column('part_of_speech', sa.String(length=20), nullable=True),
        sa.Column('plural_form', sa.String(length=100), nullable=True),
        sa.Column('verb_base', sa.String(length=100), nullable=True),
        sa.Column('verb_past_simple', sa.String(length=100), nullable=True),
        sa.Column('verb_past_participle', sa.String(length=100), nullable=True),
        sa.Column('verb_present_participle', sa.String(length=100), nullable=True),
        sa.Column('verb_third_person', sa.String(length=100), nullable=True),
        sa.Column('adj_comparative', sa.String(length=100), nullable=True),
        sa.Column('adj_superlative', sa.String(length=100), nullable=True),
        sa.Column('irregular_forms_json', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_id')
    )
    op.create_index('idx_grammatical_word_id', 'grammatical_information', ['word_id'], unique=True)

    # Create learning_metadata table
    op.create_table(
        'learning_metadata',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('word_id', sa.UUID(), nullable=False),
        sa.Column('difficulty_level', sa.String(length=10), nullable=True),
        sa.Column('cefr_level', sa.String(length=5), nullable=True),
        sa.Column('frequency_rank', sa.Integer(), nullable=True),
        sa.Column('frequency_band', sa.String(length=20), nullable=True),
        sa.Column('style_tags', sa.ARRAY(sa.String()), nullable=True),
        sa.CheckConstraint('frequency_rank IS NULL OR frequency_rank > 0', name='check_frequency_rank_positive'),
        sa.CheckConstraint("cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2') OR cefr_level IS NULL", name='check_cefr_level'),
        sa.CheckConstraint("difficulty_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2') OR difficulty_level IS NULL", name='check_difficulty_level'),
        sa.CheckConstraint("frequency_band IN ('top-100', 'top-1000', 'top-5000', 'top-10000', 'rare', 'very-rare') OR frequency_band IS NULL", name='check_frequency_band'),
        sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word_id')
    )
    op.create_index('idx_learning_metadata_word_id', 'learning_metadata', ['word_id'], unique=True)
    op.create_index('idx_learning_metadata_frequency_rank', 'learning_metadata', ['frequency_rank'])
    op.create_index('idx_learning_metadata_difficulty_level', 'learning_metadata', ['difficulty_level'])

    # Create related_words table
    op.create_table(
        'related_words',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('source_word_id', sa.UUID(), nullable=False),
        sa.Column('target_word_id', sa.UUID(), nullable=False),
        sa.Column('relationship_type', sa.String(length=30), nullable=False),
        sa.Column('usage_notes', sa.Text(), nullable=True),
        sa.Column('strength', sa.Float(), nullable=True),
        sa.CheckConstraint('source_word_id != target_word_id', name='check_no_self_relation'),
        sa.CheckConstraint('strength IS NULL OR (strength >= 0.0 AND strength <= 1.0)', name='check_strength_range'),
        sa.CheckConstraint("relationship_type IN ('synonym', 'antonym', 'derivative', 'compound', 'hypernym', 'hyponym', 'related')", name='check_relationship_type'),
        sa.ForeignKeyConstraint(['source_word_id'], ['words.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_word_id'], ['words.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_related_words_source', 'related_words', ['source_word_id'])
    op.create_index('idx_related_words_target', 'related_words', ['target_word_id'])
    op.create_index('idx_related_words_source_type', 'related_words', ['source_word_id', 'relationship_type'])
    op.create_index('idx_related_words_unique', 'related_words', ['source_word_id', 'target_word_id', 'relationship_type'], unique=True)


def downgrade() -> None:
    op.drop_table('related_words')
    op.drop_table('learning_metadata')
    op.drop_table('grammatical_information')
    op.drop_table('phonetic_representations')
    op.drop_table('usage_examples')
    op.drop_table('definitions')
    op.drop_table('words')
