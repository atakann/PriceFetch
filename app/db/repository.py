from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Tuple
from . import models


class PriceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_price_point(self, timestamp: int, price: float) -> models.CurrentPrice:
        """Create a single price point"""
        db_price = models.CurrentPrice(
            timestamp=timestamp,
            price=price,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    def create_price_points_batch(
        self, price_points: List[Tuple[int, float]]
    ) -> List[models.CurrentPrice]:
        """Create multiple price points from range endpoint"""
        now = datetime.now(timezone.utc)
        db_prices = [
            models.CurrentPrice(timestamp=timestamp, price=price, created_at=now)
            for timestamp, price in price_points
        ]
        self.db.bulk_save_objects(db_prices)
        self.db.commit()
        return db_prices

    def get_price_range(
        self, from_timestamp: int, to_timestamp: int
    ) -> list[models.CurrentPrice]:
        """Get price points within timestamp range"""
        return (
            self.db.query(models.CurrentPrice)
            .filter(models.CurrentPrice.timestamp.between(from_timestamp, to_timestamp))
            .order_by(models.CurrentPrice.timestamp.desc())
            .all()
        )
