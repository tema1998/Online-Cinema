import requests

from fastapi import Depends, APIRouter, HTTPException, Body
from config.settings import settings
from notification_gen_app.api.v1.dependencies import get_user_info
from notification_gen_app.schemas.messages import InstantMessageRequest, WelcomeMessageRequest, \
    WelcomeLinkMessageRequest
from notification_gen_app.services.messages import MessageService, MessageSendException, get_message_service
from notification_gen_app.utils.short_links import generate_confirmation_link
from uuid import UUID

router = APIRouter()


# Endpoint for creating an instant message
@router.post("/instant_messages/{content_id}/")
async def create_instant_message(
        content_id: UUID,
        message: InstantMessageRequest,
        message_service: MessageService = Depends(get_message_service)
):
    try:
        result = await message_service.send_single_message(content_id, message, 'email', settings.instant_message_queue)
        return result
    except MessageSendException as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Endpoint for sending a welcome message
@router.post("/welcome_message/")
async def create_welcome_message(
        message: WelcomeMessageRequest,
        message_service: MessageService = Depends(get_message_service),
        user_info: dict = Depends(get_user_info)
):
    try:
        email = user_info.get('email')
        user_id = user_info.get('sub')
        confirmation_link = generate_confirmation_link(user_id, settings.redirect_url, settings.expires_in)

        message_data = message.message_data
        message_data['confirmation_link'] = confirmation_link

        result = await message_service.send_welcome_message(email, message_data, 'email',
                                                            settings.instant_message_queue)
        return result
    except MessageSendException as exception:
        raise HTTPException(status_code=500, detail=str(exception))

# Endpoint send notification for new comment to user's review(UGC-service)
@router.post("/notification_about_new_comment/{review_id}/")
async def create_notification(
        review_id: UUID,
        message_service: MessageService = Depends(get_message_service),
        user_id: str = Body(embed=True)
):
    try:
        url = settings.get_user_info_url
        body = {'user_id': user_id}

        response = requests.post(url, json=body, headers={"X-Request-Id":"RandomRequestId"})

        user_email = response.json().get('email')
        first_name = response.json().get('first_name')
        last_name = response.json().get('last_name')



        result = await message_service.send_notification_about_new_comment(review_id, user_email,
                                                                           {"first_name": first_name,
                                                                            "last_name": last_name},
                                                                           'email', settings.instant_message_queue)
        return result
    except MessageSendException as exception:
        raise HTTPException(status_code=500, detail=str(exception))