"""Word model - Primary entity representing an English word."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Word(Base):
    """
    Primary entity representing an English word.

    Attributes:
        word_text: The word itself (lowercase, normalized)
        language: Language code (default: "en")
        last_enriched_at: Last time AI enrichment was performed

    Relationships:
        definitions: Collection of definitions for this word
        phonetic: Phonetic representation (1:1)
        grammatical_info: Grammatical information (1:1)
        learning_metadata: Learning-specific metadata (1:1)
        related_words_source: Related words where this word is the source
        related_words_target: Related words where this word is the target
    """

    __tablename__ = "words"

    # Fields
    word_text: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        doc="The word itself (lowercase, normalized)"
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        server_default="en",
        doc="Language code (ISO 639-1)"
    )

    last_enriched_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        doc="Last time AI enrichment was performed"
    )

    # Relationships
    definitions: Mapped[List["Definition"]] = relationship(
        "Definition",
        back_populates="word",
        cascade="all, delete-orphan",
        order_by="Definition.order_index"
    )

    phonetic: Mapped[Optional["PhoneticRepresentation"]] = relationship(
        "PhoneticRepresentation",
        back_populates="word",
        cascade="all, delete-orphan",
        uselist=False
    )

    grammatical_info: Mapped[Optional["GrammaticalInformation"]] = relationship(
        "GrammaticalInformation",
        back_populates="word",
        cascade="all, delete-orphan",
        uselist=False
    )

    learning_metadata: Mapped[Optional["LearningMetadata"]] = relationship(
        "LearningMetadata",
        back_populates="word",
        cascade="all, delete-orphan",
        uselist=False
    )

    related_words_source: Mapped[List["RelatedWord"]] = relationship(
        "RelatedWord",
        foreign_keys="RelatedWord.source_word_id",
        back_populates="source_word",
        cascade="all, delete-orphan"
    )

    related_words_target: Mapped[List["RelatedWord"]] = relationship(
        "RelatedWord",
        foreign_keys="RelatedWord.target_word_id",
        back_populates="target_word",
        cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "word_text ~ '^[a-z]+(-[a-z]+)*$'",
            name="check_word_text_pattern"
        ),
        Index("idx_words_language", "language"),
        Index("idx_words_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Word(id={self.id}, word_text='{self.word_text}', language='{self.language}')>"
