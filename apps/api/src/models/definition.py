"""Definition model - Represents a single meaning/definition of a word."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class Definition(Base):
    """
    Represents a single meaning/definition of a word.

    Attributes:
        word_id: Foreign key to parent word
        definition_text: Clear, learner-appropriate definition
        part_of_speech: Part of speech (noun, verb, adjective, etc.)
        usage_context: Context where this definition applies (e.g., "informal", "technical")
        order_index: Display order (1, 2, 3...)

    Relationships:
        word: Parent word
        usage_examples: Collection of usage examples for this definition
    """

    __tablename__ = "definitions"

    # Foreign Keys
    word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Parent word ID"
    )

    # Fields
    definition_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Clear, learner-appropriate definition (10-500 characters)"
    )

    part_of_speech: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Part of speech: noun, verb, adjective, adverb, etc."
    )

    usage_context: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Context where this definition applies (e.g., 'informal', 'technical')"
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Display order (1, 2, 3...)"
    )

    # Relationships
    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="definitions"
    )

    usage_examples: Mapped[List["UsageExample"]] = relationship(
        "UsageExample",
        back_populates="definition",
        cascade="all, delete-orphan",
        order_by="UsageExample.order_index"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "order_index > 0",
            name="check_order_index_positive"
        ),
        CheckConstraint(
            "part_of_speech IN ('noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'determiner', 'modal')",
            name="check_part_of_speech_valid"
        ),
        CheckConstraint(
            "length(definition_text) >= 10 AND length(definition_text) <= 500",
            name="check_definition_text_length"
        ),
        Index("idx_definitions_word_id", "word_id"),
        Index("idx_definitions_word_order", "word_id", "order_index"),
    )

    def __repr__(self) -> str:
        return f"<Definition(id={self.id}, word_id={self.word_id}, part_of_speech='{self.part_of_speech}', order={self.order_index})>"
