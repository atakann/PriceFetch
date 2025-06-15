class CoinGeckoRateLimitError(Exception):
    """Raised when CoinGecko rate limit is hit"""

    pass


class CoinGeckoAPIError(Exception):
    """Raised when CoinGecko API returns an error"""

    pass
