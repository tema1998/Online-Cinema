from fastapi import HTTPException, status

from core.config import config
from models.entity import Order, Subscription
from schemas.entity import OrderCreate
from services.async_pg_repository import PostgresAsyncRepository


class OrderService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_order(self, order_data: dict, user_info:dict) -> Order:
        """
        Method for creating order.
        :param order_data:
        :param user_info:
        :return:
        """

        # Get subscription.
        subscription = await self.db.fetch_by_query_first(Subscription, 'id', order_data['subscription_id'])

        # Get subscription's price.
        if subscription:
            subscription_price = subscription.to_dict()['price']
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subscription with ID={order_data['subscription_id']} doesn't exist."
            )

        # Validate order data through OrderCreate pydantic model.
        order = OrderCreate(status='Processed', user_id=user_info['id'], user_email=user_info['email'],
                            total_price=subscription_price*order_data['number_of_month'], **order_data)

        # Create ORM Order model.
        order_orm = Order(**order.model_dump())
        # Insert order to DB.
        order_db = await self.db.insert(order_orm)

        return order_db

    async def update_order_payment_data(self, order: Order, payment_id: str, payment_url: str) -> Order:
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


def get_order_service() -> OrderService:
    return OrderService(
        db=PostgresAsyncRepository(dsn=config.dsn),
    )