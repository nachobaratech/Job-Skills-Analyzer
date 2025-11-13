# 📊 Job Market Skills Gap Analyzer

**A cloud-native analytics platform for real-time job market intelligence**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20Athena-orange.svg)](https://aws.amazon.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red.svg)](https://streamlit.io/)

---

## 🎯 Executive Summary

This project analyzes **1,000 real LinkedIn job postings** to identify in-demand skills across the job market. Using cloud-native architecture (AWS S3 + Athena) and NLP techniques, we discovered that **soft skills dominate**: Communication appears in 66.4% of jobs with identified skills, far exceeding technical skills like Python (3.8%) or SQL (4.6%).

**Key Finding:** Employers prioritize communication, leadership, and teamwork over pure technical skills.

---

## 🏆 Key Achievements

- ✅ **1,000 real jobs** processed from Kaggle LinkedIn dataset
- ✅ **848 jobs (84.8%)** with skills successfully identified
- ✅ **70 skills tracked** across 8 categories (66 found in data)
- ✅ **Cloud-native architecture** (AWS S3 + Athena)
- ✅ **Interactive dashboard** (Streamlit)
- ✅ **REST API** with authentication (FastAPI)
- ✅ **Production-grade security** (API keys, rate limiting, logging)

---

## 📊 Major Insights Discovered

### Top 10 Skills by Demand:

1. **Communication** - 66.4% 💬
2. **Sales** - 29.7% 💼
3. **Leadership** - 26.5% 👥
4. **Excel** - 19.2% 📊
5. **Customer Service** - 18.0% 🤝
6. **Teamwork** - 15.8% 🤜🤛
7. **Project Management** - 10.5% 📋
8. **Social Media** - 10.3% 📱
9. **REST API** - 7.2% 🔧
10. **PowerPoint** - 7.1% 📈

### Skill Categories:
- **Soft Skills** (Communication, Leadership, Teamwork): Most demanded
- **Business Tools** (Excel, PowerPoint, CRM): Second tier
- **Technical Skills** (Python, JavaScript, SQL): Third tier
- **Marketing** (Social Media, SEO): Growing demand
- **Design** (UI/UX, Figma): Specialized roles

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACES                       │
│  ┌──────────────────────┐    ┌─────────────────────┐   │
│  │  Streamlit Dashboard │    │   FastAPI REST API   │   │
│  │   localhost:8501     │    │   localhost:8000     │   │
│  └──────────┬───────────┘    └──────────┬──────────┘   │
└─────────────┼────────────────────────────┼──────────────┘
              │                            │
              └──────────┬─────────────────┘
                         │
┌────────────────────────┼────────────────────────────────┐
│                  QUERY LAYER (SQL)                       │
│              ┌─────────▼──────────┐                      │
│              │   AWS Athena       │                      │
│              │  - Serverless SQL  │                      │
│              │  - job_skills_db   │                      │
│              └─────────┬──────────┘                      │
└──────────────────────────┼─────────────────────────────┘
                           │
┌──────────────────────────┼─────────────────────────────┐
│                  DATA LAKE (S3)                          │
│         ┌────────────────▼──────────────┐               │
│         │   job-skills-raw-*            │               │
│         │   processed/dt=2025-11-11/    │               │
│         │   └─ kaggle-jobs.jsonl        │               │
│         │      (763 KB, 1,000 jobs)     │               │
│         └───────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼─────────────────────────────┐
│                PROCESSING LAYER                          │
│         ┌────────────────▼──────────────┐               │
│         │   ETL Pipeline (Python)       │               │
│         │  - extract_skills.py          │               │
│         │  - etl_pipeline.py            │               │
│         │  - NLP skill extraction       │               │
│         └───────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- AWS Account (AWS Academy)
- 2GB RAM minimum
- Internet connection

### Installation
```bash
# 1. Clone/download project
cd ~/mainFolder

# 2. Install dependencies
pip3 install pandas boto3 streamlit plotly fastapi uvicorn python-dotenv slowapi --break-system-packages

# 3. Configure AWS credentials
nano ~/.aws/credentials
# Paste AWS Academy credentials

# 4. Set environment variables
cat > .env << 'EOF'
API_KEY=job-skills-analyzer-secret-key-2024
DATABASE_NAME=job_skills_db
AWS_REGION=us-east-1
EOF
```

### Running the Project

**Terminal 1 - Dashboard:**
```bash
cd ~/mainFolder
streamlit run dashboard/app.py --server.port 8501
```
Open: http://localhost:8501

**Terminal 2 - API:**
```bash
cd ~/mainFolder
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Open: http://localhost:8000/docs

---

## 📁 Project Structure
```
mainFolder/
├── README.md                          # This file
├── .env                               # Environment variables (not in git)
├── .gitignore                         # Git ignore rules
│
├── api/                               # REST API
│   ├── auth.py                        # API key authentication
│   └── main.py                        # FastAPI application (6 endpoints)
│
├── dashboard/                         # Interactive Dashboard
│   ├── app.py                         # Streamlit application
│   └── athena_helper.py               # AWS Athena connector
│
├── processing/                        # Data Processing
│   ├── extract_skills.py              # NLP skill extraction
│   ├── etl_pipeline.py                # ETL orchestration
│   └── advanced_analytics.py          # Category analysis
│
└── skills-data/                       # Data Files
    ├── skills-dictionary.json         # 70 skills with aliases
    ├── kaggle-1k-expanded.jsonl       # Processed jobs (JSONL)
    └── postings.csv                   # Raw Kaggle data (493 MB)
```

---

## 🔐 Security Features

- **API Key Authentication**: All endpoints require `X-API-Key` header
- **Rate Limiting**: 100 requests per minute per IP
- **Request Logging**: All requests logged with duration
- **Environment Variables**: Secrets stored in `.env` file
- **Error Tracking**: Comprehensive error logging

### API Authentication Example:
```bash
# Without key (fails)
curl http://localhost:8000/stats

# With key (works)
curl -H "X-API-Key: job-skills-analyzer-secret-key-2024" \
  http://localhost:8000/stats
```

---

## 📊 API Endpoints

### Public Endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Protected Endpoints (require API key):
- `GET /stats` - Overall statistics
- `GET /skills/top?limit=N` - Top N skills
- `GET /skills/{skill_name}` - Specific skill details

### Example Response:
```json
{
  "total_jobs": 1000,
  "jobs_with_skills": 848,
  "avg_skills_per_job": 2.5,
  "unique_skills": 66
}
```

---

## 💾 Data Pipeline

### 1. Data Source
- **Source**: Kaggle - LinkedIn Job Postings (2023-2024)
- **Original Size**: 3.3M jobs, 493 MB
- **Sample Used**: 1,000 jobs (quality over quantity)

### 2. Skill Extraction
- **Method**: Dictionary-based NLP with regex
- **Dictionary**: 70 skills across 8 categories
- **Aliases**: "k8s" → Kubernetes, "js" → JavaScript
- **Success Rate**: 84.8% jobs with skills identified

### 3. Storage
- **S3 Bucket**: `job-skills-raw-*`
- **Format**: JSONL (one JSON per line)
- **Partitioning**: By date (`dt=2025-11-11`)
- **Size**: 763 KB

### 4. Query Engine
- **Tool**: AWS Athena (serverless SQL)
- **Database**: `job_skills_db`
- **Table**: `jobs_with_skills`
- **Query Time**: 0.5-2 seconds average

---

## 🧪 Testing

### Verify All Components:
```bash
cd ~/mainFolder

# Test AWS credentials
aws sts get-caller-identity

# Test S3 data
aws s3 ls s3://job-skills-raw-223280412524/processed/ --recursive

# Test Athena
python3 -c "from dashboard.athena_helper import AthenaHelper; \
  athena = AthenaHelper(); \
  print(athena.get_job_stats())"

# Test API
curl http://localhost:8000/health

# Test Dashboard
# Open http://localhost:8501 in browser
```

---

## 📈 Performance Metrics

- **Query Speed**: 0.5-2 seconds (Athena)
- **API Response**: 3-4 seconds (includes Athena query)
- **Dashboard Load**: 4-5 seconds
- **Storage Cost**: $0.00 (AWS Free Tier)
- **Query Cost**: $0.00 (under 1 TB scanned)

---

## 🎓 Skills Demonstrated

### Cloud Computing
- AWS S3 (object storage, data lakes)
- AWS Athena (serverless SQL)
- IAM (security, access control)
- Cloud architecture design

### Data Engineering
- ETL pipeline development
- Data lake architecture (bronze/silver/gold)
- Schema design
- Data quality assurance

### Programming
- Python (pandas, boto3, regex)
- SQL (complex queries with UNNEST, CROSS JOIN)
- REST API development (FastAPI)
- Web applications (Streamlit)

### Data Analysis
- NLP (text extraction, pattern matching)
- Statistical analysis
- Data visualization (Plotly)
- Business intelligence

### Software Engineering
- API design and documentation
- Authentication and authorization
- Rate limiting
- Error handling and logging
- Environment configuration

---

## 🔮 Future Enhancements

### Short-term:
- [ ] Add more data sources (Indeed, Glassdoor)
- [ ] Implement skill trending over time
- [ ] Add location-based analysis
- [ ] Export reports to PDF

### Long-term:
- [ ] Machine learning skill predictions
- [ ] Real-time data ingestion (Lambda)
- [ ] User accounts and saved searches
- [ ] Mobile application
- [ ] Integration with resume parsers

---

## 📝 Lessons Learned

1. **Data Quality Matters**: Real-world data is messy - the Kaggle dataset had significant corruption issues
2. **Soft Skills Win**: Our biggest insight - communication beats coding skills
3. **Dictionary Approach Works**: Simple regex matching was 84.8% effective
4. **Cloud is Cost-Effective**: Entire project ran on AWS Free Tier ($0 cost)
5. **Multiple Access Methods**: Dashboard + API = maximum value

---

## 👥 Team

- **Ignacio Baratech** - Data Engineering, Cloud Architecture, NLP
- **Maxence Jeux** - Dashboard Development, Data Analysis
- **Alain Castaños** - API Development, Security Implementation

**Course**: Cloud Solutions  
**Institution**: ESADE Business School  
**Instructor**: René Serral  
**Date**: November 2025

---

## 📚 References

- **Dataset**: [LinkedIn Job Postings 2023-2024](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) by Arsh Koneru
- **AWS Documentation**: https://docs.aws.amazon.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://streamlit.io/
- **Pandas**: https://pandas.pydata.org/

---

## 📄 License

This project was created for educational purposes as part of ESADE Business School's Cloud Solutions course.

---

## 🙏 Acknowledgments

- René Serral for excellent guidance throughout the project
- AWS Academy for providing cloud resources
- Arsh Koneru for the LinkedIn dataset
- ESADE Business School for the opportunity

---

**Built with ❤️ using AWS, Python, and open-source tools**

*Last Updated: November 11, 2025*
