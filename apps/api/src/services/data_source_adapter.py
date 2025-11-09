"""Abstract base class for data source adapters."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class DataSourceAdapter(ABC):
    """
    Abstract base class for data source adapters.

    Data source adapters are responsible for fetching word information
    from various sources (WordNet, CMU Dictionary, CEFR databases, etc.).

    Each adapter should implement methods to fetch data and report
    which fields it can provide.
    """

    @abstractmethod
    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch word data from the data source.

        Args:
            word: Word text to look up (normalized)

        Returns:
            Dictionary containing word data fields supported by this adapter.
            Structure should align with Word model and related entities.

        Raises:
            Exception: If data fetching fails

        Example return structure:
            {
                "phonetic": {
                    "ipa_transcription": "/wɜːrd/",
                    "audio_url": None
                },
                "definitions": [
                    {
                        "definition_text": "A single unit of language...",
                        "part_of_speech": "noun",
                        "usage_context": None,
                        "examples": ["This is a word.", "Words have meaning."]
                    }
                ],
                "grammatical_info": {
                    "part_of_speech": "noun",
                    "plural_form": "words",
                    ...
                },
                "learning_metadata": {
                    "difficulty_level": "A1",
                    "cefr_level": "A1",
                    "frequency_rank": 100,
                    ...
                },
                "related_words": [
                    {
                        "word": "vocabulary",
                        "relationship_type": "related",
                        "usage_notes": "Collection of words"
                    }
                ]
            }
        """
        pass

    @abstractmethod
    def supports_field(self, field: str) -> bool:
        """
        Check if this adapter supports a specific field.

        Args:
            field: Field name to check (e.g., "phonetic", "definitions", "cefr_level")

        Returns:
            True if this adapter can provide data for the field

        Example:
            >>> adapter = WordNetAdapter()
            >>> adapter.supports_field("definitions")
            True
            >>> adapter.supports_field("cefr_level")
            False
        """
        pass

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide

        Note:
            This is a convenience method that can be overridden
            for better performance, or it will check all known fields.
        """
        known_fields = [
            "phonetic",
            "definitions",
            "grammatical_info",
            "learning_metadata",
            "related_words",
            "cefr_level",
            "frequency_rank",
        ]
        return [field for field in known_fields if self.supports_field(field)]
