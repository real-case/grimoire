"""PhoneticRepresentation model - Pronunciation information for a word."""
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class PhoneticRepresentation(Base):
    """
    Pronunciation information for a word.

    Attributes:
        word_id: Foreign key to parent word (one-to-one)
        ipa_transcription: IPA phonetic transcription
        audio_url: URL to pronunciation audio (future feature)

    Relationships:
        word: Parent word (1:1)
    """

    __tablename__ = "phonetic_representations"

    # Foreign Keys (one-to-one relationship with Word)
    word_id: Mapped[UUID] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        doc="Parent word ID (one-to-one relationship)"
    )

    # Fields
    ipa_transcription: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="IPA phonetic transcription (e.g., /ˈwɜːrd/)"
    )

    audio_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="URL to pronunciation audio (future feature)"
    )

    # Relationships
    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="phonetic"
    )

    # Table constraints
    __table_args__ = (
        Index("idx_phonetic_word_id", "word_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<PhoneticRepresentation(id={self.id}, word_id={self.word_id}, ipa='{self.ipa_transcription}')>"
