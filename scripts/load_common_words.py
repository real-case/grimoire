#!/usr/bin/env python3
"""
Database seed script to batch-load common English words.

This script:
1. Loads a frequency-ordered word list (top N words)
2. Batch enriches words via Claude API (parallelized)
3. Supplements with WordNet, CMU Dict, CEFR-J data
4. Stores enriched data in PostgreSQL
5. Caches in Redis for fast lookups

Usage:
    python scripts/load_common_words.py --count 10000
    python scripts/load_common_words.py --count 1000 --batch-size 50 --max-workers 10
"""
import asyncio
import argparse
import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import init_db, close_db, async_session_maker
from src.core.cache import init_redis, close_redis
from src.services.word_service import WordService
from src.services.enrichment_service import EnrichmentService
from src.services.cache_service import CacheService
from src.repositories.word_repository import WordRepository


# Common English words by frequency (top 10,000)
# Source: Google Books Ngram corpus / COCA
COMMON_WORDS = [
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
    # Add more words as needed - this is just a starter set
    # Full list should be loaded from a word frequency file
]


async def load_word_frequency_list(count: int) -> List[str]:
    """
    Load top N words from frequency corpus.

    Args:
        count: Number of words to load

    Returns:
        List of words ordered by frequency (most common first)
    """
    # In production, load from a file (e.g., Google Books Ngram, COCA)
    # For now, return the sample list
    logger.info(f"Loading top {count} words from frequency corpus")

    # TODO: Load from actual frequency corpus file
    # Example:
    # with open("data/word_frequency.txt") as f:
    #     words = [line.strip() for line in f][:count]

    words = COMMON_WORDS[:count]
    logger.info(f"Loaded {len(words)} words")
    return words


async def enrich_word_batch(
    words: List[str],
    word_service: WordService,
    session: AsyncSession
) -> int:
    """
    Enrich a batch of words and store in database.

    Args:
        words: List of words to enrich
        word_service: Word service instance
        session: Database session

    Returns:
        Number of successfully enriched words
    """
    success_count = 0

    for word in words:
        try:
            logger.info(f"Enriching word: {word}")

            # Check if word already exists
            existing_word = await word_service.word_repository.get_by_word_text(
                word_text=word,
                session=session
            )

            if existing_word:
                logger.info(f"Word '{word}' already exists, skipping")
                success_count += 1
                continue

            # Enrich and store word
            word_data = await word_service.lookup_word(word, session)

            if word_data:
                logger.info(f"Successfully enriched and stored: {word}")
                success_count += 1
            else:
                logger.warning(f"Failed to enrich word: {word}")

        except Exception as e:
            logger.error(f"Error enriching word '{word}': {e}")
            continue

    return success_count


async def main(args):
    """Main execution function."""
    logger.info("Starting word database seeding")
    logger.info(f"Configuration:")
    logger.info(f"  - Words to load: {args.count}")
    logger.info(f"  - Batch size: {args.batch_size}")
    logger.info(f"  - Max workers: {args.max_workers}")

    try:
        # Initialize database and Redis
        logger.info("Initializing database connection...")
        await init_db()

        logger.info("Initializing Redis connection...")
        await init_redis()

        # Load word list
        words = await load_word_frequency_list(args.count)
        total_words = len(words)

        # Initialize services
        async with async_session_maker() as session:
            word_repository = WordRepository()
            enrichment_service = EnrichmentService()
            cache_service = CacheService()
            word_service = WordService(
                word_repository=word_repository,
                enrichment_service=enrichment_service,
                cache_service=cache_service
            )

            # Process words in batches
            total_enriched = 0

            for i in range(0, total_words, args.batch_size):
                batch = words[i:i + args.batch_size]
                batch_num = (i // args.batch_size) + 1
                total_batches = (total_words + args.batch_size - 1) // args.batch_size

                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} words)")

                # Enrich batch (can be parallelized with asyncio.gather for better performance)
                enriched = await enrich_word_batch(batch, word_service, session)
                total_enriched += enriched

                # Commit after each batch
                await session.commit()

                logger.info(f"Batch {batch_num} complete: {enriched}/{len(batch)} words enriched")
                logger.info(f"Progress: {total_enriched}/{total_words} words ({100*total_enriched/total_words:.1f}%)")

        logger.info(f"Word seeding complete!")
        logger.info(f"Successfully enriched {total_enriched}/{total_words} words")

    except Exception as e:
        logger.error(f"Fatal error during seeding: {e}", exc_info=True)
        raise

    finally:
        # Cleanup
        logger.info("Closing connections...")
        await close_db()
        await close_redis()
        logger.info("Seed script complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load common English words into the database with AI enrichment"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="Number of words to load (default: 1000)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing (default: 50)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help="Maximum parallel workers (default: 5)"
    )

    args = parser.parse_args()

    # Run async main
    asyncio.run(main(args))
