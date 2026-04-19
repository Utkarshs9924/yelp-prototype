#!/bin/bash

# Build all Docker images for Yelp Prototype Lab 2
# Usage: ./build-images.sh

echo "🐳 Building Docker images for Yelp Prototype Lab 2"
echo "=================================================="

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# AWS ECR configuration
AWS_ACCOUNT_ID="149410638858"
AWS_REGION="us-east-1"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Services to build
SERVICES=(
  "user-api"
  "user-worker"
  "restaurant-api"
  "restaurant-worker"
  "review-api"
  "review-worker"
)

# Build backend services
for service in "${SERVICES[@]}"; do
  echo ""
  echo "📦 Building $service..."
  docker build \
    -f "services/${service}/Dockerfile" \
    -t "yelp-${service}:latest" \
    -t "${ECR_REGISTRY}/yelp-${service}:latest" \
    .
  
  if [ $? -eq 0 ]; then
    echo "✅ $service built successfully"
  else
    echo "❌ Failed to build $service"
    exit 1
  fi
done

# Build frontend
echo ""
echo "📦 Building frontend..."
docker build \
  -f "frontend/Dockerfile" \
  -t "yelp-frontend:latest" \
  -t "${ECR_REGISTRY}/yelp-frontend:latest" \
  ./frontend

if [ $? -eq 0 ]; then
  echo "✅ Frontend built successfully"
else
  echo "❌ Failed to build frontend"
  exit 1
fi

echo ""
echo "=================================================="
echo "✅ All images built successfully!"
echo ""
echo "📋 Built images:"
docker images | grep yelp | grep latest

echo ""
echo "Next steps:"
echo "1. Run locally: docker-compose up"
echo "2. Push to ECR: ./deploy/push-to-ecr.sh"
echo "3. Deploy to EKS: kubectl apply -f k8s/"
