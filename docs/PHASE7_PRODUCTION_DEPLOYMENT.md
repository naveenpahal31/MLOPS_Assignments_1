# Phase 7: Production Deployment

## Overview

This guide provides step-by-step instructions for deploying the Heart Disease Prediction API to production using Docker Hub and Kubernetes. Since Docker is not installed locally, we'll use GitHub Actions or a cloud-based build service to build and push the Docker image to Docker Hub.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building and Pushing Docker Image](#building-and-pushing-docker-image)
3. [Deployment Options](#deployment-options)
4. [Testing the Deployment](#testing-the-deployment)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Screenshots for Assignment](#screenshots-for-assignment)

---

## Prerequisites

### Required Accounts and Tools

1. **Docker Hub Account**: `2024aa05871` (provided)
2. **Trained Model**: Ensure you have a trained model in the `models/` directory
3. **Kubernetes Cluster** (choose one):
   - **Google Kubernetes Engine (GKE)** - Recommended for cloud
   - **Amazon EKS** - Alternative cloud option
   - **Azure AKS** - Alternative cloud option
   - **Minikube** - Local development (requires Docker Desktop)
   - **Docker Desktop Kubernetes** - Local development
   - **Play with Kubernetes** (PWK) - Free online K8s playground

### Install kubectl

```bash
# Windows (PowerShell)
choco install kubernetes-cli

# Or download from:
# https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

# Verify installation
kubectl version --client
```

---

## Building and Pushing Docker Image

Since you don't have Docker installed locally, you have three options:

### Option 1: GitHub Actions (Recommended)

Create `.github/workflows/docker-build.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: 2024aa05871
          password: ${{ secrets.DOCKER_HUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            2024aa05871/heart-disease-api:latest
            2024aa05871/heart-disease-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Steps:**
1. Go to Docker Hub → Account Settings → Security → New Access Token
2. Copy the token
3. Go to your GitHub repository → Settings → Secrets and variables → Actions
4. Create new secret: `DOCKER_HUB_TOKEN` with your Docker Hub token
5. Commit the workflow file and push to GitHub
6. GitHub Actions will automatically build and push your image

### Option 2: Play with Docker (PWD)

1. Go to https://labs.play-with-docker.com/
2. Login and start a new session
3. Clone your repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
4. Login to Docker Hub:
   ```bash
   docker login -u 2024aa05871
   # Enter your password when prompted
   ```
5. Build the image:
   ```bash
   docker build -t 2024aa05871/heart-disease-api:latest .
   ```
6. Push to Docker Hub:
   ```bash
   docker push 2024aa05871/heart-disease-api:latest
   ```

### Option 3: Cloud Shell (GCP/AWS/Azure)

Use Google Cloud Shell, AWS CloudShell, or Azure Cloud Shell which have Docker pre-installed:

```bash
# Clone your repository
git clone <your-repo-url>
cd <your-repo-directory>

# Login to Docker Hub
docker login -u 2024aa05871

# Build and push
docker build -t 2024aa05871/heart-disease-api:latest .
docker push 2024aa05871/heart-disease-api:latest
```

---

## Deployment Options

### Option A: Google Kubernetes Engine (GKE) - Recommended

#### Step 1: Create GKE Cluster

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create heart-disease-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 3

# Get credentials
gcloud container clusters get-credentials heart-disease-cluster --zone us-central1-a
```

#### Step 2: Deploy Application

```bash
# Apply deployment and service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# Get external IP (may take a few minutes)
kubectl get service heart-disease-api-service -w
```

#### Step 3: Access the API

```bash
# Get the external IP
export EXTERNAL_IP=$(kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test the API
curl http://$EXTERNAL_IP/health
curl http://$EXTERNAL_IP/
```

### Option B: Minikube (Local Development)

```bash
# Start Minikube
minikube start --cpus 2 --memory 4096

# Enable metrics server (for HPA)
minikube addons enable metrics-server

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Get service URL
minikube service heart-disease-api-service --url

# Test the API
curl $(minikube service heart-disease-api-service --url)/health
```

### Option C: Play with Kubernetes (Free Online)

1. Go to https://labs.play-with-k8s.com/
2. Initialize master node:
   ```bash
   kubeadm init --apiserver-advertise-address $(hostname -i) --pod-network-cidr 10.5.0.0/16
   ```
3. Copy the join command for worker nodes
4. Set up kubectl:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/master/daemonset/kubeadm-kuberouter.yaml
   ```
5. Deploy your application:
   ```bash
   # You'll need to upload your YAML files or create them
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

---

## Testing the Deployment

### 1. Check Pod Status

```bash
# Check if pods are running
kubectl get pods -l app=heart-disease-api

# Check logs
kubectl logs -l app=heart-disease-api --tail=50

# Describe pod for more details
kubectl describe pod <pod-name>
```

### 2. Test API Endpoints

```bash
# Get service endpoint
kubectl get service heart-disease-api-service

# For LoadBalancer
export API_URL=http://<EXTERNAL-IP>

# For Minikube
export API_URL=$(minikube service heart-disease-api-service --url)

# Test health endpoint
curl $API_URL/health

# Test root endpoint
curl $API_URL/

# Test prediction endpoint
curl -X POST $API_URL/predict \
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
  }'
```

### 3. Test Batch Prediction

```bash
curl -X POST $API_URL/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "age": 63, "sex": 1, "cp": 1, "trestbps": 145,
        "chol": 233, "fbs": 1, "restecg": 2, "thalach": 150,
        "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6
      },
      {
        "age": 67, "sex": 1, "cp": 4, "trestbps": 160,
        "chol": 286, "fbs": 0, "restecg": 2, "thalach": 108,
        "exang": 1, "oldpeak": 1.5, "slope": 2, "ca": 3, "thal": 3
      }
    ]
  }'
```

---

## Monitoring and Maintenance

### View Logs

```bash
# Stream logs from all pods
kubectl logs -f -l app=heart-disease-api

# View logs from specific pod
kubectl logs <pod-name> --tail=100

# View previous pod logs (if crashed)
kubectl logs <pod-name> --previous
```

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment heart-disease-api --replicas=3

# Check HPA status
kubectl get hpa
kubectl describe hpa heart-disease-api-hpa
```

### Update Deployment

```bash
# After pushing new image to Docker Hub
kubectl rollout restart deployment heart-disease-api

# Check rollout status
kubectl rollout status deployment heart-disease-api

# View rollout history
kubectl rollout history deployment heart-disease-api

# Rollback if needed
kubectl rollout undo deployment heart-disease-api
```

### Resource Monitoring

```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# Get detailed pod info
kubectl describe pod <pod-name>
```

---

## Screenshots for Assignment

Capture the following screenshots for your assignment submission:

### 1. Docker Hub

- Screenshot showing your Docker image in Docker Hub
- URL: https://hub.docker.com/r/2024aa05871/heart-disease-api

### 2. Kubernetes Deployment

```bash
# Capture these commands and their output:

# 1. Deployment status
kubectl get deployments -o wide

# 2. Pod status
kubectl get pods -o wide

# 3. Service with external IP
kubectl get services

# 4. HPA status
kubectl get hpa

# 5. Detailed deployment info
kubectl describe deployment heart-disease-api
```

### 3. API Testing

```bash
# Capture curl commands and responses:

# Health check
curl http://<EXTERNAL-IP>/health

# Root endpoint
curl http://<EXTERNAL-IP>/

# Prediction endpoint
curl -X POST http://<EXTERNAL-IP>/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6}'
```

### 4. Kubernetes Dashboard (Optional)

```bash
# For Minikube
minikube dashboard

# For GKE, use Google Cloud Console
# Navigate to: Kubernetes Engine → Workloads
```

### 5. Monitoring

- Screenshot of pod logs: `kubectl logs <pod-name>`
- Screenshot of resource usage: `kubectl top pods`

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# 1. Image pull error - verify Docker Hub image exists
# 2. Missing model files - ensure models/ directory has trained models
# 3. Resource limits - adjust in deployment.yaml
```

### Service Not Accessible

```bash
# Check service
kubectl get service heart-disease-api-service
kubectl describe service heart-disease-api-service

# For LoadBalancer, external IP may take time
kubectl get service heart-disease-api-service -w

# For Minikube, use:
minikube service heart-disease-api-service --url
```

### Health Check Failures

```bash
# Check if app is running in pod
kubectl exec -it <pod-name> -- curl localhost:8000/health

# Adjust probe timing in deployment.yaml if needed
```

---

## Cleanup

### Delete Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete individually
kubectl delete deployment heart-disease-api
kubectl delete service heart-disease-api-service
kubectl delete hpa heart-disease-api-hpa
```

### Delete GKE Cluster

```bash
gcloud container clusters delete heart-disease-cluster --zone us-central1-a
```

### Delete Minikube Cluster

```bash
minikube delete
```

---

## Alternative: Helm Chart Deployment

For a more advanced deployment, you can create a Helm chart:

```bash
# Create Helm chart
helm create heart-disease-chart

# Customize values.yaml with your image and settings

# Install
helm install heart-disease-api ./heart-disease-chart

# Upgrade
helm upgrade heart-disease-api ./heart-disease-chart

# Uninstall
helm uninstall heart-disease-api
```

---

## Summary

You have successfully:

1. ✅ Created a Dockerfile for containerizing the API
2. ✅ Built and pushed Docker image to Docker Hub
3. ✅ Created Kubernetes deployment manifests
4. ✅ Deployed to a Kubernetes cluster (GKE/EKS/AKS/Minikube)
5. ✅ Exposed API via LoadBalancer/Ingress
6. ✅ Verified endpoints are working
7. ✅ Captured screenshots for assignment submission

**Docker Hub Image**: `2024aa05871/heart-disease-api:latest`

**Key Features Implemented**:
- Multi-stage Docker build for optimization
- Health checks and readiness probes
- Horizontal Pod Autoscaling (HPA)
- Resource limits and requests
- High availability with multiple replicas
- LoadBalancer service for external access

---

## Next Steps

- Set up CI/CD pipeline for automated deployments
- Implement monitoring with Prometheus and Grafana
- Add logging aggregation with ELK stack
- Set up SSL/TLS with cert-manager
- Implement API authentication and rate limiting
- Add database for storing predictions
