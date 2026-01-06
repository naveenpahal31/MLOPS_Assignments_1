# Phase 7: Production Deployment - Quick Start Guide

## 🚀 Quick Start (Without Docker Installed Locally)

Since you don't have Docker installed on your machine, follow these steps to deploy using Docker Hub and Kubernetes.

---

## Step 1: Build and Push Docker Image (Choose One Method)

### Method A: GitHub Actions (Recommended - Automated)

1. **Set up Docker Hub Token**:
   - Go to https://hub.docker.com/settings/security
   - Click "New Access Token"
   - Name it: `github-actions-token`
   - Copy the token

2. **Add Token to GitHub**:
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DOCKER_HUB_TOKEN`
   - Value: Paste the token from step 1

3. **Trigger Build**:
   ```bash
   # Commit and push your changes
   git add .
   git commit -m "Add Phase 7 deployment files"
   git push origin main
   ```
   
   GitHub Actions will automatically build and push your Docker image to `2024aa05871/heart-disease-api:latest`

4. **Monitor Build**:
   - Go to GitHub → Actions tab
   - Watch the "Build and Push Docker Image" workflow

### Method B: Play with Docker (Manual - 5 minutes)

1. Go to https://labs.play-with-docker.com/
2. Login and click "Start"
3. Click "Add New Instance"
4. Run these commands:

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Login to Docker Hub
docker login -u 2024aa05871
# Enter your Docker Hub password

# Build the image
docker build -t 2024aa05871/heart-disease-api:latest .

# Push to Docker Hub
docker push 2024aa05871/heart-disease-api:latest
```

### Method C: Google Cloud Shell (Free)

1. Go to https://console.cloud.google.com/
2. Click the Cloud Shell icon (top right)
3. Run:

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Login to Docker Hub
docker login -u 2024aa05871

# Build and push
docker build -t 2024aa05871/heart-disease-api:latest .
docker push 2024aa05871/heart-disease-api:latest
```

---

## Step 2: Deploy to Kubernetes (Choose One Platform)

### Option A: Google Kubernetes Engine (GKE) - Cloud

#### Prerequisites
- Google Cloud account (free tier available)
- Install `gcloud` CLI: https://cloud.google.com/sdk/docs/install

#### Steps

1. **Setup GKE Cluster**:
```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Create cluster
gcloud container clusters create heart-disease-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium

# Get credentials
gcloud container clusters get-credentials heart-disease-cluster --zone us-central1-a
```

2. **Deploy Application**:
```bash
# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services

# Wait for external IP (takes 2-5 minutes)
kubectl get service heart-disease-api-service -w
```

3. **Test API**:
```bash
# Get external IP
export EXTERNAL_IP=$(kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test
curl http://$EXTERNAL_IP/health
```

### Option B: Minikube - Local (Free)

#### Prerequisites
- Install Minikube: https://minikube.sigs.k8s.io/docs/start/
- Install kubectl: https://kubernetes.io/docs/tasks/tools/

#### Steps

1. **Start Minikube**:
```bash
# Start cluster
minikube start --cpus 2 --memory 4096

# Enable metrics (for autoscaling)
minikube addons enable metrics-server
```

2. **Deploy Application**:
```bash
# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services
```

3. **Access API**:
```bash
# Get service URL
minikube service heart-disease-api-service --url

# Test (use the URL from above)
curl $(minikube service heart-disease-api-service --url)/health
```

### Option C: Play with Kubernetes - Free Online

1. Go to https://labs.play-with-k8s.com/
2. Login and click "Start"
3. Click "Add New Instance"
4. Initialize cluster:

```bash
# Initialize master
kubeadm init --apiserver-advertise-address $(hostname -i) --pod-network-cidr 10.5.0.0/16

# Copy the join command shown

# Setup network
kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/master/daemonset/kubeadm-kuberouter.yaml

# Deploy your app
kubectl apply -f https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/k8s/deployment.yaml
kubectl apply -f https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/k8s/service.yaml
```

---

## Step 3: Verify Deployment

### Check Pod Status
```bash
kubectl get pods -l app=heart-disease-api
kubectl logs -l app=heart-disease-api --tail=50
```

### Test API Endpoints

**Get API URL**:
```bash
# For GKE/AKS/EKS (LoadBalancer)
export API_URL=http://$(kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# For Minikube
export API_URL=$(minikube service heart-disease-api-service --url)
```

**Test Endpoints**:
```bash
# Health check
curl $API_URL/health

# API info
curl $API_URL/

# Model info
curl $API_URL/model/info

# Single prediction
curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 63, "sex": 1, "cp": 1, "trestbps": 145,
    "chol": 233, "fbs": 1, "restecg": 2, "thalach": 150,
    "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6
  }'
