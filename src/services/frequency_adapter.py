"""Word frequency adapter for learning prioritization."""
from typing import Any, Dict, Optional

from loguru import logger

from src.services.data_source_adapter import DataSourceAdapter


class FrequencyAdapter(DataSourceAdapter):
    """
    Adapter for word frequency rankings to help learners prioritize vocabulary.

    Provides frequency ranks and bands based on corpus analysis.
    Uses simplified mapping of common words to frequency ranks.

    For production: This should use data from Google Books Ngram or
    COCA (Corpus of Contemporary American English) with 50,000+ words.
    """

    def __init__(self):
        """Initialize frequency adapter with basic frequency rankings."""
        # Simplified frequency rankings for common words
        # In production, load this from a frequency corpus data file
        self.frequency_rankings = self._load_frequency_rankings()

        logger.info("FrequencyAdapter initialized with basic frequency rankings")

    def _load_frequency_rankings(self) -> Dict[str, int]:
        """
        Load word frequency rankings.

        Returns:
            Dictionary mapping word -> frequency rank (1 = most common)

        Note:
            This is a simplified implementation with ~200 example words.
            Production should load from frequency corpus (50,000+ words).
            Based on common English word frequency lists.
        """
        # Top 100 words (function words, pronouns, common verbs)
        top_100 = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
        ]

        # Top 101-1000 words
        top_1000 = [
            "find", "here", "thing", "tell", "own", "man", "house", "world", "still",
            "between", "last", "need", "hand", "place", "case", "too", "follow", "same",
            "great", "where", "help", "through", "much", "before", "line", "right", "mean",
            "old", "any", "same", "tell", "boy", "different", "move", "since", "need",
            "try", "large", "call", "woman", "child", "there", "long", "leave", "put",
            "believe", "become", "seem", "turn", "problem", "feel", "try", "fact", "water",
            "eye", "play", "run", "small", "build", "ask", "late", "part", "young",
            "important", "use", "during", "without", "place", "example", "book", "end",
            "lot", "money", "business", "company", "system", "program", "question", "school",
            "group", "area", "high", "such", "provide", "service", "show", "around",
            "family", "friend", "city", "country", "life", "real", "state", "point",
        ]

        # Top 1001-5000 words
        top_5000 = [
            "develop", "appear", "study", "continue", "learn", "lead", "understand",
            "include", "involve", "require", "suggest", "consider", "expect", "issue",
            "public", "social", "change", "interest", "possible", "certain", "experience",
            "national", "government", "increase", "provide", "whether", "effect", "several",
            "community", "society", "education", "health", "particular", "individual",
            "difficult", "available", "economic", "support", "growth", "research",
            "achieve", "maintain", "receive", "produce", "create", "design", "report",
            "process", "data", "information", "knowledge", "policy", "practice", "method",
        ]

        # Top 5001-10000 words
        top_10000 = [
            "demonstrate", "establish", "determine", "analyze", "implement", "framework",
            "context", "perspective", "concept", "principle", "methodology", "hypothesis",
            "phenomenon", "criterion", "comprehensive", "significant", "substantial",
            "relevant", "adequate", "consistent", "predominant", "prevalent", "inherent",
            "facilitate", "emphasize", "recognize", "dimension", "environmental", "political",
        ]

        # 10001-25000 (uncommon but not rare)
        uncommon = [
            "ubiquitous", "serendipity", "paradox", "conundrum", "ephemeral",
            "ambiguous", "arbitrary", "coherent", "intrinsic", "juxtapose",
            "alleviate", "exacerbate", "perpetuate", "undermine", "facilitate",
            "dichotomy", "paradigm", "rhetoric", "nuance", "meticulous",
        ]

        # 25000+ (rare/specialized words)
        rare = [
            "photosynthesis", "extemporaneous", "obfuscate", "recalcitrant",
            "sycophant", "perspicacious", "pusillanimous", "verisimilitude",
            "laconic", "insouciant", "magnanimous", "prodigious", "quintessential",
        ]

        # Build frequency dictionary
        freq_dict = {}

        # Assign ranks to each tier
        rank = 1
        for word in top_100:
            freq_dict[word.lower()] = rank
            rank += 1

        for word in top_1000:
            if word.lower() not in freq_dict:  # Avoid duplicates
                freq_dict[word.lower()] = rank
                rank += 1

        for word in top_5000:
            if word.lower() not in freq_dict:
                freq_dict[word.lower()] = rank
                rank += 1

        for word in top_10000:
            if word.lower() not in freq_dict:
                freq_dict[word.lower()] = rank
                rank += 1

        # Assign estimated ranks for uncommon/rare words
        for word in uncommon:
            if word.lower() not in freq_dict:
                freq_dict[word.lower()] = 15000  # Approximate rank

        for word in rare:
            if word.lower() not in freq_dict:
                freq_dict[word.lower()] = 30000  # Approximate rank

        logger.debug(f"Loaded {len(freq_dict)} words with frequency rankings")
        return freq_dict

    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch frequency rank and band for a word.

        Args:
            word: Word text to look up (normalized to lowercase)

        Returns:
            Dictionary with frequency rank and band, or empty if not found
            Format: {
                "frequency_rank": 123,
                "frequency_band": "top-1000"
            }
        """
        word_lower = word.lower()

        frequency_rank = self.frequency_rankings.get(word_lower)

        if frequency_rank:
            frequency_band = self._calculate_frequency_band(frequency_rank)

            logger.debug(
                f"Found frequency for '{word}': rank {frequency_rank}, band {frequency_band}"
            )

            return {
                "frequency_rank": frequency_rank,
                "frequency_band": frequency_band,
                "source": "frequency_adapter"
            }
        else:
            logger.debug(f"No frequency data found for '{word}'")
            return {}

    def _calculate_frequency_band(self, rank: int) -> str:
        """
        Calculate frequency band from rank.

        Args:
            rank: Frequency rank (1 = most common)

        Returns:
            Band label: "top-100", "top-1000", "top-5000", "top-10000", "rare", "very-rare"
        """
        if rank <= 100:
            return "top-100"
        elif rank <= 1000:
            return "top-1000"
        elif rank <= 5000:
            return "top-5000"
        elif rank <= 10000:
            return "top-10000"
        elif rank <= 25000:
            return "rare"
        else:
            return "very-rare"

    def supports_field(self, field: str) -> bool:
        """
        Check if frequency adapter supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if field is supported (frequency_rank, frequency_band, frequency)
        """
        supported_fields = {
            "frequency_rank", "frequency_band", "frequency", "rank", "band"
        }
        return field in supported_fields

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide
        """
        return ["frequency_rank", "frequency_band"]

    def get_rank(self, word: str) -> Optional[int]:
        """
        Get frequency rank for a word (synchronous convenience method).

        Args:
            word: Word text to look up

        Returns:
            Frequency rank or None if not found
        """
        return self.frequency_rankings.get(word.lower())

    def get_band(self, word: str) -> Optional[str]:
        """
        Get frequency band for a word (synchronous convenience method).

        Args:
            word: Word text to look up

        Returns:
            Frequency band string or None if not found
        """
        rank = self.get_rank(word)
        if rank:
            return self._calculate_frequency_band(rank)
        return None
