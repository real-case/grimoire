"""CEFR level adapter for word difficulty classification."""
from typing import Any, Dict, Optional

from loguru import logger

from src.services.data_source_adapter import DataSourceAdapter


class CEFRAdapter(DataSourceAdapter):
    """
    Adapter for CEFR (Common European Framework of Reference) difficulty levels.

    Provides difficulty levels (A1-C2) for English words based on EFL standards.
    Uses simplified mapping of common words to CEFR levels.

    For production: This should be replaced with CEFR-J wordlist data
    from Tamagawa University (10,000+ words with research-backed levels).
    """

    def __init__(self):
        """Initialize CEFR adapter with basic word-level mappings."""
        # Simplified CEFR level mapping for common words
        # In production, load this from a data file (CEFR-J wordlist)
        self.cefr_levels = self._load_cefr_mappings()

        logger.info("CEFRAdapter initialized with basic word mappings")

    def _load_cefr_mappings(self) -> Dict[str, str]:
        """
        Load CEFR level mappings for common words.

        Returns:
            Dictionary mapping word -> CEFR level (A1, A2, B1, B2, C1, C2)

        Note:
            This is a simplified implementation with ~100 example words.
            Production should load from CEFR-J wordlist (10,000+ words).
        """
        # A1: Beginner (basic everyday words)
        a1_words = [
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "down", "out", "about", "into",
            "i", "you", "he", "she", "it", "we", "they", "my", "your", "his",
            "be", "have", "do", "say", "go", "get", "make", "know", "see", "come",
            "think", "take", "give", "use", "find", "tell", "ask", "work", "seem",
            "cat", "dog", "house", "book", "water", "food", "man", "woman", "child",
            "day", "time", "year", "way", "thing", "place", "work", "life", "hand",
            "good", "new", "first", "last", "long", "great", "little", "own", "other",
            "old", "right", "big", "high", "small", "large", "next", "early", "young",
        ]

        # A2: Elementary (common daily life words)
        a2_words = [
            "become", "leave", "feel", "try", "call", "move", "live", "believe",
            "bring", "happen", "write", "sit", "stand", "lose", "pay", "meet",
            "family", "friend", "people", "person", "city", "country", "world",
            "money", "business", "school", "job", "problem", "question", "answer",
            "important", "different", "possible", "available", "similar", "recent",
            "happy", "difficult", "easy", "hard", "simple", "common", "special",
        ]

        # B1: Intermediate (general topics, abstract concepts)
        b1_words = [
            "develop", "require", "consider", "continue", "appear", "expect",
            "suggest", "involve", "increase", "provide", "receive", "produce",
            "society", "government", "company", "system", "service", "community",
            "education", "health", "issue", "situation", "experience", "knowledge",
            "significant", "various", "particular", "specific", "general", "public",
            "individual", "social", "economic", "political", "environmental",
        ]

        # B2: Upper Intermediate (complex ideas, nuanced language)
        b2_words = [
            "demonstrate", "establish", "determine", "indicate", "analyze",
            "emphasize", "implement", "achieve", "maintain", "recognize",
            "concept", "framework", "perspective", "context", "dimension",
            "phenomenon", "hypothesis", "methodology", "principle", "criterion",
            "substantial", "comprehensive", "extensive", "adequate", "relevant",
            "consistent", "significant", "predominant", "prevalent", "inherent",
        ]

        # C1: Advanced (sophisticated academic/professional language)
        c1_words = [
            "ubiquitous", "serendipity", "juxtapose", "paradox", "conundrum",
            "ephemeral", "ambiguous", "arbitrary", "coherent", "intrinsic",
            "facilitate", "perpetuate", "undermine", "alleviate", "exacerbate",
            "phenomenon", "paradigm", "dichotomy", "nuance", "rhetoric",
            "meticulous", "prodigious", "quintessential", "rudimentary", "exemplary",
        ]

        # C2: Proficiency (highly specialized, literary, rare words)
        c2_words = [
            "photosynthesis", "extemporaneous", "obfuscate", "recalcitrant",
            "sycophant", "ephemeral", "perspicacious", "pusillanimous",
            "verisimilitude", "laconic", "insouciant", "magnanimous",
        ]

        # Build dictionary with all mappings
        cefr_dict = {}

        for word in a1_words:
            cefr_dict[word.lower()] = "A1"

        for word in a2_words:
            cefr_dict[word.lower()] = "A2"

        for word in b1_words:
            cefr_dict[word.lower()] = "B1"

        for word in b2_words:
            cefr_dict[word.lower()] = "B2"

        for word in c1_words:
            cefr_dict[word.lower()] = "C1"

        for word in c2_words:
            cefr_dict[word.lower()] = "C2"

        logger.debug(f"Loaded {len(cefr_dict)} words with CEFR levels")
        return cefr_dict

    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch CEFR difficulty level for a word.

        Args:
            word: Word text to look up (normalized to lowercase)

        Returns:
            Dictionary with difficulty level or empty if not found
            Format: {"difficulty_level": "A1|A2|B1|B2|C1|C2"}
        """
        word_lower = word.lower()

        cefr_level = self.cefr_levels.get(word_lower)

        if cefr_level:
            logger.debug(f"Found CEFR level for '{word}': {cefr_level}")
            return {
                "difficulty_level": cefr_level,
                "cefr_level": cefr_level,
                "source": "cefr_adapter"
            }
        else:
            logger.debug(f"No CEFR level found for '{word}' (will use Claude estimation)")
            return {}

    def supports_field(self, field: str) -> bool:
        """
        Check if CEFR adapter supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if field is supported (difficulty_level, cefr_level)
        """
        supported_fields = {"difficulty_level", "cefr_level", "difficulty", "cefr"}
        return field in supported_fields

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide
        """
        return ["difficulty_level", "cefr_level"]

    def get_level(self, word: str) -> Optional[str]:
        """
        Get CEFR level for a word (synchronous convenience method).

        Args:
            word: Word text to look up

        Returns:
            CEFR level string (A1-C2) or None if not found
        """
        return self.cefr_levels.get(word.lower())