```

---

## Step 4: Capture Screenshots for Assignment

### 1. Docker Hub
- Navigate to: https://hub.docker.com/r/2024aa05871/heart-disease-api
- Take screenshot showing your image

### 2. Kubernetes Deployment
```bash
# Run these commands and capture screenshots

# Deployment overview
kubectl get all -l app=heart-disease-api

# Detailed deployment
kubectl describe deployment heart-disease-api

# Pod status
kubectl get pods -o wide

# Service with external IP
kubectl get service heart-disease-api-service
```

### 3. API Testing
```bash
# Capture these curl commands and their JSON responses

curl $API_URL/health
curl $API_URL/
curl $API_URL/model/info

curl -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1, "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6}'
```

### 4. Monitoring
```bash
# Logs
kubectl logs -l app=heart-disease-api --tail=50

# Resource usage (if metrics-server is enabled)
kubectl top pods
kubectl top nodes

# HPA status
kubectl get hpa
```

---

## Step 5: Cleanup (When Done)

```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# For GKE - delete cluster to avoid charges
gcloud container clusters delete heart-disease-cluster --zone us-central1-a

# For Minikube
minikube stop
minikube delete
```

---

## Troubleshooting

### Image Pull Errors
```bash
# Verify image exists on Docker Hub
docker pull 2024aa05871/heart-disease-api:latest

# Check if deployment can pull
kubectl describe pod <pod-name>
```

### Pod Not Starting
```bash
# Check pod logs
kubectl logs <pod-name>

# Check pod events
kubectl describe pod <pod-name>

# Common fix: Ensure models/ directory has trained models
```

### Service Not Accessible
```bash
# For LoadBalancer, external IP may take 2-5 minutes
kubectl get service heart-disease-api-service -w

# For Minikube, use minikube service command
minikube service heart-disease-api-service
```

---

## Using PowerShell Deployment Script (Windows)

```powershell
# Navigate to project directory
cd "path\to\your\project"

# Run deployment script
.\scripts\deploy_k8s.ps1
```

---

## Summary Checklist

- [ ] Docker image built and pushed to `2024aa05871/heart-disease-api:latest`
- [ ] Kubernetes cluster created (GKE/Minikube/PWK)
- [ ] Deployment applied (`kubectl apply -f k8s/deployment.yaml`)
- [ ] Service applied (`kubectl apply -f k8s/service.yaml`)
- [ ] Pods running (`kubectl get pods`)
- [ ] External IP assigned (`kubectl get service`)
- [ ] Health endpoint working (`curl $API_URL/health`)
- [ ] Prediction endpoint working
- [ ] Screenshots captured for submission

---

## What You've Achieved ✅

1. **Containerization**: Dockerized the FastAPI application
2. **Cloud Deployment**: Deployed to Kubernetes cluster
3. **High Availability**: 2 replicas with autoscaling
4. **Load Balancing**: External LoadBalancer service
5. **Health Monitoring**: Liveness and readiness probes
6. **Production Ready**: Resource limits, security, and best practices

**Docker Hub**: https://hub.docker.com/r/2024aa05871/heart-disease-api

---

For detailed instructions, see [PHASE7_PRODUCTION_DEPLOYMENT.md](PHASE7_PRODUCTION_DEPLOYMENT.md)
