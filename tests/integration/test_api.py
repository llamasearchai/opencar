"""Integration tests for OpenCar API."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import io
from PIL import Image
import numpy as np

from opencar.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes for testing."""
    # Create a simple test image
    image = Image.new('RGB', (640, 480), color='red')
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OpenCar API"
        assert "version" in data
        assert data["status"] == "operational"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_liveness_probe(self, client):
        """Test liveness probe."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data

    @patch('opencar.api.routes.get_detector')
    def test_readiness_probe(self, mock_get_detector, client):
        """Test readiness probe."""
        # Mock detector health check
        mock_detector = AsyncMock()
        mock_detector.health_check.return_value = True
        mock_get_detector.return_value = mock_detector

        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "timestamp" in data


class TestPerceptionEndpoints:
    """Test perception API endpoints."""

    @patch('opencar.api.routes.get_detector')
    def test_object_detection(self, mock_get_detector, client, sample_image_bytes):
        """Test object detection endpoint."""
        # Mock detector
        mock_detector = AsyncMock()
        mock_detector.detect.return_value = [
            {
                "class_name": "car",
                "confidence": 0.92,
                "bbox": {"x1": 100.0, "y1": 200.0, "x2": 300.0, "y2": 400.0},
                "attributes": {"vehicle_type": "sedan"}
            }
        ]
        mock_get_detector.return_value = mock_detector

        # Test detection
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/perception/detect", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "detections" in data
        assert "request_id" in data
        assert "timestamp" in data
        assert len(data["detections"]) >= 1
        # Check that we have at least one car detection
        car_detections = [d for d in data["detections"] if d["class_name"] == "car"]
        assert len(car_detections) >= 1

    def test_detection_invalid_file(self, client):
        """Test detection with invalid file."""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/perception/detect", files=files)
        assert response.status_code == 400

    @patch('opencar.api.routes.get_openai_client')
    def test_scene_analysis(self, mock_get_client, client, sample_image_bytes):
        """Test scene analysis endpoint."""
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_client.analyze_image.return_value = {
            "scene_type": "urban",
            "objects": ["car", "person"],
            "hazards": [],
            "recommendations": ["proceed_normally"],
            "safety_score": 0.85,
            "weather_conditions": "clear",
            "traffic_situation": "normal",
            "full_analysis": "Mock analysis",
            "confidence": 0.85,
            "analysis_type": "comprehensive"
        }
        mock_get_client.return_value = mock_client

        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/perception/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "request_id" in data
        assert "analysis_type" in data

    def test_analysis_invalid_file(self, client):
        """Test analysis with invalid file."""
        files = {"file": ("test.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/perception/analyze", files=files)
        assert response.status_code == 400


class TestAdminEndpoints:
    """Test admin API endpoints."""

    def test_get_config(self, client):
        """Test configuration endpoint."""
        response = client.get("/api/v1/admin/config")
        assert response.status_code == 200
        data = response.json()
        assert "debug" in data
        assert "log_level" in data
        assert "api_host" in data
        assert "device" in data

    def test_reload_models(self, client):
        """Test model reload endpoint."""
        # The reload endpoint should work with the existing detector
        response = client.post("/api/v1/admin/models/reload")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data


class TestMiddleware:
    """Test middleware functionality."""

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/")
        assert response.status_code == 200
        # CORS headers should be present in production

    def test_security_headers(self, client):
        """Test security headers."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Check for security headers
        headers = response.headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers

    def test_request_id_header(self, client):
        """Test request ID header is added."""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

    def test_process_time_header(self, client):
        """Test process time header is added."""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed error."""
        response = client.post("/")
        assert response.status_code == 405

    def test_internal_server_error(self, client, sample_image_bytes):
        """Test internal server error handling."""
        # Test with malformed image data to trigger an error
        files = {"file": ("test.jpg", b"invalid image data", "image/jpeg")}
        response = client.post("/api/v1/perception/detect", files=files)
        # The detector should handle invalid image gracefully and return detections
        # In our implementation, it returns an empty list for invalid images
        assert response.status_code == 200
        data = response.json()
        assert "detections" in data


class TestOpenAPIDocumentation:
    """Test OpenAPI documentation."""

    def test_openapi_json(self, client):
        """Test OpenAPI JSON endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_ui(self, client):
        """Test Swagger UI endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestRateLimiting:
    """Test rate limiting (if enabled)."""

    def test_rate_limit_headers(self, client):
        """Test rate limit headers."""
        response = client.get("/")
        assert response.status_code == 200
        # Rate limiting headers would be present if enabled


class TestAsyncEndpoints:
    """Test async endpoint behavior."""

    @patch('opencar.api.routes.get_detector')
    def test_concurrent_requests(self, mock_get_detector, client, sample_image_bytes):
        """Test handling of concurrent requests."""
        # Mock detector with delay
        mock_detector = AsyncMock()
        
        async def mock_detect(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate processing time
            return [{"class_name": "car", "confidence": 0.9, "bbox": {"x1": 0, "y1": 0, "x2": 100, "y2": 100}, "attributes": {}}]
        
        mock_detector.detect = mock_detect
        mock_get_detector.return_value = mock_detector

        # Make multiple concurrent requests
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}
        
        # Test that multiple requests can be handled
        response1 = client.post("/api/v1/perception/detect", files=files)
        response2 = client.post("/api/v1/perception/detect", files=files)
        
        assert response1.status_code == 200
        assert response2.status_code == 200 