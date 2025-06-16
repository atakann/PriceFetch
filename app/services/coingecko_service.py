from typing import Dict, Any
import httpx
from app.core.config import get_settings
from app.core.exceptions import CoinGeckoRateLimitError, CoinGeckoAPIError

settings = get_settings()


class CoinGeckoService:
    def __init__(self):
        self.base_url = settings.COINGECKO_BASE_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.headers = {"accept": "application/json", "x-cg-demo-api-key": self.api_key}

    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)

                if response.status_code == 429:
                    raise CoinGeckoRateLimitError("Rate limit exceeded")

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise CoinGeckoAPIError(f"Bad request: {e.response.text}")
            raise CoinGeckoAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise CoinGeckoAPIError(f"Network error: {str(e)}")

    async def get_current_price(self) -> Dict[str, Any]:
        """Fetch current Bitcoin price in USD"""
        return await self._make_request(
            "GET",
            f"{self.base_url}/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_last_updated_at": "true",
                "precision": "3",
            },
            headers=self.headers,
        )

    async def get_price_history_range(
        self, from_timestamp: int, to_timestamp: int
    ) -> Dict[str, Any]:
        """Fetch Bitcoin price history for specific range"""
        from_seconds = from_timestamp // 1000
        to_seconds = to_timestamp // 1000

        url = f"{self.base_url}/coins/bitcoin/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": from_seconds,
            "to": to_seconds,
            "precision": "3",
        }

        try:
            response = await self._make_request(
                "GET",
                url,
                params=params,
                headers=self.headers,
            )
            return response
        except Exception as e:
            print(f"Error in CoinGecko API call: {e}")
            raise
