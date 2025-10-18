"""RelatedWord model - Semantic relationships between words."""
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class RelatedWord(Base):
    """
    Semantic relationships between words (synonyms, antonyms, derivatives).

    Attributes:
        source_word_id: Foreign key to source word
        target_word_id: Foreign key to related/target word
        relationship_type: Type of relationship (synonym, antonym, derivative, etc.)
        usage_notes: Explanation of subtle differences in usage
        strength: Relationship strength (0.0-1.0, for synonyms)

    Relationships:
        source_word: Source word
        target_word: Related/target word

    Relationship Types:
        - synonym: Words with similar meanings (e.g., "happy" ↔ "joyful")
        - antonym: Words with opposite meanings (e.g., "hot" ↔ "cold")
        - derivative: Morphologically related (e.g., "happy" → "happiness")
        - compound: Compound word relationship (e.g., "book" → "bookshelf")
        - hypernym: More general term (e.g., "dog" → "animal")
        - hyponym: More specific term (e.g., "animal" → "dog")
        - related: General semantic relation

    Notes:
        Relationships are directional (source → target).
        Synonym relationships should be bidirectional (created in both directions).
        usage_notes help learners understand when to use one synonym over another.
    """

    __tablename__ = "related_words"

    # Foreign Keys
    source_word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Source word ID"
    )

    target_word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Related/target word ID"
    )

    # Fields
    relationship_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        doc="Type of relationship: synonym, antonym, derivative, compound, hypernym, hyponym, related"
    )

    usage_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Explanation of subtle differences in usage"
    )

    strength: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="Relationship strength (0.0-1.0, for synonyms)"
    )

    # Relationships
    source_word: Mapped["Word"] = relationship(
        "Word",
        foreign_keys=[source_word_id],
        back_populates="related_words_source"
    )

    target_word: Mapped["Word"] = relationship(
        "Word",
        foreign_keys=[target_word_id],
        back_populates="related_words_target"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "source_word_id != target_word_id",
            name="check_no_self_relation"
        ),
        CheckConstraint(
            "strength IS NULL OR (strength >= 0.0 AND strength <= 1.0)",
            name="check_strength_range"
        ),
        CheckConstraint(
            "relationship_type IN ('synonym', 'antonym', 'derivative', 'compound', 'hypernym', 'hyponym', 'related')",
            name="check_relationship_type"
        ),
        Index("idx_related_words_source", "source_word_id"),
        Index("idx_related_words_target", "target_word_id"),
        Index("idx_related_words_source_type", "source_word_id", "relationship_type"),
        Index("idx_related_words_unique", "source_word_id", "target_word_id", "relationship_type", unique=True),
    )

    def __repr__(self) -> str:
        return f"<RelatedWord(id={self.id}, source={self.source_word_id}, target={self.target_word_id}, type='{self.relationship_type}')>"
