import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.main import app
from app.db.session import get_db, SessionLocal
from app.core.config import get_settings
from app.db.models import Base

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Get settings
settings = get_settings()

# Test database name
TEST_DB_NAME = f"{settings.POSTGRES_DB}_test"


def create_test_database():
    """Create a test database"""
    # Connect to default postgres database to create/drop test database
    engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    )

    # Drop test database if it exists
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Close any open transactions
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    # Create tables in test database
    test_engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{TEST_DB_NAME}"
    )
    Base.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture(scope="session")
def test_engine():
    """Create test database and return engine"""
    engine = create_test_database()
    yield engine
    # Force close all connections before dropping the database
    engine.dispose()
    # Drop the test database
    drop_engine = create_engine(
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    )
    with drop_engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with a test database"""

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis cache"""

    class MockRedis:
        def __init__(self):
            self.cache = {}

        async def get(self, key: str):
            return self.cache.get(key)

        async def set(self, key: str, value: any):
            self.cache[key] = value

        async def delete(self, key: str):
            if key in self.cache:
                del self.cache[key]

    monkeypatch.setattr("app.cache.redis_cache.RedisCache", MockRedis)
    return MockRedis()


@pytest.fixture
def mock_coingecko(monkeypatch):
    """Mock CoinGecko API responses"""

    class MockCoinGecko:
        async def get_current_price(self):
            from app.services.coingecko_service import CoinGeckoService

            real_service = CoinGeckoService()
            return await real_service.get_current_price()

        async def get_price_history_range(self, from_timestamp: int, to_timestamp: int):
            return {
                "prices": [
                    [from_timestamp, 50000.0],
                    [from_timestamp + 1800000, 50100.0],
                ]
            }

    monkeypatch.setattr("app.services.price_service.CoinGeckoService", MockCoinGecko)
    return MockCoinGecko()
