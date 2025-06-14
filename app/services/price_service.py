from datetime import datetime
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

    async def get_current_price(self) -> Dict[str, Any]:
        """Get current price from cache or API"""
        cached_data = await self.cache.get(self.cache_key)
        if cached_data:
            return cached_data

        data = await self.coingecko.get_current_price()
        price_data = data["bitcoin"]

        stored_price = self.repository.create_current_price(
            price=price_data["usd"], last_updated_at=price_data["last_updated_at="]
        )

        return {
            "price": stored_price.price,
            "last_updated_at": stored_price.last_updated_at,
        }

    async def get_price_history(self, days: str = "1") -> List[Dict[str, Any]]:
        """Get price history and store it"""
        data = await self.coingecko.get_price_history(days)

        stored_prices = []
        for timestamp, price in data["prices"]:
            stored_price = self.repository.create_price_history(
                timestamp=int(timestamp), price=price
            )
            stored_price.append(
                {"timestamp": stored_price.timestamp, "price": stored_price.price}
            )
        return stored_price
