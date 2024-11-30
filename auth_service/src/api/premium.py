import logging

from fastapi import APIRouter, Depends, Body, status, HTTPException

from src.services.user_service import UserService, get_user_service
from src.schemas.entity import SetUserPremiumRequest

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()


@router.post(
    "/set-premium-status",
    summary="Get user's info by access token.",
    status_code=status.HTTP_200_OK,
)
async def set_premium_status(
    user_service: UserService = Depends(get_user_service),
    user: SetUserPremiumRequest = Body(..., description="User's ID"),
) -> bool:
    """
    Set user's status - premium.
    """
    result = await user_service.set_premium(user_id=user.user_id)
    return result
