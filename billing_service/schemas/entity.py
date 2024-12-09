from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class OrderPremiumIn(BaseModel):
    number_of_month: int = Field(None, gt=0)


class OrderPremium(OrderPremiumIn):
    total_price: float = Field(None, gt=0)
    status: str
    user_id: UUID
    user_email: EmailStr
    premium_purchase_management_id: UUID


class OrderPremiumOut(OrderPremium):
    created_at: datetime
    payment_url: str


class OrderFilmIn(BaseModel):
    film_id: UUID = Field(None)


class OrderFilm(OrderFilmIn):
    price: float = Field(None, gt=0)
    status: str
    user_id: UUID
    film_id: UUID
    user_email: EmailStr
    film_purchase_management_id: UUID


class OrderFilmOut(OrderFilm):
    created_at: datetime
    payment_url: str


class CheckUserFilmIn(BaseModel):
    film_id: UUID = Field(None)
    user_id: UUID = Field(None)


class CheckUserFilmOut(BaseModel):
    result: bool


class PurchaseManageIn(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    is_active: bool = True


class PurchaseManageOut(PurchaseManageIn):
    pass
