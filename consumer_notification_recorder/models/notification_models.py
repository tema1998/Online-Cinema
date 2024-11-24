import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from consumer_notification_recorder.config.postgresql import Base


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), unique=False, nullable=True)
    recipient = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    message_transfer = Column(String, nullable=False)

