from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.session import get_db
from app.services.price_service import PriceService
from app.schemas.price import (
    CurrentPriceResponse,
    PriceHistoryRangeParams,
    PriceHistoryResponse,
)

router = APIRouter(prefix="/api/v1", tags=["prices"])


@router.get("/current-price", response_model=CurrentPriceResponse)
async def get_current_price(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current Bitcoin price"""
    try:
        price_service = PriceService(db)
        return await price_service.get_current_price()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch current price: {str(e)}"
        )


@router.get("/price-history", response_model=PriceHistoryResponse)
async def get_price_history_range(
    from_timestamp: int, to_timestamp: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get Bitcoin price history for specific range"""
    try:
        params = PriceHistoryRangeParams(
            from_timestamp=from_timestamp, to_timestamp=to_timestamp
        )

        price_service = PriceService(db)
        result = await price_service.get_price_history_range(
            params.from_timestamp, params.to_timestamp
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
