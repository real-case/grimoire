"""Enrichment service orchestrating data from multiple sources."""
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger

from src.services.claude_enrichment_adapter import ClaudeEnrichmentAdapter
from src.services.wordnet_adapter import WordNetAdapter
from src.services.cmu_phonetic_adapter import CMUPhoneticAdapter
from src.services.cefr_adapter import CEFRAdapter
from src.services.frequency_adapter import FrequencyAdapter


class EnrichmentService:
    """
    Service for enriching word data by orchestrating multiple data source adapters.

    Combines data from:
    - Claude AI (primary source for definitions, examples, grammar)
    - WordNet (supplementary synonyms and antonyms)
    - CMU Dictionary (supplementary phonetics)
    """

    def __init__(self):
        """Initialize enrichment service with all adapters."""
        self.claude_adapter = ClaudeEnrichmentAdapter()
        self.wordnet_adapter = WordNetAdapter()
        self.cmu_adapter = CMUPhoneticAdapter()
        self.cefr_adapter = CEFRAdapter()
        self.frequency_adapter = FrequencyAdapter()

        logger.info("EnrichmentService initialized with all adapters")

    async def enrich_word(self, word: str) -> Dict[str, Any]:
        """
        Enrich word data by orchestrating calls to all adapters.

        Claude is the primary authoritative source. WordNet and CMU provide
        supplementary data that enhances or validates Claude's output.

        Args:
            word: Word text to enrich (normalized)

        Returns:
            Comprehensive word data dictionary with all available information

        Raises:
            Exception: If enrichment fails critically (e.g., Claude API error)
        """
        logger.info(f"Starting enrichment for word: {word}")

        try:
            # Fetch data from Claude (primary source - REQUIRED)
            claude_data = await self.claude_adapter.fetch_word_data(word)

            # Fetch supplementary data from WordNet (synonyms, antonyms)
            wordnet_data = await self.wordnet_adapter.fetch_word_data(word)

            # Fetch supplementary phonetics from CMU
            cmu_data = await self.cmu_adapter.fetch_word_data(word)

            # Fetch CEFR difficulty level
            cefr_data = await self.cefr_adapter.fetch_word_data(word)

            # Fetch frequency data
            frequency_data = await self.frequency_adapter.fetch_word_data(word)

            # Merge all data sources
            enriched_data = self._merge_data_sources(
                word=word,
                claude_data=claude_data,
                wordnet_data=wordnet_data,
                cmu_data=cmu_data,
                cefr_data=cefr_data,
                frequency_data=frequency_data
            )

            # Validate completeness
            self._validate_enriched_data(enriched_data)

            logger.info(f"Successfully enriched word: {word}")
            logger.debug(f"Enriched data for '{word}': {enriched_data}")

            return enriched_data

        except Exception as e:
            logger.error(f"Enrichment failed for word '{word}': {e}")
            raise

    def _merge_data_sources(
        self,
        word: str,
        claude_data: Dict[str, Any],
        wordnet_data: Dict[str, Any],
        cmu_data: Dict[str, Any],
        cefr_data: Dict[str, Any],
        frequency_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge data from all sources with Claude as authoritative source.

        Args:
            word: Word being enriched
            claude_data: Data from Claude AI
            wordnet_data: Data from WordNet
            cmu_data: Data from CMU Dictionary
            cefr_data: Data from CEFR adapter
            frequency_data: Data from frequency adapter

        Returns:
            Merged word data dictionary
        """
        logger.debug(f"Merging data sources for word: {word}")

        # Start with Claude data as base (authoritative)
        merged = {
            "word_text": word,
            "language": "en",
            "last_enriched_at": datetime.utcnow()
        }

        # Phonetics: Prefer Claude, fallback to CMU
        if claude_data.get("phonetic") and claude_data["phonetic"].get("ipa_transcription"):
            merged["phonetic"] = claude_data["phonetic"]
        elif cmu_data.get("phonetic") and cmu_data["phonetic"].get("ipa_transcription"):
            merged["phonetic"] = cmu_data["phonetic"]
            logger.info(f"Using CMU phonetics for '{word}' (Claude didn't provide)")
        else:
            merged["phonetic"] = None
            logger.warning(f"No phonetic transcription available for '{word}'")

        # Definitions: From Claude only (most reliable for learner-appropriate content)
        merged["definitions"] = claude_data.get("definitions", [])

        # Grammatical info: From Claude with validation
        grammatical_info = claude_data.get("grammatical_info", {})
        merged["grammatical_info"] = self._validate_grammatical_forms(word, grammatical_info)

        # Related words: Merge WordNet synonyms/antonyms with Claude data
        merged["related_words"] = self._merge_related_words(
            claude_data.get("related_words", []),
            wordnet_data
        )

        # Learning metadata: Merge CEFR and frequency data
        merged["learning_metadata"] = self._merge_learning_metadata(
            word=word,
            cefr_data=cefr_data,
            frequency_data=frequency_data,
            claude_data=claude_data
        )

        return merged

    def _merge_related_words(
        self,
        claude_related: List[Dict[str, Any]],
        wordnet_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Merge related words from Claude and WordNet with strength calculation.

        Args:
            claude_related: Related words from Claude (with usage notes)
            wordnet_data: Data from WordNet containing synonyms/antonyms/related

        Returns:
            Merged list of related words with strength scores
        """
        related_words = []
        word_data = {}  # Track word data by (word, relationship_type) key

        # Process Claude's related words first (they have usage notes - higher priority)
        for rel in claude_related:
            word = rel.get("word", "").lower()
            rel_type = rel.get("relationship_type", "related")
            key = (word, rel_type)

            if word and rel_type:
                word_data[key] = {
                    "word": rel.get("word"),  # Original case
                    "relationship_type": rel_type,
                    "usage_notes": rel.get("usage_notes"),
                    "strength": self._calculate_relationship_strength(
                        rel_type,
                        has_usage_notes=bool(rel.get("usage_notes")),
                        source="claude"
                    )
                }

        # Add WordNet synonyms
        for synonym in wordnet_data.get("synonyms", []):
            key = (synonym.lower(), "synonym")
            if key not in word_data:  # Don't override Claude data
                word_data[key] = {
                    "word": synonym,
                    "relationship_type": "synonym",
                    "usage_notes": None,
                    "strength": self._calculate_relationship_strength(
                        "synonym",
                        has_usage_notes=False,
                        source="wordnet"
                    )
                }

        # Add WordNet antonyms
        for antonym in wordnet_data.get("antonyms", []):
            key = (antonym.lower(), "antonym")
            if key not in word_data:
                word_data[key] = {
                    "word": antonym,
                    "relationship_type": "antonym",
                    "usage_notes": None,
                    "strength": self._calculate_relationship_strength(
                        "antonym",
                        has_usage_notes=False,
                        source="wordnet"
                    )
                }

        # Add WordNet related words (hypernyms, hyponyms, derivatives, etc.)
        for related in wordnet_data.get("related_words", []):
            word = related.get("word", "").lower()
            rel_type = related.get("relationship_type", "related")
            key = (word, rel_type)

            if key not in word_data:
                word_data[key] = {
                    "word": related.get("word"),
                    "relationship_type": rel_type,
                    "usage_notes": related.get("usage_notes"),
                    "strength": self._calculate_relationship_strength(
                        rel_type,
                        has_usage_notes=bool(related.get("usage_notes")),
                        source="wordnet"
                    )
                }

        # Convert to list and sort by strength (highest first)
        unique_related = sorted(
            word_data.values(),
            key=lambda x: x.get("strength", 0.0),
            reverse=True
        )

        # Limit to top 15 related words
        unique_related = unique_related[:15]

        logger.debug(f"Merged {len(unique_related)} unique related words with strength scores")

        return unique_related

    def _calculate_relationship_strength(
        self,
        relationship_type: str,
        has_usage_notes: bool,
        source: str
    ) -> float:
        """
        Calculate strength score for a related word relationship.

        Args:
            relationship_type: Type of relationship
            has_usage_notes: Whether usage notes are provided
            source: Data source (claude or wordnet)

        Returns:
            Strength score between 0.0 and 1.0
        """
        # Base strength by relationship type
        base_strength = {
            "synonym": 0.9,
            "antonym": 0.8,
            "derivative": 0.7,
            "hypernym": 0.6,
            "hyponym": 0.6,
            "related": 0.5,
        }.get(relationship_type, 0.5)

        # Boost for having usage notes (very helpful for learners)
        if has_usage_notes:
            base_strength += 0.1

        # Slight boost for Claude source (more learner-appropriate)
        if source == "claude":
            base_strength += 0.05

        # Cap at 1.0
        return min(base_strength, 1.0)

    def _merge_learning_metadata(
        self,
        word: str,
        cefr_data: Dict[str, Any],
        frequency_data: Dict[str, Any],
        claude_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge learning metadata from CEFR, frequency, and Claude sources.

        Priority for CEFR level:
        1. CEFR adapter (if available)
        2. Claude estimation (if CEFR adapter doesn't have data)
        3. None

        Args:
            word: Word being enriched
            cefr_data: Data from CEFR adapter
            frequency_data: Data from frequency adapter
            claude_data: Data from Claude AI

        Returns:
            Merged learning metadata dictionary
        """
        metadata = {
            "difficulty_level": None,
            "cefr_level": None,
            "frequency_rank": None,
            "frequency_band": None,
            "style_tags": []
        }

        # CEFR/Difficulty level: Prefer CEFR adapter, fallback to Claude estimation
        if cefr_data.get("cefr_level"):
            metadata["difficulty_level"] = cefr_data["cefr_level"]
            metadata["cefr_level"] = cefr_data["cefr_level"]
            logger.debug(f"Using CEFR level from adapter for '{word}': {cefr_data['cefr_level']}")
        elif claude_data.get("learning_metadata", {}).get("cefr_level"):
            # Claude can estimate CEFR level for words not in CEFR-J wordlist
            metadata["difficulty_level"] = claude_data["learning_metadata"]["cefr_level"]
            metadata["cefr_level"] = claude_data["learning_metadata"]["cefr_level"]
            logger.debug(f"Using Claude-estimated CEFR level for '{word}': {metadata['cefr_level']}")
        else:
            # Estimate based on frequency if available
            metadata["cefr_level"] = self._estimate_cefr_from_frequency(frequency_data)
            metadata["difficulty_level"] = metadata["cefr_level"]
            if metadata["cefr_level"]:
                logger.debug(f"Estimated CEFR level from frequency for '{word}': {metadata['cefr_level']}")

        # Frequency data: From frequency adapter
        if frequency_data.get("frequency_rank"):
            metadata["frequency_rank"] = frequency_data["frequency_rank"]
            metadata["frequency_band"] = frequency_data["frequency_band"]
            logger.debug(
                f"Using frequency data for '{word}': "
                f"rank {metadata['frequency_rank']}, band {metadata['frequency_band']}"
            )

        # Style tags: From Claude (if available)
        if claude_data.get("learning_metadata", {}).get("style_tags"):
            metadata["style_tags"] = claude_data["learning_metadata"]["style_tags"]

        return metadata

    def _estimate_cefr_from_frequency(self, frequency_data: Dict[str, Any]) -> Optional[str]:
        """
        Estimate CEFR level based on frequency rank when CEFR data unavailable.

        Rough mapping:
        - top-100: A1 (most basic words)
        - top-1000: A2 (elementary)
        - top-5000: B1 (intermediate)
        - top-10000: B2 (upper intermediate)
        - rare: C1 (advanced)
        - very-rare: C2 (proficiency)

        Args:
            frequency_data: Data from frequency adapter

        Returns:
            Estimated CEFR level or None if frequency data unavailable
        """
        frequency_rank = frequency_data.get("frequency_rank")

        if not frequency_rank:
            return None

        # Map frequency rank to CEFR level
        if frequency_rank <= 100:
            return "A1"
        elif frequency_rank <= 1000:
            return "A2"
        elif frequency_rank <= 5000:
            return "B1"
        elif frequency_rank <= 10000:
            return "B2"
        elif frequency_rank <= 25000:
            return "C1"
        else:
            return "C2"

    def _validate_enriched_data(self, data: Dict[str, Any]) -> None:
        """
        Validate that enriched data meets minimum quality standards.

        Args:
            data: Enriched word data to validate

        Raises:
            ValueError: If data doesn't meet minimum standards
        """
        # Require at least one definition
        if not data.get("definitions") or len(data["definitions"]) == 0:
            raise ValueError(f"No definitions found for word: {data.get('word_text')}")

        # Validate each definition has required fields
        for idx, definition in enumerate(data["definitions"]):
            if not definition.get("definition_text"):
                raise ValueError(f"Definition {idx} missing definition_text")

            if not definition.get("part_of_speech"):
                raise ValueError(f"Definition {idx} missing part_of_speech")

            # Check definition text length
            def_text = definition["definition_text"]
            if len(def_text) < 10:
                raise ValueError(f"Definition {idx} too short: {def_text}")

            if len(def_text) > 500:
                logger.warning(f"Definition {idx} too long ({len(def_text)} chars), truncating")
                definition["definition_text"] = def_text[:500]

            # Ensure examples list exists and process examples
            if "examples" not in definition:
                definition["examples"] = []
            else:
                # Process and classify examples
                definition["examples"] = self._process_examples(
                    definition["examples"],
                    data.get("word_text", "")
                )

        logger.debug(f"Validation passed for word: {data.get('word_text')}")

    def _process_examples(
        self,
        examples: List[Any],
        word_text: str
    ) -> List[Dict[str, Any]]:
        """
        Process and classify usage examples with context detection.

        Args:
            examples: List of examples (can be strings or dicts)
            word_text: The word being defined

        Returns:
            List of processed example dictionaries with context_type
        """
        processed_examples = []
        valid_contexts = {"casual", "academic", "business", "technical", "formal"}

        for idx, example in enumerate(examples):
            # Handle both string and dict formats
            if isinstance(example, str):
                example_text = example
                context_type = self._detect_context(example_text)
            elif isinstance(example, dict):
                example_text = example.get("example_text", "")
                context_type = example.get("context_type")

                # If context_type is missing or invalid, auto-detect
                if not context_type or context_type not in valid_contexts:
                    context_type = self._detect_context(example_text)
            else:
                logger.warning(f"Invalid example format at index {idx}: {type(example)}")
                continue

            # Validate example quality
            if not self._validate_example_quality(example_text, word_text):
                logger.warning(f"Example failed quality check: {example_text}")
                continue

            processed_examples.append({
                "example_text": example_text,
                "context_type": context_type
            })

        logger.debug(f"Processed {len(processed_examples)} valid examples from {len(examples)} total")
        return processed_examples

    def _detect_context(self, example_text: str) -> str:
        """
        Detect the context type of an example sentence.

        Uses keyword matching to classify examples into context categories.

        Args:
            example_text: Example sentence

        Returns:
            Context type: 'casual', 'academic', 'business', 'technical', or 'formal'
        """
        example_lower = example_text.lower()

        # Academic context keywords
        academic_keywords = [
            "research", "study", "theory", "hypothesis", "analysis",
            "experiment", "data", "scholar", "academic", "university",
            "thesis", "dissertation", "journal", "findings", "conclude"
        ]

        # Business context keywords
        business_keywords = [
            "company", "business", "client", "customer", "market",
            "sales", "profit", "revenue", "meeting", "project",
            "deadline", "manager", "employee", "corporate", "office"
        ]

        # Technical context keywords
        technical_keywords = [
            "system", "software", "hardware", "code", "algorithm",
            "function", "parameter", "database", "network", "protocol",
            "interface", "configuration", "implementation"
        ]

        # Formal context keywords
        formal_keywords = [
            "hereby", "therefore", "furthermore", "moreover",
            "shall", "cordially", "respectfully", "kindly",
            "sincerely", "distinguished", "honorable"
        ]

        # Count keyword matches
        academic_score = sum(1 for kw in academic_keywords if kw in example_lower)
        business_score = sum(1 for kw in business_keywords if kw in example_lower)
        technical_score = sum(1 for kw in technical_keywords if kw in example_lower)
        formal_score = sum(1 for kw in formal_keywords if kw in example_lower)

        # Determine context based on highest score
        scores = {
            "academic": academic_score,
            "business": business_score,
            "technical": technical_score,
            "formal": formal_score
        }

        max_score = max(scores.values())

        # If no keywords matched, default to casual
        if max_score == 0:
            return "casual"

        # Return context with highest score (ties default to casual)
        for context, score in scores.items():
            if score == max_score:
                return context

        return "casual"

    def _validate_example_quality(self, example_text: str, word_text: str) -> bool:
        """
        Validate that an example meets quality standards.

        Args:
            example_text: Example sentence to validate
            word_text: The word that should appear in the example

        Returns:
            True if example passes quality checks, False otherwise
        """
        # Check 1: Example text exists and is non-empty
        if not example_text or len(example_text.strip()) == 0:
            return False

        # Check 2: Length is within bounds (5-300 characters)
        if len(example_text) < 5 or len(example_text) > 300:
            logger.debug(f"Example length out of bounds: {len(example_text)} chars")
            return False

        # Check 3: Example contains the target word (case-insensitive)
        if word_text.lower() not in example_text.lower():
            logger.debug(f"Example does not contain word '{word_text}': {example_text}")
            return False

        # Check 4: Example looks like natural language (contains spaces and reasonable punctuation)
        if " " not in example_text:
            logger.debug(f"Example appears to be a single word, not a sentence: {example_text}")
            return False

        # Quality checks passed
        return True

    def calculate_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate data completeness metrics.

        Args:
            data: Enriched word data

        Returns:
            Dictionary with missing_fields and completeness_percentage
        """
        expected_fields = [
            "phonetic",
            "definitions",
            "grammatical_info",
            "related_words",
            "learning_metadata"
        ]

        missing_fields = []
        present_count = 0

        for field in expected_fields:
            value = data.get(field)

            # Check if field is meaningfully present
            if field == "phonetic":
                if value and value.get("ipa_transcription"):
                    present_count += 1
                else:
                    missing_fields.append("phonetic_transcription")

            elif field == "definitions":
                if value and len(value) > 0:
                    present_count += 1
                    # Check for examples in definitions
                    has_examples = any(
                        def_item.get("examples") and len(def_item["examples"]) > 0
                        for def_item in value
                    )
                    if not has_examples:
                        missing_fields.append("usage_examples")
                else:
                    missing_fields.append("definitions")

            elif field == "grammatical_info":
                if value and any(v for k, v in value.items() if k != "part_of_speech" and v):
                    present_count += 1
                else:
                    missing_fields.append("grammatical_forms")

            elif field == "related_words":
                if value and len(value) > 0:
                    present_count += 1
                else:
                    missing_fields.append("related_words")

            elif field == "learning_metadata":
                # For now, this is always missing until US4 is implemented
                metadata = value or {}
                if metadata.get("difficulty_level") or metadata.get("frequency_rank"):
                    present_count += 1
                else:
                    missing_fields.append("difficulty_level")

        completeness_percentage = int((present_count / len(expected_fields)) * 100)

        return {
            "missing_fields": missing_fields,
            "completeness_percentage": completeness_percentage
        }

    def _validate_grammatical_forms(
        self,
        word: str,
        grammatical_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and enhance grammatical form data (T065).

        Ensures:
        - Verb forms are consistent (if any verb field present, base form required)
        - Plural forms are present for nouns
        - Adjective forms follow rules (comparative/superlative together)
        - Irregular forms are properly flagged

        Args:
            word: The word being validated
            grammatical_info: Grammatical information dictionary

        Returns:
            Validated and enhanced grammatical information
        """
        if not grammatical_info:
            return {}

        validated = grammatical_info.copy()
        part_of_speech = validated.get("part_of_speech", "").lower()

        # Validate verb forms
        verb_fields = [
            "verb_base",
            "verb_past_simple",
            "verb_past_participle",
            "verb_present_participle",
            "verb_third_person"
        ]
        has_any_verb_form = any(validated.get(field) for field in verb_fields)

        if has_any_verb_form or part_of_speech == "verb":
            # If any verb field is populated, base form must be present
            if not validated.get("verb_base"):
                validated["verb_base"] = word
                logger.debug(f"Added missing verb_base for '{word}'")

            # Check for irregular verb forms
            if validated.get("verb_past_simple") or validated.get("verb_past_participle"):
                is_irregular = self._is_irregular_verb(
                    validated.get("verb_base", word),
                    validated.get("verb_past_simple"),
                    validated.get("verb_past_participle")
                )

                if is_irregular:
                    irregular_json = validated.get("irregular_forms_json") or {}
                    if not irregular_json.get("irregular_verb"):
                        irregular_json["irregular_verb"] = True
                        irregular_json["note"] = f"Irregular verb: {validated['verb_base']}/{validated.get('verb_past_simple')}/{validated.get('verb_past_participle')}"
                        validated["irregular_forms_json"] = irregular_json
                        logger.debug(f"Flagged irregular verb: {word}")

        # Validate adjective forms
        if validated.get("adj_comparative") and validated.get("adj_superlative"):
            is_irregular = self._is_irregular_adjective(
                word,
                validated["adj_comparative"],
                validated["adj_superlative"]
            )

            if is_irregular:
                irregular_json = validated.get("irregular_forms_json") or {}
                if not irregular_json.get("irregular_comparison"):
                    irregular_json["irregular_comparison"] = True
                    irregular_json["note"] = f"Irregular adjective: {word}/{validated['adj_comparative']}/{validated['adj_superlative']}"
                    validated["irregular_forms_json"] = irregular_json
                    logger.debug(f"Flagged irregular adjective: {word}")

        # Validate noun plural forms
        if part_of_speech == "noun" and validated.get("plural_form"):
            is_irregular = self._is_irregular_plural(word, validated["plural_form"])

            if is_irregular:
                irregular_json = validated.get("irregular_forms_json") or {}
                if not irregular_json.get("irregular_plural"):
                    irregular_json["irregular_plural"] = True
                    irregular_json["note"] = f"Irregular plural: {word} → {validated['plural_form']}"
                    validated["irregular_forms_json"] = irregular_json
                    logger.debug(f"Flagged irregular plural: {word} → {validated['plural_form']}")

        return validated

    def _is_irregular_verb(self, base: str, past: Optional[str], past_part: Optional[str]) -> bool:
        """
        Check if verb forms are irregular (T066).

        Args:
            base: Base form
            past: Past simple form
            past_part: Past participle

        Returns:
            True if irregular, False otherwise
        """
        if not past or not base:
            return False

        # Regular verbs typically add -ed to base form
        # Check if past form doesn't follow regular pattern
        regular_past = base + "ed" if not base.endswith("e") else base + "d"

        # Handle consonant doubling (stop → stopped)
        if len(base) >= 2 and base[-1] not in "aeiou" and base[-2] in "aeiou":
            regular_past = base + base[-1] + "ed"

        # Handle y → ied (try → tried)
        if base.endswith("y") and len(base) > 2 and base[-2] not in "aeiou":
            regular_past = base[:-1] + "ied"

        # If past doesn't match regular form, it's irregular
        if past.lower() != regular_past.lower():
            return True

        # If past participle differs from past simple, it's irregular
        if past_part and past_part.lower() != past.lower():
            return True

        return False

    def _is_irregular_adjective(self, base: str, comparative: str, superlative: str) -> bool:
        """
        Check if adjective comparison is irregular.

        Args:
            base: Base form
            comparative: Comparative form
            superlative: Superlative form

        Returns:
            True if irregular, False otherwise
        """
        # Regular adjectives add -er/-est or use more/most
        # Check for irregular patterns (good/better/best, bad/worse/worst)
        irregular_patterns = {
            "good": ("better", "best"),
            "bad": ("worse", "worst"),
            "little": ("less", "least"),
            "much": ("more", "most"),
            "many": ("more", "most"),
            "far": ("farther", "farthest"),  # or further/furthest
        }

        base_lower = base.lower()
        if base_lower in irregular_patterns:
            expected_comp, expected_sup = irregular_patterns[base_lower]
            if comparative.lower() == expected_comp and superlative.lower() == expected_sup:
                return True

        # Check if it doesn't follow regular -er/-est pattern
        regular_comp = base + "er" if not base.endswith("e") else base + "r"
        regular_sup = base + "est" if not base.endswith("e") else base + "st"

        # Handle y → ier/iest (happy → happier/happiest)
        if base.endswith("y"):
            regular_comp = base[:-1] + "ier"
            regular_sup = base[:-1] + "iest"

        # If comparative/superlative don't match regular patterns, it's irregular
        if comparative.lower() != regular_comp.lower() and not comparative.lower().startswith("more"):
            return True

        return False

    def _is_irregular_plural(self, singular: str, plural: str) -> bool:
        """
        Check if noun plural is irregular (T066).

        Args:
            singular: Singular form
            plural: Plural form

        Returns:
            True if irregular, False otherwise
        """
        # Regular plurals typically add -s or -es
        regular_plural = singular + "s"

        # Handle -es cases (box → boxes, church → churches)
        if singular.endswith(("s", "x", "z", "ch", "sh")):
            regular_plural = singular + "es"

        # Handle consonant + y → ies (baby → babies)
        if singular.endswith("y") and len(singular) > 1 and singular[-2] not in "aeiou":
            regular_plural = singular[:-1] + "ies"

        # Handle -f/-fe → -ves (knife → knives, leaf → leaves)
        if singular.endswith("f"):
            regular_plural = singular[:-1] + "ves"
        elif singular.endswith("fe"):
            regular_plural = singular[:-2] + "ves"

        # If plural doesn't match regular form, it's irregular
        if plural.lower() != regular_plural.lower():
            return True

        return False
