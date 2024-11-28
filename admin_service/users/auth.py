import http
import json
import uuid
import logging
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from config import settings
from users.token_services import decode_token

User = get_user_model()
logging.basicConfig(level=logging.INFO)

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {'login': username, 'password': password}
        headers = {'X-Request-Id': str(uuid.uuid4()).replace('-', '')}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            # Decode access token from auth service to get user data.
            user_data = decode_token(data.get('access_token'))

            user, created = User.objects.get_or_create(id=user_data['sub'], )
            user.login = user_data.get('login')
            user.first_name = user_data.get('first_name')
            user.last_name = user_data.get('last_name')
            user.is_staff = user_data.get('is_superuser')
            user.is_active = user_data.get('is_active')

            # Save user model from auth service to django db.
            user.save()
        except Exception as ex:
            logging.info(f"Django auth service exception:{ex}")
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
