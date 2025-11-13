from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dashboard"))
from athena_helper import AthenaHelper

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_api_key

# Logging setup
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

async def log_requests(request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Request: {request.method} {request.url.path} from {client_host}")
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Response: {response.status_code} - Duration: {duration:.2f}s")
    return response

# Rate limiter - 100 requests per minute
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Job Skills Analyzer API",
    description="Real-time job market intelligence (API Key Required)",
    version="2.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)

class SkillInfo(BaseModel):
    skill: str
    job_count: int
    percentage: float

class StatsResponse(BaseModel):
    total_jobs: int
    jobs_with_skills: int
    avg_skills_per_job: float
    unique_skills: int

athena = AthenaHelper()

@app.get("/")
async def root():
    return {
        "message": "Job Skills Analyzer API v2.0",
        "authentication": "API Key required",
        "rate_limit": "100 requests per minute",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/stats", response_model=StatsResponse)
@limiter.limit("100/minute")
async def get_stats(request: Request, api_key: str = Depends(get_api_key)):
    stats_df = athena.get_job_stats()
    skills_df = athena.get_top_skills(limit=100)
    
    return StatsResponse(
        total_jobs=int(stats_df["total_jobs"].iloc[0]),
        jobs_with_skills=int(stats_df["jobs_with_skills"].iloc[0]),
        avg_skills_per_job=float(stats_df["avg_skills"].iloc[0]),
        unique_skills=len(skills_df)
    )

@app.get("/skills/top", response_model=List[SkillInfo])
@limiter.limit("100/minute")
async def get_top_skills(request: Request, limit: int = 10, api_key: str = Depends(get_api_key)):
    df = athena.get_top_skills(limit=limit)
    return [
        SkillInfo(
            skill=row["skill"],
            job_count=int(row["job_count"]),
            percentage=float(row["percentage"])
        )
        for _, row in df.iterrows()
    ]

@app.get("/skills/{skill_name}")
@limiter.limit("100/minute")
async def get_skill_details(request: Request, skill_name: str, api_key: str = Depends(get_api_key)):
    df = athena.get_top_skills(limit=100)
    skill_row = df[df["skill"].str.lower() == skill_name.lower()]
    
    if skill_row.empty:
        raise HTTPException(status_code=404, detail=f"Skill not found")
    
    row = skill_row.iloc[0]
    return {
        "skill": row["skill"],
        "job_count": int(row["job_count"]),
        "percentage": float(row["percentage"])
    }
