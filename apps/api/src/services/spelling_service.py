"""Spelling suggestion service for word lookups."""
from typing import List

from loguru import logger


class SpellingService:
    """
    Service for generating spelling suggestions using Levenshtein distance.

    Provides suggestions for misspelled words to help users find the correct word.
    """

    def __init__(self):
        """Initialize spelling service."""
        # Load common word list for suggestions (simple implementation)
        # In production, this could load from a file or database
        self.common_words = set()
        self._load_common_words()

    def _load_common_words(self) -> None:
        """
        Load common English words for spelling suggestions.

        For now, this is a placeholder. In production, this would load
        a comprehensive word list from a file or database.
        """
        # Basic starter list - in production, load from a proper word list
        common = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
            # Common words that students might look up
            "hello", "goodbye", "please", "thank", "sorry", "yes", "no", "maybe",
            "love", "hate", "happy", "sad", "angry", "afraid", "tired", "hungry",
            "cat", "dog", "house", "car", "book", "school", "teacher", "student",
            "friend", "family", "mother", "father", "sister", "brother", "child",
            "beautiful", "ugly", "big", "small", "hot", "cold", "fast", "slow",
            "run", "walk", "eat", "drink", "sleep", "wake", "read", "write",
            "serendipity", "ubiquitous", "ephemeral", "ambiguous", "analyze",
            "receive", "believe", "achieve", "perceive", "conceive", "deceive",
        ]
        self.common_words = set(w.lower() for w in common)
        logger.info(f"Loaded {len(self.common_words)} common words for spelling suggestions")

    def suggest_similar_words(self, word: str, max_distance: int = 2, max_suggestions: int = 3) -> List[str]:
        """
        Generate spelling suggestions for a word using Levenshtein distance.

        Args:
            word: The misspelled word
            max_distance: Maximum edit distance to consider (default: 2)
            max_suggestions: Maximum number of suggestions to return (default: 3)

        Returns:
            List of suggested words sorted by edit distance (closest first)
        """
        if not word:
            return []

        word_lower = word.lower()

        # Calculate edit distance for all common words
        suggestions = []

        for candidate in self.common_words:
            distance = self._levenshtein_distance(word_lower, candidate)

            if distance <= max_distance and distance > 0:  # Don't suggest exact matches
                suggestions.append((candidate, distance))

        # Sort by distance (closest first), then alphabetically
        suggestions.sort(key=lambda x: (x[1], x[0]))

        # Return top N suggestions
        suggested_words = [word for word, dist in suggestions[:max_suggestions]]

        if suggested_words:
            logger.info(f"Found {len(suggested_words)} spelling suggestions for '{word}': {suggested_words}")
        else:
            logger.debug(f"No spelling suggestions found for '{word}' within distance {max_distance}")

        return suggested_words

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.

        The Levenshtein distance is the minimum number of single-character edits
        (insertions, deletions, or substitutions) required to change one word
        into another.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance as integer
        """
        # Create a matrix to store distances
        len1, len2 = len(s1), len(s2)

        # If one string is empty, distance is length of the other
        if len1 == 0:
            return len2
        if len2 == 0:
            return len1

        # Initialize matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Fill first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        # Calculate distances
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i - 1] == s2[j - 1]:
                    cost = 0  # Characters match, no operation needed
                else:
                    cost = 1  # Characters differ, substitution needed

                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,      # Deletion
                    matrix[i][j - 1] + 1,      # Insertion
                    matrix[i - 1][j - 1] + cost  # Substitution
                )

        # Return bottom-right cell (final distance)
        return matrix[len1][len2]

    def add_word_to_dictionary(self, word: str) -> None:
        """
        Add a word to the internal dictionary for future suggestions.

        This is useful for building up the dictionary with successfully
        queried words.

        Args:
            word: Word to add to dictionary
        """
        if word:
            self.common_words.add(word.lower())
