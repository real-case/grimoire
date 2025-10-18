"""Claude AI enrichment adapter for comprehensive word information."""
from typing import Any, Dict
import json

from anthropic import AsyncAnthropic
from loguru import logger

from src.core.config import settings
from src.services.data_source_adapter import DataSourceAdapter


class ClaudeEnrichmentAdapter(DataSourceAdapter):
    """
    Adapter for enriching word data using Claude AI via Anthropic API.

    Provides:
    - Learner-appropriate definitions
    - IPA phonetic transcriptions
    - Usage examples (3-5 sentences)
    - Grammatical information
    - Part of speech analysis
    """

    def __init__(self):
        """Initialize Claude adapter with Anthropic client."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens

    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch comprehensive word data from Claude AI.

        Args:
            word: Word text to look up (normalized)

        Returns:
            Dictionary containing definitions, phonetics, examples, and grammatical info

        Raises:
            Exception: If API call fails
        """
        try:
            prompt = self._build_enrichment_prompt(word)

            logger.info(f"Requesting word enrichment from Claude for: {word}")

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3  # Lower temperature for more consistent, factual responses
            )

            # Extract content from response
            content = response.content[0].text

            # Parse JSON response from Claude
            word_data = json.loads(content)

            logger.info(f"Successfully enriched word '{word}' with Claude")
            logger.debug(f"Claude response for '{word}': {word_data}")

            return word_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response for '{word}': {e}")
            logger.error(f"Raw response: {content if 'content' in locals() else 'N/A'}")
            raise Exception(f"Invalid JSON response from Claude for word '{word}'")

        except Exception as e:
            logger.error(f"Claude API error for word '{word}': {e}")
            raise Exception(f"Failed to enrich word '{word}' with Claude: {str(e)}")

    def supports_field(self, field: str) -> bool:
        """
        Check if Claude adapter supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if field is supported (definitions, phonetics, examples, grammar)
        """
        supported_fields = {
            "definitions",
            "phonetic",
            "phonetics",
            "examples",
            "grammar",
            "grammatical_info",
            "related_words",
            "synonyms",
            "antonyms",
        }
        return field in supported_fields

    def _build_enrichment_prompt(self, word: str) -> str:
        """
        Build structured prompt for Claude to generate word information.

        Args:
            word: Word to enrich

        Returns:
            Formatted prompt string
        """
        return f"""You are a helpful English language teacher creating dictionary entries for English as a Foreign Language (EFL) learners.

Provide comprehensive information about the word: "{word}"

Return your response as valid JSON with the following structure:

{{
  "phonetic": {{
    "ipa_transcription": "IPA phonetic transcription (e.g., /wɜːrd/)",
    "audio_url": null
  }},
  "definitions": [
    {{
      "definition_text": "Clear, simple definition appropriate for learners (10-500 characters)",
      "part_of_speech": "noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection|determiner|modal",
      "usage_context": "optional context like 'informal', 'technical', 'formal', or null",
      "examples": [
        {{
          "example_text": "Natural example sentence using the word",
          "context_type": "casual"
        }},
        {{
          "example_text": "Another example in a different context",
          "context_type": "academic"
        }},
        {{
          "example_text": "A third example showing different usage",
          "context_type": "business"
        }}
      ]
    }}
  ],
  "grammatical_info": {{
    "part_of_speech": "primary part of speech",
    "plural_form": "plural form for nouns (or null)",
    "verb_base": "base form for verbs (or null)",
    "verb_past_simple": "past simple tense (or null)",
    "verb_past_participle": "past participle (or null)",
    "verb_present_participle": "present participle (or null)",
    "verb_third_person": "3rd person singular present (or null)",
    "adj_comparative": "comparative form for adjectives (or null)",
    "adj_superlative": "superlative form for adjectives (or null)",
    "irregular_forms_json": {{}}
  }},
  "related_words": [
    {{
      "word": "synonym word",
      "relationship_type": "synonym",
      "usage_notes": "Explain subtle differences in usage or context"
    }},
    {{
      "word": "antonym word",
      "relationship_type": "antonym",
      "usage_notes": "Explain the contrast or difference"
    }},
    {{
      "word": "derivative word",
      "relationship_type": "derivative",
      "usage_notes": "Explain the morphological relationship"
    }}
  ]
}}

IMPORTANT GUIDELINES:
1. Definitions should be clear, simple, and appropriate for language learners
2. Provide 3-5 natural usage examples that show the word in DIFFERENT CONTEXTS
3. Each example MUST include:
   - example_text: A complete, natural sentence (5-300 characters)
   - context_type: One of 'casual', 'academic', 'business', 'technical', or 'formal'
4. Vary the context_type across examples to demonstrate different usage scenarios:
   - casual: Everyday conversation, informal situations
   - academic: Educational, scholarly contexts
   - business: Professional, workplace settings
   - technical: Specialized, domain-specific usage
   - formal: Official, ceremonial, or polite contexts
5. Examples should be complete sentences that sound natural and contain the target word
6. Include IPA phonetic transcription (use standard IPA notation)
7. For grammatical forms, ALWAYS fill in ALL fields relevant to the part of speech:
   - Nouns: plural_form (REQUIRED if countable, show irregular plurals like "children", "mice", "feet")
   - Verbs: ALL verb forms REQUIRED (base, past_simple, past_participle, present_participle, third_person)
     * Pay special attention to irregular verbs (go/went/gone, swim/swam/swum, etc.)
   - Adjectives: comparative and superlative forms (REQUIRED if gradable, show irregular forms like "good/better/best")
8. Mark irregular forms in irregular_forms_json with detailed notes:
   - For irregular plurals: {{"irregular_plural": true, "note": "irregular plural form"}}
   - For irregular verbs: {{"irregular_verb": true, "forms": {{"past": "went", "past_participle": "gone"}}, "note": "highly irregular"}}
   - For irregular adjectives: {{"irregular_comparison": true, "note": "irregular comparative/superlative"}}
9. GRAMMATICAL COMPLETENESS IS CRITICAL FOR LEARNERS - Always provide complete conjugations and forms
9. If the word has multiple common meanings, include multiple definitions
10. Order definitions by commonality (most common first)
11. For related_words, provide 3-5 key related words with usage notes:
   - synonyms: Include 2-3 common synonyms with usage notes explaining subtle differences
   - antonyms: Include 1-2 antonyms if applicable
   - derivatives: Include morphologically related words (e.g., happy → happiness)
   - Usage notes should help learners understand when to use one word vs another
   - Example usage note: "While 'joyful' emphasizes strong emotion, 'happy' is more general"

Return ONLY valid JSON, no additional text or explanation."""

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide
        """
        return [
            "definitions",
            "phonetic",
            "phonetics",
            "examples",
            "grammar",
            "grammatical_info",
            "related_words",
            "synonyms",
            "antonyms",
        ]
