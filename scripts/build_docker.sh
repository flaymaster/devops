#!/bin/bash
set -e

AWS_REGION="us-east-1"
ECR_URI="${AWS_ECR_DEPLOYMENT_ACCOUNT_URI}"
DOCKER_SERVICES=("rest-docker" "backend-docker")
DOCKER_DIR="services/docker"
TAG=${1:-latest}

# Login to ECR
docker login --username AWS -p $(aws ecr get-login-password --region $AWS_REGION) $ECR_URI

for SERVICE in "${DOCKER_SERVICES[@]}"; do
    IMAGE_NAME="${SERVICE}"
    REPO_NAME="${SERVICE}"

    # Create ECR repo if it doesn't exist
    if ! aws ecr describe-repositories --repository-names "$REPO_NAME" > /dev/null 2>&1; then
        aws ecr create-repository --repository-name "$REPO_NAME"
        echo "Created ECR repository: $REPO_NAME"
    fi

    # Build and push (single arch, simple)
    docker build -t $ECR_URI/$REPO_NAME:$TAG $DOCKER_DIR/$SERVICE
    docker push $ECR_URI/$REPO_NAME:$TAG

    # If you want multi-arch, use buildx:
    # docker buildx build --platform linux/amd64,linux/arm64 -t $ECR_URI/$REPO_NAME:$TAG --push $DOCKER_DIR/$SERVICE
done