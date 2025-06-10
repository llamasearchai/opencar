"""Test configuration module."""

import pytest

from opencar.config.settings import Settings, get_settings


class TestSettings:
    """Test settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.app_name == "OpenCar"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_settings_validation(self):
        """Test settings validation."""
        # Test invalid log level
        with pytest.raises(ValueError):
            Settings(log_level="INVALID")
        
        # Test temperature bounds
        with pytest.raises(ValueError):
            Settings(openai_temperature=3.0)

    def test_device_fallback(self):
        """Test device fallback to CPU."""
        settings = Settings(device="cuda")
        # Should not raise an error and handle gracefully
        assert settings.device in ["cuda", "cpu"]

    def test_database_settings(self):
        """Test database settings property."""
        settings = Settings(
            database_url="postgresql://user:pass@localhost/test",
            debug=True,
        )
        
        db_settings = settings.database_settings
        
        assert db_settings["url"] == "postgresql://user:pass@localhost/test"
        assert db_settings["echo"] is True
        assert db_settings["pool_size"] == 10

    def test_settings_singleton(self):
        """Test settings singleton pattern."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same instance due to lru_cache
        assert settings1 is settings2
 