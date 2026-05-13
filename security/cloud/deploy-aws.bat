@echo off
REM Cortex AI - AWS Deployment Script (Windows)
REM Generated: 2026-05-12T23:51:29.193Z

set REGION=us-east-1
set STACK_NAME=cortex-production
set ECR_REPO=cortex-ai

echo 🚀 Deploying Cortex to AWS...

REM Step 1: Create ECR repository
echo Creating ECR repository...
aws ecr create-repository --repository-name %ECR_REPO% --region %REGION% 2>nul || echo Repository may already exist

REM Step 2: Login to ECR
echo Logging into ECR...
for /f "tokens=*" %%a in ('aws ecr get-login-password --region %REGION%') do set ECR_PASSWORD=%%a
for /f "tokens=*" %%a in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%a
echo %ECR_PASSWORD% | docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

REM Step 3: Build image
echo Building Docker image...
docker build -t %ECR_REPO%:latest -f cloud/Dockerfile .

REM Step 4: Tag and push
echo Tagging image...
docker tag %ECR_REPO%:latest %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%ECR_REPO%:latest
echo Pushing to ECR...
docker push %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%ECR_REPO%:latest

REM Step 5: Deploy CloudFormation
echo Deploying infrastructure...
aws cloudformation create-stack ^
  --stack-name %STACK_NAME% ^
  --template-body file://cloud/aws-infrastructure.yml ^
  --capabilities CAPABILITY_IAM ^
  --region %REGION% ^
  --parameters ^
    ParameterKey=Environment,ParameterValue=production ^
    ParameterKey=InstanceType,ParameterValue=t3.medium

echo ⏳ Deployment started! Check AWS Console for progress.
echo    ECS: https://%REGION%.console.aws.amazon.com/ecs
echo    CloudFormation: https://%REGION%.console.aws.amazon.com/cloudformation

pause
