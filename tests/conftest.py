"""Pytest fixtures for asynchronous testing of the Mystery Match API."""

import asyncio
import pytest
from httpx import AsyncClient

# Import your FastAPI app. Adjust path if your app is defined elsewhere.
try:
    from backend.server import app
except ImportError:
    from server import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for pytest.mark.asyncio."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Yield an AsyncClient instance pointed at the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
