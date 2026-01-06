#!/bin/bash

# Heart Disease API - Kubernetes Deployment Script
# This script helps deploy the API to Kubernetes

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="2024aa05871"
IMAGE_NAME="heart-disease-api"
K8S_DIR="k8s"

echo -e "${GREEN}=== Heart Disease API Kubernetes Deployment ===${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command_exists kubectl; then
    echo -e "${RED}❌ kubectl is not installed. Please install it first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check if kubectl can connect to cluster
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster. Please configure kubectl first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Kubernetes cluster${NC}\n"

# Display cluster info
echo -e "${YELLOW}Current Kubernetes context:${NC}"
kubectl config current-context
echo ""

# Ask for confirmation
read -p "Do you want to deploy to this cluster? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Deploy application
echo -e "\n${YELLOW}Deploying application...${NC}"

echo -e "${YELLOW}Applying deployment manifest...${NC}"
kubectl apply -f "$K8S_DIR/deployment.yaml"

echo -e "${YELLOW}Applying service manifest...${NC}"
kubectl apply -f "$K8S_DIR/service.yaml"

echo -e "${GREEN}✓ Manifests applied successfully${NC}\n"

# Wait for deployment to be ready
echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/heart-disease-api

echo -e "${GREEN}✓ Deployment is ready${NC}\n"

# Show deployment status
echo -e "${YELLOW}Deployment Status:${NC}"
kubectl get deployments -l app=heart-disease-api
echo ""

echo -e "${YELLOW}Pod Status:${NC}"
kubectl get pods -l app=heart-disease-api
echo ""

echo -e "${YELLOW}Service Status:${NC}"
kubectl get service heart-disease-api-service
echo ""

# Get service endpoint
echo -e "${YELLOW}Getting service endpoint...${NC}"
SERVICE_TYPE=$(kubectl get service heart-disease-api-service -o jsonpath='{.spec.type}')

if [ "$SERVICE_TYPE" = "LoadBalancer" ]; then
    echo -e "${YELLOW}Waiting for external IP (this may take a few minutes)...${NC}"
    kubectl wait --for=jsonpath='{.status.loadBalancer.ingress}' service/heart-disease-api-service --timeout=300s 2>/dev/null || true
    
    EXTERNAL_IP=$(kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -z "$EXTERNAL_IP" ]; then
        EXTERNAL_IP=$(kubectl get service heart-disease-api-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    fi
    
    if [ -n "$EXTERNAL_IP" ]; then
        API_URL="http://$EXTERNAL_IP"
        echo -e "${GREEN}✓ External IP: $EXTERNAL_IP${NC}"
    else
        echo -e "${YELLOW}⚠ External IP not yet assigned. Check again with: kubectl get service heart-disease-api-service${NC}"
    fi
elif [ "$SERVICE_TYPE" = "NodePort" ]; then
    NODE_PORT=$(kubectl get service heart-disease-api-service -o jsonpath='{.spec.ports[0].nodePort}')
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
    if [ -z "$NODE_IP" ]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    fi
    API_URL="http://$NODE_IP:$NODE_PORT"
    echo -e "${GREEN}✓ NodePort: $NODE_PORT${NC}"
    echo -e "${GREEN}✓ Node IP: $NODE_IP${NC}"
fi

# Test API if URL is available
if [ -n "$API_URL" ]; then
    echo -e "\n${YELLOW}Testing API endpoints...${NC}"
    
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    if curl -s -f "$API_URL/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Health check passed${NC}"
        curl -s "$API_URL/health" | jq '.' 2>/dev/null || curl -s "$API_URL/health"
    else
        echo -e "${YELLOW}⚠ Health check not responding yet (pods may still be initializing)${NC}"
    fi
    
    echo -e "\n${YELLOW}API URL: ${GREEN}$API_URL${NC}"
    echo -e "\n${YELLOW}Available endpoints:${NC}"
    echo -e "  - ${GREEN}GET  $API_URL/${NC} - API information"
    echo -e "  - ${GREEN}GET  $API_URL/health${NC} - Health check"
    echo -e "  - ${GREEN}POST $API_URL/predict${NC} - Single prediction"
    echo -e "  - ${GREEN}POST $API_URL/predict/batch${NC} - Batch prediction"
    echo -e "  - ${GREEN}GET  $API_URL/model/info${NC} - Model information"
fi

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  kubectl get pods -l app=heart-disease-api"
echo -e "  kubectl logs -f -l app=heart-disease-api"
echo -e "  kubectl describe deployment heart-disease-api"
echo -e "  kubectl get service heart-disease-api-service"

# HPA status
if kubectl get hpa heart-disease-api-hpa &>/dev/null; then
    echo -e "\n${YELLOW}Horizontal Pod Autoscaler Status:${NC}"
    kubectl get hpa heart-disease-api-hpa
fi

echo -e "\n${YELLOW}To delete the deployment:${NC}"
echo -e "  kubectl delete -f $K8S_DIR/"
