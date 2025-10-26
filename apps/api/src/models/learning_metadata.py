"""LearningMetadata model - Learning-specific metadata for EFL students."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import ARRAY, CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class LearningMetadata(Base):
    """
    Learning-specific metadata for EFL students.

    Attributes:
        word_id: Foreign key to parent word (one-to-one)
        difficulty_level: CEFR level (A1, A2, B1, B2, C1, C2)
        cefr_level: Specific CEFR level (same as difficulty_level, for clarity)
        frequency_rank: Word rank by frequency (1 = most common)
        frequency_band: Band label (e.g., "top-1000", "top-5000", "rare")
        style_tags: Array of style tags (e.g., ["formal", "technical"])

    Relationships:
        word: Parent word (1:1)

    Notes:
        CEFR (Common European Framework of Reference) is the standard for EFL proficiency.
        Frequency data helps learners prioritize essential vocabulary.
        Style tags help learners use words in appropriate contexts.
    """

    __tablename__ = "learning_metadata"

    # Foreign Keys (one-to-one relationship with Word)
    word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        doc="Parent word ID (one-to-one relationship)"
    )

    # Fields
    difficulty_level: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        doc="CEFR level (A1, A2, B1, B2, C1, C2)"
    )

    cefr_level: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True,
        doc="Specific CEFR level (same as difficulty_level, for clarity)"
    )

    frequency_rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        doc="Word rank by frequency (1 = most common)"
    )

    frequency_band: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Band label (e.g., 'top-1000', 'top-5000', 'rare')"
    )

    style_tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        doc="Array of style tags (e.g., ['formal', 'technical'])"
    )

    # Relationships
    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="learning_metadata"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "frequency_rank IS NULL OR frequency_rank > 0",
            name="check_frequency_rank_positive"
        ),
        CheckConstraint(
            "cefr_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2') OR cefr_level IS NULL",
            name="check_cefr_level"
        ),
        CheckConstraint(
            "difficulty_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2') OR difficulty_level IS NULL",
            name="check_difficulty_level"
        ),
        CheckConstraint(
            "frequency_band IN ('top-100', 'top-1000', 'top-5000', 'top-10000', 'rare', 'very-rare') OR frequency_band IS NULL",
            name="check_frequency_band"
        ),
        Index("idx_learning_metadata_word_id", "word_id", unique=True),
        Index("idx_learning_metadata_frequency_rank", "frequency_rank"),
        Index("idx_learning_metadata_difficulty_level", "difficulty_level"),
    )

    def __repr__(self) -> str:
        return f"<LearningMetadata(id={self.id}, word_id={self.word_id}, cefr_level='{self.cefr_level}', frequency_rank={self.frequency_rank})>"
