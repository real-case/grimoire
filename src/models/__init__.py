"""SQLAlchemy models and base configuration."""
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Type annotation for SQLAlchemy 2.0
    __abstract__ = True

    # Common fields for all models
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# Import all models here for Alembic autogenerate
from src.models.word import Word  # noqa: E402, F401
from src.models.definition import Definition  # noqa: E402, F401
from src.models.usage_example import UsageExample  # noqa: E402, F401
from src.models.phonetic import PhoneticRepresentation  # noqa: E402, F401
from src.models.grammar import GrammaticalInformation  # noqa: E402, F401
from src.models.learning_metadata import LearningMetadata  # noqa: E402, F401
from src.models.related_word import RelatedWord  # noqa: E402, F401
