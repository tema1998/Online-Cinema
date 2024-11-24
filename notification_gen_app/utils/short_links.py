from datetime import timedelta

from itsdangerous import URLSafeTimedSerializer

from notification_gen_app.config.settings import settings


def generate_confirmation_link(user_id: str, redirect_url: str, expires_in: timedelta):
    serializer = URLSafeTimedSerializer(settings.secret_key)
    token_expiration = expires_in.total_seconds()
    token = serializer.dumps({
        "user_id": user_id,
        "redirect_url": redirect_url,
        "expires_in": token_expiration
    }, salt="email-confirmation-salt")
    return f"{settings.confirmation_base_url}/{token}"