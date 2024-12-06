import json
from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID


class PaymentService(ABC):
    @abstractmethod
    async def create_payment(
        self, order_id: UUID, total_price: float, customer_email: str, order_type: str
    ) -> Optional[Any]:
        """
        Method for creating payment.
        :param order_type:
        :param order_id:
        :param total_price:
        :param customer_email:
        :return: Payment ID, Payment URL.
        """
        pass

    @abstractmethod
    async def process_premium_order_payment(self, request: json) -> Optional[Any]:
        """
        Method for processing of response from payment service.
        :param request:
        """
        pass

    @abstractmethod
    async def process_film_order_payment(self, request: json) -> Optional[Any]:
        """
        Method for processing of response from payment service.
        :param request:
        """
        pass
