import pytest
from datetime import datetime, timezone
from app.services.price_service import PriceService


@pytest.mark.asyncio
async def test_get_current_price(test_db, mock_redis, mock_coingecko):
    """Test getting current price"""
    service = PriceService(test_db)
    result = await service.get_current_price()

    assert "price" in result
    assert "timestamp" in result
    assert isinstance(result["price"], float)
    assert isinstance(result["timestamp"], int)


@pytest.mark.asyncio
async def test_get_price_history_range(test_db, mock_redis, mock_coingecko):
    """Test getting price history range"""
    service = PriceService(test_db)
    from_timestamp = (
        int(datetime.now(timezone.utc).timestamp() * 1000) - 3600000
    )  # 1 hour ago
    to_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    result = await service.get_price_history_range(from_timestamp, to_timestamp)

    assert "prices" in result
    assert isinstance(result["prices"], list)
    assert len(result["prices"]) == 2  # We expect 2 price points from our mock
