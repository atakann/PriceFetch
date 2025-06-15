from pydantic import BaseModel, ConfigDict, field_validator
from typing import List
from datetime import datetime, timedelta, timezone


class CurrentPriceResponse(BaseModel):
    price: float
    timestamp: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 105487.095,
                "timestamp": 1749994297000,
            }
        }
    )


class PriceHistoryRangeParams(BaseModel):
    from_timestamp: int
    to_timestamp: int

    @field_validator("from_timestamp")
    @classmethod
    def validate_from_timestamp(cls, from_timestamp: int) -> int:
        """Validate from_timestamp"""
        current = int(datetime.now(timezone.utc).timestamp() * 1000)

        if from_timestamp > current:
            raise ValueError("from_timestamp cannot be in the future")

        return from_timestamp

    @field_validator("to_timestamp")
    @classmethod
    def validate_timestamps(cls, to_timestamp: int, info) -> int:
        """Validate timestamp range"""
        from_ts = info.data.get("from_timestamp")
        if from_ts:
            current = int(datetime.now(timezone.utc).timestamp() * 1000)

            if to_timestamp <= from_ts:
                raise ValueError("to_timestamp must be greater than from_timestamp")

            if to_timestamp > current:
                raise ValueError("to_timestamp cannot be in the future")

        return to_timestamp

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "from_timestamp": 1747393698896,
                "to_timestamp": 1749981787521,
            }
        }
    )


class PricePoint(BaseModel):
    timestamp: int
    price: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": 1749981787521,
                "price": 104941.085,
            }
        }
    )


class PriceHistoryResponse(BaseModel):
    prices: List[PricePoint]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prices": [
                    {"timestamp": 1749981787521, "price": 104941.085},
                    {"timestamp": 1749978205180, "price": 105211.979},
                ]
            }
        }
    )
