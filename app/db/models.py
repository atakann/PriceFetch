from sqlalchemy import Column, Integer, Float, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CurrentPrice(Base):
    __tablename__ = "current_prices"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    last_updated_at = Column(BigInteger, nullable=False) # Unix timestamp
    created_at = Column(DateTime, nullable=False)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(BigInteger, nullable=False) # Unix timestamp
    price = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)