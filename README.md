# Job Skills Analyzer - Cloud-Native Analytics Platform

🚀 **Real-time job market intelligence powered by AWS serverless architecture**

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20API%20Gateway%20%7C%20Athena-orange)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)](https://www.terraform.io/)

## 📊 Live API Endpoint

**Base URL:** `https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev`

**Try it now:**
```bash
# Health check
curl https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev/health

# Get top skills (requires API key)
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
     "https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev/skills/top?limit=5"

# Get statistics
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
     https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev/stats
```

## 🏗️ Architecture

**Fully Serverless AWS Architecture:**
```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│   API Gateway (REST API)             │
│   • Rate Limiting: 100 req/min       │
│   • HTTPS Only                       │
│   • API Key Authentication           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Lambda Function (FastAPI)          │
│   • Runtime: Python 3.13             │
│   • Memory: 512MB                    │
│   • Timeout: 30s                     │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Amazon Athena (SQL Analytics)      │
│   • Serverless Query Engine          │
│   • Query S3 Data Lake               │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   S3 Data Lake (3-Tier)              │
│   • Raw: job-skills-raw-*            │
│   • Curated: job-skills-curated-*    │
│   • Results: job-skills-athena-*     │
└──────────────────────────────────────┘

       Monitoring & Alerting
              ▼
┌──────────────────────────────────────┐
│   CloudWatch + SNS                   │
│   • Custom Dashboards                │
│   • Error Alarms                     │
│   • Email Notifications              │
└──────────────────────────────────────┘
```

## 🔑 Key Features

### ✅ **Production-Grade Infrastructure**
- **100% Serverless** - No servers to manage, auto-scaling
- **Infrastructure as Code** - Fully reproducible with Terraform
- **Event-Driven** - S3 triggers → Lambda → Athena updates
- **Cost-Optimized** - Pay-per-request, ~$0/month within free tier

### ✅ **RESTful API**
- **FastAPI Framework** - Modern, fast, OpenAPI compliant
- **Rate Limited** - 100 requests/minute, 10K/day quota
- **Authenticated** - API key protection
- **Monitored** - CloudWatch logs and metrics

### ✅ **Data Analytics**
- **1000+ Job Postings** analyzed
- **66 Unique Skills** tracked
- **Real-time Queries** via Athena
- **Skill Co-occurrence** analysis

### ✅ **Observability**
- CloudWatch Dashboard with custom metrics
- Lambda execution logs
- Error rate alarms (>5 errors in 5min)
- Latency monitoring (threshold: 5s)
- SNS email notifications

## 📁 Project Structure
```
mainFolder/
├── api/                    # FastAPI Application
│   ├── main.py            # API endpoints
│   ├── auth.py            # API key authentication
│   ├── lambda_handler.py  # Mangum adapter for Lambda
│   └── requirements.txt   # Python dependencies
│
├── dashboard/             # Streamlit Dashboard
│   ├── app.py            # Dashboard UI
│   └── athena_helper.py  # Athena query helper
│
├── lambda/               # Lambda Functions
│   └── etl_trigger.py   # S3 event handler
│
├── processing/          # Data Processing Scripts
│   ├── etl_pipeline.py # ETL logic
│   └── extract_skills.py # NLP skill extraction
│
├── terraform/          # Infrastructure as Code
│   ├── main.tf        # Core infrastructure
│   ├── api_gateway.tf # API Gateway + Lambda
│   ├── variables.tf   # Input variables
│   └── outputs.tf     # Output values
│
└── skills-data/       # Data Assets
    ├── kaggle-1k-expanded.jsonl  # Job postings
    └── skills-dictionary.json     # Skills taxonomy
```

## 🚀 Deployment

### Prerequisites
- AWS Account (AWS Academy or standard)
- Terraform >= 1.5
- Python 3.13
- AWS CLI configured

### Quick Start
```bash
# 1. Clone the repository
git clone <your-repo>
cd mainFolder

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 3. Get your API URL
terraform output api_gateway_url

# 4. Test the API
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
     $(terraform output -raw api_gateway_url)/health
```

### What Gets Deployed

| Resource | Purpose | Cost |
|----------|---------|------|
| **3 S3 Buckets** | Data lake (raw, curated, results) | ~$0 (5GB free) |
| **2 Lambda Functions** | API + ETL processing | ~$0 (1M free req/month) |
| **API Gateway** | HTTPS REST API | ~$0 (1M free req/month) |
| **Athena Database** | Serverless SQL analytics | Pay per query (~$5/TB) |
| **CloudWatch** | Monitoring & logs | ~$0 (basic free) |
| **SNS Topic** | Email notifications | ~$0 (1000 free/month) |

**Total Monthly Cost:** ~$0 within AWS free tier ✅

## 📊 API Endpoints

### `GET /health`
Health check endpoint (no auth required)

**Response:**
```json
{"status": "healthy"}
```

### `GET /stats`
Overall job market statistics

**Headers:** `X-API-Key: <your-api-key>`

**Response:**
```json
{
  "total_jobs": 1000,
  "jobs_with_skills": 848,
  "avg_skills_per_job": 2.528,
  "unique_skills": 66
}
```

### `GET /skills/top?limit=10`
Top N most demanded skills

**Headers:** `X-API-Key: <your-api-key>`

**Response:**
```json
[
  {
    "skill": "Communication",
    "job_count": 563,
    "percentage": 66.39
  },
  {
    "skill": "Sales",
    "job_count": 252,
    "percentage": 29.72
  }
]
```

### `GET /skills/{skill_name}`
Details for a specific skill

**Headers:** `X-API-Key: <your-api-key>`

**Example:** `/skills/Python`

## 🔧 Local Development

### Run API Locally
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload

# Test locally
curl http://localhost:8000/health
```

### Run Dashboard Locally
```bash
cd dashboard
pip install streamlit boto3 pandas
streamlit run app.py
```

### Process Data
```bash
cd processing
python etl_pipeline.py
```

## 🛡️ Security

- ✅ **API Key Authentication** - All endpoints except /health require valid API key
- ✅ **Rate Limiting** - 100 requests/minute per IP
- ✅ **HTTPS Only** - API Gateway enforces TLS
- ✅ **IAM Least Privilege** - Lambda uses minimal permissions
- ✅ **Private Data** - S3 buckets not publicly accessible
- ✅ **Monitoring** - CloudWatch alarms for anomalies

## 📈 Monitoring

**CloudWatch Dashboard:** `JobSkillsAnalyzer`

**Metrics tracked:**
- API request count
- Lambda invocations
- Error rates
- Response latency (p50, p95, p99)
- Athena query execution time

**Alarms configured:**
- Lambda errors >2 in 5 minutes
- API errors >5 in 5 minutes
- API latency >5 seconds

## 🎓 Course Alignment

This project demonstrates mastery of:

### ✅ Module 7: Serverless Architecture
- Lambda functions (API + ETL)
- Event-driven design (S3 → Lambda)
- API Gateway integration
- Serverless data processing

### ✅ Module 8: Infrastructure as Code
- Complete Terraform configuration
- Reproducible deployments
- State management
- Modular design

### ✅ Module 9: Monitoring & Observability
- CloudWatch dashboards
- Custom metrics
- Alarms and notifications
- Structured logging

### ✅ Module 10: Data Processing & Analytics
- ETL pipeline
- Data lake architecture
- Athena serverless analytics
- Partitioned data storage

## 🏆 Results

**Dataset:** 1000 job postings from Kaggle

**Key Insights:**
- **Communication** is the #1 skill (66% of jobs)
- **Technical skills** (Python, SQL) in 15-20% of jobs
- **Leadership** required in 27% of positions
- **Average:** 2.5 skills per job posting

**Top 10 Skills:**
1. Communication (66.39%)
2. Sales (29.72%)
3. Leadership (26.53%)
4. Excel (19.22%)
5. Customer Service (18.04%)
6. Python (15.92%)
7. SQL (14.62%)
8. Problem Solving (13.56%)
9. Teamwork (12.74%)
10. Project Management (11.79%)

## 🔄 ETL Pipeline

**Data Flow:**
```
Raw Data (S3) → Lambda Trigger → Athena MSCK REPAIR → 
Curated Data → API Queries → Dashboard Visualization
```

**Automation:**
- Manual upload triggers Lambda automatically
- Lambda updates Athena table partitions
- SNS sends email notification
- Dashboard shows updated data immediately

## 🎯 Future Enhancements

- [ ] **Cognito Authentication** - Replace API key with JWT
- [ ] **Advanced NLP** - spaCy NER for skill extraction
- [ ] **Automated Scraping** - EventBridge scheduled data collection
- [ ] **Time-Series Analysis** - Track skill trends over time
- [ ] **Predictive Analytics** - Forecast emerging skills
- [ ] **GraphQL API** - More flexible queries
- [ ] **React Dashboard** - Modern web UI

## 📝 License

Educational project for Cloud Solutions course.

## 👥 Team

- Ignacio Baratech
- Maxence Jeux
- Alain Castaños

**Professor:** René Serral  
**Course:** Cloud Solutions  
**Institution:** ESADE Business School

---

**Built with ❤️ using AWS, Python, and Terraform**
