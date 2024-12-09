import json

from aiohttp import ClientSession
from fastapi import HTTPException
from http import HTTPStatus

from core.config import config


async def check_whether_user_bought_film(user_id: str, film_id: str) -> bool:
    """
    Function make request to Billing service and check whether the user bought film.
    :param user_id:
    :param film_id:
    :return: bool
    """
    body = {
        "film_id": film_id,
        "user_id": user_id,
    }

    # try:
    # Make async request to Billing service
    async with ClientSession() as session:
        async with session.post(
                url=config.billing_service_url +
            config.billing_service_check_whether_user_bought_film,
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
        ) as response:
            response_json = await response.json()
            return response_json['result']

    # except Exception as e:
    #     return False


async def check_user_permission_for_film(user: dict, film: dict) -> bool:
    """
    Function check is film premium or not. Then check is user has a premium status.
    :param user:
    :param film:
    :return: bool
    """
    if film["premium"]:
        # Check whether the user bought premium.
        if user["is_premium"]:
            return True
        else:
            # Check whether the user bought film.
            result = await check_whether_user_bought_film(user['sub'], film['id'])
            return result
    return True
