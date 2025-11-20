# 🚀 Deployment Guide - Job Skills Analyzer

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Deploy Infrastructure](#deploy-infrastructure)
4. [Verify Deployment](#verify-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **AWS Account** - AWS Academy or standard
- **Terraform** >= 1.5.0
- **Python** 3.13
- **AWS CLI** configured

### AWS Permissions Required
✅ Lambda, API Gateway, S3, Athena, CloudWatch, SNS, IAM (read LabRole)

⚠️ **AWS Academy Limitations:** Cannot use VPC, EC2, ECS

---

## Quick Start Deployment
```bash
# 1. Configure AWS credentials
export AWS_DEFAULT_REGION=us-east-1

# 2. Package API Lambda
cd api
./package.sh  # Or follow manual steps below

# 3. Deploy with Terraform
cd ../terraform
terraform init
terraform apply

# 4. Get your API URL
terraform output api_gateway_url
```

## Detailed Steps

### Step 1: Package API for Lambda
```bash
cd api
rm -rf package/ api-lambda.zip
mkdir -p package

# Install dependencies for Lambda
pip install \
  --platform manylinux2014_x86_64 \
  --target=package \
  --implementation cp \
  --python-version 3.13 \
  --only-binary=:all: \
  --upgrade \
  -r requirements.txt

# Copy code
cp main.py auth.py lambda_handler.py package/
cp ../dashboard/athena_helper.py package/

# Create zip
cd package && zip -r ../api-lambda.zip . && cd ..
```

### Step 2: Deploy Infrastructure
```bash
cd terraform

terraform init    # Download providers
terraform plan    # Preview changes (should show ~15 resources)
terraform apply   # Deploy (type 'yes')
```

⏱️ **Takes 3-5 minutes** to upload Lambda code and create resources

### Step 3: Test Deployment
```bash
# Get API URL
API_URL=$(terraform output -raw api_gateway_url)

# Test health (no auth)
curl $API_URL/health

# Test stats (with auth)
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
     $API_URL/stats

# Test top skills
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
     "$API_URL/skills/top?limit=5"
```

---

## Troubleshooting

### Lambda "Function already exists"
```bash
terraform import aws_lambda_function.api JobSkillsAPI
terraform apply
```

### "Access Denied" - AWS Academy session expired
```bash
# Get new credentials from AWS Academy
export AWS_ACCESS_KEY_ID="new-key"
export AWS_SECRET_ACCESS_KEY="new-secret"
export AWS_SESSION_TOKEN="new-token"
```

### API Gateway 403 on /docs
Expected behavior - FastAPI docs may not work with Mangum adapter. API endpoints work fine.

### Athena returns no data
```bash
# Upload data manually
aws s3 cp skills-data/kaggle-1k-expanded.jsonl \
    s3://job-skills-raw-624943535027/processed/

# Check Lambda logs
aws logs tail /aws/lambda/JobSkillsETLTrigger --follow
```

---

## Updating the Application
```bash
# 1. Make code changes
# 2. Rebuild Lambda zip
cd api/package && zip -r ../api-lambda.zip . && cd ../..

# 3. Redeploy
cd terraform && terraform apply
```

---

## Destroying Infrastructure
```bash
cd terraform
terraform destroy  # Type 'yes' to confirm
```

⚠️ This deletes ALL resources and data!

---

## Cost Estimate

**Within AWS Free Tier:** ~$0.00/month

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| Lambda | 1M req/mo | <10K | $0 |
| API Gateway | 1M req/mo | <10K | $0 |
| S3 | 5 GB | <1 GB | $0 |
| Athena | - | <1 GB scanned | <$0.01 |
| CloudWatch | Basic | Logs only | $0 |

**Total: ~$0/month** ✅

---

## Deployed Resources

After `terraform apply` you'll have:

- ✅ 2 Lambda functions (API + ETL)
- ✅ API Gateway REST API (public HTTPS endpoint)
- ✅ 3 S3 buckets (raw, curated, results)
- ✅ Athena database with table
- ✅ CloudWatch dashboard + alarms
- ✅ SNS topic for notifications

View in AWS Console:
- Lambda: https://console.aws.amazon.com/lambda
- API Gateway: https://console.aws.amazon.com/apigateway
- S3: https://console.aws.amazon.com/s3
- CloudWatch: https://console.aws.amazon.com/cloudwatch

---

**Deployment Status:** ✅ Production Ready  
**Last Updated:** November 15, 2025
