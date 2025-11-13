# Job Skills Analyzer - Terraform Infrastructure

This directory contains Infrastructure as Code (IaC) for the Job Skills Analyzer project using Terraform.

## What This Creates

### AWS Resources (7 Services):
1. **3 S3 Buckets**
   - `job-skills-raw-*` - Raw data storage
   - `job-skills-curated-*` - Curated data storage
   - `job-skills-athena-results-*` - Query results cache

2. **Athena Database**
   - Database: `job_skills_db`
   - Table: `jobs_with_skills` (partitioned by date)

3. **Lambda Function**
   - Name: `JobSkillsETLTrigger`
   - Runtime: Python 3.12
   - Trigger: S3 object creation in `processed/` folder

4. **SNS Topic**
   - Name: `job-skills-alerts`
   - Email subscription for notifications

5. **IAM Roles & Policies**
   - Lambda execution role with necessary permissions

6. **CloudWatch Dashboard**
   - Name: `JobSkillsAnalyzer`
   - Monitors S3, Lambda, and Athena metrics

7. **CloudWatch Alarm**
   - Alerts on Lambda errors (>2 in 5 minutes)

8. **EventBridge Rule**
   - Daily schedule at 9 AM UTC

## Prerequisites

1. **Terraform installed** (version >= 1.0)
```bash
   brew install terraform  # macOS
```

2. **AWS credentials configured**
```bash
   export AWS_ACCESS_KEY_ID="your-key"
   export AWS_SECRET_ACCESS_KEY="your-secret"
   export AWS_SESSION_TOKEN="your-token"  # If using AWS Academy
```

3. **AWS CLI installed**
```bash
   brew install awscli  # macOS
```

## Usage

### Initialize Terraform
```bash
cd terraform
terraform init
```

### Preview Changes
```bash
terraform plan
```

### Deploy Infrastructure
```bash
terraform apply
```

### Destroy Infrastructure
```bash
terraform destroy
```

## File Structure
```
terraform/
├── provider.tf    # AWS provider configuration
├── variables.tf   # Input variables
├── main.tf        # Main infrastructure resources
├── outputs.tf     # Output values
└── README.md      # This file
```

## Customization

Edit `variables.tf` to customize:
- AWS region (default: us-east-1)
- Email address for notifications
- Lambda timeout and memory
- Account ID

## Important Notes

⚠️ **AWS Academy Limitations:**
- Some AWS Academy accounts have restricted permissions
- If you encounter permission errors, you may need to create some resources manually

✅ **Idempotency:**
- Running `terraform apply` multiple times is safe
- Terraform only creates/updates resources that changed

🔄 **State Management:**
- Terraform state is stored locally in `terraform.tfstate`
- Do NOT commit `.tfstate` files to Git (already in .gitignore)

## Troubleshooting

**Issue:** Permission denied errors
**Solution:** Ensure AWS Academy lab is running and credentials are current

**Issue:** Resources already exist
**Solution:** Import existing resources or destroy and recreate

**Issue:** S3 bucket name taken
**Solution:** Bucket names are globally unique. Change account_id in variables.tf

## After Deployment

1. **Confirm SNS subscription:** Check your email and click confirmation link
2. **Upload data:** Upload JSONL files to `s3://job-skills-raw-*/processed/`
3. **Test Lambda:** Lambda should trigger automatically on upload
4. **Check dashboard:** View metrics in CloudWatch dashboard

## Cost

All resources are designed to stay within AWS free tier:
- S3: First 5 GB free
- Lambda: 1M free requests/month
- Athena: 1 TB scanned/month free (for new customers)
- CloudWatch: Basic monitoring free

**Estimated cost: $0.00/month** (within free tier)

## Comparison to Manual Setup

| Task | Manual (Console) | Terraform |
|------|-----------------|-----------|
| Initial setup | 2-3 hours | 5 minutes |
| Recreate infrastructure | 2-3 hours | 2 minutes |
| Team onboarding | Hours of documentation | `terraform apply` |
| Version control | Screenshots/docs | Git history |
| Consistency | Error-prone | Guaranteed |


---

## 🏗️ Infrastructure Deployment

### Current Deployment: Manual Setup

The infrastructure is currently deployed using AWS Console and AWS CLI commands. This approach was chosen for educational purposes to gain hands-on experience with each AWS service's configuration.

**Manually Created Resources:**
- 3 S3 buckets (raw data, curated data, query results)
- 1 Athena database with partitioned table
- 1 Lambda function with S3 trigger
- 1 SNS topic with email subscription
- 1 CloudWatch dashboard with custom metrics
- 1 CloudWatch alarm for Lambda errors
- 1 EventBridge rule for scheduling
- IAM roles and policies for service permissions

### Alternative: Terraform (Infrastructure as Code)

Complete Terraform configuration is provided in the [`terraform/`](terraform/) directory, demonstrating Infrastructure as Code practices for reproducible deployments.

**To deploy in a fresh AWS environment:**
```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# Destroy infrastructure (when needed)
terraform destroy
```

**Terraform Benefits:**
- ✅ **Reproducible**: Recreate entire infrastructure in 2 minutes
- ✅ **Version Controlled**: Infrastructure changes tracked in Git
- ✅ **Team Collaboration**: Consistent setup across team members
- ✅ **Multi-Environment**: Easy dev/staging/prod separation
- ✅ **Documentation**: Code serves as infrastructure documentation

**Why Both Approaches?**

Manual deployment provided deep understanding of AWS service configuration. Terraform configuration demonstrates production-ready Infrastructure as Code practices and enables future scalability.

For production deployments or team environments, the Terraform approach is recommended. For learning and experimentation, manual setup offers more visibility into service interactions.

See [`terraform/README.md`](terraform/README.md) for detailed Terraform usage instructions.

