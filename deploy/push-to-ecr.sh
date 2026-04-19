#!/bin/bash

# Push Docker images to AWS ECR
# Usage: ./push-to-ecr.sh

echo "🚀 Pushing Docker images to AWS ECR"
echo "===================================="

# AWS configuration
AWS_ACCOUNT_ID="149410638858"
AWS_REGION="us-east-1"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login to ECR
echo ""
echo "🔐 Logging in to AWS ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY}

if [ $? -ne 0 ]; then
  echo "❌ Failed to login to ECR"
  exit 1
fi

echo "✅ Successfully logged in to ECR"

# Images to push
IMAGES=(
  "yelp-user-api"
  "yelp-user-worker"
  "yelp-restaurant-api"
  "yelp-restaurant-worker"
  "yelp-review-api"
  "yelp-review-worker"
  "yelp-frontend"
)

# Push each image
for image in "${IMAGES[@]}"; do
  echo ""
  echo "📤 Pushing ${image}:latest..."
  docker push "${ECR_REGISTRY}/${image}:latest"
  
  if [ $? -eq 0 ]; then
    echo "✅ ${image} pushed successfully"
  else
    echo "❌ Failed to push ${image}"
    exit 1
  fi
done

echo ""
echo "===================================="
echo "✅ All images pushed to ECR!"
echo ""
echo "📋 Images in ECR:"
aws ecr list-images --repository-name yelp-user-api --region ${AWS_REGION} | grep imageTag

echo ""
echo "Next step: Deploy to EKS"
echo "  kubectl apply -f k8s/"
