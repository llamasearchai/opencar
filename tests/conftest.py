"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path

from opencar.config.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        debug=True,
        database_url="sqlite:///:memory:",
        redis_url="redis://localhost:6379/15",
        openai_api_key="sk-test-key",
        jwt_secret_key="test-secret-key",
    )


@pytest.fixture
def sample_image_data():
    """Create sample image data for testing."""
    import numpy as np
    return np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)


@pytest.fixture
def mock_perception_data() -> dict:
    """Mock perception data for testing."""
    return {
        "detections": [
            {
                "class": "car",
                "confidence": 0.92,
                "bbox": [100, 200, 300, 400],
                "track_id": 1,
            },
            {
                "class": "person",
                "confidence": 0.87,
                "bbox": [400, 300, 150, 300],
                "track_id": 2,
            },
        ],
        "lanes": {
            "current_lane": 2,
            "total_lanes": 3,
            "lane_markings": ["solid", "dashed", "solid"],
        },
        "traffic_lights": [
            {"id": 1, "state": "green", "confidence": 0.95},
        ],
    } 