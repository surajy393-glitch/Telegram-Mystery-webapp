"""
Pytest Configuration for Async Tests
"""
import asyncio
import pytest
from httpx import AsyncClient
import sys
import os

sys.path.insert(0, '/app/backend')

# Async test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Create async HTTP client for API testing"""
    from server import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_user():
    """Mock user data for testing"""
    return {
        "tg_user_id": 123456,
        "gender": "male",
        "age": 25,
        "city": "Mumbai",
        "is_premium": False
    }
