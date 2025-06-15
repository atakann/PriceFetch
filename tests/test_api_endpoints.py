import pytest
from datetime import datetime, timezone


def test_get_current_price(client, mock_redis, mock_coingecko):
    """Test current price endpoint"""
    response = client.get("/api/v1/current-price")
    assert response.status_code == 200
    data = response.json()

    assert "price" in data
    assert "timestamp" in data
    assert isinstance(data["price"], float)
    assert isinstance(data["timestamp"], int)


def test_get_price_history_range(client, mock_redis, mock_coingecko):
    """Test price history range endpoint"""
    from_timestamp = (
        int(datetime.now(timezone.utc).timestamp() * 1000) - 3600000
    )  # 1 hour ago
    to_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    response = client.get(
        f"/api/v1/price-history?from_timestamp={from_timestamp}&to_timestamp={to_timestamp}"
    )
    assert response.status_code == 200
    data = response.json()

    assert "prices" in data
    assert isinstance(data["prices"], list)
    assert len(data["prices"]) == 2  # We expect 2 price points from our mock
