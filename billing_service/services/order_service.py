from fastapi import HTTPException, status
from uuid import uuid4

from core.config import config
from models.entity import OrderPurchasePremium, PremiumPurchaseManagement, OrderPurchaseFilm, FilmPurchaseManagement
from schemas.entity import OrderPremium, OrderFilm
from services.async_pg_repository import PostgresAsyncRepository


class OrderService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_order_premium(self, order_data: dict, user_info: dict) -> OrderPurchasePremium:
        """
        Method for creating a premium purchase order.
        :param order_data:
        :param user_info:
        :return:
        """

        # Get active premium model. There is only one active premium with actual price.
        premium_purchase_management = await self.db.fetch_by_query_first(
            PremiumPurchaseManagement, "is_active", True
        )

        # Get premium's price.
        if premium_purchase_management:
            premium_purchase_management_dict = premium_purchase_management.to_dict()
            premium_purchase_management_id, premium_purchase_management_price = (premium_purchase_management_dict["id"],
                                                                                 premium_purchase_management_dict["price"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"There is no active premium subscriptions.",
            )

        # Validate order data through OrderPremium pydantic model.
        order = OrderPremium(
            status="Processed",
            user_id=user_info["id"],
            user_email=user_info["email"],
            total_price=premium_purchase_management_price *
            order_data["number_of_month"],
            premium_purchase_management_id=premium_purchase_management_id,
            number_of_month=order_data["number_of_month"]
        )

        # Create ORM OrderPurchasePremium model.
        order_orm = OrderPurchasePremium(**order.model_dump())
        # Insert order to DB.
        order_db = await self.db.insert(order_orm)

        return order_db

    async def create_order_film(self, order_data: dict, user_info: dict) -> OrderPurchaseFilm:
        """
        Method for creating a film purchase order.
        :param order_data:
        :param user_info:
        :return:
        """

        # Get active premium model. There is only one active premium with actual price.
        film_purchase_management = await self.db.fetch_by_query_first(
            FilmPurchaseManagement, "is_active", True
        )

        # Get premium's price.
        if film_purchase_management:
            film_purchase_management_dict = film_purchase_management.to_dict()
            film_purchase_management_id, film_purchase_management_price = (film_purchase_management_dict["id"],
                                                                           film_purchase_management_dict["price"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unfortunately, this film is temporarily unavailable for purchase.",
            )

        # Validate order data through OrderPremium pydantic model.
        order = OrderFilm(
            status="Processed",
            film_id=order_data["film_id"],
            user_id=user_info["id"],
            user_email=user_info["email"],
            price=film_purchase_management_price,
            film_purchase_management_id=film_purchase_management_id,
        )

        # Create ORM OrderPurchasePremium model.
        order_orm = OrderPurchaseFilm(**order.model_dump())
        # Insert order to DB.
        order_db = await self.db.insert(order_orm)

        return order_db

    async def update_payment_data(
        self, order: OrderPurchasePremium | OrderPurchaseFilm, payment_id: str, payment_url: str
    ) -> OrderPurchasePremium | OrderPurchaseFilm:
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

    async def update_order_status(self, order_type: str, order_id: str, order_status: str) -> OrderPurchasePremium | OrderPurchaseFilm:
        """
        Method for updating status of order.
        :param order_status:
        :param order_type:
        :param order_id:
        :return:
        """
        if order_type == "premium":
            order = await self.db.fetch_by_id(OrderPurchasePremium, order_id)
        elif order_type == "film":
            order = await self.db.fetch_by_id(OrderPurchaseFilm, order_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown order type.",
            )

        # Set new status of order.
        order.status = order_status

        # Update order in DB.
        updated_order = await self.db.update(order)

        return updated_order


def get_order_service() -> OrderService:
    return OrderService(
        db=PostgresAsyncRepository(dsn=config.dsn),
    )
