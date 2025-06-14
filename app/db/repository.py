from sqlalchemy.orm import Session
from datetime import datetime
from . import models


class PriceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_current_price(
        self, price: float, last_updated_at: int
    ) -> models.CurrentPrice:
        db_price = models.CurrentPrice(
            price=price,
            last_updated_at=last_updated_at,
            created_at=datetime.now(datetime.timezone.utc),
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    def create_price_history(
        self,
        timestamp: int,
        price: float,
        market_cap: float = None,
        volume: float = None,
    ) -> models.PriceHistory:
        db_history = models.PriceHistory(
            timestamp=timestamp, price=price, market_cap=market_cap, volume=volume
        )
        self.db.add(db_history)
        self.db.commit()
        self.db.refresh(db_history)
        return db_history

    def get_price_history(self, start_time: int, end_time: int):
        return (
            self.db.query(models.PriceHistory)
            .filter(models.PriceHistory.timestamp.between(start_time, end_time))
            .order_by(models.PriceHistory.timestamp_desc())
            .all()
        )
