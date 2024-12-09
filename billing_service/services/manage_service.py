import http

from fastapi import HTTPException, status
from uuid import uuid4

from core.config import config
from models.entity import OrderPurchasePremium, PremiumPurchaseManagement, OrderPurchaseFilm, FilmPurchaseManagement
from schemas.entity import OrderPremium, OrderFilm, PurchaseManageIn
from services.async_pg_repository import PostgresAsyncRepository


class ManageService:
    def __init__(self, db: PostgresAsyncRepository):
        self.db = db

    async def create_premium_purchase_manage_model(self, premium_purchase_manage_data: PurchaseManageIn) -> PremiumPurchaseManagement:
        """
        Method for creating a premium purchase manage model. This model sets price for premium.
        :param premium_purchase_manage_data:
        :return:
        """

        # Check whether the settings with entered name exist
        settings = await self.db.fetch_by_query_first(PremiumPurchaseManagement, "name", premium_purchase_manage_data.model_dump()['name'])
        if settings:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Settings with this name is already exists.",
            )

        # Check whether the active settings exist
        current_settings = await self.db.fetch_by_query_first(PremiumPurchaseManagement, "is_active", True)

        if current_settings:
            current_settings.is_active = False
            await self.db.update(current_settings)

        premium_purchase_management_model = PremiumPurchaseManagement(
            **premium_purchase_manage_data.model_dump())

        premium_purchase_management = await self.db.insert(premium_purchase_management_model)

        return premium_purchase_management

    async def create_film_purchase_manage_model(self, film_purchase_manage_data: PurchaseManageIn) -> FilmPurchaseManagement:
        """
        Method for creating a film purchase manage model. This model sets price for film.
        :param film_purchase_manage_data:
        :return:
        """

        # Check whether the settings with entered name exist
        settings = await self.db.fetch_by_query_first(FilmPurchaseManagement, "name", film_purchase_manage_data.model_dump()['name'])
        if settings:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Settings with this name is already exists.",
            )

        # Check whether the active settings exist
        current_settings = await self.db.fetch_by_query_first(FilmPurchaseManagement, "is_active", True)

        if current_settings:
            current_settings.is_active = False
            await self.db.update(current_settings)

        film_purchase_management_model = FilmPurchaseManagement(
            **film_purchase_manage_data.model_dump())

        film_purchase_management = await self.db.insert(film_purchase_management_model)

        return film_purchase_management


def get_manage_service() -> ManageService:
    return ManageService(
        db=PostgresAsyncRepository(dsn=config.dsn),
    )
