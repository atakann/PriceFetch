from typing import Optional, Dict, Any
import httpx
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()


class CoinGeckoService:
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.headers = {"accept": "application/json", "x-cg-demo-api-key": self.api_key}

    async def get_current_price(self) -> Dict[str, Any]:
        """Fetch current Bitcoin price in USD"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/simple/price",
                params={
                    "ids": "bitcoin",
                    "vs_currencies": "usd",
                    "include_last_updated_at": "true",
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_price_history(self, days: str = "1") -> Dict[str, Any]:
        """Fetch Bitcoin price history"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/coins/bitcoin/market_chart",
                params={"vs_currency": "usd", "days": days},
                headers=self.headers,
            )
            response = response.raise_for_status()
            return response.json()
