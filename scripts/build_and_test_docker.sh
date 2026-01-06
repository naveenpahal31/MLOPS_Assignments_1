#!/usr/bin/env bash
# Script to build and test Docker container
# This script must be run with bash (not zsh)

# Ensure we're using bash
if [ -z "$BASH_VERSION" ]; then
    echo "Error: This script must be run with bash, not zsh or other shells."
    echo "Please run: bash scripts/build_and_test_docker.sh"
    exit 1
fi

# Exit on error
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

IMAGE_NAME="heart-disease-api"
CONTAINER_NAME="heart-disease-api-test"

# Check if Docker is installed
if ! command -v docker > /dev/null 2>&1; then
    echo ""
    echo "============================================================"
    echo "ERROR: Docker is not installed"
    echo "============================================================"
    echo ""
    echo "Docker is required to build and run the containerized API."
    echo ""
    echo "Installation instructions:"
    echo ""
    echo "  macOS:"
    echo "    Download Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo "    Or install via Homebrew: brew install --cask docker"
    echo ""
    echo "  Linux (Ubuntu/Debian):"
    echo "    sudo apt-get update"
    echo "    sudo apt-get install docker.io"
    echo "    sudo systemctl start docker"
    echo "    sudo systemctl enable docker"
    echo ""
    echo "  Linux (CentOS/RHEL):"
    echo "    sudo yum install docker"
    echo "    sudo systemctl start docker"
    echo "    sudo systemctl enable docker"
    echo ""
    echo "  Windows:"
    echo "    Download Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo ""
    echo "After installation, make sure Docker is running and try again."
    echo ""
    echo "To verify Docker is installed:"
    echo "  docker --version"
    echo ""
    echo "For detailed installation guide, see: docs/DOCKER_INSTALLATION.md"
    echo ""
    echo "============================================================"
    echo ""
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo ""
    echo "============================================================"
    echo "ERROR: Docker daemon is not running"
    echo "============================================================"
    echo ""
    echo "Please start Docker Desktop or the Docker daemon and try again."
    echo ""
    echo "On macOS:"
    echo "  - Open Docker Desktop from Applications"
    echo "  - Wait for it to start (whale icon in menu bar)"
    echo "  - Check status: docker info"
    echo ""
    echo "On Linux:"
    echo "  sudo systemctl start docker"
    echo "  sudo systemctl status docker"
    echo ""
    echo "Verify Docker is running:"
    echo "  docker info"
    echo ""
    echo "============================================================"
    echo ""
    exit 1
fi

echo "============================================================"
echo "Building Docker Image"
echo "============================================================"

# Build Docker image
docker build -t "${IMAGE_NAME}:latest" .

echo ""
echo "============================================================"
echo "Docker Image Built Successfully"
echo "============================================================"

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping existing container..."
    docker stop "${CONTAINER_NAME}" > /dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true
fi

echo ""
echo "============================================================"
echo "Starting Docker Container"
echo "============================================================"

# Run container
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p 8000:8000 \
    "${IMAGE_NAME}:latest"

echo "Container started. Waiting for API to be ready..."
sleep 5

# Test API
echo ""
echo "============================================================"
echo "Testing API"
echo "============================================================"

if command -v curl > /dev/null; then
    # Test health endpoint
    echo "Testing /health endpoint..."
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "Health check failed"
    
    echo ""
    echo "Testing /predict endpoint..."
    curl -s -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d '{
            "age": 63,
            "sex": 1,
            "cp": 1,
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 2,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 3,
            "ca": 0,
            "thal": 6
        }' | python3 -m json.tool || echo "Prediction test failed"
else
    echo "curl not found. Please test manually at http://localhost:8000/docs"
fi

echo ""
echo "============================================================"
echo "Container is running!"
echo "============================================================"
echo "API URL: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/health"
echo ""
echo "To stop the container: docker stop ${CONTAINER_NAME}"
echo "To view logs: docker logs ${CONTAINER_NAME}"
echo "============================================================"
