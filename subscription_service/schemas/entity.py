from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class OrderIn(BaseModel):
    number_of_month: int = Field(None, gt=0)
    subscription_id: UUID

class OrderCreate(OrderIn):
    total_price: float = Field(None, gt=0)
    order_status: str
    user_id: UUID
    user_email: EmailStr

class OrderOut(OrderCreate):
    id: UUID
    created_at: datetime
    payment_url: str
