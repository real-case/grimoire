"""GrammaticalInformation model - Grammatical metadata and word forms."""
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class GrammaticalInformation(Base):
    """
    Grammatical metadata and word forms.

    Attributes:
        word_id: Foreign key to parent word (one-to-one)
        part_of_speech: Primary part of speech (if unambiguous)
        plural_form: Plural form for nouns (e.g., "children" for "child")
        verb_base: Base form (infinitive)
        verb_past_simple: Past simple tense
        verb_past_participle: Past participle
        verb_present_participle: Present participle (-ing form)
        verb_third_person: 3rd person singular present
        adj_comparative: Comparative form (e.g., "better")
        adj_superlative: Superlative form (e.g., "best")
        irregular_forms_json: Additional irregular forms as key-value pairs

    Relationships:
        word: Parent word (1:1)

    Notes:
        Only populate fields relevant to the word's part of speech.
        Irregular forms are especially important for learners.
        Regular forms (e.g., "walk" → "walked") can be omitted if they follow standard rules.
    """

    __tablename__ = "grammatical_information"

    # Foreign Keys (one-to-one relationship with Word)
    word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        doc="Parent word ID (one-to-one relationship)"
    )

    # Fields
    part_of_speech: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Primary part of speech (if unambiguous)"
    )

    # Noun forms
    plural_form: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Plural form for nouns (e.g., 'children' for 'child')"
    )

    # Verb forms
    verb_base: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Base form (infinitive)"
    )

    verb_past_simple: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Past simple tense"
    )

    verb_past_participle: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Past participle"
    )

    verb_present_participle: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Present participle (-ing form)"
    )

    verb_third_person: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="3rd person singular present"
    )

    # Adjective forms
    adj_comparative: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Comparative form (e.g., 'better')"
    )

    adj_superlative: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Superlative form (e.g., 'best')"
    )

    # Additional irregular forms
    irregular_forms_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Additional irregular forms as key-value pairs"
    )

    # Relationships
    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="grammatical_info"
    )

    # Table constraints
    __table_args__ = (
        Index("idx_grammatical_word_id", "word_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<GrammaticalInformation(id={self.id}, word_id={self.word_id}, part_of_speech='{self.part_of_speech}')>"
