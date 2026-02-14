from datetime import datetime

from sqlalchemy import (
    Integer,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
)

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    # --- Ограничение диапазона grade ---
    __table_args__ = (
        CheckConstraint(
            "grade BETWEEN 1 AND 5",
            name="grade_range_check"
        ),
    )

    # --- Колонки ---
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    comment_date: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now,              # Python-side
        server_default=func.now()          # DB-side
    )

    grade: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true"
    )

    # --- Валидация в Python ---
    @validates("grade")
    def validate_grade(self, key, value):
        if not (1 <= value <= 5):
            raise ValueError("Grade must be between 1 and 5")
        return value
