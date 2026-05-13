#!/bin/bash
# Cortex AI - AWS Deployment Script
# Generated: 2026-05-12T23:51:29.191Z

set -e

REGION="us-east-1"
STACK_NAME="cortex-production"
ECR_REPO="cortex-ai"

echo "🚀 Deploying Cortex to AWS..."

# Step 1: Create ECR repository
echo "Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPO --region $REGION 2>/dev/null || true

# Step 2: Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com

# Step 3: Build image
echo "Building Docker image..."
docker build -t $ECR_REPO:latest -f cloud/Dockerfile .

# Step 4: Tag image
echo "Tagging image..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
docker tag $ECR_REPO:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

# Step 5: Push image
echo "Pushing to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

# Step 6: Deploy CloudFormation
echo "Deploying infrastructure..."
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://cloud/aws-infrastructure.yml \
  --capabilities CAPABILITY_IAM \
  --region $REGION \
  --parameters \
    ParameterKey=Environment,ParameterValue=production \
    ParameterKey=InstanceType,ParameterValue=t3.medium

echo "⏳ Waiting for stack creation (this takes ~10 minutes)..."
aws cloudformation wait stack-create-complete \
  --stack-name $STACK_NAME \
  --region $REGION

echo "✅ Deployment complete!"
echo ""
echo "📊 Check the AWS Console:"
echo "   ECS: https://$REGION.console.aws.amazon.com/ecs"
echo "   CloudFormation: https://$REGION.console.aws.amazon.com/cloudformation"
