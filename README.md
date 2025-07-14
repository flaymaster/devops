# DevOps Project

## Overview

This repository manages a cloud-native application using AWS CDK, Docker, and supporting scripts and CI/CD workflows. The structure is designed for modularity, automation, and best practices in infrastructure-as-code and containerization.

---

## Project Structure

### 1. `cdk-app/`
Contains the AWS CDK application, which defines your cloud infrastructure as code.

- **Stacks:**
  - **Runner Stack:**
    - Provisions the core compute and messaging resources:
      - **ECS Fargate Service** (with its own task definition and IAM role)
      - **Application Load Balancer (ALB)** to expose the service
      - **SQS Queue** for messaging
      - **Lambda Function** that can be triggered by SQS
  - **Retainable Resources Stack:**
    - Provisions persistent resources:
      - **S3 Bucket** for storage
      - **SSM Parameter Store** entry for securely storing a token

### 2. `docker/`
Contains two Dockerized applications:

- **`rest-docker/`**: The main service that runs on ECS Fargate, exposed via the ALB.
- **`queue-docker/`**: A service designed to be triggered by SQS messages.

### 3. `scripts/`
Contains helper scripts to build and package your artifacts, such as:

- Building Docker images
- Building and deploying the CDK app

### 4. CI/CD YAML Files
There are two main workflow files:

1. **Docker Build & Push Workflow:**
   - Builds the Docker images and pushes them to Amazon ECR.
2. **CDK Build & Deploy Workflow:**
   - Builds and deploys the CDK application, accepting a Docker tag as input to specify which Docker image version to use in the deployment.

---

This structure enables you to manage both your infrastructure and application code in a modular, automated, and cloud-native way.