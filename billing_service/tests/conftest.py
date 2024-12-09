from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from db.db_utils import Base
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from billing_service.core.config import config
from billing_service.db.db_utils import Base
from billing_service.models.entity import PremiumPurchaseManagement
from billing_service.services.order_service import OrderService
from billing_service.services.payment_service import PaymentService
from billing_service.services.token_service import JWTBearer
from main import app


@pytest.fixture(scope="function")
async def test_db():
    engine = create_async_engine(config.dsn_test)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture
def mock_order_service():
    """Fixture to mock OrderService."""
    mock = AsyncMock(OrderService)
    mock.create_order_premium.return_value = MagicMock(
        id=uuid4(),
        user_id=uuid4(),
        user_email="test@example.com",
        total_price=1000.0,
        premium_purchase_management_id=uuid4(),
        number_of_month=1,
        to_dict=lambda: {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "user_email": "test@example.com",
            "total_price": 1000.0,
            "number_of_month": 1,
            "payment_url": "http://test-payment-url.com",
        },
    )
    mock.update_payment_data.return_value = MagicMock(
        id=uuid4(),
        user_id=uuid4(),
        user_email="test@example.com",
        total_price=1000.0,
        premium_purchase_management_id=uuid4(),
        number_of_month=1,
        payment_url="http://test-payment-url.com",
        to_dict=lambda: {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "user_email": "test@example.com",
            "total_price": 1000.0,
            "number_of_month": 1,
            "payment_url": "http://test-payment-url.com",
        },
    )
    return mock


@pytest.fixture
async def setup_mock_data(async_session: AsyncSession, test_db):
    """Fixture to populate mock data for testing."""
    new_subscription = PremiumPurchaseManagement(
        name="Test Premium Subscription",
        description="Test subscription description",
        price=99.99,
        is_active=True,
    )
    async_session.add(new_subscription)
    await async_session.commit()
    yield
    await async_session.rollback()  # Clean up after the test


@pytest.fixture
def mock_payment_service():
    """Fixture to mock PaymentService."""
    mock = MagicMock(PaymentService)
    mock.create_payment.return_value = (
        "payment_id_123", "http://test-payment-url.com")
    return mock


@pytest.fixture
def mock_user_info():
    """Fixture to mock user info."""
    return {
        "id": str(uuid4()),
        "email": "user@example.com",
    }


@pytest.fixture(autouse=True)
def mock_jwt_bearer(monkeypatch, mock_user_info):
    """Mock the JWTBearer dependency."""

    async def mock_call(self, request):
        return mock_user_info

    monkeypatch.setattr(JWTBearer, "__call__", mock_call)


@pytest.fixture
def test_client(mock_order_service, mock_payment_service, mock_user_info, monkeypatch):
    """Fixture to provide a FastAPI test client with mocked dependencies."""

    async def mock_get_user_info(request):
        return mock_user_info

    async def mock_get_order_service():
        return mock_order_service

    async def mock_get_payment_service():
        return mock_payment_service

    monkeypatch.setattr(
        "services.token_service.JWTBearer.__call__", mock_get_user_info)
    monkeypatch.setattr(
        "services.order_service.get_order_service", lambda: mock_get_order_service)
    monkeypatch.setattr(
        "services.yookassa_service.get_yookassa_service", lambda: mock_get_payment_service)

    app.dependency_overrides = {
        JWTBearer: lambda: mock_user_info,
        mock_get_order_service: lambda: mock_order_service,
        mock_get_payment_service: lambda: mock_payment_service,
    }

    client = TestClient(app)
    yield client
    app.dependency_overrides = {}
