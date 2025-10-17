"""Pytest fixtures for asynchronous testing of the Mystery Match API."""

import asyncio
import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import your FastAPI app
from server import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for pytest.mark.asyncio."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def async_client():
    """Yield an AsyncClient instance pointed at the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
