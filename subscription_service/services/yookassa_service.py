from uuid import UUID

from pydantic_settings import BaseSettings
from yookassa import Configuration, Payment
from core.config import config
from services.payment_service import PaymentService

Configuration.account_id = config.yookassa_shop_id
Configuration.secret_key = config.yookassa_secret_key

class YookassaService(PaymentService):
    def __init__(self, config: BaseSettings):
        self.config = config
        Configuration.account_id = self.config.yookassa_shop_id
        Configuration.secret_key = self.config.yookassa_secret_key
    #TODO: use user's email
    def create_payment(self, order_id: UUID, total_price: float, customer_email: str) -> tuple:
        payment = Payment.create(
            {
                "amount": {
                    "value": total_price,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://merchant-site.ru/return_url"
                },
                "capture": True,
                "description": f"Order #{order_id}",
                "metadata": {
                    'orderID': f'{order_id}'
                }
            }
        )
        return payment.id, payment.confirmation.confirmation_url

def get_yookassa_service() -> YookassaService:
    return YookassaService(
        config=config
    )