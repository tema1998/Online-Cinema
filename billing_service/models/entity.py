import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, String, ForeignKey, DECIMAL, INTEGER, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.db_utils import Base


class TimeStampedMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UUIDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    def to_dict(self) -> dict:
        """Convert the instance to a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class PremiumPurchaseManagement(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "premiums_purchase_management"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    price = Column(DECIMAL, nullable=False)
    orders: Mapped[List["OrderPurchasePremium"]] = relationship(
        back_populates="premium_purchase_management")
    is_active = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Premium purchase management (id='{self.id}', name='{self.name}', price='{self.price}')>"


class OrderPurchasePremium(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "orders_premium"

    total_price = Column(DECIMAL, nullable=False)
    status = Column(String(255))
    number_of_month = Column(INTEGER, nullable=False)
    user_id = Column(UUID, nullable=True)
    user_email = Column(String(255), nullable=True)
    payment_url = Column(String(255), nullable=True)
    payment_id = Column(String(255), nullable=True)
    premium_purchase_management_id: Mapped[UUID] = mapped_column(
        ForeignKey("premiums_purchase_management.id"))
    premium_purchase_management: Mapped["PremiumPurchaseManagement"] = relationship(
        back_populates="orders")

    def __repr__(self) -> str:
        return f"<Premium purchase order(id='{self.id}')>"


class FilmPurchaseManagement(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "films_purchase_management"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    price = Column(DECIMAL, nullable=False)
    orders: Mapped[List["OrderPurchaseFilm"]] = relationship(
        back_populates="film_purchase_management")
    is_active = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Film purchase management (id='{self.id}', name='{self.name}', price='{self.price}')>"


class OrderPurchaseFilm(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "orders_film"

    price = Column(DECIMAL, nullable=False)
    status = Column(String(255))
    user_id = Column(UUID, nullable=True)
    user_email = Column(String(255), nullable=True)
    film_id = Column(UUID, nullable=False)
    payment_url = Column(String(255), nullable=True)
    payment_id = Column(String(255), nullable=True)
    film_purchase_management_id: Mapped[UUID] = mapped_column(
        ForeignKey("films_purchase_management.id"))
    film_purchase_management: Mapped["FilmPurchaseManagement"] = relationship(
        back_populates="orders")

    def __repr__(self) -> str:
        return f"<Film purchase order(id='{self.id}')>"
