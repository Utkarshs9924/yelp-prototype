#!/bin/bash

# Deploy Yelp Prototype to AWS EKS
# Usage: ./deploy-to-eks.sh

echo "☸️  Deploying Yelp Prototype to AWS EKS"
echo "========================================"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
K8S_DIR="${PROJECT_ROOT}/k8s"

# Check if kubectl is configured
echo ""
echo "🔍 Checking kubectl configuration..."
kubectl cluster-info

if [ $? -ne 0 ]; then
  echo "❌ kubectl is not configured properly"
  echo "Run: eksctl create cluster --name yelp-lab2 --region us-east-1"
  exit 1
fi

echo "✅ kubectl configured"

# Apply Kubernetes manifests in order
echo ""
echo "📦 Deploying Kubernetes resources..."

# 1. ConfigMap (must be first)
echo ""
echo "1️⃣  Creating ConfigMap..."
kubectl apply -f "${K8S_DIR}/configmap.yaml"

# 2. Zookeeper
echo ""
echo "2️⃣  Deploying Zookeeper..."
kubectl apply -f "${K8S_DIR}/zookeeper.yaml"
sleep 10

# 3. Kafka
echo ""
echo "3️⃣  Deploying Kafka..."
kubectl apply -f "${K8S_DIR}/kafka.yaml"
sleep 20

# 4. API Services
echo ""
echo "4️⃣  Deploying API Services..."
kubectl apply -f "${K8S_DIR}/user-api.yaml"
kubectl apply -f "${K8S_DIR}/restaurant-api.yaml"
kubectl apply -f "${K8S_DIR}/review-api.yaml"

# 5. Worker Services
echo ""
echo "5️⃣  Deploying Worker Services..."
kubectl apply -f "${K8S_DIR}/user-worker.yaml"
kubectl apply -f "${K8S_DIR}/restaurant-worker.yaml"
kubectl apply -f "${K8S_DIR}/review-worker.yaml"

# 6. Frontend
echo ""
echo "6️⃣  Deploying Frontend..."
kubectl apply -f "${K8S_DIR}/frontend.yaml"

# Wait for deployments
echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/user-api \
  deployment/restaurant-api \
  deployment/review-api \
  deployment/frontend

# Get service URLs
echo ""
echo "========================================"
echo "✅ Deployment complete!"
echo ""
echo "📋 Service URLs:"
kubectl get services

echo ""
echo "🔍 Check pod status:"
echo "  kubectl get pods"
echo ""
echo "📊 View logs:"
echo "  kubectl logs -f deployment/user-api"
echo ""
echo "🗑️  Delete cluster when done:"
echo "  eksctl delete cluster --name yelp-lab2 --region us-east-1"
