import logging
import uuid
from uuid import UUID

from core.config import config
from models.entity import Order
from pydantic_settings import BaseSettings
from services.async_pg_repository import PostgresAsyncRepository
from services.auth_service import AuthService
from services.message_service import get_publisher_service
from services.payment_service import PaymentService
from yookassa import Configuration, Payment

Configuration.account_id = config.yookassa_shop_id
Configuration.secret_key = config.yookassa_secret_key


class YookassaService(PaymentService):
    def __init__(self, config: BaseSettings, db: PostgresAsyncRepository):
        self.db = db
        self.config = config
        self.auth_service = AuthService()
        Configuration.account_id = self.config.yookassa_shop_id
        Configuration.secret_key = self.config.yookassa_secret_key

    def create_payment(
        self, order_id: UUID, total_price: float, customer_email: str
    ) -> tuple:
        """
        Method for creating payment in Yookassa service.
        :param order_id:
        :param total_price:
        :param customer_email:
        :return:
        """

        key = str(uuid.uuid4())

        payment = Payment.create(
            {
                "amount": {"value": total_price, "currency": "RUB"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.config.yookassa_return_url,
                },
                "capture": True,
                "description": f"Order #{order_id}",
                "metadata": {"orderID": f"{order_id}"},
            },
            key,
        )
        return payment.id, payment.confirmation.confirmation_url

    async def process_payment(self, request: dict):
        """
        Method for processing of response from Yookassa service
        :param request:
        :return:
        """

        order = await self.db.fetch_by_query_first(
            Order, "payment_id", request["object"]["id"]
        )

        data = {
            "order_id": order.id,
            "user_id": order.user_id,
            "email": order.user_email,
            "number_of_month": order.number_of_month,
            "created_at": order.created_at
        }

        publisher = await get_publisher_service()
        if request["event"] == "payment.succeeded":
            # Calling worker to
            # (i) set premium for user in Auth service;
            # (ii) save status 'Success' to Billing DB
            # (iii) send to user notification about successful payment
            await publisher.send_message(data, routing_key=config.billing_premium_subscription_success_queue)


        elif request["event"] == "payment.canceled":
            # Calling worker to
            # (i) save status 'Failed' to Billing DB
            # (iii) send to user notification about failed payment
            await publisher.send_message(data, routing_key=config.billing_premium_subscription_fail_queue)

        else:
            logging.info(f"Unknown event: {request['event']}")



def get_yookassa_service() -> YookassaService:
    return YookassaService(config=config, db=PostgresAsyncRepository(dsn=config.dsn))
