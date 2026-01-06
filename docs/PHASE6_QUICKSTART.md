# Phase 6: Quick Start Guide

## Prerequisites Checklist

- [ ] Models are trained (run `python src/models/train.py`)
- [ ] Docker is installed (check with `docker --version`)
- [ ] Docker is running (check with `docker info`)

## Option 1: Run API Locally (No Docker)

### Step 1: Train Models (if not done)
```bash
python src/models/train.py
```

### Step 2: Start API Server
```bash
python scripts/run_api_local.py
```

### Step 3: Test API
Open in browser: http://localhost:8000/docs

Or use the test script (in another terminal):
```bash
python scripts/test_api.py
```

**That's it!** The API is running at http://localhost:8000

---

## Option 2: Run API with Docker

### Step 1: Install Docker (if not installed)

**macOS:**
```bash
brew install --cask docker
# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
```

**Windows:** Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Verify:**
```bash
docker --version
docker info
```

### Step 2: Train Models (if not done)
```bash
python src/models/train.py
```

### Step 3: Build and Run (Automated)
```bash
bash scripts/build_and_test_docker.sh
```

**Important**: Make sure to run with `bash` (not `zsh` or `sh`)

This script will:
- ✅ Check if Docker is installed
- ✅ Check if Docker daemon is running
- ✅ Build the Docker image
- ✅ Start the container
- ✅ Test the API endpoints

**If you see an error about Docker not running:**
1. On macOS: Open Docker Desktop from Applications
2. Wait for Docker to start (check menu bar for whale icon)
3. Verify: `docker info`
4. Run the script again

### Step 3 Alternative: Manual Steps

```bash
# Build image
docker build -t heart-disease-api:latest .

# Run container
docker run -d -p 8000:8000 --name heart-disease-api heart-disease-api:latest

# Check logs
docker logs heart-disease-api

# Test API
curl http://localhost:8000/health
```

### Step 4: Access API

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000

---

## Quick Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Single Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Model Info
```bash
curl http://localhost:8000/model/info
```

### Interactive Testing
Open http://localhost:8000/docs in your browser for Swagger UI

---

## Common Commands

### Docker Management

```bash
# View running containers
docker ps

# View logs
docker logs heart-disease-api

# Stop container
docker stop heart-disease-api

# Start container
docker start heart-disease-api

# Remove container
docker rm heart-disease-api

# Remove image
docker rmi heart-disease-api:latest
```

### API Management

```bash
# Run API locally
python scripts/run_api_local.py

# Test API
python scripts/test_api.py

# Run with custom port
uvicorn src.api.app:app --host 0.0.0.0 --port 8080
```

---

## Troubleshooting

### "Docker not found"
→ Install Docker (see Step 1 above) or use Option 1 (run locally)

### "Model not loaded"
→ Train models first: `python src/models/train.py`

### "Port 8000 already in use"
→ Use a different port: `docker run -d -p 8001:8000 ...`

### "Container won't start"
→ Check logs: `docker logs heart-disease-api`

### "API not responding"
→ Check if container is running: `docker ps`
→ Check health: `curl http://localhost:8000/health`

---

## Next Steps

After Phase 6 is working:
- **Phase 7**: Kubernetes deployment
- **Phase 8**: Monitoring and logging

---

## Full Documentation

For detailed information, see:
- [Phase 6 Containerization Guide](PHASE6_CONTAINERIZATION.md)
- [Docker Installation Guide](DOCKER_INSTALLATION.md)
- [Phase 6 Summary](PHASE6_SUMMARY.md)

