from fastapi import HTTPException, status
from uuid import uuid4

from core.config import config
from models.entity import Order, Premium
from schemas.entity import OrderCreate
from services.async_pg_repository import PostgresAsyncRepository


class OrderService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_order(self, order_data: dict, user_info: dict) -> Order:
        """
        Method for creating order.
        :param order_data:
        :param user_info:
        :return:
        """

        # Get active premium model. There is only one active premium with actual price.
        premium = await self.db.fetch_by_query_first(
            Premium, "is_active", True
        )

        # Get premium's price.
        if premium:
            premium_dict = premium.to_dict()
            premium_id, premium_price = premium_dict["id"], premium_dict["price"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"There is no active premium subscriptions.",
            )

        # Validate order data through OrderCreate pydantic model.
        order = OrderCreate(
            status="Processed",
            user_id=user_info["id"],
            user_email=user_info["email"],
            total_price=premium_price * order_data["number_of_month"],
            premium_id=premium_id,
            **order_data,
        )

        # Create ORM Order model.
        order_orm = Order(**order.model_dump())
        # Insert order to DB.
        order_db = await self.db.insert(order_orm)

        return order_db

    async def update_order_payment_data(
        self, order: Order, payment_id: str, payment_url: str
    ) -> Order:
        """
        Method for updating payment data of order, after receiving a response from payment service.
        :param order:
        :param payment_id:
        :param payment_url:
        :return:
        """
        # Set payment_id and payment_url from payment service.
        order.payment_id = payment_id
        order.payment_url = payment_url

        # Update order in DB.
        updated_order = await self.db.update(order)

        return updated_order

    async  def update_order_status(self, order_id: str, status: str) -> Order:
        """
        Method for updating status of order.
        :param order_id:
        :param status:
        :return:
        """
        order: Order = await self.db.fetch_by_id(Order, order_id)
        # Set new status of order.
        order.status = status

        # Update order in DB.
        updated_order = await self.db.update(order)

        return updated_order


def get_order_service() -> OrderService:
    return OrderService(
        db=PostgresAsyncRepository(dsn=config.dsn),
    )
