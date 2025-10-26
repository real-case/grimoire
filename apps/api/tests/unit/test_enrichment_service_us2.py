"""Unit tests for EnrichmentService - User Story 2 (Contextual Examples)."""
import pytest
from unittest.mock import Mock, AsyncMock
from src.services.enrichment_service import EnrichmentService


class TestExampleContextDetection:
    """Test context detection functionality."""

    @pytest.fixture
    def enrichment_service(self):
        """Create EnrichmentService instance for testing."""
        return EnrichmentService()

    def test_detect_context_casual(self, enrichment_service):
        """Test detection of casual context examples."""
        examples = [
            "Let's grab some coffee later!",
            "I'm going to the store.",
            "That movie was awesome!"
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "casual", f"Expected 'casual' for: {example}"

    def test_detect_context_academic(self, enrichment_service):
        """Test detection of academic context examples."""
        examples = [
            "The research findings indicate a correlation.",
            "This study examines the hypothesis thoroughly.",
            "According to the data analysis, the theory holds.",
            "The experiment yielded significant results."
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "academic", f"Expected 'academic' for: {example}"

    def test_detect_context_business(self, enrichment_service):
        """Test detection of business context examples."""
        examples = [
            "Our company's revenue increased this quarter.",
            "The client requested a project deadline extension.",
            "The meeting with the manager is scheduled for Monday.",
            "Sales figures show strong market performance."
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "business", f"Expected 'business' for: {example}"

    def test_detect_context_technical(self, enrichment_service):
        """Test detection of technical context examples."""
        examples = [
            "The system crashed due to a database error.",
            "Configure the network interface settings.",
            "The algorithm optimizes parameter selection.",
            "Implement the function with proper error handling."
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "technical", f"Expected 'technical' for: {example}"

    def test_detect_context_formal(self, enrichment_service):
        """Test detection of formal context examples."""
        examples = [
            "We hereby declare this agreement binding.",
            "I respectfully submit my resignation.",
            "The distinguished guest will arrive shortly.",
            "Please kindly confirm your attendance."
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "formal", f"Expected 'formal' for: {example}"

    def test_detect_context_default_casual(self, enrichment_service):
        """Test that unknown contexts default to casual."""
        examples = [
            "This is a simple sentence.",
            "The word appears here.",
            "Just a regular example."
        ]

        for example in examples:
            context = enrichment_service._detect_context(example)
            assert context == "casual", f"Expected 'casual' default for: {example}"


class TestExampleQualityValidation:
    """Test example quality validation functionality."""

    @pytest.fixture
    def enrichment_service(self):
        """Create EnrichmentService instance for testing."""
        return EnrichmentService()

    def test_validate_example_quality_valid(self, enrichment_service):
        """Test validation of valid examples."""
        word = "serendipity"
        valid_examples = [
            "Meeting her was pure serendipity.",
            "The serendipity of finding that book changed my life.",
            "What a serendipity that we both arrived at the same time!"
        ]

        for example in valid_examples:
            result = enrichment_service._validate_example_quality(example, word)
            assert result is True, f"Example should be valid: {example}"

    def test_validate_example_quality_too_short(self, enrichment_service):
        """Test that examples < 5 chars are rejected."""
        word = "cat"
        short_examples = ["cat", "the", "a", ""]

        for example in short_examples:
            result = enrichment_service._validate_example_quality(example, word)
            assert result is False, f"Example should be rejected (too short): {example}"

    def test_validate_example_quality_too_long(self, enrichment_service):
        """Test that examples > 300 chars are rejected."""
        word = "test"
        long_example = "This is a very long example " * 20  # > 300 chars

        result = enrichment_service._validate_example_quality(long_example, word)
        assert result is False, "Example should be rejected (too long)"

    def test_validate_example_quality_missing_word(self, enrichment_service):
        """Test that examples without the target word are rejected."""
        word = "serendipity"
        examples_without_word = [
            "This is a complete sentence.",
            "The quick brown fox jumps over the lazy dog.",
            "A perfectly valid sentence that doesn't contain the target."
        ]

        for example in examples_without_word:
            result = enrichment_service._validate_example_quality(example, word)
            assert result is False, f"Example should be rejected (missing word): {example}"

    def test_validate_example_quality_case_insensitive(self, enrichment_service):
        """Test that word matching is case-insensitive."""
        word = "serendipity"
        examples_with_variations = [
            "Meeting her was pure Serendipity.",
            "The SERENDIPITY of that moment was amazing.",
            "What serendipity!"
        ]

        for example in examples_with_variations:
            result = enrichment_service._validate_example_quality(example, word)
            assert result is True, f"Example should be valid (case variations): {example}"

    def test_validate_example_quality_single_word(self, enrichment_service):
        """Test that single words (no spaces) are rejected."""
        word = "test"
        single_words = ["testing", "tester", "test"]

        for example in single_words:
            result = enrichment_service._validate_example_quality(example, word)
            assert result is False, f"Example should be rejected (single word): {example}"


class TestExampleProcessing:
    """Test example processing and classification."""

    @pytest.fixture
    def enrichment_service(self):
        """Create EnrichmentService instance for testing."""
        return EnrichmentService()

    def test_process_examples_dict_format(self, enrichment_service):
        """Test processing examples in dict format."""
        word = "ubiquitous"
        examples = [
            {
                "example_text": "The ubiquitous smartphone has changed communication.",
                "context_type": "casual"
            },
            {
                "example_text": "Research shows ubiquitous technology in education.",
                "context_type": "academic"
            }
        ]

        result = enrichment_service._process_examples(examples, word)

        assert len(result) == 2
        assert all(ex.get("example_text") for ex in result)
        assert all(ex.get("context_type") for ex in result)
        assert result[0]["context_type"] == "casual"
        assert result[1]["context_type"] == "academic"

    def test_process_examples_string_format(self, enrichment_service):
        """Test processing examples in string format (backward compatibility)."""
        word = "ubiquitous"
        examples = [
            "The ubiquitous smartphone has changed communication.",
            "Research shows ubiquitous technology in education."
        ]

        result = enrichment_service._process_examples(examples, word)

        assert len(result) == 2
        assert all(ex.get("example_text") for ex in result)
        assert all(ex.get("context_type") for ex in result)
        # Should auto-detect contexts
        assert result[1]["context_type"] == "academic"  # Contains "research"

    def test_process_examples_filters_invalid(self, enrichment_service):
        """Test that invalid examples are filtered out."""
        word = "serendipity"
        examples = [
            {
                "example_text": "Meeting her was pure serendipity.",
                "context_type": "casual"
            },
            {
                "example_text": "too short",  # Too short AND missing word
                "context_type": "casual"
            },
            {
                "example_text": "This example does not contain the target word.",
                "context_type": "casual"
            },
            {
                "example_text": "Another serendipity example that is valid.",
                "context_type": "academic"
            }
        ]

        result = enrichment_service._process_examples(examples, word)

        # Should only have 2 valid examples
        assert len(result) == 2
        assert "serendipity" in result[0]["example_text"].lower()
        assert "serendipity" in result[1]["example_text"].lower()

    def test_process_examples_auto_detects_invalid_context(self, enrichment_service):
        """Test that invalid context types are auto-detected."""
        word = "research"
        examples = [
            {
                "example_text": "The research findings are conclusive.",
                "context_type": "invalid_context"  # Invalid context type
            }
        ]

        result = enrichment_service._process_examples(examples, word)

        assert len(result) == 1
        # Should auto-detect academic context
        assert result[0]["context_type"] == "academic"

    def test_process_examples_empty_list(self, enrichment_service):
        """Test processing empty example list."""
        word = "test"
        examples = []

        result = enrichment_service._process_examples(examples, word)

        assert result == []

    def test_process_examples_mixed_formats(self, enrichment_service):
        """Test processing mixed string and dict formats."""
        word = "innovative"
        examples = [
            "The innovative solution revolutionized the industry.",  # String
            {
                "example_text": "Our company develops innovative products.",
                "context_type": "business"
            },  # Dict
            "Research on innovative teaching methods continues."  # String
        ]

        result = enrichment_service._process_examples(examples, word)

        assert len(result) == 3
        assert all(ex.get("example_text") for ex in result)
        assert all(ex.get("context_type") for ex in result)
        assert result[1]["context_type"] == "business"


class TestEnrichmentValidation:
    """Test validation of enriched data with examples."""

    @pytest.fixture
    def enrichment_service(self):
        """Create EnrichmentService instance for testing."""
        return EnrichmentService()

    def test_validate_enriched_data_processes_examples(self, enrichment_service):
        """Test that validation processes examples."""
        data = {
            "word_text": "test",
            "definitions": [
                {
                    "definition_text": "A procedure for assessment.",
                    "part_of_speech": "noun",
                    "examples": [
                        "The test results were positive.",
                        "Students take the test tomorrow."
                    ]
                }
            ]
        }

        # Should not raise exception
        enrichment_service._validate_enriched_data(data)

        # Examples should be processed into dict format
        examples = data["definitions"][0]["examples"]
        assert all(isinstance(ex, dict) for ex in examples)
        assert all(ex.get("example_text") for ex in examples)
        assert all(ex.get("context_type") for ex in examples)

    def test_validate_enriched_data_handles_missing_examples(self, enrichment_service):
        """Test validation when examples are missing."""
        data = {
            "word_text": "test",
            "definitions": [
                {
                    "definition_text": "A procedure for assessment.",
                    "part_of_speech": "noun"
                    # No examples field
                }
            ]
        }

        # Should not raise exception
        enrichment_service._validate_enriched_data(data)

        # Examples list should be created
        assert "examples" in data["definitions"][0]
        assert data["definitions"][0]["examples"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
