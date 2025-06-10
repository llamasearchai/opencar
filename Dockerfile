# Multi-stage build for production-ready OpenCar
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

# Add metadata
LABEL org.opencontainers.image.title="OpenCar"
LABEL org.opencontainers.image.description="Advanced Autonomous Vehicle Perception System"
LABEL org.opencontainers.image.version=${VERSION}
LABEL org.opencontainers.image.created=${BUILD_DATE}
LABEL org.opencontainers.image.revision=${VCS_REF}
LABEL org.opencontainers.image.vendor="OpenCar Team"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install build && python -m build --wheel
RUN pip install dist/*.whl

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r opencar && useradd -r -g opencar -d /app -s /bin/bash opencar

# Set up application directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=opencar:opencar src/ ./src/
COPY --chown=opencar:opencar pyproject.toml README.md ./

# Install the application
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/logs /app/tmp \
    && chown -R opencar:opencar /app

# Set up environment variables
ENV PYTHONPATH=/app/src \
    OPENCAR_ENV=production \
    OPENCAR_LOG_LEVEL=INFO \
    OPENCAR_API_HOST=0.0.0.0 \
    OPENCAR_API_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER opencar

# Expose port
EXPOSE 8000

# Default command
CMD ["opencar", "serve", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install -e ".[dev]"

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to opencar user
USER opencar

# Override command for development
CMD ["opencar", "serve", "--host", "0.0.0.0", "--port", "8000", "--reload"] 