"""Word lookup endpoints."""
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from loguru import logger

from src.core.database import get_db
from src.core.cache import get_redis_dependency, CacheService
from src.services.enrichment_service import EnrichmentService
from src.services.word_service import WordService
from src.api.v1.models.responses import (
    WordResponse,
    ErrorResponse,
    WordNotFoundResponse,
    DefinitionSchema,
    PhoneticSchema,
    GrammaticalInfoSchema,
    LearningMetadataSchema,
    RelatedWordSchema,
    DataCompletenessSchema,
    VerbFormsSchema,
    AdjectiveFormsSchema,
    UsageExampleSchema
)
from src.api.middleware.error_handlers import (
    WordNotFoundException,
    InvalidWordFormatException
)
from src.api.middleware.rate_limit import limiter

# Create router
router = APIRouter()

# Word validation pattern
WORD_PATTERN = re.compile(r'^[a-z]+(-[a-z]+)*$')


def normalize_word(word: str) -> str:
    """
    Normalize word input.

    Args:
        word: Raw word input

    Returns:
        Normalized word (lowercase, stripped)

    Raises:
        InvalidWordFormatException: If word format is invalid
    """
    # Strip whitespace and convert to lowercase
    normalized = word.strip().lower()

    # Validate pattern
    if not WORD_PATTERN.match(normalized):
        raise InvalidWordFormatException(normalized)

    return normalized


def get_enrichment_service() -> EnrichmentService:
    """Dependency for getting EnrichmentService instance."""
    return EnrichmentService()


async def get_word_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_dependency),
    enrichment_service: EnrichmentService = Depends(get_enrichment_service)
) -> WordService:
    """
    Dependency for getting WordService instance.

    Args:
        db: Database session
        redis: Redis client
        enrichment_service: Enrichment service

    Returns:
        WordService instance
    """
    cache_service = CacheService(redis)
    return WordService(db, cache_service, enrichment_service)


