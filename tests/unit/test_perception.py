"""Test perception models."""

import pytest

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
        assert detector.model is not None

    def test_detection(self, detector, sample_image_data):
        """Test object detection."""
        result = detector.detect(sample_image_data, return_time=True)
        
        assert "detections" in result
        assert "image_size" in result
        assert "inference_time_ms" in result
        
        assert isinstance(result["detections"], list)
        assert len(result["detections"]) >= 0
        assert result["inference_time_ms"] >= 0

    def test_detection_output_format(self, detector, sample_image_data):
        """Test detection output format."""
        result = detector.detect(sample_image_data)
        
        for detection in result["detections"]:
            assert "bbox" in detection
            assert "confidence" in detection
            assert "class_id" in detection
            assert "class_name" in detection
            
            assert len(detection["bbox"]) == 4
            assert 0 <= detection["confidence"] <= 1
            assert detection["class_id"] >= 0
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

    def test_yolo_detector(self, sample_image_data):
        """Test YOLO detector."""
        detector = YOLODetector(model_size="n", device="cpu")
        result = detector.detect(sample_image_data)
        
        assert "detections" in result
        assert isinstance(result["detections"], list)
        assert detector.model_size == "n"
        assert detector.model["model_type"] == "yolov8n" 