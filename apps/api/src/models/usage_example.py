"""UsageExample model - Example sentences demonstrating word usage."""
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


class UsageExample(Base):
    """
    Example sentences demonstrating word usage.

    Attributes:
        definition_id: Foreign key to parent definition
        example_text: Example sentence
        context_type: Context category (e.g., "academic", "casual", "business")
        order_index: Display order

    Relationships:
        definition: Parent definition
    """

    __tablename__ = "usage_examples"

    # Foreign Keys
    definition_id: Mapped[UUID] = mapped_column(
        ForeignKey("definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Parent definition ID"
    )

    # Fields
    example_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Example sentence (5-300 characters)"
    )

    context_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        doc="Context category (e.g., 'academic', 'casual', 'business')"
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Display order (1, 2, 3...)"
    )

    # Relationships
    definition: Mapped["Definition"] = relationship(
        "Definition",
        back_populates="usage_examples"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "order_index > 0",
            name="check_order_index_positive"
        ),
        CheckConstraint(
            "length(example_text) >= 5 AND length(example_text) <= 300",
            name="check_example_text_length"
        ),
        Index("idx_usage_examples_definition_id", "definition_id"),
        Index("idx_usage_examples_definition_order", "definition_id", "order_index"),
    )

    def __repr__(self) -> str:
        return f"<UsageExample(id={self.id}, definition_id={self.definition_id}, order={self.order_index})>"
