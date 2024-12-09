import http
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status, Request, HTTPException

from schemas.entity import PurchaseManageOut, PurchaseManageIn
from services.manage_service import ManageService, get_manage_service
from services.token_service import get_user_info

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/set-premium-purchase-settings",
    response_model=PurchaseManageOut,
    summary="Handler to set a premium purchase settings.",
    status_code=status.HTTP_201_CREATED,
)
async def set_premium_purchase_settings(
    premium_settings_data: PurchaseManageIn = Body(
    ..., description="Data to set a premium purchase settings."),
    user_info: Annotated[dict, Depends(get_user_info)] = None,
    manage_service: ManageService = Depends(get_manage_service),
):

    if not user_info["is_superuser"]:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="This action only for administrator.",
        )

    premium_purchase_manage = await manage_service.create_premium_purchase_manage_model(premium_settings_data)

    return PurchaseManageOut(**premium_purchase_manage.to_dict())

@router.post(
    "/set-film-purchase-settings",
    response_model=PurchaseManageOut,
    summary="Handler to set a film purchase settings.",
    status_code=status.HTTP_201_CREATED,
)
async def set_premium_purchase_settings(
    film_settings_data: PurchaseManageIn = Body(
    ..., description="Data to set a film purchase settings."),
    user_info: Annotated[dict, Depends(get_user_info)] = None,
    manage_service: ManageService = Depends(get_manage_service),
):

    if not user_info["is_superuser"]:
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="This action only for administrator.",
        )

    film_purchase_manage = await manage_service.create_film_purchase_manage_model(film_settings_data)

    return PurchaseManageOut(**film_purchase_manage.to_dict())