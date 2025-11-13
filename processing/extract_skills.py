#!/usr/bin/env python3
import json
import re
from collections import defaultdict

def load_skills_dictionary(dict_path):
    """Load skills dictionary from JSON file"""
    with open(dict_path, 'r') as f:
        return json.load(f)

def extract_skills_from_text(text, skills_dict):
    """Extract skills from text using dictionary matching"""
    text_lower = text.lower()
    found_skills = []
    
    for canonical_skill, aliases in skills_dict.items():
        for alias in aliases:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append({
                    'skill': canonical_skill,
                    'matched_variant': alias,
                    'confidence': 0.9  # Dictionary match = high confidence
                })
                break  # Found this skill, move to next
    
    return found_skills

def process_job_posting(job, skills_dict):
    """Process a single job posting and extract skills"""
    # Combine title and description for skill extraction
    full_text = f"{job.get('title', '')} {job.get('description', '')}"
    
    skills = extract_skills_from_text(full_text, skills_dict)
    
    return {
        'job_id': job['id'],
        'title': job['title'],
        'company': job['company'],
        'country': job['country'],
        'posted_date': job['posted_date'],
        'skills': skills,
        'skill_count': len(skills)
    }

def main():
    # Load skills dictionary
    print("Loading skills dictionary...")
    skills_dict = load_skills_dictionary('skills-data/skills-dictionary.json')
    print(f"Loaded {len(skills_dict)} canonical skills")
    
    # Load job postings
    print("\nLoading job postings...")
    jobs = []
    with open('skills-data/sample-jobs.json', 'r') as f:
        for line in f:
            jobs.append(json.loads(line))
    print(f"Loaded {len(jobs)} job postings")
    
    # Process each job
    print("\nExtracting skills from jobs...")
    results = []
    for job in jobs:
        result = process_job_posting(job, skills_dict)
        results.append(result)
        print(f"\n{result['title']} ({result['company']})")
        print(f"  Found {result['skill_count']} skills: {', '.join([s['skill'] for s in result['skills']])}")
    
    # Save results
    output_file = 'skills-data/extracted-skills.json'
    with open(output_file, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Summary statistics
    all_skills = defaultdict(int)
    for result in results:
        for skill in result['skills']:
            all_skills[skill['skill']] += 1
    
    print("\n📊 Top Skills Across All Jobs:")
    for skill, count in sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {skill}: {count} jobs")

if __name__ == '__main__':
    main()
