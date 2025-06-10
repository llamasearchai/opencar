"""Test perception models."""

import pytest
import asyncio
import numpy as np

from opencar.perception.models.detector import ObjectDetector, YOLODetector


class TestObjectDetector:
    """Test object detection models."""

    @pytest.fixture
    def detector(self):
        """Create detector instance."""
        return ObjectDetector(
            num_classes=80,
            confidence_threshold=0.5,
            device="cpu",
        )

    def test_detector_initialization(self, detector):
        """Test detector initialization."""
        assert detector.num_classes == 80
        assert detector.confidence_threshold == 0.5
        assert detector.device == "cpu"
        assert not detector.is_initialized  # Should not be initialized yet

    @pytest.mark.asyncio
    async def test_detection(self, detector, sample_image_data):
        """Test object detection."""
        result = await detector.detect(sample_image_data)
        
        assert isinstance(result, list)
        assert len(result) >= 0
        
        # Check if detector was initialized
        assert detector.is_initialized

    @pytest.mark.asyncio
    async def test_detection_output_format(self, detector, sample_image_data):
        """Test detection output format."""
        result = await detector.detect(sample_image_data)
        
        for detection in result:
            assert "bbox" in detection
            assert "confidence" in detection
            assert "class_name" in detection
            assert "attributes" in detection
            
            bbox = detection["bbox"]
            assert "x1" in bbox and "y1" in bbox and "x2" in bbox and "y2" in bbox
            assert 0 <= detection["confidence"] <= 1
            assert isinstance(detection["class_name"], str)

    def test_class_name_lookup(self, detector):
        """Test class name lookup."""
        # Test known class
        name = detector._get_class_name(0)
        assert name == "person"
        
        name = detector._get_class_name(2)
        assert name == "car"
        
        # Test unknown class
        name = detector._get_class_name(999)
        assert name == "class_999"

    @pytest.mark.asyncio
    async def test_yolo_detector(self, sample_image_data):
        """Test YOLO detector."""
        detector = YOLODetector(model_size="n", device="cpu")
        result = await detector.detect(sample_image_data)
        
        assert isinstance(result, list)
        assert detector.model_size == "n"
        assert detector._mock_model["model_type"] == "yolov8n"

    @pytest.mark.asyncio
    async def test_health_check(self, detector):
        """Test health check."""
        # Should be False before initialization
        assert not await detector.health_check()
        
        # Initialize and check again
        await detector.initialize()
        assert await detector.health_check()

    @pytest.mark.asyncio
    async def test_reload(self, detector):
        """Test model reload."""
        await detector.initialize()
        assert detector.is_initialized
        
        await detector.reload()
        assert detector.is_initialized 