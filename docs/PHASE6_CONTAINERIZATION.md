# Phase 6: Model Containerization

> **Quick Start**: For a fast setup guide, see [Phase 6 Quick Start](PHASE6_QUICKSTART.md)

## Overview

Phase 6 implements containerization of the Heart Disease Prediction API using Docker. This enables:
- Consistent deployment across environments
- Easy scaling and orchestration
- Isolation of dependencies
- Simplified deployment process

## Components

### 1. FastAPI Application (`src/api/app.py`)

RESTful API with the following endpoints:

- **GET `/`**: API information and available endpoints
- **GET `/health`**: Health check endpoint
- **POST `/predict`**: Single prediction endpoint
- **POST `/predict/batch`**: Batch prediction endpoint
- **GET `/model/info`**: Model information and metadata

#### Input Schema

The API accepts JSON with the following fields:

```json
{
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
}
```

#### Response Schema

```json
{
  "prediction": 1,
  "prediction_label": "Disease Present",
  "probability": 0.85,
  "confidence": 0.85
}
```

### 2. Dockerfile

Multi-stage Dockerfile that:
- Uses Python 3.9 slim base image
- Installs system and Python dependencies
- Copies application code and models
- Exposes port 8000
- Includes health check

### 3. Docker Configuration

- **`.dockerignore`**: Excludes unnecessary files from Docker build context
- **`docker/test_api.sh`**: Script to test containerized API

## Usage

### Prerequisites

1. **Train models first**: Ensure models are trained and saved in `models/` directory
   ```bash
   python src/models/train.py
   # or
   python src/models/train_with_mlflow.py
   ```

2. **Install Docker**: Ensure Docker is installed and running

   If Docker is not installed, follow the instructions below for your operating system:

   #### macOS
   - **Option 1 (Recommended)**: Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - **Option 2**: Install via Homebrew:
     ```bash
     brew install --cask docker
     ```
   - After installation, open Docker Desktop from Applications
   - Verify installation:
     ```bash
     docker --version
     docker info
     ```

   #### Linux (Ubuntu/Debian)
   ```bash
   # Update package index
   sudo apt-get update
   
   # Install Docker
   sudo apt-get install -y docker.io
   
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add your user to docker group (optional, to run without sudo)
   sudo usermod -aG docker $USER
   # Log out and log back in for group changes to take effect
   
   # Verify installation
   docker --version
   docker info
   ```

   #### Linux (CentOS/RHEL/Fedora)
   ```bash
   # Install Docker
   sudo yum install -y docker
   # Or on newer versions:
   # sudo dnf install -y docker
   
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add your user to docker group (optional)
   sudo usermod -aG docker $USER
   
   # Verify installation
   docker --version
   docker info
   ```

   #### Windows
   - Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Run the installer and follow the setup wizard
   - Restart your computer if prompted
   - Open Docker Desktop from the Start menu
   - Verify installation in PowerShell or Command Prompt:
     ```bash
     docker --version
     docker info
     ```

   #### Verify Docker is Running
   After installation, verify Docker is running:
   ```bash
   docker info
   ```
   
   If you see an error like "Cannot connect to the Docker daemon", make sure:
   - Docker Desktop is running (macOS/Windows)
   - Docker service is started (Linux): `sudo systemctl status docker`

### Running Locally (Without Docker)

```bash
# Start the API server
python scripts/run_api_local.py

# Or using uvicorn directly
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Building Docker Image

```bash
# Build the image
docker build -t heart-disease-api:latest .

# Verify image was created
docker images | grep heart-disease-api
```

### Running Docker Container

```bash
# Run container in detached mode
docker run -d -p 8000:8000 --name heart-disease-api heart-disease-api:latest

# View logs
docker logs heart-disease-api

# Follow logs
docker logs -f heart-disease-api

# Stop container
docker stop heart-disease-api

# Remove container
docker rm heart-disease-api
```

### Testing the API

#### Using the test script:
```bash
# Make sure API is running first
python scripts/test_api.py
```

#### Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @test_request.json

# Model info
curl http://localhost:8000/model/info
```

#### Using the interactive docs:
Open http://localhost:8000/docs in your browser for Swagger UI.

### Automated Build and Test

```bash
# Build, run, and test in one command
bash scripts/build_and_test_docker.sh
```

## API Endpoints Details

### GET `/health`

Returns the health status of the API and whether the model is loaded.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "API is ready to serve predictions"
}
```

### POST `/predict`

Makes a prediction for a single patient record.

**Request Body:** JSON object with patient features (see Input Schema above)

**Response:** PredictionResponse object with prediction, label, probability, and confidence

### POST `/predict/batch`

Makes predictions for multiple patient records.

**Request Body:** Array of JSON objects

**Response:**
```json
{
  "predictions": [
    {
      "prediction": 1,
      "prediction_label": "Disease Present",
      "probability": 0.85,
      "confidence": 0.85
    },
    ...
  ],
  "count": 2
}
```

### GET `/model/info`

Returns information about the loaded model.

**Response:**
```json
{
  "model_name": "random_forest",
  "model_type": "RandomForestClassifier",
  "preprocessor_loaded": true,
  "training_metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.88,
    "roc_auc": 0.91
  }
}
```

## Docker Image Details

### Image Size
- Base image: Python 3.9 slim (~45MB)
- With dependencies: ~500-600MB

### Ports
- **8000**: API server port (exposed)

### Environment Variables
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered
- `PYTHONDONTWRITEBYTECODE=1`: Prevents creation of .pyc files

### Health Check
The Dockerfile includes a health check that runs every 30 seconds:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

## Troubleshooting

### Model Not Found Error

If you see "Model not loaded" in the health check:

1. Ensure models are trained and saved:
   ```bash
   python src/models/train.py
   ```

2. Verify models exist:
   ```bash
   ls -la models/
   ```

3. Check model directory in Docker:
   ```bash
   docker exec heart-disease-api ls -la /app/models/
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
docker run -d -p 8001:8000 --name heart-disease-api heart-disease-api:latest
```

Then access the API at http://localhost:8001

### Container Won't Start

Check logs for errors:
```bash
docker logs heart-disease-api
```

Common issues:
- Missing models directory
- Missing dependencies
- Port conflicts

## Next Steps

After Phase 6, proceed to:
- **Phase 7**: Kubernetes deployment manifests
- **Phase 8**: Monitoring and logging integration

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

