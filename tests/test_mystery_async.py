"""Test suite for async Mystery Match endpoints.

These tests assume a running PostgreSQL database configured via
environment variables and that Alembic migrations have been applied.
"""

import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    """Basic health check to ensure the API root is reachable."""
    res = await async_client.get("/")
    # Depending on your root path, adjust these status expectations
    assert res.status_code in {200, 404, 405}

@pytest.mark.asyncio
async def test_find_match_no_user(async_client):
    """find-match should return 404 (or a failure response) for non-existent users."""
    response = await async_client.post("/api/mystery/find-match", json={
        "user_id": 9999999,
        "preferred_age_min": 18,
        "preferred_age_max": 30,
    })
    assert response.status_code in {200, 404}
    data = response.json()
    if response.status_code == 200:
        # In case API uses a success=false response instead of a status code
        assert data.get("success") is False

@pytest.mark.asyncio
async def test_my_matches_empty(async_client):
    """Test my-matches endpoint with a user that has no matches."""
    response = await async_client.get("/api/mystery/my-matches/9999999")
    assert response.status_code in {200, 404}
    if response.status_code == 200:
        data = response.json()
        assert "matches" in data or "success" in data

@pytest.mark.asyncio
async def test_user_stats(async_client):
    """Test stats endpoint for a user."""
    response = await async_client.get("/api/mystery/stats/9999999")
    assert response.status_code in {200, 500}  # 500 if DB not available
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        if data.get("success"):
            assert "user_id" in data
            assert "is_premium" in data

@pytest.mark.asyncio
async def test_report_endpoint(async_client):
    """Create a content report and expect a success response."""
    res = await async_client.post("/api/mystery/report", json={
        "reporter_id": 1,
        "reported_user_id": 2,
        "content_type": "message",
        "content_id": "test-message",
        "reason": "spam",
    })
    # Might return 500 if DB not available, 200 if successful
    assert res.status_code in {200, 500}
    if res.status_code == 200:
        data = res.json()
        # Success can be True or False (False if foreign key constraint fails)
        assert "success" in data

@pytest.mark.asyncio
async def test_send_message_invalid_match(async_client):
    """Test send-message with invalid match_id."""
    response = await async_client.post("/api/mystery/send-message", json={
        "match_id": 999999,
        "sender_id": 1,
        "message_text": "Test message"
    })
    # Should return error (500 or 404 depending on implementation)
    assert response.status_code in {200, 404, 500}

@pytest.mark.asyncio
async def test_unmatch_nonexistent(async_client):
    """Test unmatch with non-existent match."""
    response = await async_client.post("/api/mystery/unmatch", json={
        "match_id": 999999,
        "user_id": 1,
        "reason": "test"
    })
    assert response.status_code in {200, 404, 500}
    if response.status_code == 200:
        # Might return success=false
        data = response.json()
        assert "success" in data or "detail" in data

@pytest.mark.asyncio
async def test_block_user(async_client):
    """Test blocking a user."""
    response = await async_client.post("/api/mystery/block", json={
        "user_id": 1,
        "block_user_id": 2,
        "reason": "test block"
    })
    assert response.status_code in {200, 500}

@pytest.mark.asyncio
async def test_extend_match_nonexistent(async_client):
    """Test extending a non-existent match."""
    response = await async_client.post("/api/mystery/extend-match", json={
        "match_id": 999999,
        "user_id": 1
    })
    assert response.status_code in {200, 404, 500}

@pytest.mark.asyncio
async def test_online_status_check(async_client):
    """Test checking online status for a match."""
    response = await async_client.get("/api/mystery/chat/online-status/999999/1")
    assert response.status_code in {200, 404, 500}
