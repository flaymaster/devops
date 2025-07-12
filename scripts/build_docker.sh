#!/bin/bash
set -e

AWS_REGION="us-east-1"
SERVICE=${1}
TAG=${2:-latest}

if [ -z "$SERVICE" ]; then
  echo "Usage: $0 <service-name> [tag]"
  exit 1
fi
cur_dir=$(pwd)
ECR_URI="472765722896.dkr.ecr.us-east-1.amazonaws.com/$SERVICE"
DOCKER_DIR="docker"

# Login to ECR
docker login --username AWS -p $(aws ecr get-login-password --region $AWS_REGION) 472765722896.dkr.ecr.us-east-1.amazonaws.com

IMAGE_NAME="$SERVICE"
REPO_NAME="$SERVICE"

# Create ECR repo if it doesn't exist
if ! aws ecr describe-repositories --repository-names "$REPO_NAME" > /dev/null 2>&1; then
    aws ecr create-repository --repository-name "$REPO_NAME"
    echo "Created ECR repository: $REPO_NAME"
fi
cd $cur_dir
docker build -t ${SERVICE}:${TAG} -f $DOCKER_DIR/$SERVICE/Dockerfile . &&
docker tag ${SERVICE}:${TAG} ${ECR_URI}/${SERVICE}:${TAG} &&
docker push ${ECR_URI}/${SERVICE}:${TAG}