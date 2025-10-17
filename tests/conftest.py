"""Pytest fixtures for asynchronous testing of the Mystery Match API."""

import asyncio
import sys
import os
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set DATABASE_URL for tests
os.environ['DATABASE_URL'] = "postgresql://luvhive:luvhive123@localhost:5432/luvhive_bot"

# Import your FastAPI app
from server import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop for pytest.mark.asyncio."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Yield an AsyncClient instance pointed at the FastAPI app."""
    # Import and reset the database pool for each test
    from database.async_db import close_db_pool, init_db_pool
    
    # Close any existing pool
    await close_db_pool()
    
    # Create new pool for this test
    await init_db_pool()
    
    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up pool after test
    await close_db_pool()
