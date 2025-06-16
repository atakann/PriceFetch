from app.db.repository import PriceRepository
from app.schemas.price import (
    CurrentPriceResponse,
    PriceHistoryResponse,
    PricePoint,
)
from app.services.coingecko_service import CoinGeckoService
from app.cache.redis_cache import RedisCache
from sqlalchemy.orm import Session


class PriceService:
    def __init__(self, db: Session):
        self.repository = PriceRepository(db)
        self.coingecko = CoinGeckoService()
        self.cache = RedisCache()
        self.cache_key = "bitcoin_current_price"

    def _normalize_timestamp(self, timestamp: int) -> int:
        """Convert timestamp to milliseconds if needed"""
        return timestamp * 1000 if len(str(timestamp)) == 10 else timestamp

    async def get_current_price(self) -> CurrentPriceResponse:
        """Get current price from cache or API"""
        cached_data = await self.cache.get(self.cache_key)
        if cached_data:
            return CurrentPriceResponse(**cached_data)

        data = await self.coingecko.get_current_price()
        price_data = data["bitcoin"]
        normalized_timestamp = self._normalize_timestamp(price_data["last_updated_at"])

        stored_price = self.repository.create_price_point(
            timestamp=normalized_timestamp, price=price_data["usd"]
        )

        response = CurrentPriceResponse(
            price=stored_price.price,
            timestamp=stored_price.timestamp,
        )

        await self.cache.set(self.cache_key, response.model_dump())
        return response

    async def get_price_history_range(
        self, from_timestamp: int, to_timestamp: int
    ) -> PriceHistoryResponse:
        """Get price history for specific range"""
        from_timestamp = self._normalize_timestamp(from_timestamp)
        to_timestamp = self._normalize_timestamp(to_timestamp)

        cache_key = f"bitcoin_price_range_{from_timestamp}_{to_timestamp}"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return PriceHistoryResponse(**cached_data)

        data = await self.coingecko.get_price_history_range(
            from_timestamp, to_timestamp
        )

        if data.get("prices"):
            valid_prices = []
            for price_point in data["prices"]:
                if (
                    len(price_point) >= 2
                    and price_point[0] is not None
                    and price_point[1] is not None
                ):
                    try:
                        timestamp = int(price_point[0])
                        price = float(price_point[1])
                        valid_prices.append((timestamp, price))
                    except (ValueError, TypeError):
                        continue

            if valid_prices:
                self.repository.create_price_points_batch(valid_prices)

        db_prices = self.repository.get_price_range(from_timestamp, to_timestamp)

        response = PriceHistoryResponse(
            prices=[PricePoint(timestamp=p.timestamp, price=p.price) for p in db_prices]
        )

        await self.cache.set(cache_key, response.model_dump())
        return response
