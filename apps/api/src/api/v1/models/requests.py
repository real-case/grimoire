"""Pydantic request schemas for API endpoints."""
from typing import Optional

from pydantic import BaseModel, Field


class WordLookupRequest(BaseModel):
    """
    Request schema for word lookup with optional query parameters.

    Attributes:
        include_examples: Whether to include usage examples in response
        include_related: Whether to include related words (synonyms, antonyms, etc.)
    """

    include_examples: bool = Field(
        default=True,
        description="Include usage examples in the response"
    )

    include_related: bool = Field(
        default=True,
        description="Include related words (synonyms, antonyms, derivatives) in the response"
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "include_examples": True,
                "include_related": True
            }
        }
