"""WordNet adapter for synonyms and antonyms."""
from typing import Any, Dict, List
import nltk
from nltk.corpus import wordnet as wn
from loguru import logger

from src.services.data_source_adapter import DataSourceAdapter


class WordNetAdapter(DataSourceAdapter):
    """
    Adapter for fetching synonyms and antonyms from WordNet.

    Provides:
    - Synonyms (words with similar meanings)
    - Antonyms (words with opposite meanings)
    - Related words (hypernyms, hyponyms)
    """

    def __init__(self):
        """Initialize WordNet adapter and ensure data is downloaded."""
        self._ensure_wordnet_data()

    def _ensure_wordnet_data(self):
        """Ensure WordNet data is available, download if necessary."""
        try:
            # Try to access wordnet to verify it's available
            wn.synsets('test')
            logger.debug("WordNet data is available")
        except LookupError:
            logger.info("WordNet data not found, downloading...")
            try:
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)  # Open Multilingual WordNet
                logger.info("WordNet data downloaded successfully")
            except Exception as e:
                logger.error(f"Failed to download WordNet data: {e}")
                raise

    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch synonyms and antonyms from WordNet.

        Args:
            word: Word text to look up (normalized)

        Returns:
            Dictionary containing synonyms and antonyms lists

        Raises:
            Exception: If data fetching fails
        """
        try:
            logger.debug(f"Fetching WordNet data for: {word}")

            synsets = wn.synsets(word)

            if not synsets:
                logger.debug(f"No WordNet synsets found for: {word}")
                return {
                    "synonyms": [],
                    "antonyms": [],
                    "related_words": []
                }

            # Collect synonyms (lemmas from all synsets)
            synonyms = set()
            antonyms = set()
            related_words = []
            seen_related = set()  # Track to avoid duplicates

            for synset in synsets:
                # Get synonyms (other lemmas in the same synset)
                for lemma in synset.lemmas():
                    lemma_name = lemma.name().replace('_', ' ')
                    if lemma_name.lower() != word.lower():
                        synonyms.add(lemma_name)

                    # Get antonyms
                    for antonym in lemma.antonyms():
                        antonym_name = antonym.name().replace('_', ' ')
                        antonyms.add(antonym_name)

                    # Get derivationally related forms (e.g., happy -> happiness)
                    for related_form in lemma.derivationally_related_forms():
                        related_name = related_form.name().replace('_', ' ')
                        if related_name.lower() != word.lower():
                            key = (related_name.lower(), 'derivative')
                            if key not in seen_related:
                                seen_related.add(key)
                                related_words.append({
                                    "word": related_name,
                                    "relationship_type": "derivative",
                                    "usage_notes": f"Derived from the same root as {word}"
                                })

                # Get hypernyms (more general terms)
                for hypernym in synset.hypernyms()[:2]:  # Limit to 2 per synset
                    for lemma in hypernym.lemmas():
                        hypernym_name = lemma.name().replace('_', ' ')
                        if hypernym_name.lower() != word.lower():
                            key = (hypernym_name.lower(), 'hypernym')
                            if key not in seen_related:
                                seen_related.add(key)
                                related_words.append({
                                    "word": hypernym_name,
                                    "relationship_type": "hypernym",
                                    "usage_notes": f"A more general term for {word}"
                                })

                # Get hyponyms (more specific terms) - limit to first synset only
                if synset == synsets[0]:  # Only for primary meaning
                    for hyponym in synset.hyponyms()[:3]:  # Limit to 3 hyponyms
                        for lemma in hyponym.lemmas()[:1]:  # One lemma per hyponym
                            hyponym_name = lemma.name().replace('_', ' ')
                            if hyponym_name.lower() != word.lower():
                                key = (hyponym_name.lower(), 'hyponym')
                                if key not in seen_related:
                                    seen_related.add(key)
                                    related_words.append({
                                        "word": hyponym_name,
                                        "relationship_type": "hyponym",
                                        "usage_notes": f"A more specific type of {word}"
                                    })

                # Get also-see relationships (related concepts)
                for also_see in synset.also_sees()[:2]:  # Limit to 2
                    for lemma in also_see.lemmas()[:1]:
                        related_name = lemma.name().replace('_', ' ')
                        if related_name.lower() != word.lower():
                            key = (related_name.lower(), 'related')
                            if key not in seen_related:
                                seen_related.add(key)
                                related_words.append({
                                    "word": related_name,
                                    "relationship_type": "related",
                                    "usage_notes": f"Related concept to {word}"
                                })

            result = {
                "synonyms": sorted(list(synonyms))[:10],  # Limit to top 10
                "antonyms": sorted(list(antonyms))[:10],
                "related_words": related_words[:10]  # Limit to 10 related words
            }

            logger.info(f"WordNet found {len(result['synonyms'])} synonyms, "
                       f"{len(result['antonyms'])} antonyms for '{word}'")

            return result

        except Exception as e:
            logger.error(f"WordNet error for word '{word}': {e}")
            # Return empty results instead of failing
            return {
                "synonyms": [],
                "antonyms": [],
                "related_words": []
            }

    def supports_field(self, field: str) -> bool:
        """
        Check if WordNet adapter supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if field is supported (synonyms, antonyms, related_words)
        """
        supported_fields = {
            "synonyms",
            "antonyms",
            "related_words",
        }
        return field in supported_fields

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide
        """
        return ["synonyms", "antonyms", "related_words"]
