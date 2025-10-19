"""Core business logic for word lookups."""
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.models.word import Word
from src.repositories.word_repository import WordRepository
from src.core.cache import CacheService
from src.services.enrichment_service import EnrichmentService
from src.services.spelling_service import SpellingService


class WordService:
    """
    Core business logic for word lookups.

    Handles the complete word lookup flow:
    1. Check cache
    2. Check database
    3. Enrich from external sources
    4. Store in database
    5. Cache result
    6. Return comprehensive data
    """

    def __init__(
        self,
        db: AsyncSession,
        cache_service: CacheService,
        enrichment_service: EnrichmentService
    ):
        """
        Initialize word service.

        Args:
            db: Database session
            cache_service: Cache service instance
            enrichment_service: Enrichment service instance
        """
        self.db = db
        self.cache_service = cache_service
        self.enrichment_service = enrichment_service
        self.word_repository = WordRepository(db)
        self.spelling_service = SpellingService()

    async def lookup_word(self, word: str) -> Dict[str, Any]:
        """
        Lookup word with comprehensive data.

        Flow: Cache → Database → Enrichment → Store → Cache → Return

        Args:
            word: Word text to lookup (should be normalized)

        Returns:
            Dictionary containing comprehensive word data

        Raises:
            Exception: If lookup fails critically
        """
        word_normalized = word.lower().strip()

        logger.info(f"Looking up word: {word_normalized}")

        # Step 1: Check cache
        cached_data = await self.cache_service.get_cached_word(word_normalized)
        if cached_data:
            logger.info(f"Cache HIT for word: {word_normalized}")
            cached_data["_cache_status"] = "HIT"
            return cached_data

        logger.debug(f"Cache MISS for word: {word_normalized}")

        # Step 2: Check database
        word_model = await self.word_repository.get_by_word_text(
            word_normalized,
            eager_load=True
        )

        if word_model:
            logger.info(f"Word found in database: {word_normalized}")
            word_data = self._model_to_dict(word_model)
            word_data["_cache_status"] = "MISS"

            # Cache the result
            frequency_rank = None
            if word_model.learning_metadata:
                frequency_rank = word_model.learning_metadata.frequency_rank

            await self.cache_service.set_cached_word(
                word_normalized,
                word_data,
                frequency_rank=frequency_rank
            )

            return word_data

        # Step 3: Check if this word previously failed lookup
        if await self.cache_service.is_failed_lookup(word_normalized):
            logger.info(f"Word '{word_normalized}' is in failed lookup cache")
            from src.api.middleware.error_handlers import WordNotFoundException
            suggestions = self.get_spelling_suggestions(word_normalized)
            raise WordNotFoundException(word_normalized, suggestions=suggestions)

        # Step 4: Enrich from external sources
        logger.info(f"Word not in database, enriching: {word_normalized}")

        try:
            enriched_data = await self.enrichment_service.enrich_word(word_normalized)
        except Exception as e:
            logger.error(f"Enrichment failed for '{word_normalized}': {e}")
            # Cache the failed lookup
            await self.cache_service.set_failed_lookup(word_normalized)
            from src.api.middleware.error_handlers import WordNotFoundException
            suggestions = self.get_spelling_suggestions(word_normalized)
            raise WordNotFoundException(word_normalized, suggestions=suggestions)

        # Step 5: Store in database
        try:
            word_model = await self.create_word_from_enrichment(enriched_data)
            await self.db.commit()
            logger.info(f"Word '{word_normalized}' stored in database")
        except Exception as e:
            logger.error(f"Failed to store word '{word_normalized}' in database: {e}")
            await self.db.rollback()
            # Still return the enriched data even if storage fails
            enriched_data["_cache_status"] = "MISS"
            return enriched_data

        # Step 6: Convert to dict and cache
        word_data = self._model_to_dict(word_model)
        word_data["_cache_status"] = "MISS"

        frequency_rank = None
        if word_model.learning_metadata:
            frequency_rank = word_model.learning_metadata.frequency_rank

        await self.cache_service.set_cached_word(
            word_normalized,
            word_data,
            frequency_rank=frequency_rank
        )

        return word_data

    async def create_word_from_enrichment(
        self,
        enriched_data: Dict[str, Any]
    ) -> Word:
        """
        Create Word model and all related entities from enriched data.

        Args:
            enriched_data: Enriched word data from EnrichmentService

        Returns:
            Created Word model instance

        Raises:
            Exception: If creation fails
        """
        word_text = enriched_data["word_text"]

        logger.debug(f"Creating word model for: {word_text}")

        # Prepare phonetic data
        phonetic_data = None
        if enriched_data.get("phonetic"):
            phonetic_data = enriched_data["phonetic"]

        # Prepare definitions data
        definitions_data = enriched_data.get("definitions", [])

        # Prepare grammatical data
        grammatical_data = None
        if enriched_data.get("grammatical_info"):
            gram_info = enriched_data["grammatical_info"]
            # Only include if there's meaningful data
            if any(v for k, v in gram_info.items() if v):
                grammatical_data = gram_info

        # Prepare learning metadata
        learning_metadata_data = None
        if enriched_data.get("learning_metadata"):
            metadata = enriched_data["learning_metadata"]
            # Only include if there's meaningful data
            if any(v for k, v in metadata.items() if v):
                learning_metadata_data = metadata

        # Create word with all relations
        word = await self.word_repository.create_word_with_all_relations(
            word_text=word_text,
            language="en",
            phonetic_data=phonetic_data,
            definitions_data=definitions_data,
            grammatical_data=grammatical_data,
            learning_metadata_data=learning_metadata_data,
            related_words_data=None  # Will be handled separately
        )

        # Update last_enriched_at timestamp
        word.last_enriched_at = datetime.utcnow()

        # Note: Related words will be created in a separate process
        # to avoid circular dependencies (need both source and target words to exist)

        logger.info(f"Created word model for: {word_text}")

        return word

    def _model_to_dict(self, word: Word) -> Dict[str, Any]:
        """
        Convert Word model to dictionary for API response.

        Args:
            word: Word model instance

        Returns:
            Dictionary representation with all relationships
        """
        # Build phonetic data
        phonetic = None
        if word.phonetic:
            phonetic = {
                "ipa_transcription": word.phonetic.ipa_transcription,
                "audio_url": word.phonetic.audio_url
            }

        # Build definitions with examples
        definitions = []
        for definition in word.definitions:
            # Build examples with context_type
            examples = []
            for ex in definition.usage_examples:
                examples.append({
                    "example_text": ex.example_text,
                    "context_type": ex.context_type
                })

            definitions.append({
                "definition_text": definition.definition_text,
                "part_of_speech": definition.part_of_speech,
                "usage_context": definition.usage_context,
                "examples": examples,
                "order_index": definition.order_index
            })

        # Build grammatical info
        grammatical_info = None
        if word.grammatical_info:
            gram = word.grammatical_info
            grammatical_info = {
                "part_of_speech": gram.part_of_speech,
                "plural_form": gram.plural_form,
                "verb_base": gram.verb_base,
                "verb_past_simple": gram.verb_past_simple,
                "verb_past_participle": gram.verb_past_participle,
                "verb_present_participle": gram.verb_present_participle,
                "verb_third_person": gram.verb_third_person,
                "adj_comparative": gram.adj_comparative,
                "adj_superlative": gram.adj_superlative,
                "irregular_forms_json": gram.irregular_forms_json
            }

        # Build learning metadata
        learning_metadata = None
        if word.learning_metadata:
            meta = word.learning_metadata
            learning_metadata = {
                "difficulty_level": meta.difficulty_level,
                "cefr_level": meta.cefr_level,
                "frequency_rank": meta.frequency_rank,
                "frequency_band": meta.frequency_band,
                "style_tags": meta.style_tags or []
            }

        # Build related words
        related_words = []
        for rel in word.related_words_source:
            if rel.target_word:
                related_words.append({
                    "word": rel.target_word.word_text,
                    "relationship_type": rel.relationship_type,
                    "usage_notes": rel.usage_notes
                })

        # Calculate data completeness
        word_dict = {
            "word_text": word.word_text,
            "language": word.language,
            "phonetic": phonetic,
            "definitions": definitions,
            "grammatical_info": grammatical_info,
            "learning_metadata": learning_metadata,
            "related_words": related_words
        }

        completeness = self.calculate_data_completeness(word_dict)
        word_dict["data_completeness"] = completeness

        return word_dict

    def calculate_data_completeness(self, word_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate data completeness metrics.

        Args:
            word_data: Word data dictionary

        Returns:
            Dictionary with missing_fields and completeness_percentage
        """
        return self.enrichment_service.calculate_completeness(word_data)

    def get_spelling_suggestions(self, word: str) -> list[str]:
        """
        Get spelling suggestions for a potentially misspelled word (T071).

        Args:
            word: The misspelled word

        Returns:
            List of suggested words (up to 3)
        """
        return self.spelling_service.suggest_similar_words(word, max_distance=2, max_suggestions=3)
