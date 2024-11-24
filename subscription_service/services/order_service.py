from fastapi import HTTPException, status

from core.config import config
from models.entity import Order, Subscription
from schemas.entity import OrderIn, OrderCreate
from services.async_pg_repository import PostgresAsyncRepository


class OrderService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_order(self, order_data: dict, user_info:dict) -> Order:
        #TODO Create payment URL

        #Checking whether the user has a subscription
        #TODO Add check whether the user has a subscription (from Auth service)
            #TODO Если не опалчено - вернуть ссылку на оплату, если есть подписка - сказать что есть

        #Get subscription's price.
        subscription = await self.db.fetch_by_query_first(Subscription, 'id', order_data['subscription_id'])
        if subscription:
            subscription_price = subscription.to_dict()['price']
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subscription with ID={order_data['subscription_id']} doesn't exist."
            )

        order = OrderCreate(order_status='Processed', user_id=user_info['id'], user_email=user_info['email'],
                            total_price=subscription_price*order_data['number_of_month'], **order_data)

        order_orm = Order(**order.model_dump())
        order_db = await self.db.insert(order_orm)

        return order_db

    async def update_order_payment_data(self, order: Order, payment_id: str, payment_url: str) -> Order:

        order.payment_id = payment_id
        order.payment_url = payment_url

        updated_order = await self.db.update(order)

        return updated_order


def get_order_service() -> OrderService:
    return OrderService(
        db=PostgresAsyncRepository(dsn=config.dsn),
    )