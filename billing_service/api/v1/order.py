import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status, Request

from schemas.entity import OrderPremiumOut, OrderPremiumIn, OrderFilmOut, OrderFilmIn, CheckUserFilmIn, CheckUserFilmOut
from services.payment_service import PaymentService
from services.token_service import get_user_info
from services.order_service import OrderService, get_order_service
from services.yookassa_service import get_yookassa_service
from services.async_pg_repository import PostgresAsyncRepository

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/order-premium",
    response_model=OrderPremiumOut,
    summary="Handler for creating a purchase order for a premium.",
    status_code=status.HTTP_201_CREATED,
)
async def create_order_premium(
    order_data: OrderPremiumIn = Body(
        ..., description="Data for creating a purchase order for a premium."),
    user_info: Annotated[dict, Depends(get_user_info)] = None,
    order_service: OrderService = Depends(get_order_service),
    payment_service: PaymentService = Depends(get_yookassa_service),
):
    # Create order
    order = await order_service.create_order_premium(order_data.model_dump(), user_info)

    # Create Yookassa payment
    payment_id, payment_url = payment_service.create_payment(
        order_id=order.to_dict()["id"],
        total_price=order.to_dict()["total_price"],
        customer_email=order.to_dict()["user_email"],
        order_type="premium"
    )

    # Update order's payment data
    order = await order_service.update_payment_data(
        order, payment_id, payment_url
    )

    # Convert the saved user data to the response model
    return OrderPremiumOut(**order.to_dict())


@router.post(
    "/order-film",
    response_model=OrderFilmOut,
    summary="Handler for creating a purchase order for a film.",
    status_code=status.HTTP_201_CREATED,
)
async def create_order_film(
    order_data: OrderFilmIn = Body(
        ..., description="Data for creating a purchase order for a film."),
    user_info: Annotated[dict, Depends(get_user_info)] = None,
    order_service: OrderService = Depends(get_order_service),
    payment_service: PaymentService = Depends(get_yookassa_service),
):
    # Create order
    order = await order_service.create_order_film(order_data.model_dump(), user_info)

    # Create Yookassa payment
    payment_id, payment_url = payment_service.create_payment(
        order_id=order.to_dict()["id"],
        total_price=order.to_dict()["price"],
        customer_email=order.to_dict()["user_email"],
        order_type="film"
    )

    # Update order's payment data
    order = await order_service.update_payment_data(
        order, payment_id, payment_url
    )

    # Convert the saved user data to the response model
    return OrderFilmOut(**order.to_dict())


@router.post(
    "/payment-notification",
    summary="Catch notification from payment service about status of user's payment.",
    status_code=status.HTTP_200_OK,
)
async def catch_payment_notification(
    request: Request, payment_service: PaymentService = Depends(get_yookassa_service)
):
    json_request = await request.json()
    # Process a premium purchase order.
    if json_request["object"]["metadata"]["order_type"] == "premium":
        await payment_service.process_premium_order_payment(json_request)

    # Process a movie purchase order.
    elif json_request["object"]["metadata"]["order_type"] == "film":
        await payment_service.process_film_order_payment(json_request)


@router.post(
    "/change-status",
    summary="Changes the order status.",
    status_code=status.HTTP_200_OK,
)
async def order_status_change(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
):
    json_request = await request.json()

    order_type = json_request["order_type"]
    order_id = json_request["order_id"]
    order_status = json_request["order_status"]
    await order_service.update_order_status(order_type, order_id, order_status)


@router.post(
    "/check-user-film",
    summary="Check whether the user bought film.",
    status_code=status.HTTP_200_OK,
)
async def check_user_film(
    order_data: CheckUserFilmIn = Body(
        ..., description="Data for checking whether the user bought film."),
    order_service: OrderService = Depends(get_order_service),
):
    order_data_dict = order_data.model_dump()
    user_id = order_data_dict["user_id"]
    film_id = order_data_dict["film_id"]

    result = await order_service.check_whether_user_bought_film(user_id, film_id)

    return CheckUserFilmOut(result=result)
