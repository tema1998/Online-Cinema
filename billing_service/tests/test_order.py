def test_create_order_premium(test_client, setup_mock_data):
    """Test the /order-premium endpoint."""
    order_data = {
        "number_of_month": 3,
    }

    response = test_client.post("/api/v1/order/order-premium", json=order_data)

    print("Response:", response.json())
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert "payment_url" in response_data
    assert response_data["payment_url"] == "http://test-payment-url.com"

def test_create_order_film_success(test_client, setup_mock_data):
    """Test the successful creation of a film order."""
    order_data = {
        "film_id": "123e4567-e89b-12d3-a456-426614174000",  # Example UUID
        "user_email": "test@example.com",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert "payment_url" in response_data
    assert response_data["payment_url"] == "http://test-payment-url.com"

def test_create_order_film_missing_field(test_client):
    """Test creating an order with missing required fields."""
    order_data = {
        # Missing "film_id"
        "user_email": "test@example.com",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"

def test_create_order_film_invalid_email(test_client):
    """Test creating an order with an invalid email format."""
    order_data = {
        "film_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_email": "invalid-email-format",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid email address"

def test_create_order_film_user_info_dependency(test_client, mock_user_info):
    """Test that the user info dependency is correctly used."""
    order_data = {
        "film_id": "123e4567-e89b-12d3-a456-426614174000",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_id"] == mock_user_info["id"]
    assert response_data["user_email"] == mock_user_info["email"]

def test_create_order_film_payment_service_failure(test_client, monkeypatch):
    """Test that the API handles payment service failure gracefully."""
    async def mock_create_payment(*args, **kwargs):
        raise Exception("Payment service unavailable")

    monkeypatch.setattr(
        "services.payment_service.PaymentService.create_payment", mock_create_payment
    )

    order_data = {
        "film_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_email": "test@example.com",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"

def test_create_order_film_nonexistent_film(test_client):
    """Test ordering a film that does not exist."""
    order_data = {
        "film_id": "nonexistent-film-id",  # Simulating a film that doesn't exist
        "user_email": "test@example.com",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Film not found"

def test_create_order_film_order_service_failure(test_client, monkeypatch):
    """Test that the API handles order service failure gracefully."""
    async def mock_create_order_film(*args, **kwargs):
        raise Exception("Order service unavailable")

    monkeypatch.setattr(
        "services.order_service.OrderService.create_order_film", mock_create_order_film
    )

    order_data = {
        "film_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_email": "test@example.com",
    }

    response = test_client.post("/api/v1/order/order-film", json=order_data)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"