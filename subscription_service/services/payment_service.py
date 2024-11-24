from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID


class PaymentService(ABC):
    @abstractmethod
    async def create_payment(self, order_id: UUID, total_price: float, customer_email: str) -> Optional[Any]:
        """
        Method for creating payment
        :param order_id:
        :param total_price:
        :param customer_email:
        :return: Payment ID, Payment URL.
        """
        pass