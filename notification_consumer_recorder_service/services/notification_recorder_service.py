from sqlalchemy.ext.asyncio import AsyncSession

from notification_consumer_recorder_service.config.postgresql import get_db_session
from notification_consumer_recorder_service.models.notification_models import Notifications
from notification_consumer_recorder_service.services.postgresql_base import BaseService


class NotificationService(BaseService[Notifications]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Notifications, db_session)


# Dependency injection for NotificationService
async def get_notification_service() -> NotificationService:
    db_session: AsyncSession = await get_db_session()
    return NotificationService(db_session)
