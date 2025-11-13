#!/usr/bin/env python3
"""
ETL Pipeline for Job Skills Analyzer
Reads raw job postings, cleans and normalizes them, extracts skills
"""
import json
import re
from datetime import datetime
from collections import defaultdict

def clean_text(text):
    """Remove extra whitespace and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_job(job):
    """Normalize a job posting to standardized schema"""
    return {
        'job_id': job.get('id', ''),
        'title': clean_text(job.get('title', '')),
        'company': clean_text(job.get('company', '')),
        'location': clean_text(job.get('location', '')),
        'country': job.get('country', 'UNKNOWN'),
        'description': clean_text(job.get('description', '')),
        'posted_date': job.get('posted_date', ''),
        'source': job.get('source', 'unknown'),
        'processed_at': datetime.now().isoformat(),
        'schema_version': '1.0'
    }

def extract_skills(text, skills_dict):
    """Extract skills from text using dictionary"""
    text_lower = text.lower()
    found_skills = []
    
    for canonical_skill, aliases in skills_dict.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(canonical_skill)
                break
    
    return found_skills

def process_jobs(raw_jobs_file, skills_dict_file, output_file):
    """Main ETL process"""
    
    # Load skills dictionary
    print("📚 Loading skills dictionary...")
    with open(skills_dict_file, 'r') as f:
        skills_dict = json.load(f)
    print(f"   Loaded {len(skills_dict)} skills")
    
    # Process jobs
    print("\n📊 Processing jobs...")
    processed_jobs = []
    skill_stats = defaultdict(int)
    
    with open(raw_jobs_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                raw_job = json.loads(line)
                
                # Normalize job
                clean_job = normalize_job(raw_job)
                
                # Extract skills
                full_text = f"{clean_job['title']} {clean_job['description']}"
                skills = extract_skills(full_text, skills_dict)
                
                # Add skills to job
                clean_job['skills'] = skills
                clean_job['skill_count'] = len(skills)
                
                processed_jobs.append(clean_job)
                
                # Update stats
                for skill in skills:
                    skill_stats[skill] += 1
                
                print(f"   ✓ Processed: {clean_job['title']} ({len(skills)} skills)")
                
            except json.JSONDecodeError as e:
                print(f"   ✗ Error on line {line_num}: {e}")
                continue
    
    # Save processed jobs
    print(f"\n💾 Saving {len(processed_jobs)} processed jobs...")
    with open(output_file, 'w') as f:
        for job in processed_jobs:
            f.write(json.dumps(job) + '\n')
    
    # Print summary
    print(f"\n✅ ETL Complete!")
    print(f"   Jobs processed: {len(processed_jobs)}")
    print(f"   Unique skills found: {len(skill_stats)}")
    print(f"   Output: {output_file}")
    
    print(f"\n📈 Top 10 Skills:")
    for skill, count in sorted(skill_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(processed_jobs)) * 100
        print(f"   {skill:20s}: {count:2d} jobs ({percentage:5.1f}%)")
    
    return processed_jobs, skill_stats

if __name__ == '__main__':
    process_jobs(
        'skills-data/all-jobs.json',
        'skills-data/skills-dictionary.json',
        'skills-data/processed-jobs.json'
    )
