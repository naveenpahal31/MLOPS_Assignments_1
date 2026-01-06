# Heart Disease API - Kubernetes Deployment Script (PowerShell)
# This script helps deploy the API to Kubernetes on Windows

# Configuration
$DOCKER_USERNAME = "2024aa05871"
$IMAGE_NAME = "heart-disease-api"
$K8S_DIR = "k8s"

Write-Host "=== Heart Disease API Kubernetes Deployment ===" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check kubectl
try {
    $null = kubectl version --client 2>$null
    Write-Host "✓ kubectl is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check cluster connection
try {
    $null = kubectl cluster-info 2>$null
    Write-Host "✓ Connected to Kubernetes cluster" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to Kubernetes cluster. Please configure kubectl first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Display cluster info
Write-Host "Current Kubernetes context:" -ForegroundColor Yellow
kubectl config current-context
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to deploy to this cluster? (y/n)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Deploy application
Write-Host ""
Write-Host "Deploying application..." -ForegroundColor Yellow

Write-Host "Applying deployment manifest..." -ForegroundColor Yellow
kubectl apply -f "$K8S_DIR/deployment.yaml"

Write-Host "Applying service manifest..." -ForegroundColor Yellow
kubectl apply -f "$K8S_DIR/service.yaml"

Write-Host "✓ Manifests applied successfully" -ForegroundColor Green
Write-Host ""

# Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/heart-disease-api

Write-Host "✓ Deployment is ready" -ForegroundColor Green
Write-Host ""

# Show deployment status
Write-Host "Deployment Status:" -ForegroundColor Yellow
kubectl get deployments -l app=heart-disease-api
Write-Host ""

Write-Host "Pod Status:" -ForegroundColor Yellow
kubectl get pods -l app=heart-disease-api
Write-Host ""

Write-Host "Service Status:" -ForegroundColor Yellow
kubectl get service heart-disease-api-service
Write-Host ""

# Get service endpoint
Write-Host "Getting service endpoint..." -ForegroundColor Yellow
$SERVICE_TYPE = kubectl get service heart-disease-api-service -o jsonpath='{.spec.type}'

if ($SERVICE_TYPE -eq "LoadBalancer") {
    Write-Host "Waiting for external IP (this may take a few minutes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    $EXTERNAL_IP = kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
    if ([string]::IsNullOrEmpty($EXTERNAL_IP)) {
        $EXTERNAL_IP = kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
    }
    
    if (![string]::IsNullOrEmpty($EXTERNAL_IP)) {
        $API_URL = "http://$EXTERNAL_IP"
        Write-Host "✓ External IP: $EXTERNAL_IP" -ForegroundColor Green
    } else {
        Write-Host "⚠ External IP not yet assigned. Check again with: kubectl get service heart-disease-api-service" -ForegroundColor Yellow
    }
} elseif ($SERVICE_TYPE -eq "NodePort") {
    $NODE_PORT = kubectl get service heart-disease-api-service -o jsonpath='{.spec.ports[0].nodePort}'
    $NODE_IP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}'
    if ([string]::IsNullOrEmpty($NODE_IP)) {
        $NODE_IP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
    }
    $API_URL = "http://${NODE_IP}:${NODE_PORT}"
    Write-Host "✓ NodePort: $NODE_PORT" -ForegroundColor Green
    Write-Host "✓ Node IP: $NODE_IP" -ForegroundColor Green
}

# Test API if URL is available
if (![string]::IsNullOrEmpty($API_URL)) {
    Write-Host ""
    Write-Host "Testing API endpoints..." -ForegroundColor Yellow
    
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "$API_URL/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "✓ Health check passed" -ForegroundColor Green
        $response.Content
    } catch {
        Write-Host "⚠ Health check not responding yet (pods may still be initializing)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "API URL: $API_URL" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available endpoints:" -ForegroundColor Yellow
    Write-Host "  - GET  $API_URL/ - API information" -ForegroundColor Green
    Write-Host "  - GET  $API_URL/health - Health check" -ForegroundColor Green
    Write-Host "  - POST $API_URL/predict - Single prediction" -ForegroundColor Green
    Write-Host "  - POST $API_URL/predict/batch - Batch prediction" -ForegroundColor Green
    Write-Host "  - GET  $API_URL/model/info - Model information" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  kubectl get pods -l app=heart-disease-api"
Write-Host "  kubectl logs -f -l app=heart-disease-api"
Write-Host "  kubectl describe deployment heart-disease-api"
Write-Host "  kubectl get service heart-disease-api-service"

# HPA status
try {
    $null = kubectl get hpa heart-disease-api-hpa 2>$null
    Write-Host ""
    Write-Host "Horizontal Pod Autoscaler Status:" -ForegroundColor Yellow
    kubectl get hpa heart-disease-api-hpa
} catch {
    # HPA not found, skip
}

Write-Host ""
Write-Host "To delete the deployment:" -ForegroundColor Yellow
Write-Host "  kubectl delete -f $K8S_DIR/"
