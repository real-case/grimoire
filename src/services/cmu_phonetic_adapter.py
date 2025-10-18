"""CMU Pronouncing Dictionary adapter for phonetic transcriptions."""
from typing import Any, Dict, Optional
import nltk
from nltk.corpus import cmudict
from loguru import logger

from src.services.data_source_adapter import DataSourceAdapter


class CMUPhoneticAdapter(DataSourceAdapter):
    """
    Adapter for fetching phonetic transcriptions from CMU Pronouncing Dictionary.

    Converts ARPABET notation to IPA (International Phonetic Alphabet).

    Provides:
    - IPA phonetic transcription
    """

    # ARPABET to IPA conversion mapping
    ARPABET_TO_IPA = {
        'AA': 'ɑ', 'AE': 'æ', 'AH': 'ə', 'AO': 'ɔ', 'AW': 'aʊ',
        'AY': 'aɪ', 'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð',
        'EH': 'ɛ', 'ER': 'ɜr', 'EY': 'eɪ', 'F': 'f', 'G': 'ɡ',
        'HH': 'h', 'IH': 'ɪ', 'IY': 'i', 'JH': 'dʒ', 'K': 'k',
        'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'OW': 'oʊ',
        'OY': 'ɔɪ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ',
        'T': 't', 'TH': 'θ', 'UH': 'ʊ', 'UW': 'u', 'V': 'v',
        'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'
    }

    def __init__(self):
        """Initialize CMU adapter and ensure data is downloaded."""
        self._ensure_cmudict_data()
        self.cmu_dict = cmudict.dict()

    def _ensure_cmudict_data(self):
        """Ensure CMU Dictionary data is available, download if necessary."""
        try:
            # Try to access cmudict to verify it's available
            cmudict.dict()
            logger.debug("CMU Dictionary data is available")
        except LookupError:
            logger.info("CMU Dictionary data not found, downloading...")
            try:
                nltk.download('cmudict', quiet=True)
                logger.info("CMU Dictionary data downloaded successfully")
            except Exception as e:
                logger.error(f"Failed to download CMU Dictionary data: {e}")
                raise

    async def fetch_word_data(self, word: str) -> Dict[str, Any]:
        """
        Fetch phonetic transcription from CMU Dictionary.

        Args:
            word: Word text to look up (normalized)

        Returns:
            Dictionary containing IPA transcription

        Raises:
            Exception: If data fetching fails
        """
        try:
            logger.debug(f"Fetching CMU phonetics for: {word}")

            # CMU dict uses lowercase
            word_lower = word.lower()

            if word_lower not in self.cmu_dict:
                logger.debug(f"Word '{word}' not found in CMU Dictionary")
                return {
                    "phonetic": {
                        "ipa_transcription": None,
                        "audio_url": None
                    }
                }

            # Get first pronunciation (most common)
            arpabet = self.cmu_dict[word_lower][0]

            # Convert ARPABET to IPA
            ipa = self._arpabet_to_ipa(arpabet)

            logger.info(f"CMU phonetic for '{word}': {ipa}")

            return {
                "phonetic": {
                    "ipa_transcription": ipa,
                    "audio_url": None
                }
            }

        except Exception as e:
            logger.error(f"CMU Dictionary error for word '{word}': {e}")
            # Return empty result instead of failing
            return {
                "phonetic": {
                    "ipa_transcription": None,
                    "audio_url": None
                }
            }

    def _arpabet_to_ipa(self, arpabet: list) -> str:
        """
        Convert ARPABET phonemes to IPA transcription.

        Args:
            arpabet: List of ARPABET phonemes (e.g., ['W', 'ER1', 'D'])

        Returns:
            IPA transcription string (e.g., '/wɜrd/')
        """
        ipa_phones = []
        stress_mark = ''

        for phone in arpabet:
            # Remove stress markers (0, 1, 2) from vowels
            clean_phone = phone.rstrip('012')

            # Check for primary stress
            if phone.endswith('1'):
                stress_mark = 'ˈ'
            # Check for secondary stress
            elif phone.endswith('2'):
                stress_mark = 'ˌ'
            else:
                stress_mark = ''

            # Convert to IPA
            if clean_phone in self.ARPABET_TO_IPA:
                if stress_mark:
                    ipa_phones.append(stress_mark + self.ARPABET_TO_IPA[clean_phone])
                else:
                    ipa_phones.append(self.ARPABET_TO_IPA[clean_phone])
            else:
                logger.warning(f"Unknown ARPABET phoneme: {clean_phone}")
                ipa_phones.append(clean_phone.lower())

        # Join and wrap in slashes
        ipa = '/' + ''.join(ipa_phones) + '/'

        return ipa

    def supports_field(self, field: str) -> bool:
        """
        Check if CMU adapter supports a specific field.

        Args:
            field: Field name to check

        Returns:
            True if field is supported (phonetics)
        """
        supported_fields = {
            "phonetic",
            "phonetics",
        }
        return field in supported_fields

    def get_supported_fields(self) -> list[str]:
        """
        Get list of all supported fields.

        Returns:
            List of field names this adapter can provide
        """
        return ["phonetic", "phonetics"]
