from typing import List, Dict, Any
from app.db.repository import PriceRepository
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

    async def get_current_price(self) -> Dict[str, Any]:
        """Get current price from cache or API"""
        cached_data = await self.cache.get(self.cache_key)
        if cached_data:
            return cached_data

        data = await self.coingecko.get_current_price()
        price_data = data["bitcoin"]

        normalized_timestamp = self._normalize_timestamp(price_data["last_updated_at"])

        stored_price = self.repository.create_price_point(
            timestamp=normalized_timestamp, price=price_data["usd"]
        )

        response = {
            "price": stored_price.price,
            "timestamp": stored_price.timestamp,
        }

        await self.cache.set(self.cache_key, response)
        return response

    async def get_price_history_range(
        self, from_timestamp: int, to_timestamp: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get price history for specific range"""
        cache_key = f"bitcoin_price_range_{from_timestamp}_{to_timestamp}"

        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data

        data = await self.coingecko.get_price_history_range(
            from_timestamp, to_timestamp
        )

        stored_prices = self.repository.create_price_points_batch(data["prices"])

        response = {
            "prices": [
                {"timestamp": p.timestamp, "price": p.price} for p in stored_prices
            ]
        }

        await self.cache.set(cache_key, response)

        return response
