import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, String, ForeignKey, DECIMAL, INTEGER, ARRAY
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


class Subscription(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "subscriptions"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    price = Column(DECIMAL, nullable=False)
    orders: Mapped[List["Order"]] = relationship(back_populates="subscription")
    permissions = Column(ARRAY(String))

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, name='{self.name}', description='{self.description}')>"


class Order(Base, UUIDMixin, TimeStampedMixin):
    __tablename__ = "orders"

    total_price = Column(DECIMAL, nullable=False)
    status = Column(String(255))
    number_of_month = Column(INTEGER, nullable=False)
    user_id = Column(UUID, nullable=True)
    user_email = Column(String(255), nullable=True)
    payment_url = Column(String(255), nullable=True)
    payment_id = Column(String(255), nullable=True)
    subscription_id: Mapped[UUID] = mapped_column(ForeignKey("subscriptions.id"))
    subscription: Mapped["Subscription"] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order(id={self.id}')>"
