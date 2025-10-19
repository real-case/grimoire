"""Repository for Word model data access."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from loguru import logger

from src.models.word import Word
from src.models.definition import Definition
from src.models.usage_example import UsageExample
from src.models.phonetic import PhoneticRepresentation
from src.models.grammar import GrammaticalInformation
from src.models.learning_metadata import LearningMetadata
from src.models.related_word import RelatedWord


class WordRepository:
    """Repository for accessing and managing Word entities."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def get_by_word_text(
        self,
        word_text: str,
        eager_load: bool = True
    ) -> Optional[Word]:
        """
        Get word by text with optional eager loading of relationships.

        Args:
            word_text: Word text to search for (normalized)
            eager_load: Whether to eagerly load all relationships

        Returns:
            Word instance or None if not found
        """
        try:
            query = select(Word).where(Word.word_text == word_text.lower())

            if eager_load:
                # Eager load all relationships to avoid N+1 queries
                query = query.options(
                    selectinload(Word.definitions).selectinload(Definition.usage_examples),
                    selectinload(Word.phonetic),
                    selectinload(Word.grammatical_info),
                    selectinload(Word.learning_metadata),
                    selectinload(Word.related_words_source).selectinload(RelatedWord.target_word),
                )

            result = await self.db.execute(query)
            word = result.scalar_one_or_none()

            if word:
                logger.debug(f"Found word in database: {word_text}")
            else:
                logger.debug(f"Word not found in database: {word_text}")

            return word

        except Exception as e:
            logger.error(f"Error fetching word '{word_text}': {e}")
            raise

    async def get_by_id(self, word_id: UUID) -> Optional[Word]:
        """
        Get word by ID.

        Args:
            word_id: Word UUID

        Returns:
            Word instance or None if not found
        """
        try:
            query = select(Word).where(Word.id == word_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching word by ID '{word_id}': {e}")
            raise

    async def create_word_with_all_relations(
        self,
        word_text: str,
        language: str = "en",
        phonetic_data: Optional[dict] = None,
        definitions_data: Optional[list[dict]] = None,
        grammatical_data: Optional[dict] = None,
        learning_metadata_data: Optional[dict] = None,
        related_words_data: Optional[list[dict]] = None,
    ) -> Word:
        """
        Create a new word with all related entities in a single transaction.

        Args:
            word_text: Word text (will be normalized to lowercase)
            language: Language code (default: "en")
            phonetic_data: Dict with 'ipa_transcription' and optional 'audio_url'
            definitions_data: List of dicts with definition fields
            grammatical_data: Dict with grammatical information fields
            learning_metadata_data: Dict with learning metadata fields
            related_words_data: List of dicts with related word fields

        Returns:
            Created Word instance with all relationships

        Raises:
            Exception: If creation fails
        """
        try:
            # Create word entity
            word = Word(
                word_text=word_text.lower(),
                language=language
            )
            self.db.add(word)
            await self.db.flush()  # Get word ID for foreign keys

            # Create phonetic representation (1:1)
            if phonetic_data:
                phonetic = PhoneticRepresentation(
                    word_id=word.id,
                    ipa_transcription=phonetic_data.get("ipa_transcription", ""),
                    audio_url=phonetic_data.get("audio_url")
                )
                self.db.add(phonetic)

            # Create definitions (1:many)
            if definitions_data:
                for idx, def_data in enumerate(definitions_data, start=1):
                    definition = Definition(
                        word_id=word.id,
                        definition_text=def_data["definition_text"],
                        part_of_speech=def_data["part_of_speech"],
                        usage_context=def_data.get("usage_context"),
                        order_index=def_data.get("order_index", idx)
                    )
                    self.db.add(definition)
                    await self.db.flush()  # Get definition ID for usage examples

                    # Create usage examples for this definition
                    examples = def_data.get("examples", [])
                    for ex_idx, example_data in enumerate(examples, start=1):
                        if example_data:
                            # Handle both dict and string formats for backward compatibility
                            if isinstance(example_data, dict):
                                example_text = example_data.get("example_text", "")
                                context_type = example_data.get("context_type")
                            else:
                                # String format (legacy)
                                example_text = str(example_data)
                                context_type = None

                            if example_text:
                                usage_example = UsageExample(
                                    definition_id=definition.id,
                                    example_text=example_text,
                                    context_type=context_type,
                                    order_index=ex_idx
                                )
                                self.db.add(usage_example)

            # Create grammatical information (1:1)
            if grammatical_data:
                grammar = GrammaticalInformation(
                    word_id=word.id,
                    **grammatical_data
                )
                self.db.add(grammar)

            # Create learning metadata (1:1)
            if learning_metadata_data:
                metadata = LearningMetadata(
                    word_id=word.id,
                    **learning_metadata_data
                )
                self.db.add(metadata)

            # Create related words (many:many)
            if related_words_data:
                for rel_data in related_words_data:
                    # Note: target_word_id should already exist or be created separately
                    related = RelatedWord(
                        source_word_id=word.id,
                        target_word_id=rel_data["target_word_id"],
                        relationship_type=rel_data["relationship_type"],
                        usage_notes=rel_data.get("usage_notes"),
                        strength=rel_data.get("strength")
                    )
                    self.db.add(related)

            await self.db.flush()
            logger.info(f"Created word '{word_text}' with all relations")

            # Refresh to load all relationships
            await self.db.refresh(word)
            return word

        except Exception as e:
            logger.error(f"Error creating word '{word_text}': {e}")
            await self.db.rollback()
            raise

    async def update_word(
        self,
        word: Word,
        **updates
    ) -> Word:
        """
        Update word fields.

        Args:
            word: Word instance to update
            **updates: Keyword arguments of fields to update

        Returns:
            Updated word instance
        """
        try:
            for key, value in updates.items():
                if hasattr(word, key):
                    setattr(word, key, value)

            await self.db.flush()
            await self.db.refresh(word)

            logger.info(f"Updated word '{word.word_text}'")
            return word

        except Exception as e:
            logger.error(f"Error updating word '{word.word_text}': {e}")
            raise

    async def delete_word(self, word: Word) -> None:
        """
        Delete word and all related entities (cascade).

        Args:
            word: Word instance to delete
        """
        try:
            await self.db.delete(word)
            await self.db.flush()
            logger.info(f"Deleted word '{word.word_text}'")
        except Exception as e:
            logger.error(f"Error deleting word '{word.word_text}': {e}")
            raise

    async def get_related_words(
        self,
        word: Word,
        relationship_type: Optional[str] = None
    ) -> list[RelatedWord]:
        """
        Get related words for a given word with optional filtering by relationship type.

        Args:
            word: Source word instance
            relationship_type: Optional filter for relationship type
                             (e.g., 'synonym', 'antonym', 'derivative')

        Returns:
            List of RelatedWord instances
        """
        try:
            query = (
                select(RelatedWord)
                .where(RelatedWord.source_word_id == word.id)
                .options(selectinload(RelatedWord.target_word))
            )

            if relationship_type:
                query = query.where(RelatedWord.relationship_type == relationship_type)

            # Order by strength (highest first)
            query = query.order_by(RelatedWord.strength.desc().nullslast())

            result = await self.db.execute(query)
            related_words = result.scalars().all()

            logger.debug(f"Found {len(related_words)} related words for '{word.word_text}'")
            return list(related_words)

        except Exception as e:
            logger.error(f"Error fetching related words for '{word.word_text}': {e}")
            raise
