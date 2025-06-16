from sqlalchemy import Column, Integer, Float, DateTime, BigInteger
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CurrentPrice(Base):
    __tablename__ = "price_points"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(BigInteger, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)
