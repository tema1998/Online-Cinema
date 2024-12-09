def test_order_status_change_premium_success(test_client, monkeypatch):
    """Test successful status change for a premium order."""
    async def mock_update_order_status(order_type, order_id, order_status):
        assert order_type == "premium"
        assert order_id == "123e4567-e89b-12d3-a456-426614174000"
        assert order_status == "completed"

    monkeypatch.setattr(
        "services.order_service.OrderService.update_order_status",
        mock_update_order_status,
    )

    request_data = {
        "order_type": "premium",
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "order_status": "completed",
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 200


def test_order_status_change_film_success(test_client, monkeypatch):
    """Test successful status change for a film order."""
    async def mock_update_order_status(order_type, order_id, order_status):
        assert order_type == "film"
        assert order_id == "123e4567-e89b-12d3-a456-426614174001"
        assert order_status == "failed"

    monkeypatch.setattr(
        "services.order_service.OrderService.update_order_status",
        mock_update_order_status,
    )

    request_data = {
        "order_type": "film",
        "order_id": "123e4567-e89b-12d3-a456-426614174001",
        "order_status": "failed",
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 200


def test_order_status_change_invalid_order_type(test_client, monkeypatch):
    """Test API behavior with an invalid order type."""
    async def mock_update_order_status(order_type, order_id, order_status):
        raise ValueError("Invalid order type")

    monkeypatch.setattr(
        "services.order_service.OrderService.update_order_status",
        mock_update_order_status,
    )

    request_data = {
        "order_type": "invalid",
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "order_status": "completed",
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order type"


def test_order_status_change_missing_fields(test_client):
    """Test API behavior when fields are missing in the request."""
    request_data = {
        "order_type": "premium",
        # Missing "order_id" and "order_status"
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"


def test_order_status_change_invalid_order_id(test_client):
    """Test API behavior with an invalid order ID format."""
    request_data = {
        "order_type": "premium",
        "order_id": "invalid-id-format",
        "order_status": "completed",
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid order ID format"


def test_order_status_change_service_failure(test_client, monkeypatch):
    """Test API behavior when the order service fails."""
    async def mock_update_order_status(order_type, order_id, order_status):
        raise Exception("Order service unavailable")

    monkeypatch.setattr(
        "services.order_service.OrderService.update_order_status",
        mock_update_order_status,
    )

    request_data = {
        "order_type": "premium",
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "order_status": "completed",
    }

    response = test_client.post("/api/v1/change-status", json=request_data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def test_order_status_change_missing_body(test_client):
    """Test API behavior when no JSON body is provided."""
    response = test_client.post("/api/v1/change-status", data=None)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "field required"
