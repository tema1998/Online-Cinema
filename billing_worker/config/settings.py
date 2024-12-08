from base_config.settings import BaseProjectSettings
import os


class Settings(BaseProjectSettings):
    auth_service_url: str = os.getenv(
        "AUTH_SERVICE_URL", "http://auth_service:8081/")
    auth_service_set_premium_user: str = os.getenv("AUTH_SERVICE_SET_PREMIUM_HANDLER",
                                                   "api/v1/premium/set-premium-status")
    billing_service_url: str = os.getenv(
        "BILLING_SERVICE_URL", "http://billing_service:8082/")
    billing_service_change_order_status: str = os.getenv("BILLING_SERVICE_CHANGE_ORDER_STATUS",
                                                         "api/v1/order/change-status")

settings = Settings()
