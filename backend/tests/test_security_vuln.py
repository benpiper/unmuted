import pytest
from httpx import AsyncClient
from main import app
from pathlib import Path

@pytest.mark.asyncio
async def test_get_video_unauthenticated():
    """Verify that get_video requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/project/video", params={"directory_path": "/tmp"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_frame_image_unauthenticated():
    """Verify that get_frame_image requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/project/frame_image", params={"directory_path": "/tmp", "frame_index": 0})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_download_artifact_unauthenticated():
    """Verify that download_artifact requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/project/download/json", params={"directory_path": "/tmp"})
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_cache_stats_unauthenticated():
    """Verify that get_cache_stats requires authentication."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/cache/stats")
        assert response.status_code == 401
