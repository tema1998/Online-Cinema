import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status, Request

from schemas.entity import OrderOut, OrderIn
from services.payment_service import PaymentService
from services.token_service import get_user_info
from services.order_service import OrderService, get_order_service
from services.yookassa_service import get_yookassa_service
from services.async_pg_repository import PostgresAsyncRepository

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/create",
    response_model=OrderOut,
    summary="Order creation page.",
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order_data: OrderIn = Body(..., description="Order creation data."),
    user_info: Annotated[dict, Depends(get_user_info)] = None,
    order_service: OrderService = Depends(get_order_service),
    payment_service: PaymentService = Depends(get_yookassa_service),
):
    # Create order
    order = await order_service.create_order(order_data.model_dump(), user_info)

    # Create Yookassa payment
    payment_id, payment_url = payment_service.create_payment(
        order_id=order.to_dict()["id"],
        total_price=order.to_dict()["total_price"],
        customer_email=order.to_dict()["user_email"],
    )

    # Update order's payment data
    order = await order_service.update_order_payment_data(
        order, payment_id, payment_url
    )

    # Convert the saved user data to the response model
    return OrderOut(**order.to_dict())


@router.post(
    "/payment-notification",
    summary="Catch notification from payment service about status of user's payment.",
    status_code=status.HTTP_200_OK,
)
async def catch_payment_notification(
    request: Request, payment_service: PaymentService = Depends(get_yookassa_service)
):
    json_request = await request.json()
    result = await payment_service.process_payment(json_request)

@router.post(
    "/change-status",
    summary="Changes the order status.",
    status_code=status.HTTP_200_OK,
)
async def order_status_change(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
):
    print(Request)
    json_request = await request.json()
    print(json_request)
    order_id = json_request["order_id"]
    order_status = json_request["order_status"]
    await order_service.update_order_status(order_id, order_status)
