from sqlalchemy.ext.asyncio import AsyncSession

from consumer_notification_recorder.config.postgresql import get_db_session
from consumer_notification_recorder.models.notification_models import Notifications
from consumer_notification_recorder.services.postgresql_base import BaseService


class NotificationService(BaseService[Notifications]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Notifications, db_session)


# Dependency injection for NotificationService
async def get_notification_service() -> NotificationService:
    db_session: AsyncSession = await get_db_session()
    return NotificationService(db_session)
