# OpenCar

[![PyPI version](https://badge.fury.io/py/opencar.svg)](https://badge.fury.io/py/opencar)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**OpenCar** is a production-ready autonomous vehicle perception system featuring state-of-the-art computer vision models, real-time processing capabilities, and seamless integration with OpenAI's advanced AI models.

## Features

- **Advanced Perception Models**: YOLOv8, SegFormer, and custom multimodal fusion models
- **Real-time Processing**: WebSocket support for streaming perception data
- **OpenAI Integration**: GPT-4 powered scene understanding and analysis
- **Production Ready**: Docker support and comprehensive monitoring
- **Interactive CLI**: Rich terminal interface with progress bars and formatted output
- **Extensive Testing**: Comprehensive test suite with unit and integration tests
- **Modern Python**: Async/await, type hints, and latest Python 3.10+ features

## Quick Start

### Installation

```bash
# Install from PyPI
pip install opencar

# Or install from source
git clone https://github.com/yourusername/opencar.git
cd opencar
pip install -e ".[dev,ml]"
```

### Basic Usage

```bash
# Start the API server
opencar serve

# Display system information
opencar info

# Check system status
opencar status

# Initialize a new project
opencar init my-project
```

### Python API

```python
from opencar.perception.models.detector import YOLODetector
import numpy as np

# Initialize detector
detector = YOLODetector(model_size="n")

# Process image
image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
results = detector.detect(image, return_time=True)
print(f"Detected {len(results['detections'])} objects")
```

## Installation

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM recommended
- NVIDIA GPU optional (will use CPU if not available)

### Detailed Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/opencar.git
cd opencar

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install OpenCar
pip install -e ".[dev,ml]"

# 4. Set up configuration
cp .env.example .env
# Edit .env with your settings

# 5. Run tests to verify installation
pytest tests/ -v

# 6. Start the server
opencar serve
```

## Architecture

The OpenCar system consists of several key components:

- **API Layer**: FastAPI with WebSocket support for real-time communication
- **Perception Core**: Modular pipeline for object detection and analysis
- **ML Models**: Optimized models with efficient inference
- **Integration Layer**: OpenAI API client with retry logic and caching
- **CLI Interface**: Rich terminal UI with interactive commands

## Configuration

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# OpenAI Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# ML Configuration
DEVICE=cuda
BATCH_SIZE=32
MODEL_CACHE_SIZE=5
```

## API Documentation

### REST Endpoints

```http
# Health check
GET /health

# API documentation
GET /docs

# Root endpoint
GET /
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=opencar --cov-report=html

# Run specific test categories
pytest tests/unit -v
pytest tests/integration -v
```

## Performance

| Model    | Device | FPS | Memory |
|----------|--------|-----|---------|
| YOLOv8n  | GPU    | 140 | 6.2MB   |
| YOLOv8n  | CPU    | 35  | 6.2MB   |

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/opencar.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and run tests
pytest

# Commit with conventional commits
git commit -m "feat: add amazing feature"

# Push and create a pull request
git push origin feature/amazing-feature
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT-4 and vision models
- FastAPI for the excellent web framework
- Rich for beautiful terminal UI
- PyTorch for ML capabilities

## Support

- Documentation: Available at `/docs` when running the server
- Issues: [GitHub Issues](https://github.com/yourusername/opencar/issues)

---

Built with modern Python and production-ready practices. 