import uuid
from uuid import UUID

from pydantic_settings import BaseSettings
from yookassa import Configuration, Payment
from core.config import config
from models.entity import Order, Subscription
from services.async_pg_repository import PostgresAsyncRepository
from services.payment_service import PaymentService

Configuration.account_id = config.yookassa_shop_id
Configuration.secret_key = config.yookassa_secret_key

class YookassaService(PaymentService):
    def __init__(self, config: BaseSettings, db: PostgresAsyncRepository):
        self.db = db
        self.config = config
        Configuration.account_id = self.config.yookassa_shop_id
        Configuration.secret_key = self.config.yookassa_secret_key

    #TODO: use user's email
    def create_payment(self, order_id: UUID, total_price: float, customer_email: str) -> tuple:
        key=str(uuid.uuid4())
        payment = Payment.create(
            {
                "amount": {
                    "value": total_price,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.config.yookassa_return_url
                },
                "capture": True,
                "description": f"Order #{order_id}",
                "metadata": {
                    'orderID': f'{order_id}'
                }
            },
            key
        )
        return payment.id, payment.confirmation.confirmation_url

    async def process_payment(self, request:dict):

        order = await self.db.fetch_by_query_first(Order, 'payment_id', request["object"]["id"])
        subscription = await self.db.fetch_by_query_first(Subscription, 'id', order.subscription_id)

        data_for_worker = {"order_id": order.id, "user_id": order.user_id, "email": order.user_email,
                           "subscription_id": order.subscription_id, "subscription_name": subscription.name,
                           "subscription_permissions": subscription.permissions}

        if request["event"] == "payment.succeeded":
            pass
            #TODO: Call worker.


        elif request["event"] == "payment.canceled":
            pass
            #TODO: Call worker

        else:
            pass
            #TODO: Return error.


def get_yookassa_service() -> YookassaService:
    return YookassaService(
        config=config,
        db=PostgresAsyncRepository(dsn=config.dsn)
    )