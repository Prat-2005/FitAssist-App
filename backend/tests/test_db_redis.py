"""
Tests for backend/db/redis.py

Covers:
  - cache_set (with and without TTL)
  - cache_get (hit, miss, error)
  - cache_delete
  - cache_clear
  - get_redis_client
"""

import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_redis_mock(**overrides):
    """Return an AsyncMock representing a redis.asyncio.Redis client."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.setex = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.flushdb = AsyncMock(return_value=True)
    for attr, val in overrides.items():
        setattr(client, attr, val)
    return client


# ---------------------------------------------------------------------------
# cache_set
# ---------------------------------------------------------------------------

class TestCacheSet:
    @pytest.mark.asyncio
    async def test_set_without_ttl_calls_set(self):
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("key1", "value1")
        assert result is True
        mock_client.set.assert_awaited_once_with("key1", "value1")

    @pytest.mark.asyncio
    async def test_set_with_ttl_calls_setex(self):
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("key1", "value1", ttl=300)
        assert result is True
        mock_client.setex.assert_awaited_once_with("key1", 300, "value1")

    @pytest.mark.asyncio
    async def test_set_with_ttl_zero_calls_set_not_setex(self):
        """TTL of 0 is falsy; should call set (not setex)."""
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("key1", "value1", ttl=0)
        assert result is True
        mock_client.set.assert_awaited_once()
        mock_client.setex.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self):
        mock_client = _make_redis_mock()
        mock_client.set = AsyncMock(side_effect=Exception("Redis down"))
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("key1", "value1")
        assert result is False

    @pytest.mark.asyncio
    async def test_setex_exception_returns_false(self):
        mock_client = _make_redis_mock()
        mock_client.setex = AsyncMock(side_effect=ConnectionError("timeout"))
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("key1", "value1", ttl=60)
        assert result is False

    @pytest.mark.asyncio
    async def test_empty_key_and_value(self):
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_set
            result = await cache_set("", "")
        assert result is True


# ---------------------------------------------------------------------------
# cache_get
# ---------------------------------------------------------------------------

class TestCacheGet:
    @pytest.mark.asyncio
    async def test_returns_cached_value(self):
        mock_client = _make_redis_mock()
        mock_client.get = AsyncMock(return_value="cached_value")
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_get
            result = await cache_get("key1")
        assert result == "cached_value"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_key(self):
        mock_client = _make_redis_mock()
        mock_client.get = AsyncMock(return_value=None)
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_get
            result = await cache_get("missing_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self):
        mock_client = _make_redis_mock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_get
            result = await cache_get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_calls_get_with_correct_key(self):
        mock_client = _make_redis_mock()
        mock_client.get = AsyncMock(return_value="val")
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_get
            await cache_get("my_special_key")
        mock_client.get.assert_awaited_once_with("my_special_key")

    @pytest.mark.asyncio
    async def test_returns_string_value(self):
        mock_client = _make_redis_mock()
        mock_client.get = AsyncMock(return_value="some_string")
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_get
            result = await cache_get("k")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# cache_delete
# ---------------------------------------------------------------------------

class TestCacheDelete:
    @pytest.mark.asyncio
    async def test_delete_returns_true_on_success(self):
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_delete
            result = await cache_delete("key1")
        assert result is True
        mock_client.delete.assert_awaited_once_with("key1")

    @pytest.mark.asyncio
    async def test_delete_returns_false_on_exception(self):
        mock_client = _make_redis_mock()
        mock_client.delete = AsyncMock(side_effect=Exception("Redis error"))
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_delete
            result = await cache_delete("key1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key_still_returns_true(self):
        """Redis delete of a nonexistent key returns 0 but doesn't raise."""
        mock_client = _make_redis_mock()
        mock_client.delete = AsyncMock(return_value=0)
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_delete
            result = await cache_delete("nonexistent")
        assert result is True


# ---------------------------------------------------------------------------
# cache_clear
# ---------------------------------------------------------------------------

class TestCacheClear:
    @pytest.mark.asyncio
    async def test_clear_returns_true_on_success(self):
        mock_client = _make_redis_mock()
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_clear
            result = await cache_clear()
        assert result is True
        mock_client.flushdb.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_clear_returns_false_on_exception(self):
        mock_client = _make_redis_mock()
        mock_client.flushdb = AsyncMock(side_effect=Exception("Redis down"))
        with patch("db.redis.redis_client", mock_client):
            from db.redis import cache_clear
            result = await cache_clear()
        assert result is False


# ---------------------------------------------------------------------------
# get_redis_client
# ---------------------------------------------------------------------------

class TestGetRedisClient:
    def test_returns_same_client_instance(self):
        import db.redis as redis_module
        from db.redis import get_redis_client
        client = get_redis_client()
        assert client is redis_module.redis_client

    def test_returns_non_none(self):
        from db.redis import get_redis_client
        client = get_redis_client()
        assert client is not None