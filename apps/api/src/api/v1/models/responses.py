"""Pydantic response schemas for API endpoints."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UsageExampleSchema(BaseModel):
    """Usage example for a definition."""

    example_text: str = Field(
        description="Example sentence demonstrating word usage"
    )
    context_type: Optional[str] = Field(
        default=None,
        description="Context category (e.g., 'academic', 'casual', 'business')"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True


class DefinitionSchema(BaseModel):
    """Definition schema with part of speech and examples."""

    part_of_speech: str = Field(
        description="Part of speech (noun, verb, adjective, etc.)"
    )
    definition: str = Field(
        description="Clear, learner-appropriate definition",
        alias="definition_text"
    )
    usage_context: Optional[str] = Field(
        default=None,
        description="Context where this definition applies"
    )
    examples: List[UsageExampleSchema] = Field(
        default_factory=list,
        description="Usage examples (3-5 sentences) with context types"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class PhoneticSchema(BaseModel):
    """Phonetic representation schema."""

    ipa: str = Field(
        description="IPA phonetic transcription",
        alias="ipa_transcription"
    )
    audio_url: Optional[str] = Field(
        default=None,
        description="URL to pronunciation audio"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class VerbFormsSchema(BaseModel):
    """Verb conjugation forms."""

    base: Optional[str] = Field(default=None, description="Base form", alias="verb_base")
    past_simple: Optional[str] = Field(default=None, description="Past simple tense", alias="verb_past_simple")
    past_participle: Optional[str] = Field(default=None, description="Past participle", alias="verb_past_participle")
    present_participle: Optional[str] = Field(default=None, description="Present participle", alias="verb_present_participle")
    third_person: Optional[str] = Field(default=None, description="3rd person singular", alias="verb_third_person")

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class AdjectiveFormsSchema(BaseModel):
    """Adjective comparative/superlative forms."""

    comparative: Optional[str] = Field(default=None, description="Comparative form", alias="adj_comparative")
    superlative: Optional[str] = Field(default=None, description="Superlative form", alias="adj_superlative")

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class GrammaticalInfoSchema(BaseModel):
    """Grammatical information schema."""

    part_of_speech: Optional[str] = Field(
        default=None,
        description="Primary part of speech"
    )
    plural_form: Optional[str] = Field(
        default=None,
        description="Plural form for nouns"
    )
    verb_forms: Optional[VerbFormsSchema] = Field(
        default=None,
        description="Verb conjugations"
    )
    adjective_forms: Optional[AdjectiveFormsSchema] = Field(
        default=None,
        description="Adjective forms"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True


class LearningMetadataSchema(BaseModel):
    """Learning metadata schema for EFL students."""

    difficulty_level: Optional[str] = Field(
        default=None,
        description="CEFR difficulty level (A1, A2, B1, B2, C1, C2)"
    )
    cefr_level: Optional[str] = Field(
        default=None,
        description="CEFR level"
    )
    frequency_rank: Optional[int] = Field(
        default=None,
        description="Word frequency rank (1 = most common)"
    )
    frequency_band: Optional[str] = Field(
        default=None,
        description="Frequency band label"
    )
    style_tags: List[str] = Field(
        default_factory=list,
        description="Stylistic usage tags"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True


class RelatedWordSchema(BaseModel):
    """Related word schema."""

    word: str = Field(
        description="Related word text"
    )
    relationship: str = Field(
        description="Type of relationship",
        alias="relationship_type"
    )
    usage_notes: Optional[str] = Field(
        default=None,
        description="Explanation of usage differences"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class DataCompletenessSchema(BaseModel):
    """Data completeness information."""

    missing_fields: List[str] = Field(
        default_factory=list,
        description="List of fields that are unavailable"
    )
    completeness_percentage: int = Field(
        description="Percentage of expected fields that are populated",
        ge=0,
        le=100
    )

    class Config:
        """Pydantic config."""
        from_attributes = True


class WordResponse(BaseModel):
    """Complete word information response."""

    word: str = Field(
        description="The queried word (normalized to lowercase)",
        alias="word_text"
    )
    language: str = Field(
        description="Language code (ISO 639-1)"
    )
    phonetic: Optional[PhoneticSchema] = Field(
        default=None,
        description="Phonetic representation"
    )
    definitions: List[DefinitionSchema] = Field(
        description="List of definitions"
    )
    grammatical_info: Optional[GrammaticalInfoSchema] = Field(
        default=None,
        description="Grammatical information"
    )
    learning_metadata: Optional[LearningMetadataSchema] = Field(
        default=None,
        description="Learning metadata"
    )
    related_words: Optional[List[RelatedWordSchema]] = Field(
        default=None,
        description="Related words (synonyms, antonyms, derivatives)"
    )
    data_completeness: DataCompletenessSchema = Field(
        description="Data completeness information"
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Standard error response."""

    error_code: str = Field(
        description="Machine-readable error code"
    )
    message: str = Field(
        description="Human-readable error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_WORD_FORMAT",
                "message": "Word must contain only letters and hyphens",
                "details": {
                    "field": "word",
                    "pattern": "^[a-zA-Z]+(-[a-zA-Z]+)*$"
                }
            }
        }


class WordNotFoundResponse(ErrorResponse):
    """Word not found error response with suggestions."""

    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Spelling suggestions for misspelled words"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error_code": "WORD_NOT_FOUND",
                "message": "The word 'xyz' was not found in our database",
                "suggestions": [
                    "Did you mean: 'yes'?",
                    "Did you mean: 'zoo'?"
                ]
            }
        }