@router.get(
    "/words/{word}",
    response_model=WordResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid word format"},
        404: {"model": WordNotFoundResponse, "description": "Word not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Look up a word",
    description="""
    Get comprehensive information about an English word including:
    - Definitions with parts of speech
    - Phonetic transcription (IPA)
    - Usage examples
    - Grammatical information
    - Related words (synonyms, antonyms)
    - Learning metadata (difficulty, frequency)

    Rate limit: 100 requests/hour for anonymous users, 10 requests/minute burst.
    """
)
@limiter.limit("100/hour")
@limiter.limit("10/minute")
async def lookup_word(
    request: Request,
    word: str,
    response: Response,
    include_examples: bool = Query(
        default=True,
        description="Include usage examples in the response"
    ),
    include_related: bool = Query(
        default=True,
        description="Include related words (synonyms, antonyms, etc.)"
    ),
    word_service: WordService = Depends(get_word_service)
):
    """
    Look up a word and return comprehensive information.

    Args:
        request: FastAPI request object (for rate limiting)
        word: Word to look up (path parameter)
        response: FastAPI response object (for headers)
        include_examples: Whether to include usage examples
        include_related: Whether to include related words
        word_service: Word service dependency

    Returns:
        WordResponse with comprehensive word information

    Raises:
        InvalidWordFormatException: If word format is invalid
        WordNotFoundException: If word is not found
    """
    # T040: Word normalization and validation
    try:
        normalized_word = normalize_word(word)
    except InvalidWordFormatException:
        raise

    logger.info(f"Word lookup request: {normalized_word}")

    # Perform lookup
    try:
        word_data = await word_service.lookup_word(normalized_word)
    except WordNotFoundException:
        # T043: Handle 404 with suggestions (placeholder for now)
        raise

    # T041: Add X-Cache-Status header
    cache_status = word_data.pop("_cache_status", "MISS")
    response.headers["X-Cache-Status"] = cache_status

    # T042: Rate limit headers are automatically added by slowapi
    # slowapi automatically adds X-RateLimit-Remaining and X-RateLimit-Reset headers

    # Filter response based on query parameters
    if not include_examples:
        # Remove examples from all definitions
        for definition in word_data.get("definitions", []):
            definition["examples"] = []
    # Note: include_examples parameter is respected here, filtering examples before response conversion

    if not include_related:
        # Remove related words
        word_data["related_words"] = []

    # Convert to response model
    return _convert_to_response(word_data)


def _convert_to_response(word_data: dict) -> WordResponse:
    """
    Convert word data dictionary to WordResponse model.

    Args:
        word_data: Word data from service

    Returns:
        WordResponse model
    """
    # Build phonetic schema
    phonetic = None
    if word_data.get("phonetic"):
        phonetic = PhoneticSchema(
            ipa_transcription=word_data["phonetic"]["ipa_transcription"],
            audio_url=word_data["phonetic"].get("audio_url")
        )

    # Build definition schemas
    definitions = []
    for def_data in word_data.get("definitions", []):
        # Build usage example schemas
        examples = []
        for ex_data in def_data.get("examples", []):
            if isinstance(ex_data, dict):
                examples.append(UsageExampleSchema(
                    example_text=ex_data.get("example_text", ""),
                    context_type=ex_data.get("context_type")
                ))
            elif isinstance(ex_data, str):
                # Backward compatibility: convert string examples
                examples.append(UsageExampleSchema(
                    example_text=ex_data,
                    context_type="casual"
                ))

        definitions.append(DefinitionSchema(
            definition_text=def_data["definition_text"],
            part_of_speech=def_data["part_of_speech"],
            usage_context=def_data.get("usage_context"),
            examples=examples
        ))

    # Build grammatical info schema
    grammatical_info = None
    if word_data.get("grammatical_info"):
        gram = word_data["grammatical_info"]

        verb_forms = None
        if any([gram.get("verb_base"), gram.get("verb_past_simple"),
                gram.get("verb_past_participle"), gram.get("verb_present_participle"),
                gram.get("verb_third_person")]):
            verb_forms = VerbFormsSchema(
                verb_base=gram.get("verb_base"),
                verb_past_simple=gram.get("verb_past_simple"),
                verb_past_participle=gram.get("verb_past_participle"),
                verb_present_participle=gram.get("verb_present_participle"),
                verb_third_person=gram.get("verb_third_person")
            )

        adjective_forms = None
        if gram.get("adj_comparative") or gram.get("adj_superlative"):
            adjective_forms = AdjectiveFormsSchema(
                adj_comparative=gram.get("adj_comparative"),
                adj_superlative=gram.get("adj_superlative")
            )

        grammatical_info = GrammaticalInfoSchema(
            part_of_speech=gram.get("part_of_speech"),
            plural_form=gram.get("plural_form"),
            verb_forms=verb_forms,
            adjective_forms=adjective_forms
        )

    # Build learning metadata schema
    learning_metadata = None
    if word_data.get("learning_metadata"):
        meta = word_data["learning_metadata"]
        learning_metadata = LearningMetadataSchema(
            difficulty_level=meta.get("difficulty_level"),
            cefr_level=meta.get("cefr_level"),
            frequency_rank=meta.get("frequency_rank"),
            frequency_band=meta.get("frequency_band"),
            style_tags=meta.get("style_tags", [])
        )

    # Build related words schemas
    related_words = []
    if word_data.get("related_words"):
        for rel in word_data["related_words"]:
            related_words.append(RelatedWordSchema(
                word=rel["word"],
                relationship_type=rel["relationship_type"],
                usage_notes=rel.get("usage_notes")
            ))

    # Build data completeness schema
    completeness_data = word_data.get("data_completeness", {
        "missing_fields": [],
        "completeness_percentage": 100
    })
    data_completeness = DataCompletenessSchema(
        missing_fields=completeness_data["missing_fields"],
        completeness_percentage=completeness_data["completeness_percentage"]
    )

    # Create response
    return WordResponse(
        word_text=word_data["word_text"],
        language=word_data["language"],
        phonetic=phonetic,
        definitions=definitions,
        grammatical_info=grammatical_info,
        learning_metadata=learning_metadata,
        related_words=related_words if related_words else None,
        data_completeness=data_completeness
    )
