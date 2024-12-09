def test_catch_payment_notification_premium_success(test_client, monkeypatch):
    """Test the successful processing of a premium order payment notification."""

    async def mock_process_premium_order_payment(json_request):
        assert json_request["object"]["metadata"]["order_type"] == "premium"

    monkeypatch.setattr(
        "services.payment_service.PaymentService.process_premium_order_payment",
        mock_process_premium_order_payment,
    )

    notification_data = {
        "object": {
            "metadata": {
                "order_type": "premium",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 200


def test_catch_payment_notification_film_success(test_client, monkeypatch):
    """Test the successful processing of a film order payment notification."""

    async def mock_process_film_order_payment(json_request):
        assert json_request["object"]["metadata"]["order_type"] == "film"

    monkeypatch.setattr(
        "services.payment_service.PaymentService.process_film_order_payment",
        mock_process_film_order_payment,
    )

    notification_data = {
        "object": {
            "metadata": {
                "order_type": "film",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 200


def test_catch_payment_notification_invalid_order_type(test_client):
    """Test the API's behavior when an invalid order type is provided."""
    notification_data = {
        "object": {
            "metadata": {
                "order_type": "unknown_type",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order type"


def test_catch_payment_notification_missing_metadata(test_client):
    """Test the API's behavior when metadata is missing."""
    notification_data = {
        "object": {
            "metadata": None  # Missing metadata
        }
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"


def test_catch_payment_notification_service_failure(test_client, monkeypatch):
    """Test the API's behavior when the payment service fails."""

    async def mock_process_premium_order_payment(json_request):
        raise Exception("Payment service unavailable")

    monkeypatch.setattr(
        "services.payment_service.PaymentService.process_premium_order_payment",
        mock_process_premium_order_payment,
    )

    notification_data = {
        "object": {
            "metadata": {
                "order_type": "premium",
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_catch_payment_notification_missing_object(test_client):
    """Test the API's behavior when the 'object' key is missing."""
    notification_data = {
        # Missing "object" key
    }

    response = test_client.post(
        "/api/v1/payment-notification", json=notification_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"


def test_catch_payment_notification_invalid_json(test_client):
    """Test the API's behavior when invalid JSON is sent."""
    invalid_json_data = "invalid-json-string"

    response = test_client.post(
        "/api/v1/payment-notification", data=invalid_json_data
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON format"
